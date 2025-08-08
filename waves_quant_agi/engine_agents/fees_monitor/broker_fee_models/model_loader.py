import json
import time
import redis
from typing import Dict, Any, List
from pathlib import Path
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class ModelLoader:
    """Loads and manages broker fee models with Redis caching."""
    
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
        self.last_load_time = 0
        self.load_interval = config.get("load_interval", 3600)  # 1 hour

    def load_fee_models(self) -> Dict[str, Dict[str, Any]]:
        """Load broker fee models from JSON and cache in Redis."""
        try:
            current_time = time.time()
            
            # Check if we need to reload
            if current_time - self.last_load_time < self.load_interval:
                self.logger.log(f"Fee models loaded recently, using cached version")
                return self.fee_models
            
            if not self.fee_db_path.exists():
                self.logger.log_error(f"Fee database not found: {self.fee_db_path}")
                self.cache.store_incident({
                    "type": "fee_model_load_error",
                    "timestamp": int(current_time),
                    "description": f"Fee database not found: {self.fee_db_path}",
                    "path": str(self.fee_db_path)
                })
                return {}

            with open(self.fee_db_path, "r") as f:
                fee_models = json.load(f)

            # Clear existing models
            self.fee_models.clear()
            
            loaded_count = 0
            for broker, model in fee_models.items():
                try:
                    # Validate model structure
                    if self._validate_fee_model(model):
                        self.fee_models[broker] = model
                        redis_key = f"fee_model:{broker}"
                        self.redis_client.hset(redis_key, mapping=model)
                        self.redis_client.expire(redis_key, 604800)  # Expire after 7 days
                        loaded_count += 1
                        self.logger.log(f"Loaded fee model for {broker}")
                    else:
                        self.logger.log_error(f"Invalid fee model structure for {broker}")
                        self.cache.store_incident({
                            "type": "fee_model_validation_error",
                            "broker": broker,
                            "timestamp": int(current_time),
                            "description": f"Invalid fee model structure for {broker}"
                        })
                except Exception as e:
                    self.logger.log_error(f"Error loading fee model for {broker}: {e}")
                    self.cache.store_incident({
                        "type": "fee_model_load_error",
                        "broker": broker,
                        "timestamp": int(current_time),
                        "description": f"Error loading fee model for {broker}: {str(e)}"
                    })

            self.last_load_time = current_time
            
            self.logger.log_metric("fee_models_loaded", loaded_count, {
                "total_models": len(fee_models),
                "successful_loads": loaded_count
            })
            
            self.cache.store_incident({
                "type": "fee_model_load",
                "timestamp": int(current_time),
                "description": f"Loaded {loaded_count} broker fee models",
                "total_models": len(fee_models),
                "successful_loads": loaded_count
            })
            
            return self.fee_models
            
        except Exception as e:
            self.logger.log_error(f"Error loading fee models: {e}")
            self.cache.store_incident({
                "type": "fee_model_load_error",
                "timestamp": int(time.time()),
                "description": f"Error loading fee models: {str(e)}"
            })
            return {}

    def _validate_fee_model(self, model: Dict[str, Any]) -> bool:
        """Validate fee model structure."""
        required_fields = ["fees", "broker_info"]
        fee_required_fields = ["commission", "spread", "minimum_fee"]
        
        # Check required top-level fields
        for field in required_fields:
            if field not in model:
                return False
        
        # Check required fee fields
        fees = model.get("fees", {})
        for field in fee_required_fields:
            if field not in fees:
                return False
        
        # Validate data types
        try:
            float(fees.get("commission", 0))
            float(fees.get("spread", 0))
            float(fees.get("minimum_fee", 0))
        except (ValueError, TypeError):
            return False
        
        return True

    def get_fee_model(self, broker: str) -> Dict[str, Any]:
        """Retrieve fee model for a specific broker from Redis or memory."""
        try:
            # Check memory cache first
            if broker in self.fee_models:
                self.logger.log_metric("fee_model_cache_hit", 1, {"broker": broker})
                return self.fee_models[broker]
            
            # Check Redis cache
            redis_key = f"fee_model:{broker}"
            model = self.redis_client.hgetall(redis_key)
            if model:
                self.fee_models[broker] = model
                self.logger.log(f"Retrieved fee model for {broker} from Redis")
                self.logger.log_metric("fee_model_redis_hit", 1, {"broker": broker})
                return model
            
            # Try to reload models if not found
            self.logger.log(f"No fee model found for {broker}, attempting reload")
            self.load_fee_models()
            
            if broker in self.fee_models:
                return self.fee_models[broker]
            
            self.logger.log_error(f"No fee model found for {broker} after reload")
            self.cache.store_incident({
                "type": "fee_model_not_found",
                "broker": broker,
                "timestamp": int(time.time()),
                "description": f"No fee model for broker {broker}"
            })
            
            # Return default model
            return self._get_default_fee_model(broker)
            
        except Exception as e:
            self.logger.log_error(f"Error retrieving fee model for {broker}: {e}")
            self.cache.store_incident({
                "type": "fee_model_retrieve_error",
                "broker": broker,
                "timestamp": int(time.time()),
                "description": f"Error retrieving fee model for {broker}: {str(e)}"
            })
            return self._get_default_fee_model(broker)

    def _get_default_fee_model(self, broker: str) -> Dict[str, Any]:
        """Get default fee model for unknown brokers."""
        return {
            "broker_info": {
                "name": broker,
                "type": "unknown"
            },
            "fees": {
                "commission": 0.001,  # 0.1% default
                "spread": 0.0001,     # 0.01% default
                "minimum_fee": 1.0,   # $1 minimum
                "maker_fee": 0.001,
                "taker_fee": 0.001
            },
            "limits": {
                "min_order_size": 0.001,
                "max_order_size": 1000000.0
            }
        }

    def update_fee_model(self, broker: str, model: Dict[str, Any]):
        """Update fee model for a broker in memory and Redis."""
        try:
            if not self._validate_fee_model(model):
                self.logger.log_error(f"Invalid fee model structure for {broker}")
                return False
            
            self.fee_models[broker] = model
            redis_key = f"fee_model:{broker}"
            self.redis_client.hset(redis_key, mapping=model)
            self.redis_client.expire(redis_key, 604800)
            
            self.logger.log(f"Updated fee model for {broker}")
            self.logger.log_metric("fee_model_updated", 1, {"broker": broker})
            
            self.cache.store_incident({
                "type": "fee_model_update",
                "broker": broker,
                "timestamp": int(time.time()),
                "description": f"Updated fee model for {broker}"
            })
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error updating fee model for {broker}: {e}")
            self.cache.store_incident({
                "type": "fee_model_update_error",
                "broker": broker,
                "timestamp": int(time.time()),
                "description": f"Error updating fee model for {broker}: {str(e)}"
            })
            return False

    def get_all_brokers(self) -> List[str]:
        """Get list of all available brokers."""
        return list(self.fee_models.keys())

    def get_fee_model_stats(self) -> Dict[str, Any]:
        """Get statistics about fee models."""
        try:
            return {
                "total_models": len(self.fee_models),
                "brokers": list(self.fee_models.keys()),
                "last_load_time": self.last_load_time,
                "load_interval": self.load_interval
            }
        except Exception as e:
            self.logger.log_error(f"Error getting fee model stats: {e}")
            return {
                "total_models": 0,
                "brokers": [],
                "last_load_time": 0,
                "load_interval": self.load_interval,
                "error": str(e)
            }