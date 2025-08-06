from typing import Dict, Any, List
import redis
from ...market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ...market_conditions.memory.incident_cache import IncidentCache

class StrategyRegistry:
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
        self.active_strategies: Dict[str, Dict[str, Any]] = {}

    async def register_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Register a new strategy in the system."""
        try:
            strategy_id = f"{strategy['type']}:{strategy['symbol']}:{strategy['timestamp']}"
            if strategy_id in self.active_strategies:
                self.logger.log(f"Strategy {strategy_id} already registered")
                return False

            self.active_strategies[strategy_id] = strategy
            self.redis_client.set(f"strategy_engine:registry:{strategy_id}", str(strategy), ex=604800)
            self.logger.log_issue({
                "type": "strategy_registered",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Registered strategy {strategy_id}"
            })
            self.cache.store_incident({
                "type": "strategy_registered",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Registered strategy {strategy_id}"
            })
            await self.notify_core({
                "type": "strategy_registered",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Registered strategy {strategy_id}"
            })
            return True
        except Exception as e:
            self.logger.log(f"Error registering strategy: {e}")
            self.cache.store_incident({
                "type": "strategy_registry_error",
                "timestamp": int(time.time()),
                "description": f"Error registering strategy: {str(e)}"
            })
            return False

    async def get_active_strategies(self) -> List[Dict[str, Any]]:
        """Retrieve all active strategies."""
        return list(self.active_strategies.values())

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of registry updates."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))