from typing import Dict, Any, List
import redis
import numpy as np
from ...market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ...market_conditions.memory.incident_cache import IncidentCache

class PerformanceTracker:
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
        self.sharpe_threshold = config.get("sharpe_threshold", 1.0)
        self.drawdown_threshold = config.get("drawdown_threshold", 0.1)

    async def track_performance(self, strategy_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Track strategy performance metrics (PnL, Sharpe, drawdowns)."""
        try:
            performances = []
            for data in strategy_data:
                strategy_id = data.get("strategy_id", "unknown")
                symbol = data.get("symbol", "unknown")
                returns = data.get("returns", [0.0])
                if not returns:
                    continue

                sharpe_ratio = self._calculate_sharpe(returns)
                max_drawdown = self._calculate_max_drawdown(returns)
                performance = {
                    "type": "performance_metrics",
                    "strategy_id": strategy_id,
                    "symbol": symbol,
                    "sharpe_ratio": sharpe_ratio,
                    "max_drawdown": max_drawdown,
                    "timestamp": int(time.time()),
                    "description": f"Performance for {strategy_id} ({symbol}): Sharpe {sharpe_ratio:.2f}, Drawdown {max_drawdown:.2f}"
                }
                performances.append(performance)
                self.logger.log_issue(performance)
                self.cache.store_incident(performance)
                self.redis_client.set(f"strategy_engine:performance:{strategy_id}", str(performance), ex=604800)

                if sharpe_ratio < self.sharpe_threshold or max_drawdown > self.drawdown_threshold:
                    await self._flag_strategy(strategy_id, symbol, sharpe_ratio, max_drawdown)

            summary = {
                "type": "performance_summary",
                "tracked_count": len(performances),
                "timestamp": int(time.time()),
                "description": f"Tracked performance for {len(performances)} strategies"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return performances
        except Exception as e:
            self.logger.log(f"Error tracking performance: {e}")
            self.cache.store_incident({
                "type": "performance_tracker_error",
                "timestamp": int(time.time()),
                "description": f"Error tracking performance: {str(e)}"
            })
            return []

    def _calculate_sharpe(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio for strategy returns."""
        mean_return = np.mean(returns)
        std_return = np.std(returns) if len(returns) > 1 else 1.0
        return mean_return / std_return * np.sqrt(252) if std_return != 0 else 0.0

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown from returns."""
        cumulative = np.cumsum(returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        return float(np.max(drawdown)) if len(drawdown) > 0 else 0.0

    async def _flag_strategy(self, strategy_id: str, symbol: str, sharpe: float, drawdown: float):
        """Flag underperforming strategies for review."""
        issue = {
            "type": "strategy_flagged",
            "strategy_id": strategy_id,
            "symbol": symbol,
            "sharpe_ratio": sharpe,
            "max_drawdown": drawdown,
            "timestamp": int(time.time()),
            "description": f"Flagged {strategy_id} for {symbol}: Sharpe {sharpe:.2f}, Drawdown {drawdown:.2f}"
        }
        self.logger.log_issue(issue)
        self.cache.store_incident(issue)
        await self.notify_core(issue)

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of performance metrics."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))