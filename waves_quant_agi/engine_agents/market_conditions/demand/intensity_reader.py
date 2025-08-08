import time
from typing import Dict, Any, List, Optional
import redis
from ..logs.market_conditions_logger import MarketConditionsLogger

class DemandIntensityReader:
    """Advanced demand intensity analyzer with quantum-inspired processing."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = self._init_redis()
        self.logger = MarketConditionsLogger("demand_intensity_reader", self.redis_client)
        
        # Configuration parameters
        self.intensity_threshold = config.get("intensity_threshold", 1.5)
        self.price_sensitivity = config.get("price_sensitivity", 0.02)  # 2% price sensitivity
        self.volume_weight = config.get("volume_weight", 0.6)
        self.price_weight = config.get("price_weight", 0.4)
        self.analysis_window = config.get("analysis_window", 3600)  # 1 hour
        
        # Performance tracking
        self.stats = {
            "total_analyses": 0,
            "high_demand_detected": 0,
            "low_demand_detected": 0,
            "normal_demand_detected": 0,
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

    async def measure_demand_intensity(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Measure urgency and strength of buying in real-time."""
        try:
            if not market_data:
                self.logger.log("No market data provided for demand intensity analysis")
                return {}

            intensities = []
            for data in market_data:
                try:
                    symbol = data.get("symbol", "unknown")
                    buy_volume = float(data.get("buy_volume", 0.0))
                    avg_buy_volume = float(data.get("avg_buy_volume", 1.0))
                    price_change = float(data.get("price_change", 0.0))
                    bid_volume = float(data.get("bid_volume", 0.0))
                    spread = float(data.get("spread", 0.0))
                    
                    # Enhanced intensity calculation
                    intensity = self._calculate_intensity(buy_volume, avg_buy_volume, price_change, bid_volume, spread)
                    intensity_level = self._classify_intensity(intensity)
                    demand_strength = self._calculate_demand_strength(buy_volume, price_change, spread)
                    
                    result = {
                        "type": "demand_intensity",
                        "symbol": symbol,
                        "intensity": intensity_level,
                        "intensity_score": intensity,
                        "demand_strength": demand_strength,
                        "buy_volume": buy_volume,
                        "price_change": price_change,
                        "bid_volume": bid_volume,
                        "spread": spread,
                        "timestamp": int(time.time()),
                        "description": f"Demand intensity for {symbol}: {intensity_level} (score: {intensity:.2f})"
                    }
                    
                    intensities.append(result)
                    self.logger.log_demand_intensity(symbol, result)
                    
                    # Update stats
                    self.stats["total_analyses"] += 1
                    if intensity_level == "high_demand":
                        self.stats["high_demand_detected"] += 1
                    elif intensity_level == "low_demand":
                        self.stats["low_demand_detected"] += 1
                    else:
                        self.stats["normal_demand_detected"] += 1
                    
                except (ValueError, TypeError) as e:
                    self.logger.log_error(f"Error processing market data: {e}", {"data": data})
                    continue

            # Create summary
            summary = {
                "type": "demand_intensity_summary",
                "intensity_count": len(intensities),
                "high_demand_count": self.stats["high_demand_detected"],
                "low_demand_count": self.stats["low_demand_detected"],
                "normal_demand_count": self.stats["normal_demand_detected"],
                "timestamp": int(time.time()),
                "description": f"Analyzed demand intensity for {len(intensities)} symbols"
            }
            
            # Store summary in Redis
            if self.redis_client:
                try:
                    self.redis_client.hset("market_conditions:demand_summary", mapping=summary)
                    self.redis_client.expire("market_conditions:demand_summary", 86400)  # 24 hours
                except Exception as e:
                    self.logger.log_error(f"Failed to store demand summary: {e}")
            
            # Log metrics
            self.logger.log_metric("demand_analyses", self.stats["total_analyses"])
            self.logger.log_metric("high_demand_detected", self.stats["high_demand_detected"])
            self.logger.log_metric("low_demand_detected", self.stats["low_demand_detected"])
            
            await self.notify_core(summary)
            return summary
            
        except Exception as e:
            self.logger.log_error(f"Error measuring demand intensity: {e}")
            return {}

    def _calculate_intensity(self, buy_volume: float, avg_buy_volume: float, price_change: float, bid_volume: float, spread: float) -> float:
        """Calculate demand intensity score using multiple factors."""
        try:
            # Volume factor
            volume_ratio = buy_volume / avg_buy_volume if avg_buy_volume > 0 else 1.0
            volume_factor = min(volume_ratio / self.intensity_threshold, 2.0)  # Cap at 2x
            
            # Price change factor
            price_factor = abs(price_change) / self.price_sensitivity if self.price_sensitivity > 0 else 0.0
            price_factor = min(price_factor, 2.0)  # Cap at 2x
            
            # Bid volume factor
            bid_factor = min(bid_volume / max(buy_volume, 1.0), 1.0)
            
            # Spread factor (tighter spread = higher demand)
            spread_factor = max(0.0, 1.0 - (spread / 0.01))  # Normalize to 1% spread
            
            # Weighted combination
            intensity = (
                volume_factor * self.volume_weight +
                price_factor * self.price_weight +
                bid_factor * 0.2 +
                spread_factor * 0.2
            )
            
            return min(intensity, 2.0)  # Cap at 2.0
            
        except Exception as e:
            self.logger.log_error(f"Error calculating intensity: {e}")
            return 1.0

    def _classify_intensity(self, intensity_score: float) -> str:
        """Classify demand intensity based on calculated score."""
        try:
            if intensity_score > 1.5:
                return "high_demand"
            elif intensity_score < 0.5:
                return "low_demand"
            else:
                return "normal_demand"
                
        except Exception as e:
            self.logger.log_error(f"Error classifying intensity: {e}")
            return "unknown"

    def _calculate_demand_strength(self, buy_volume: float, price_change: float, spread: float) -> float:
        """Calculate demand strength based on volume, price change, and spread."""
        try:
            # Normalize factors
            volume_factor = min(buy_volume / 1000.0, 1.0)  # Normalize to 0-1
            price_factor = min(abs(price_change) / 0.1, 1.0)  # Normalize to 0-1, cap at 10%
            spread_factor = max(0.0, 1.0 - (spread / 0.01))  # Tighter spread = stronger demand
            
            # Weighted combination
            strength = (volume_factor * 0.5 + price_factor * 0.3 + spread_factor * 0.2)
            
            return min(strength, 1.0)  # Cap at 1.0
            
        except Exception as e:
            self.logger.log_error(f"Error calculating demand strength: {e}")
            return 0.0

    async def detect_demand_anomalies(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect demand anomalies using statistical analysis."""
        try:
            anomalies = []
            
            for data in market_data:
                try:
                    symbol = data.get("symbol", "unknown")
                    buy_volume = float(data.get("buy_volume", 0.0))
                    avg_buy_volume = float(data.get("avg_buy_volume", 1.0))
                    price_change = float(data.get("price_change", 0.0))
                    
                    # Calculate z-score for buy volume
                    volume_z_score = (buy_volume - avg_buy_volume) / max(avg_buy_volume * 0.1, 1.0)
                    
                    # Detect anomalies
                    if abs(volume_z_score) > 3.0:  # 3 standard deviations
                        anomaly = {
                            "type": "demand_anomaly",
                            "symbol": symbol,
                            "anomaly_type": "volume_spike" if volume_z_score > 0 else "volume_drop",
                            "z_score": volume_z_score,
                            "buy_volume": buy_volume,
                            "avg_buy_volume": avg_buy_volume,
                            "price_change": price_change,
                            "timestamp": int(time.time()),
                            "description": f"Demand anomaly detected for {symbol}: volume z-score {volume_z_score:.2f}"
                        }
                        anomalies.append(anomaly)
                        self.logger.log_market_anomaly("demand_anomaly", anomaly)
                    
                except (ValueError, TypeError) as e:
                    self.logger.log_error(f"Error processing anomaly data: {e}", {"data": data})
                    continue
            
            return anomalies
            
        except Exception as e:
            self.logger.log_error(f"Error detecting demand anomalies: {e}")
            return []

    async def predict_demand_trends(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict demand trends based on historical patterns."""
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
                    buy_volumes = [float(d.get("buy_volume", 0.0)) for d in data_list]
                    price_changes = [float(d.get("price_change", 0.0)) for d in data_list]
                    
                    if len(buy_volumes) < 3:
                        continue
                    
                    # Simple trend analysis
                    volume_trend = "increasing" if buy_volumes[-1] > buy_volumes[0] else "decreasing"
                    price_trend = "increasing" if price_changes[-1] > price_changes[0] else "decreasing"
                    
                    # Predict future demand behavior
                    if volume_trend == "increasing" and price_trend == "increasing":
                        prediction = "increasing_demand_pressure"
                    elif volume_trend == "decreasing" and price_trend == "decreasing":
                        prediction = "decreasing_demand_pressure"
                    else:
                        prediction = "stable_demand"
                    
                    predictions[symbol] = {
                        "prediction": prediction,
                        "volume_trend": volume_trend,
                        "price_trend": price_trend,
                        "confidence": 0.7,  # Placeholder confidence
                        "timestamp": int(time.time())
                    }
                    
                    self.logger.log_prediction("demand_trend", {
                        "symbol": symbol,
                        "prediction": prediction,
                        "description": f"Demand trend prediction for {symbol}: {prediction}"
                    })
                    
                except Exception as e:
                    self.logger.log_error(f"Error predicting trends for {symbol}: {e}")
                    continue
            
            return {
                "type": "demand_trend_predictions",
                "predictions": predictions,
                "timestamp": int(time.time()),
                "description": f"Generated demand trend predictions for {len(predictions)} symbols"
            }
            
        except Exception as e:
            self.logger.log_error(f"Error predicting demand trends: {e}")
            return {}

    async def notify_core(self, summary: Dict[str, Any]):
        """Notify Core Agent of demand intensity results."""
        try:
            self.logger.log(f"Notifying Core Agent: {summary.get('description', 'unknown')}")
            
            if self.redis_client:
                self.redis_client.publish("market_conditions_output", str(summary))
                
        except Exception as e:
            self.logger.log_error(f"Error notifying core agent: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get demand intensity reader statistics."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "uptime_seconds": uptime,
            "total_analyses": self.stats["total_analyses"],
            "high_demand_detected": self.stats["high_demand_detected"],
            "low_demand_detected": self.stats["low_demand_detected"],
            "normal_demand_detected": self.stats["normal_demand_detected"],
            "analyses_per_hour": self.stats["total_analyses"] / max(uptime / 3600, 1),
            "intensity_threshold": self.intensity_threshold,
            "price_sensitivity": self.price_sensitivity
        }