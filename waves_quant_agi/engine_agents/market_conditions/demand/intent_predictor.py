import time
from typing import Dict, Any, List
import redis
from ..logs.failure_agent_logger import FailureAgentLogger
from ..logs.incident_cache import IncidentCache

class IntentPredictor:
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
        self.intent_confidence = config.get("intent_confidence", 0.6)  # Confidence threshold

    async def predict_demand_intent(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict demand intent using real-time order book and volume analysis."""
        try:
            intents = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                buy_volume = float(data.get("buy_volume", 0.0))
                sell_volume = float(data.get("sell_volume", 0.0))
                order_count = int(data.get("order_count", 1))
                price_change = float(data.get("price_change", 0.0))
                spread = float(data.get("spread", 0.001))
                order_imbalance = float(data.get("order_imbalance", 0.0))
                
                # Real-time intent analysis based on multiple factors
                intent_score = self._calculate_intent_score(
                    buy_volume, sell_volume, order_count, price_change, spread, order_imbalance
                )
                
                intent_type = self._classify_intent_type(intent_score, order_count, spread)
                confidence = self._calculate_confidence(buy_volume, sell_volume, order_imbalance)
                
                intent = {
                    "type": "demand_intent_prediction",
                    "symbol": symbol,
                    "intent_type": intent_type,
                    "intent_score": intent_score,
                    "confidence": confidence,
                    "buy_volume": buy_volume,
                    "sell_volume": sell_volume,
                    "order_count": order_count,
                    "price_change": price_change,
                    "spread": spread,
                    "order_imbalance": order_imbalance,
                    "timestamp": int(time.time()),
                    "description": f"Demand intent for {symbol}: {intent_type} (score: {intent_score:.2f}, confidence: {confidence:.2f})"
                }
                
                intents.append(intent)
                self.logger.log_issue(intent)
                self.cache.store_incident(intent)
                self.redis_client.set(f"market_conditions:intent:{symbol}", str(intent), ex=604800)
            
            summary = {
                "type": "demand_intent_summary",
                "intent_count": len(intents),
                "timestamp": int(time.time()),
                "description": f"Predicted demand intent for {len(intents)} symbols"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return intents
            
        except Exception as e:
            self.logger.log(f"Error predicting demand intent: {e}")
            self.cache.store_incident({
                "type": "demand_intent_error",
                "timestamp": int(time.time()),
                "description": f"Error predicting demand intent: {str(e)}"
            })
            return []
    
    def _calculate_intent_score(self, buy_volume: float, sell_volume: float, order_count: int, 
                               price_change: float, spread: float, order_imbalance: float) -> float:
        """Calculate real-time intent score based on market dynamics."""
        try:
            # Volume dominance factor (0-1)
            total_volume = buy_volume + sell_volume
            if total_volume == 0:
                return 0.5
            
            volume_dominance = buy_volume / total_volume
            
            # Order count factor (0-1) - more orders suggest retail activity
            order_factor = min(1.0, order_count / 100.0)
            
            # Price momentum factor (-1 to 1)
            price_factor = max(-1.0, min(1.0, price_change / 0.1))  # Normalize to 10% change
            
            # Spread factor (0-1) - tighter spread suggests stronger intent
            spread_factor = max(0.0, 1.0 - (spread / 0.01))  # Normalize to 1% spread
            
            # Order imbalance factor (-1 to 1)
            imbalance_factor = max(-1.0, min(1.0, order_imbalance))
            
            # Weighted combination
            intent_score = (
                volume_dominance * 0.3 +
                order_factor * 0.2 +
                price_factor * 0.2 +
                spread_factor * 0.15 +
                imbalance_factor * 0.15
            )
            
            return max(0.0, min(1.0, intent_score))
            
        except Exception as e:
            self.logger.log_error(f"Error calculating intent score: {e}")
            return 0.5
    
    def _classify_intent_type(self, intent_score: float, order_count: int, spread: float) -> str:
        """Classify demand intent type based on score and market conditions."""
        try:
            if intent_score > 0.7:
                if order_count > 50 and spread < 0.005:
                    return "aggressive_buying"
                elif order_count > 20:
                    return "strong_buying"
                else:
                    return "moderate_buying"
            elif intent_score > 0.5:
                if spread < 0.003:
                    return "steady_buying"
                else:
                    return "cautious_buying"
            elif intent_score > 0.3:
                return "weak_buying"
            else:
                return "no_buying_intent"
                
        except Exception as e:
            self.logger.log_error(f"Error classifying intent type: {e}")
            return "unknown"
    
    def _calculate_confidence(self, buy_volume: float, sell_volume: float, order_imbalance: float) -> float:
        """Calculate prediction confidence based on data quality and consistency."""
        try:
            total_volume = buy_volume + sell_volume
            if total_volume == 0:
                return 0.0
            
            # Volume consistency factor
            volume_consistency = min(1.0, total_volume / 10000.0)  # Normalize to 10k volume
            
            # Imbalance clarity factor
            imbalance_clarity = abs(order_imbalance)
            
            # Data quality factor (higher volume = higher quality)
            data_quality = min(1.0, total_volume / 50000.0)  # Normalize to 50k volume
            
            # Combined confidence
            confidence = (
                volume_consistency * 0.4 +
                imbalance_clarity * 0.3 +
                data_quality * 0.3
            )
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.log_error(f"Error calculating confidence: {e}")
            return 0.5

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of demand intent results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))