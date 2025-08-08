from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ..logs.risk_management_logger import RiskManagementLogger

class TemporalLimitGuard:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.hourly_drawdown_limit = config.get("hourly_drawdown_limit", 0.01)  # 1% per hour
        self.daily_drawdown_limit = config.get("daily_drawdown_limit", 0.03)  # 3% per day
        self.weekly_drawdown_limit = config.get("weekly_drawdown_limit", 0.05)  # 5% per week

    async def enforce_drawdown_limits(self, performance_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Enforce maximum drawdown limits per hour, day, and week."""
        try:
            limits = []
            for _, row in performance_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                hourly_drawdown = float(row.get("hourly_drawdown", 0.0))
                daily_drawdown = float(row.get("daily_drawdown", 0.0))
                weekly_drawdown = float(row.get("weekly_drawdown", 0.0))

                triggered_limits = []
                if hourly_drawdown > self.hourly_drawdown_limit:
                    triggered_limits.append(f"Hourly drawdown {hourly_drawdown:.2%}")
                if daily_drawdown > self.daily_drawdown_limit:
                    triggered_limits.append(f"Daily drawdown {daily_drawdown:.2%}")
                if weekly_drawdown > self.weekly_drawdown_limit:
                    triggered_limits.append(f"Weekly drawdown {weekly_drawdown:.2%}")

                if triggered_limits:
                    limit = {
                        "type": "drawdown_limit",
                        "symbol": symbol,
                        "hourly_drawdown": hourly_drawdown,
                        "daily_drawdown": daily_drawdown,
                        "weekly_drawdown": weekly_drawdown,
                        "timestamp": int(time.time()),
                        "description": f"Drawdown limit triggered for {symbol}: {', '.join(triggered_limits)}"
                    }
                    limits.append(limit)
                    self.logger.log_risk_assessment("assessment", limit)
                    self.redis_client.set(f"risk_management:drawdown_limit:{symbol}", str(limit), ex=3600)
                    await self.notify_execution(limit)

            summary = {
                "type": "drawdown_limit_summary",
                "limit_count": len(limits),
                "timestamp": int(time.time()),
                "description": f"Enforced {len(limits)} drawdown limits"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return limits
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, limit: Dict[str, Any]):
        """Notify Executions Agent of drawdown limit triggers."""
        self.logger.log(f"Notifying Executions Agent: {limit.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(limit))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of drawdown limit results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))