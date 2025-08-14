import time
from typing import Dict, Any, List
import redis
from ..logs.failure_agent_logger import FailureAgentLogger
from ..logs.incident_cache import IncidentCache

class SupplySourceTracer:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.source_threshold = config.get("source_threshold", 0.5)  # Confidence score for source

    async def trace_supply_source(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Trace supply source using real-time order book and market microstructure analysis."""
        try:
            sources = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                volume = float(data.get("volume", 0.0))
                offers = float(data.get("offers", 0.0))
                order_book_depth = int(data.get("order_book_depth", 0))
                spread = float(data.get("spread", 0.001))
                order_size_distribution = data.get("order_size_distribution", [])
                time_of_day = data.get("time_of_day", 0)  # Hour of day (0-23)
                
                # Real-time source analysis based on multiple factors
                source_type = self._analyze_supply_source(
                    volume, offers, order_book_depth, spread, order_size_distribution, time_of_day
                )
                
                source_confidence = self._calculate_source_confidence(
                    volume, order_book_depth, spread, order_size_distribution
                )
                
                source_characteristics = self._extract_source_characteristics(
                    volume, offers, spread, order_size_distribution
                )
                
                source = {
                    "type": "supply_source_trace",
                    "symbol": symbol,
                    "source_type": source_type,
                    "source_confidence": source_confidence,
                    "source_characteristics": source_characteristics,
                    "volume": volume,
                    "offers": offers,
                    "order_book_depth": order_book_depth,
                    "spread": spread,
                    "order_size_distribution": order_size_distribution,
                    "time_of_day": time_of_day,
                    "timestamp": int(time.time()),
                    "description": f"Supply source for {symbol}: {source_type} (confidence: {source_confidence:.2f})"
                }
                
                sources.append(source)
                self.logger.log_issue(source)
                self.cache.store_incident(source)
                self.redis_client.set(f"market_conditions:supply_source:{symbol}", str(source), ex=604800)
            
            summary = {
                "type": "supply_source_summary",
                "source_count": len(sources),
                "timestamp": int(time.time()),
                "description": f"Traced supply sources for {len(sources)} symbols"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return sources
            
        except Exception as e:
            self.logger.log(f"Error tracing supply source: {e}")
            self.cache.store_incident({
                "type": "supply_source_error",
                "timestamp": int(time.time()),
                "description": f"Error tracing supply source: {str(e)}"
            })
            return []
    
    def _analyze_supply_source(self, volume: float, offers: float, order_book_depth: int, 
                              spread: float, order_size_distribution: List[float], time_of_day: int) -> str:
        """Analyze supply source using real-time market microstructure data."""
        try:
            # Market maker indicators
            if self._is_market_maker_activity(volume, offers, spread, order_size_distribution):
                return "market_maker"
            
            # Institutional indicators
            if self._is_institutional_activity(volume, order_book_depth, order_size_distribution):
                return "institutional"
            
            # Retail indicators
            if self._is_retail_activity(volume, order_size_distribution, time_of_day):
                return "retail"
            
            # Algorithmic trading indicators
            if self._is_algorithmic_activity(volume, offers, spread, time_of_day):
                return "algorithmic"
            
            # Natural supply indicators
            if self._is_natural_supply(volume, offers, spread):
                return "natural_supply"
            
            return "unknown_source"
            
        except Exception as e:
            self.logger.log_error(f"Error analyzing supply source: {e}")
            return "unknown_source"
    
    def _is_market_maker_activity(self, volume: float, offers: float, spread: float, 
                                 order_size_distribution: List[float]) -> bool:
        """Detect market maker activity patterns."""
        try:
            # Market makers typically maintain tight spreads
            tight_spread = spread < 0.002  # 0.2% spread
            
            # Consistent order sizes
            consistent_sizes = len(set(order_size_distribution)) <= 3 if order_size_distribution else False
            
            # Balanced volume between bids and offers
            balanced_volume = 0.8 <= (offers / max(volume, 1)) <= 1.2
            
            return tight_spread and consistent_sizes and balanced_volume
            
        except Exception as e:
            self.logger.log_error(f"Error detecting market maker activity: {e}")
            return False
    
    def _is_institutional_activity(self, volume: float, order_book_depth: int, 
                                 order_size_distribution: List[float]) -> bool:
        """Detect institutional trading activity."""
        try:
            # Large order sizes
            large_orders = any(size > 10000 for size in order_size_distribution) if order_size_distribution else False
            
            # Deep order book impact
            deep_impact = order_book_depth > 10000
            
            # High volume
            high_volume = volume > 50000
            
            return large_orders and deep_impact and high_volume
            
        except Exception as e:
            self.logger.log_error(f"Error detecting institutional activity: {e}")
            return False
    
    def _is_retail_activity(self, volume: float, order_size_distribution: List[float], 
                           time_of_day: int) -> bool:
        """Detect retail trading activity."""
        try:
            # Small order sizes
            small_orders = all(size < 1000 for size in order_size_distribution) if order_size_distribution else False
            
            # Moderate volume
            moderate_volume = 1000 <= volume <= 10000
            
            # Trading hours (retail activity peaks during market hours)
            market_hours = 9 <= time_of_day <= 16
            
            return small_orders and moderate_volume and market_hours
            
        except Exception as e:
            self.logger.log_error(f"Error detecting retail activity: {e}")
            return False
    
    def _is_algorithmic_activity(self, volume: float, offers: float, spread: float, 
                                time_of_day: int) -> bool:
        """Detect algorithmic trading activity."""
        try:
            # High frequency characteristics
            high_frequency = volume > 100000 and offers > 50000
            
            # Dynamic spread management
            dynamic_spread = 0.001 <= spread <= 0.01
            
            # 24/7 activity (not limited to market hours)
            continuous_activity = True  # Algos trade continuously
            
            return high_frequency and dynamic_spread and continuous_activity
            
        except Exception as e:
            self.logger.log_error(f"Error detecting algorithmic activity: {e}")
            return False
    
    def _is_natural_supply(self, volume: float, offers: float, spread: float) -> bool:
        """Detect natural supply (non-trading related)."""
        try:
            # Natural supply typically has wider spreads
            natural_spread = spread > 0.005  # 0.5% spread
            
            # Moderate volume
            moderate_volume = 1000 <= volume <= 50000
            
            # Offers roughly match volume
            balanced_offers = 0.7 <= (offers / max(volume, 1)) <= 1.3
            
            return natural_spread and moderate_volume and balanced_offers
            
        except Exception as e:
            self.logger.log_error(f"Error detecting natural supply: {e}")
            return False
    
    def _calculate_source_confidence(self, volume: float, order_book_depth: int, 
                                   spread: float, order_size_distribution: List[float]) -> float:
        """Calculate confidence in source identification."""
        try:
            # Data quality factors
            volume_quality = min(1.0, volume / 100000.0)  # Normalize to 100k volume
            depth_quality = min(1.0, order_book_depth / 50000.0)  # Normalize to 50k depth
            spread_quality = max(0.0, 1.0 - (spread / 0.02))  # Normalize to 2% spread
            
            # Distribution quality
            distribution_quality = 1.0 if len(order_size_distribution) >= 3 else 0.5
            
            # Combined confidence
            confidence = (
                volume_quality * 0.3 +
                depth_quality * 0.3 +
                spread_quality * 0.2 +
                distribution_quality * 0.2
            )
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.log_error(f"Error calculating source confidence: {e}")
            return 0.5
    
    def _extract_source_characteristics(self, volume: float, offers: float, spread: float, 
                                      order_size_distribution: List[float]) -> Dict[str, Any]:
        """Extract detailed characteristics of the supply source."""
        try:
            characteristics = {
                "volume_profile": "high" if volume > 50000 else "medium" if volume > 10000 else "low",
                "spread_profile": "tight" if spread < 0.002 else "normal" if spread < 0.01 else "wide",
                "order_size_profile": "large" if any(size > 10000 for size in order_size_distribution) else "medium" if any(size > 1000 for size in order_size_distribution) else "small",
                "liquidity_provider": offers > volume * 0.8,
                "aggressive_supplier": offers > volume * 1.2
            }
            
            return characteristics
            
        except Exception as e:
            self.logger.log_error(f"Error extracting source characteristics: {e}")
            return {"error": "Unable to extract characteristics"}