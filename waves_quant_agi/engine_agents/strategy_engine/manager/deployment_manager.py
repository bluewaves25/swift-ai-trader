from typing import Dict, Any, List
import time
import redis
from ..logs.strategy_engine_logger import StrategyEngineLogger

class DeploymentManager:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.risk_threshold = config.get("risk_threshold", 0.05)  # Max drawdown threshold

    async def deploy_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Deploy a strategy after risk and fee checks."""
        try:
            symbol = strategy.get("symbol", "unknown")
            strategy_id = f"{strategy['type']}:{symbol}:{strategy['timestamp']}"
            risk_score = float(self.redis_client.get(f"risk_management:{symbol}:risk_score") or 0.0)
            fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

            if risk_score > self.risk_threshold or fee_score > self.config.get("fee_threshold", 0.01):
                self.logger.log(f"Strategy {strategy_id} blocked: high risk ({risk_score}) or fees ({fee_score})")
                return False

            self.redis_client.publish("execution_agent", str(strategy))
            self.logger.log_strategy_deployment("deployment", {
                "type": "strategy_deployed",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Deployed strategy {strategy_id} for {symbol}"
            })
            await self.notify_core({
                "type": "strategy_deployed",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Deployed strategy {strategy_id} for {symbol}"
            })
            return True
        except Exception as e:
            self.logger.log_error(f"Error deploying strategy: {e}")
            return False

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of deployment status."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))