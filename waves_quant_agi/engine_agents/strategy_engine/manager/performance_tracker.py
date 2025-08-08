from typing import Dict, Any, List
import redis
import numpy as np
import time
from ..logs.strategy_engine_logger import StrategyEngineLogger

class PerformanceTracker:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = self._init_redis()
        self.logger = StrategyEngineLogger("performance_tracker", self.redis_client)
        self.sharpe_threshold = config.get("sharpe_threshold", 1.0)
        self.drawdown_threshold = config.get("drawdown_threshold", 0.1)
        self.stats = {
            "strategies_tracked": 0,
            "performance_alerts": 0,
            "metrics_calculated": 0,
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
                
                # Log performance metrics
                self.logger.log_strategy_performance(strategy_id, performance)
                
                # Store in Redis
                self.redis_client.set(f"strategy_engine:performance:{strategy_id}", str(performance), ex=604800)
                
                # Update stats
                self.stats["strategies_tracked"] += 1
                self.stats["metrics_calculated"] += 1

                if sharpe_ratio < self.sharpe_threshold or max_drawdown > self.drawdown_threshold:
                    await self._flag_strategy(strategy_id, symbol, sharpe_ratio, max_drawdown)

            summary = {
                "type": "performance_summary",
                "tracked_count": len(performances),
                "timestamp": int(time.time()),
                "description": f"Tracked performance for {len(performances)} strategies"
            }
            self.logger.log_strategy_performance("summary", summary)
            await self.notify_core(summary)
            return performances
        except Exception as e:
            self.logger.log_error(f"Error tracking performance: {e}")
            self.stats["errors"] += 1
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
        self.logger.log_strategy_alert("performance_flag", issue)
        self.stats["performance_alerts"] += 1
        await self.notify_core(issue)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance tracker statistics."""
        return {
            **self.stats,
            "uptime": time.time() - self.stats["start_time"]
        }

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of performance metrics."""
        try:
            self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}", "info")
            self.redis_client.publish("strategy_engine_output", str(issue))
        except Exception as e:
            self.logger.log_error(f"Error notifying core: {e}")
            self.stats["errors"] += 1