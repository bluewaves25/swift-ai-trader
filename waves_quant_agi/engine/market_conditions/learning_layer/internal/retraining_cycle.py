from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class RetrainingCycle:
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
        self.performance_threshold = config.get("performance_threshold", 0.1)  # 10% performance drop

    async def retrain_models(self, model_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Refine models based on new market feedback."""
        try:
            retrainings = []
            for data in model_data:
                symbol = data.get("symbol", "unknown")
                current_performance = float(data.get("current_performance", 0.5))
                previous_performance = float(self.redis_client.get(f"market_conditions:performance:{symbol}") or 0.5)

                if abs(current_performance - previous_performance) > self.performance_threshold:
                    retraining = {
                        "type": "model_retraining",
                        "symbol": symbol,
                        "current_performance": current_performance,
                        "previous_performance": previous_performance,
                        "timestamp": int(time.time()),
                        "description": f"Retrained model for {symbol}: current {current_performance:.2f}, previous {previous_performance:.2f}"
                    }
                    retrainings.append(retraining)
                    self.logger.log_issue(retraining)
                    self.cache.store_incident(retraining)
                    self.redis_client.set(f"market_conditions:performance:{symbol}", str(current_performance), ex=604800)  # Expire after 7 days

            summary = {
                "type": "retraining_summary",
                "retraining_count": len(retrainings),
                "timestamp": int(time.time()),
                "description": f"Retrained {len(retrainings)} models"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return retrainings
        except Exception as e:
            self.logger.log(f"Error retraining models: {e}")
            self.cache.store_incident({
                "type": "retraining_cycle_error",
                "timestamp": int(time.time()),
                "description": f"Error retraining models: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of retraining results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))