import time
from typing import Dict, Any, List
import redis
from ..logs.failure_agent_logger import FailureAgentLogger
from ..logs.incident_cache import IncidentCache

class ConditionModelUpdater:
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
        self.update_threshold = config.get("update_threshold", 0.1)  # 10% model performance deviation

    async def update_condition_models(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Adjust internal models based on new market evidence."""
        try:
            updates = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                current_score = float(data.get("model_score", 0.5))
                historical_score = float(self.redis_client.get(f"market_conditions:model_score:{symbol}") or 0.5)

                if abs(current_score - historical_score) > self.update_threshold:
                    update = {
                        "type": "model_update",
                        "symbol": symbol,
                        "new_score": current_score,
                        "old_score": historical_score,
                        "timestamp": int(time.time()),
                        "description": f"Model update for {symbol}: new score {current_score:.2f}, old score {historical_score:.2f}"
                    }
                    updates.append(update)
                    self.logger.log_issue(update)
                    self.cache.store_incident(update)
                    self.redis_client.set(f"market_conditions:model_score:{symbol}", str(current_score), ex=604800)  # Expire after 7 days

            summary = {
                "type": "model_update_summary",
                "update_count": len(updates),
                "timestamp": int(time.time()),
                "description": f"Updated {len(updates)} condition models"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return summary
        except Exception as e:
            self.logger.log(f"Error updating condition models: {e}")
            self.cache.store_incident({
                "type": "model_update_error",
                "timestamp": int(time.time()),
                "description": f"Error updating condition models: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of model update results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))