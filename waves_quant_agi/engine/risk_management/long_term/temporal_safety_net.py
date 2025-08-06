from typing import Dict, Any, List
import redis
import pandas as pd
from ..market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ..market_conditions.memory.incident_cache import IncidentCache

class TemporalSafetyNet:
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
        self.drawdown_threshold = config.get("drawdown_threshold", 0.03)  # 3% weekly drawdown
        self.recession_risk_threshold = config.get("recession_risk_threshold", 0.7)

    async def enforce_limits(self, portfolio_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Enforce pullback and recession-aware loss limits."""
        try:
            limits = []
            for _, row in portfolio_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                drawdown = float(row.get("drawdown", 0.0))
                recession_score = float(row.get("recession_score", 0.0))

                if drawdown > self.drawdown_threshold or recession_score > self.recession_risk_threshold:
                    limit = {
                        "type": "temporal_limit",
                        "symbol": symbol,
                        "drawdown": drawdown,
                        "recession_score": recession_score,
                        "timestamp": int(time.time()),
                        "description": f"Temporal limit triggered for {symbol}: Drawdown {drawdown:.2%}, Recession score {recession_score:.2f}"
                    }
                    limits.append(limit)
                    self.logger.log_issue(limit)
                    self.cache.store_incident(limit)
                    self.redis_client.set(f"risk_management:temporal_limit:{symbol}", str(limit), ex=3600)
                    await self.notify_execution(limit)

            summary = {
                "type": "temporal_safety_summary",
                "limit_count": len(limits),
                "timestamp": int(time.time()),
                "description": f"Enforced {len(limits)} temporal limits"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return limits
        except Exception as e:
            self.logger.log(f"Error enforcing temporal limits: {e}")
            self.cache.store_incident({
                "type": "temporal_safety_net_error",
                "timestamp": int(time.time()),
                "description": f"Error enforcing temporal limits: {str(e)}"
            })
            return []

    async def notify_execution(self, limit: Dict[str, Any]):
        """Notify Executions Agent of temporal limit triggers."""
        self.logger.log(f"Notifying Executions Agent: {limit.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(limit))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of temporal limit results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))