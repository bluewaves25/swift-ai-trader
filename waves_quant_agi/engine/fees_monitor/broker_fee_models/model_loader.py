import json
import redis
from typing import Dict, Any, List
from pathlib import Path
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class ModelLoader:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.fee_db_path = Path(config.get("fee_db_path", "fees_monitor/broker_fee_models/broker_fee_db.json"))
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.fee_models = {}

    def load_fee_models(self) -> Dict[str, Dict[str, Any]]:
        """Load broker fee models from JSON and cache in Redis."""
        try:
            if not self.fee_db_path.exists():
                self.logger.log(f"Fee database not found: {self.fee_db_path}")
                return {}

            with open(self.fee_db_path, "r") as f:
                fee_models = json.load(f)

            for broker, model in fee_models.items():
                self.fee_models[broker] = model
                redis_key = f"fee_model:{broker}"
                self.redis_client.hset(redis_key, mapping=model)
                self.redis_client.expire(redis_key, 604800)  # Expire after 7 days
                self.logger.log(f"Loaded fee model for {broker}")

            self.cache.store_incident({
                "type": "fee_model_load",
                "timestamp": int(time.time()),
                "description": f"Loaded {len(fee_models)} broker fee models"
            })
            return self.fee_models
        except Exception as e:
            self.logger.log(f"Error loading fee models: {e}")
            self.cache.store_incident({
                "type": "fee_model_load_error",
                "timestamp": int(time.time()),
                "description": f"Error loading fee models: {str(e)}"
            })
            return {}

    def get_fee_model(self, broker: str) -> Dict[str, Any]:
        """Retrieve fee model for a specific broker from Redis or memory."""
        try:
            if broker in self.fee_models:
                return self.fee_models[broker]
            
            redis_key = f"fee_model:{broker}"
            model = self.redis_client.hgetall(redis_key)
            if model:
                self.fee_models[broker] = model
                self.logger.log(f"Retrieved fee model for {broker} from Redis")
                return model
            
            self.logger.log(f"No fee model found for {broker}")
            self.cache.store_incident({
                "type": "fee_model_not_found",
                "broker": broker,
                "timestamp": int(time.time()),
                "description": f"No fee model for broker {broker}"
            })
            return {}
        except Exception as e:
            self.logger.log(f"Error retrieving fee model for {broker}: {e}")
            self.cache.store_incident({
                "type": "fee_model_retrieve_error",
                "broker": broker,
                "timestamp": int(time.time()),
                "description": f"Error retrieving fee model for {broker}: {str(e)}"
            })
            return {}

    def update_fee_model(self, broker: str, model: Dict[str, Any]):
        """Update fee model for a broker in memory and Redis."""
        try:
            self.fee_models[broker] = model
            redis_key = f"fee_model:{broker}"
            self.redis_client.hset(redis_key, mapping=model)
            self.redis_client.expire(redis_key, 604800)
            self.logger.log(f"Updated fee model for {broker}")
            self.cache.store_incident({
                "type": "fee_model_update",
                "broker": broker,
                "timestamp": int(time.time()),
                "description": f"Updated fee model for {broker}"
            })
        except Exception as e:
            self.logger.log(f"Error updating fee model for {broker}: {e}")
            self.cache.store_incident({
                "type": "fee_model_update_error",
                "broker": broker,
                "timestamp": int(time.time()),
                "description": f"Error updating fee model for {broker}: {str(e)}"
            })