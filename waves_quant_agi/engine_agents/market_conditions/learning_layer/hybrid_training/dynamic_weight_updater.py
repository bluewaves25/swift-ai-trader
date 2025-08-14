import time
from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...logs.incident_cache import IncidentCache

class DynamicWeightUpdater:
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
        self.weight_threshold = config.get("weight_threshold", 0.1)  # 10% weight adjustment threshold

    async def update_weights(self, model_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Dynamically adjust model weights based on performance."""
        try:
            updates = []
            for data in model_data:
                symbol = data.get("symbol", "unknown")
                current_weight = float(data.get("current_weight", 0.5))
                performance = float(data.get("performance", 0.5))
                previous_weight = float(self.redis_client.get(f"market_conditions:weight:{symbol}") or 0.5)

                if abs(current_weight - previous_weight) > self.weight_threshold:
                    update = {
                        "type": "weight_update",
                        "symbol": symbol,
                        "new_weight": current_weight,
                        "performance": performance,
                        "timestamp": int(time.time()),
                        "description": f"Weight update for {symbol}: new weight {current_weight:.2f}, performance {performance:.2f}"
                    }
                    updates.append(update)
                    self.logger.log_issue(update)
                    self.cache.store_incident(update)
                    self.redis_client.set(f"market_conditions:weight:{symbol}", str(current_weight), ex=604800)  # Expire after 7 days

            summary = {
                "type": "weight_update_summary",
                "update_count": len(updates),
                "timestamp": int(time.time()),
                "description": f"Updated {len(updates)} model weights"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return updates
        except Exception as e:
            self.logger.log(f"Error updating weights: {e}")
            self.cache.store_incident({
                "type": "weight_updater_error",
                "timestamp": int(time.time()),
                "description": f"Error updating weights: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of weight update results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))