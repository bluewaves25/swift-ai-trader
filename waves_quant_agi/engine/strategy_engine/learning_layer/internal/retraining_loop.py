from typing import Dict, Any, List
import redis
import asyncio
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class RetrainingLoop:
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
        self.retrain_interval = config.get("retrain_interval", 86400)  # 1 day in seconds
        self.performance_threshold = config.get("performance_threshold", 0.5)

    async def run_retraining(self, performance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Periodically retrain strategy models based on performance."""
        try:
            retrain_results = []
            for data in performance_data:
                strategy_id = data.get("strategy_id", "unknown")
                symbol = data.get("symbol", "unknown")
                accuracy = float(data.get("accuracy", 0.0))

                if accuracy < self.performance_threshold:
                    result = {
                        "type": "retraining_trigger",
                        "strategy_id": strategy_id,
                        "symbol": symbol,
                        "accuracy": accuracy,
                        "timestamp": int(time.time()),
                        "description": f"Triggered retraining for {strategy_id} ({symbol}): Accuracy {accuracy:.2f}"
                    }
                    retrain_results.append(result)
                    self.logger.log_issue(result)
                    self.cache.store_incident(result)
                    self.redis_client.set(f"strategy_engine:retraining:{strategy_id}", str(result), ex=604800)
                    await self.notify_training(result)
                    await asyncio.sleep(1)  # Prevent overloading

            summary = {
                "type": "retraining_summary",
                "retrain_count": len(retrain_results),
                "timestamp": int(time.time()),
                "description": f"Triggered {len(retrain_results)} retraining processes"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return retrain_results
        except Exception as e:
            self.logger.log(f"Error in retraining loop: {e}")
            self.cache.store_incident({
                "type": "retraining_loop_error",
                "timestamp": int(time.time()),
                "description": f"Error in retraining loop: {str(e)}"
            })
            return []

    async def notify_training(self, result: Dict[str, Any]):
        """Notify Training Module of retraining trigger."""
        self.logger.log(f"Notifying Training Module: {result.get('description', 'unknown')}")
        self.redis_client.publish("training_module", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of retraining results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))