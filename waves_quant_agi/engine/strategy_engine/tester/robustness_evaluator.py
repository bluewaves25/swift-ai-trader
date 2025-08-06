from typing import Dict, Any, List
import redis
import pandas as pd
from ...market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ...market_conditions.memory.incident_cache import IncidentCache

class RobustnessEvaluator:
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
        self.stress_threshold = config.get("stress_threshold", 0.15)

    async def evaluate_robustness(self, strategy: Dict[str, Any], stress_data: pd.DataFrame) -> Dict[str, Any]:
        """Stress-test strategy under extreme market conditions."""
        try:
            strategy_id = strategy.get("strategy_id", "unknown")
            symbol = strategy.get("symbol", "unknown")
            strategy_type = strategy.get("strategy_type", "unknown")

            returns = self._simulate_stress_trades(strategy_type, stress_data)
            max_drawdown = self._calculate_max_drawdown(returns)
            result = {
                "type": "robustness_result",
                "strategy_id": strategy_id,
                "symbol": symbol,
                "max_drawdown": max_drawdown,
                "timestamp": int(time.time()),
                "description": f"Robustness test for {strategy_id} ({symbol}): Drawdown {max_drawdown:.2f}"
            }
            if max_drawdown > self.stress_threshold:
                result["status"] = "failed"
                self.logger.log(f"Robustness test failed for {strategy_id}: Drawdown {max_drawdown:.2f}")
            else:
                result["status"] = "passed"

            self.logger.log_issue(result)
            self.cache.store_incident(result)
            self.redis_client.set(f"strategy_engine:robustness:{strategy_id}", str(result), ex=604800)
            await self.notify_core(result)
            return result
        except Exception as e:
            self.logger.log(f"Error evaluating robustness: {e}")
            self.cache.store_incident({
                "type": "robustness_evaluator_error",
                "timestamp": int(time.time()),
                "description": f"Error evaluating robustness: {str(e)}"
            })
            return {}

    def _simulate_stress_trades(self, strategy_type: str, data: pd.DataFrame) -> List[float]:
        """Simulate trades under stress conditions (placeholder)."""
        if strategy_type == "statistical_arbitrage":
            return [-0.02 if row["volatility"] > 0.5 else 0.01 for _, row in data.iterrows()]
        return [0.0] * len(data)

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown from returns."""
        cumulative = np.cumsum(returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        return float(np.max(drawdown)) if len(drawdown) > 0 else 0.0

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of robustness test results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))