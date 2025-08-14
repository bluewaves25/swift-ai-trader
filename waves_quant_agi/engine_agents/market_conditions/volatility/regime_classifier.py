import time
from typing import Dict, Any, List
import redis
from ..logs.failure_agent_logger import FailureAgentLogger
from ..logs.incident_cache import IncidentCache

class RegimeClassifier:
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
        self.volatility_threshold = config.get("volatility_threshold", 0.015)  # 1.5% price change

    async def classify_volatility_regime(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify volatility regime using real-time statistical analysis and market dynamics."""
        try:
            regimes = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                price_changes = data.get("price_changes", [])
                volume = float(data.get("volume", 0.0))
                spread = float(data.get("spread", 0.001))
                order_imbalance = float(data.get("order_imbalance", 0.0))
                time_series_length = len(price_changes)
                
                if time_series_length < 10:  # Need minimum data for regime classification
                    continue
                
                # Real-time regime analysis based on multiple factors
                regime_type = self._classify_regime_type(
                    price_changes, volume, spread, order_imbalance
                )
                
                regime_confidence = self._calculate_regime_confidence(
                    price_changes, volume, spread, time_series_length
                )
                
                regime_characteristics = self._extract_regime_characteristics(
                    price_changes, volume, spread, order_imbalance
                )
                
                regime = {
                    "type": "volatility_regime_classification",
                    "symbol": symbol,
                    "regime_type": regime_type,
                    "regime_confidence": regime_confidence,
                    "regime_characteristics": regime_characteristics,
                    "price_changes": price_changes,
                    "volume": volume,
                    "spread": spread,
                    "order_imbalance": order_imbalance,
                    "time_series_length": time_series_length,
                    "timestamp": int(time.time()),
                    "description": f"Volatility regime for {symbol}: {regime_type} (confidence: {regime_confidence:.2f})"
                }
                
                regimes.append(regime)
                self.logger.log_issue(regime)
                self.cache.store_incident(regime)
                self.redis_client.set(f"market_conditions:volatility_regime:{symbol}", str(regime), ex=604800)
            
            summary = {
                "type": "volatility_regime_summary",
                "regime_count": len(regimes),
                "timestamp": int(time.time()),
                "description": f"Classified volatility regimes for {len(regimes)} symbols"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return regimes
            
        except Exception as e:
            self.logger.log(f"Error classifying volatility regime: {e}")
            self.cache.store_incident({
                "type": "volatility_regime_error",
                "timestamp": int(time.time()),
                "description": f"Error classifying volatility regime: {str(e)}"
            })
            return []
    
    def _classify_regime_type(self, price_changes: List[float], volume: float, 
                             spread: float, order_imbalance: float) -> str:
        """Classify volatility regime using real-time statistical analysis."""
        try:
            # Calculate statistical measures
            volatility = self._calculate_realized_volatility(price_changes)
            skewness = self._calculate_skewness(price_changes)
            kurtosis = self._calculate_kurtosis(price_changes)
            
            # Volume analysis
            volume_factor = min(1.0, volume / 100000.0)  # Normalize to 100k volume
            
            # Spread analysis
            spread_factor = max(0.0, 1.0 - (spread / 0.02))  # Normalize to 2% spread
            
            # Order imbalance analysis
            imbalance_factor = abs(order_imbalance)
            
            # Regime classification logic
            if volatility > 0.05:  # High volatility
                if skewness > 0.5 and kurtosis > 5:
                    return "extreme_volatility"
                elif volume_factor > 0.7 and spread_factor < 0.5:
                    return "high_volatility_stressed"
                else:
                    return "high_volatility"
            
            elif volatility > 0.02:  # Medium volatility
                if imbalance_factor > 0.6:
                    return "medium_volatility_imbalanced"
                elif volume_factor > 0.5:
                    return "medium_volatility_active"
                else:
                    return "medium_volatility"
            
            else:  # Low volatility
                if spread_factor > 0.8 and volume_factor < 0.3:
                    return "low_volatility_stable"
                elif imbalance_factor < 0.2:
                    return "low_volatility_balanced"
                else:
                    return "low_volatility"
                    
        except Exception as e:
            self.logger.log_error(f"Error classifying regime type: {e}")
            return "unknown_regime"
    
    def _calculate_realized_volatility(self, price_changes: List[float]) -> float:
        """Calculate realized volatility from price changes."""
        try:
            if len(price_changes) < 2:
                return 0.0
            
            # Calculate standard deviation of price changes
            mean_change = sum(price_changes) / len(price_changes)
            variance = sum((x - mean_change) ** 2 for x in price_changes) / len(price_changes)
            
            return (variance ** 0.5) if variance > 0 else 0.0
            
        except Exception as e:
            self.logger.log_error(f"Error calculating realized volatility: {e}")
            return 0.0
    
    def _calculate_skewness(self, price_changes: List[float]) -> float:
        """Calculate skewness of price changes."""
        try:
            if len(price_changes) < 3:
                return 0.0
            
            mean_change = sum(price_changes) / len(price_changes)
            std_dev = (sum((x - mean_change) ** 2 for x in price_changes) / len(price_changes)) ** 0.5
            
            if std_dev == 0:
                return 0.0
            
            # Calculate skewness
            skewness = sum(((x - mean_change) / std_dev) ** 3 for x in price_changes) / len(price_changes)
            return skewness
            
        except Exception as e:
            self.logger.log_error(f"Error calculating skewness: {e}")
            return 0.0
    
    def _calculate_kurtosis(self, price_changes: List[float]) -> float:
        """Calculate kurtosis of price changes."""
        try:
            if len(price_changes) < 4:
                return 0.0
            
            mean_change = sum(price_changes) / len(price_changes)
            std_dev = (sum((x - mean_change) ** 2 for x in price_changes) / len(price_changes)) ** 0.5
            
            if std_dev == 0:
                return 0.0
            
            # Calculate kurtosis
            kurtosis = sum(((x - mean_change) / std_dev) ** 4 for x in price_changes) / len(price_changes)
            return kurtosis
            
        except Exception as e:
            self.logger.log_error(f"Error calculating kurtosis: {e}")
            return 0.0
    
    def _calculate_regime_confidence(self, price_changes: List[float], volume: float, 
                                   spread: float, time_series_length: int) -> float:
        """Calculate confidence in regime classification."""
        try:
            # Data quality factors
            data_length_factor = min(1.0, time_series_length / 50.0)  # Normalize to 50 data points
            volume_quality = min(1.0, volume / 100000.0)  # Normalize to 100k volume
            spread_quality = max(0.0, 1.0 - (spread / 0.02))  # Normalize to 2% spread
            
            # Statistical quality factors
            volatility = self._calculate_realized_volatility(price_changes)
            volatility_quality = min(1.0, volatility / 0.1)  # Normalize to 10% volatility
            
            # Combined confidence
            confidence = (
                data_length_factor * 0.3 +
                volume_quality * 0.25 +
                spread_quality * 0.2 +
                volatility_quality * 0.25
            )
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.log_error(f"Error calculating regime confidence: {e}")
            return 0.5
    
    def _extract_regime_characteristics(self, price_changes: List[float], volume: float, 
                                      spread: float, order_imbalance: float) -> Dict[str, Any]:
        """Extract detailed characteristics of the volatility regime."""
        try:
            volatility = self._calculate_realized_volatility(price_changes)
            skewness = self._calculate_skewness(price_changes)
            kurtosis = self._calculate_kurtosis(price_changes)
            
            characteristics = {
                "volatility_level": "high" if volatility > 0.05 else "medium" if volatility > 0.02 else "low",
                "price_distribution": "right_skewed" if skewness > 0.3 else "left_skewed" if skewness < -0.3 else "symmetric",
                "tail_risk": "high" if kurtosis > 5 else "medium" if kurtosis > 3 else "low",
                "volume_profile": "high" if volume > 50000 else "medium" if volume > 10000 else "low",
                "spread_profile": "tight" if spread < 0.002 else "normal" if spread < 0.01 else "wide",
                "order_flow": "imbalanced" if abs(order_imbalance) > 0.5 else "balanced",
                "regime_stability": "stable" if volatility < 0.02 else "moderate" if volatility < 0.05 else "unstable"
            }
            
            return characteristics
            
        except Exception as e:
            self.logger.log_error(f"Error extracting regime characteristics: {e}")
            return {"error": "Unable to extract characteristics"}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of regime classification results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))