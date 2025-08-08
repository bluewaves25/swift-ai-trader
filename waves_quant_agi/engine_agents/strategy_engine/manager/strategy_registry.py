from typing import Dict, Any, List
import redis
import time
from ..logs.strategy_engine_logger import StrategyEngineLogger

class StrategyRegistry:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = self._init_redis()
        self.logger = StrategyEngineLogger("strategy_registry", self.redis_client)
        self.active_strategies: Dict[str, Dict[str, Any]] = {}
        self.stats = {
            "strategies_registered": 0,
            "strategies_updated": 0,
            "strategies_removed": 0,
            "errors": 0,
            "start_time": time.time()
        }

    def _init_redis(self) -> redis.Redis:
        """Initialize Redis connection."""
        try:
            redis_url = self.config.get("redis_url", "redis://localhost:6379")
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            self.logger.log("Redis connection established", "info")
            return client
        except Exception as e:
            self.logger.log_error(f"Failed to connect to Redis: {e}")
            raise

    async def register_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Register a new strategy in the system."""
        try:
            strategy_id = f"{strategy['type']}:{strategy['symbol']}:{strategy['timestamp']}"
            if strategy_id in self.active_strategies:
                self.logger.log(f"Strategy {strategy_id} already registered", "warning")
                return False

            self.active_strategies[strategy_id] = strategy
            self.redis_client.set(f"strategy_engine:registry:{strategy_id}", str(strategy), ex=604800)
            
            # Log strategy registration
            self.logger.log_strategy_registration(strategy_id, strategy)
            
            # Update stats
            self.stats["strategies_registered"] += 1
            
            # Notify core
            await self.notify_core({
                "type": "strategy_registered",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Registered strategy {strategy_id}"
            })
            return True
        except Exception as e:
            self.logger.log_error(f"Error registering strategy: {e}")
            self.stats["errors"] += 1
            return False

    async def get_active_strategies(self) -> List[Dict[str, Any]]:
        """Retrieve all active strategies."""
        try:
            strategies = list(self.active_strategies.values())
            self.logger.log(f"Retrieved {len(strategies)} active strategies", "info")
            return strategies
        except Exception as e:
            self.logger.log_error(f"Error retrieving active strategies: {e}")
            self.stats["errors"] += 1
            return []

    async def update_strategy(self, strategy_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing strategy."""
        try:
            if strategy_id not in self.active_strategies:
                self.logger.log(f"Strategy {strategy_id} not found for update", "warning")
                return False
            
            self.active_strategies[strategy_id].update(updates)
            self.redis_client.set(f"strategy_engine:registry:{strategy_id}", str(self.active_strategies[strategy_id]), ex=604800)
            
            self.logger.log_strategy_registration(strategy_id, self.active_strategies[strategy_id])
            self.stats["strategies_updated"] += 1
            
            await self.notify_core({
                "type": "strategy_updated",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Updated strategy {strategy_id}"
            })
            return True
        except Exception as e:
            self.logger.log_error(f"Error updating strategy: {e}")
            self.stats["errors"] += 1
            return False

    async def remove_strategy(self, strategy_id: str) -> bool:
        """Remove a strategy from the registry."""
        try:
            if strategy_id not in self.active_strategies:
                self.logger.log(f"Strategy {strategy_id} not found for removal", "warning")
                return False
            
            del self.active_strategies[strategy_id]
            self.redis_client.delete(f"strategy_engine:registry:{strategy_id}")
            
            self.logger.log(f"Removed strategy {strategy_id}", "info")
            self.stats["strategies_removed"] += 1
            
            await self.notify_core({
                "type": "strategy_removed",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Removed strategy {strategy_id}"
            })
            return True
        except Exception as e:
            self.logger.log_error(f"Error removing strategy: {e}")
            self.stats["errors"] += 1
            return False

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            **self.stats,
            "active_strategies": len(self.active_strategies),
            "uptime": time.time() - self.stats["start_time"]
        }

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of registry updates."""
        try:
            self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}", "info")
            self.redis_client.publish("strategy_engine_output", str(issue))
        except Exception as e:
            self.logger.log_error(f"Error notifying core: {e}")
            self.stats["errors"] += 1