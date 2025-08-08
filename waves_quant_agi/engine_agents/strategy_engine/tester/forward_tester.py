from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ...logs.strategy_engine_logger import StrategyEngineLogger

class ForwardTester:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
                self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.profit_threshold = config.get("profit_threshold", 0.01)

    async def forward_test_strategy(self, strategy: Dict[str, Any], live_data: pd.DataFrame) -> Dict[str, Any]:
        """Simulate strategy performance in live-like conditions."""
        try:
            strategy_id = strategy.get("strategy_id", "unknown")
            symbol = strategy.get("symbol", "unknown")
            strategy_type = strategy.get("strategy_type", "unknown")

            returns = self._simulate_trades(strategy_type, live_data)
            profit = sum(returns)
            result = {
                "type": "forward_test_result",
                "strategy_id": strategy_id,
                "symbol": symbol,
                "profit": profit,
                "trade_count": len(returns),
                "timestamp": int(time.time()),
                "description": f"Forward test for {strategy_id} ({symbol}): Profit {profit:.2f}, Trades {len(returns)}"
            }
            if profit < self.profit_threshold:
                result["status"] = "failed"
                self.logger.log(f"Forward test failed for {strategy_id}: Profit {profit:.2f}")
            else:
                result["status"] = "passed"

            self.logger.log_strategy_deployment("deployment", result)
            result)
            self.redis_client.set(f"strategy_engine:forward_test:{strategy_id}", str(result), ex=604800)
            await self.notify_core(result)
            return result
        except Exception as e:
            self.logger.log(f"Error forward testing strategy: {e}")
            {
                "type": "forward_tester_error",
                "timestamp": int(time.time()),
                "description": f"Error forward testing strategy: {str(e)}"
            })
            return {}

    def _simulate_trades(self, strategy_type: str, data: pd.DataFrame) -> List[float]:
        """Simulate trades in live-like conditions (placeholder)."""
        if strategy_type == "market_making":
            return [0.005 if row["spread"] > 0.01 else -0.005 for _, row in data.iterrows()]
        return [0.0] * len(data)

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of forward test results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))