from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class ModelTrainer:
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
        self.accuracy_threshold = config.get("accuracy_threshold", 0.8)  # Model accuracy threshold

    async def train_models(self, training_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build AI models to classify/react to market conditions."""
        try:
            models = []
            for data in training_data:
                symbol = data.get("symbol", "unknown")
                accuracy = float(data.get("model_accuracy", 0.0))

                if accuracy > self.accuracy_threshold:
                    model = {
                        "type": "model_training",
                        "symbol": symbol,
                        "accuracy": accuracy,
                        "timestamp": int(time.time()),
                        "description": f"Trained model for {symbol}: accuracy {accuracy:.2f}"
                    }
                    models.append(model)
                    self.logger.log_issue(model)
                    self.cache.store_incident(model)
                    self.redis_client.set(f"market_conditions:model:{symbol}", str(model), ex=604800)  # Expire after 7 days

            summary = {
                "type": "model_training_summary",
                "model_count": len(models),
                "timestamp": int(time.time()),
                "description": f"Trained {len(models)} models"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return models
        except Exception as e:
            self.logger.log(f"Error training models: {e}")
            self.cache.store_incident({
                "type": "model_trainer_error",
                "timestamp": int(time.time()),
                "description": f"Error training models: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of model training results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))