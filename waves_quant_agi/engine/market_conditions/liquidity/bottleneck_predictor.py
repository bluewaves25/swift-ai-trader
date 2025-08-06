from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class BottleneckPredictor:
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
        self.bottleneck_threshold = config.get("bottleneck_threshold", 0.2)  # 20% order book depth reduction

    async def predict_bottleneck(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict where liquidity crunches will occur."""
        try:
            bottlenecks = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                order_depth = float(data.get("order_depth", 1.0))
                avg_order_depth = float(data.get("avg_order_depth", 1.0))

                depth_ratio = order_depth / avg_order_depth if avg_order_depth > 0 else 0.0
                if depth_ratio < self.bottleneck_threshold:
                    bottleneck = {
                        "type": "liquidity_bottleneck",
                        "symbol": symbol,
                        "depth_ratio": depth_ratio,
                        "timestamp": int(time.time()),
                        "description": f"Liquidity bottleneck predicted for {symbol}: depth ratio {depth_ratio:.2f}"
                    }
                    bottlenecks.append(bottleneck)
                    self.logger.log_issue(bottleneck)
                    self.cache.store_incident(bottleneck)
                    self.redis_client.set(f"market_conditions:bottleneck:{symbol}", str(bottleneck), ex=604800)  # Expire after 7 days

            summary = {
                "type": "bottleneck_summary",
                "bottleneck_count": len(bottlenecks),
                "timestamp": int(time.time()),
                "description": f"Predicted {len(bottlenecks)} liquidity bottlenecks"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return bottlenecks
        except Exception as e:
            self.logger.log(f"Error predicting bottlenecks: {e}")
            self.cache.store_incident({
                "type": "bottleneck_predictor_error",
                "timestamp": int(time.time()),
                "description": f"Error predicting bottlenecks: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of bottleneck predictions."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))