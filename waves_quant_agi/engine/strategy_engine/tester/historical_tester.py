from typing import Dict, Any, List
import redis
import pandas as pd
from ...market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ...market_conditions.memory.incident_cache import IncidentCache

class HistoricalTester:
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
        self.profit_threshold = config.get("profit_threshold", 0.02)

    async def backtest_strategy(self, strategy: Dict[str, Any], historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Backtest a strategy using historical market data."""
        try:
            strategy_id = strategy.get("strategy_id", "unknown")
            symbol = strategy.get("symbol", "unknown")
            strategy_type = strategy.get("strategy_type", "unknown")

            returns = self._simulate_trades(strategy_type, historical_data)
            profit = sum(returns)
            result = {
                "type": "backtest_result",
                "strategy_id": strategy_id,
                "symbol": symbol,
                "profit": profit,
                "trade_count": len(returns),
                "timestamp": int(time.time()),
                "description": f"Backtest for {strategy_id} ({symbol}): Profit {profit:.2f}, Trades {len(returns)}"
            }
            if profit < self.profit_threshold:
                result["status"] = "failed"
                self.logger.log(f"Backtest failed for {strategy_id}: Profit {profit:.2f}")
            else:
                result["status"] = "passed"

            self.logger.log_issue(result)
            self.cache.store_incident(result)
            self.redis_client.set(f"strategy_engine:backtest:{strategy_id}", str(result), ex=604800)
            await self.notify_core(result)
            return result
        except Exception as e:
            self.logger.log(f"Error backtesting strategy: {e}")
            self.cache.store_incident({
                "type": "historical_tester_error",
                "timestamp": int(time.time()),
                "description": f"Error backtesting strategy: {str(e)}"
            })
            return {}

    def _simulate_trades(self, strategy_type: str, data: pd.DataFrame) -> List[float]:
        """Simulate trades based on strategy type (placeholder)."""
        if strategy_type == "trend_following":
            return [0.01 if row["close"] > row["ma50"] else -0.01 for _, row in data.iterrows()]
        return [0.0] * len(data)

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of backtest results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))