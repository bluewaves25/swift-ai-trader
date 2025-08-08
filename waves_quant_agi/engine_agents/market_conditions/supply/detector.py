import time
from typing import Dict, Any, List, Optional
import redis
from ..logs.market_conditions_logger import MarketConditionsLogger

class SupplyDetector:
    """Advanced supply behavior detector with quantum-inspired analysis."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = self._init_redis()
        self.logger = MarketConditionsLogger("supply_detector", self.redis_client)
        
        # Configuration parameters
        self.volume_threshold = config.get("volume_threshold", 1.5)
        self.price_threshold = config.get("price_threshold", 0.02)  # 2% price change
        self.volatility_threshold = config.get("volatility_threshold", 0.05)  # 5% volatility
        self.analysis_window = config.get("analysis_window", 3600)  # 1 hour
        
        # Performance tracking
        self.stats = {
            "total_analyses": 0,
            "high_supply_detected": 0,
            "low_supply_detected": 0,
            "normal_supply_detected": 0,
            "start_time": time.time()
        }

    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            return redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0),
                decode_responses=True
            )
        except Exception as e:
            self.logger.log_error(f"Failed to initialize Redis: {e}")
            return None

    async def classify_supply_behavior(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Classify real-time supply behavior based on volume, price, and volatility."""
        try:
            if not market_data:
                self.logger.log("No market data provided for supply analysis")
                return {}

            behaviors = []
            for data in market_data:
                try:
                    symbol = data.get("symbol", "unknown")
                    volume = float(data.get("volume", 0.0))
                    offers = float(data.get("offers", 0.0))
                    avg_volume = float(data.get("avg_volume", 1.0))
                    price = float(data.get("price", 0.0))
                    price_change = float(data.get("price_change", 0.0))
                    volatility = float(data.get("volatility", 0.0))
                    
                    # Enhanced behavior classification
                    behavior = self._classify_behavior(volume, avg_volume, price_change, volatility)
                    
                    # Calculate supply strength
                    supply_strength = self._calculate_supply_strength(volume, offers, price_change)
                    
                    result = {
                        "type": "supply_behavior",
                        "symbol": symbol,
                        "behavior": behavior,
                        "supply_strength": supply_strength,
                        "volume": volume,
                        "offers": offers,
                        "price_change": price_change,
                        "volatility": volatility,
                        "timestamp": int(time.time()),
                        "description": f"Supply behavior for {symbol}: {behavior} (strength: {supply_strength:.2f})"
                    }
                    
                    behaviors.append(result)
                    self.logger.log_supply_behavior(symbol, result)
                    
                    # Update stats
                    self.stats["total_analyses"] += 1
                    if behavior == "high_supply":
                        self.stats["high_supply_detected"] += 1
                    elif behavior == "low_supply":
                        self.stats["low_supply_detected"] += 1
                    else:
                        self.stats["normal_supply_detected"] += 1
                    
                except (ValueError, TypeError) as e:
                    self.logger.log_error(f"Error processing market data: {e}", {"data": data})
                    continue

            # Create summary
            summary = {
                "type": "supply_behavior_summary",
                "behavior_count": len(behaviors),
                "high_supply_count": self.stats["high_supply_detected"],
                "low_supply_count": self.stats["low_supply_detected"],
                "normal_supply_count": self.stats["normal_supply_detected"],
                "timestamp": int(time.time()),
                "description": f"Analyzed supply behavior for {len(behaviors)} symbols"
            }
            
            # Store summary in Redis
            if self.redis_client:
                try:
                    self.redis_client.hset("market_conditions:supply_summary", mapping=summary)
                    self.redis_client.expire("market_conditions:supply_summary", 86400)  # 24 hours
                except Exception as e:
                    self.logger.log_error(f"Failed to store supply summary: {e}")
            
            # Log metrics
            self.logger.log_metric("supply_analyses", self.stats["total_analyses"])
            self.logger.log_metric("high_supply_detected", self.stats["high_supply_detected"])
            self.logger.log_metric("low_supply_detected", self.stats["low_supply_detected"])
            
            await self.notify_core(summary)
            return summary
            
        except Exception as e:
            self.logger.log_error(f"Error classifying supply behavior: {e}")
            return {}

    def _classify_behavior(self, volume: float, avg_volume: float, price_change: float, volatility: float) -> str:
        """Classify supply behavior based on multiple factors."""
        try:
            # Volume analysis
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
            
            # Price change analysis
            price_change_abs = abs(price_change)
            
            # Volatility analysis
            volatility_ratio = volatility / self.volatility_threshold if self.volatility_threshold > 0 else 1.0
            
            # Multi-factor classification
            if volume_ratio > self.volume_threshold and price_change_abs > self.price_threshold:
                return "high_supply"
            elif volume_ratio < 0.5 and price_change_abs < self.price_threshold * 0.5:
                return "low_supply"
            elif volatility_ratio > 1.5:
                return "volatile_supply"
            else:
                return "normal_supply"
                
        except Exception as e:
            self.logger.log_error(f"Error in behavior classification: {e}")
            return "unknown"

    def _calculate_supply_strength(self, volume: float, offers: float, price_change: float) -> float:
        """Calculate supply strength based on volume, offers, and price change."""
        try:
            # Normalize factors
            volume_factor = min(volume / 1000.0, 1.0)  # Normalize to 0-1
            offers_factor = min(offers / 100.0, 1.0)  # Normalize to 0-1
            price_factor = abs(price_change) / 0.1  # Normalize to 0-1, cap at 10%
            
            # Weighted combination
            strength = (volume_factor * 0.4 + offers_factor * 0.4 + price_factor * 0.2)
            
            return min(strength, 1.0)  # Cap at 1.0
            
        except Exception as e:
            self.logger.log_error(f"Error calculating supply strength: {e}")
            return 0.0

    async def detect_supply_anomalies(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect supply anomalies using statistical analysis."""
        try:
            anomalies = []
            
            for data in market_data:
                try:
                    symbol = data.get("symbol", "unknown")
                    volume = float(data.get("volume", 0.0))
                    avg_volume = float(data.get("avg_volume", 1.0))
                    price_change = float(data.get("price_change", 0.0))
                    
                    # Calculate z-score for volume
                    volume_z_score = (volume - avg_volume) / max(avg_volume * 0.1, 1.0)
                    
                    # Detect anomalies
                    if abs(volume_z_score) > 3.0:  # 3 standard deviations
                        anomaly = {
                            "type": "supply_anomaly",
                            "symbol": symbol,
                            "anomaly_type": "volume_spike" if volume_z_score > 0 else "volume_drop",
                            "z_score": volume_z_score,
                            "volume": volume,
                            "avg_volume": avg_volume,
                            "price_change": price_change,
                            "timestamp": int(time.time()),
                            "description": f"Supply anomaly detected for {symbol}: volume z-score {volume_z_score:.2f}"
                        }
                        anomalies.append(anomaly)
                        self.logger.log_market_anomaly("supply_anomaly", anomaly)
                    
                except (ValueError, TypeError) as e:
                    self.logger.log_error(f"Error processing anomaly data: {e}", {"data": data})
                    continue
            
            return anomalies
            
        except Exception as e:
            self.logger.log_error(f"Error detecting supply anomalies: {e}")
            return []

    async def predict_supply_trends(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict supply trends based on historical patterns."""
        try:
            if not market_data:
                return {}
            
            # Group data by symbol
            symbol_data = {}
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                if symbol not in symbol_data:
                    symbol_data[symbol] = []
                symbol_data[symbol].append(data)
            
            predictions = {}
            for symbol, data_list in symbol_data.items():
                try:
                    # Calculate trend indicators
                    volumes = [float(d.get("volume", 0.0)) for d in data_list]
                    price_changes = [float(d.get("price_change", 0.0)) for d in data_list]
                    
                    if len(volumes) < 3:
                        continue
                    
                    # Simple trend analysis
                    volume_trend = "increasing" if volumes[-1] > volumes[0] else "decreasing"
                    price_trend = "increasing" if price_changes[-1] > price_changes[0] else "decreasing"
                    
                    # Predict future supply behavior
                    if volume_trend == "increasing" and price_trend == "decreasing":
                        prediction = "increasing_supply_pressure"
                    elif volume_trend == "decreasing" and price_trend == "increasing":
                        prediction = "decreasing_supply_pressure"
                    else:
                        prediction = "stable_supply"
                    
                    predictions[symbol] = {
                        "prediction": prediction,
                        "volume_trend": volume_trend,
                        "price_trend": price_trend,
                        "confidence": 0.7,  # Placeholder confidence
                        "timestamp": int(time.time())
                    }
                    
                    self.logger.log_prediction("supply_trend", {
                        "symbol": symbol,
                        "prediction": prediction,
                        "description": f"Supply trend prediction for {symbol}: {prediction}"
                    })
                    
                except Exception as e:
                    self.logger.log_error(f"Error predicting trends for {symbol}: {e}")
                    continue
            
            return {
                "type": "supply_trend_predictions",
                "predictions": predictions,
                "timestamp": int(time.time()),
                "description": f"Generated supply trend predictions for {len(predictions)} symbols"
            }
            
        except Exception as e:
            self.logger.log_error(f"Error predicting supply trends: {e}")
            return {}

    async def notify_core(self, summary: Dict[str, Any]):
        """Notify Core Agent of supply behavior results."""
        try:
            self.logger.log(f"Notifying Core Agent: {summary.get('description', 'unknown')}")
            
            if self.redis_client:
                self.redis_client.publish("market_conditions_output", str(summary))
                
        except Exception as e:
            self.logger.log_error(f"Error notifying core agent: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get supply detector statistics."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "uptime_seconds": uptime,
            "total_analyses": self.stats["total_analyses"],
            "high_supply_detected": self.stats["high_supply_detected"],
            "low_supply_detected": self.stats["low_supply_detected"],
            "normal_supply_detected": self.stats["normal_supply_detected"],
            "analyses_per_hour": self.stats["total_analyses"] / max(uptime / 3600, 1),
            "volume_threshold": self.volume_threshold,
            "price_threshold": self.price_threshold
        }