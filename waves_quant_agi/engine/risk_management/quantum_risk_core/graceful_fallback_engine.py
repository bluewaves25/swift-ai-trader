from typing import Dict, Any, List
import redis
import pandas as pd
from ...market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ...market_conditions.memory.incident_cache import IncidentCache

class GracefulFallbackEngine:
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
        self.entropy_threshold = config.get("entropy_threshold", 0.8)  # 80% entropy threshold
        self.fallback_risk_level = config.get("fallback_risk_level", 0.01)  # 1% max risk

    async def apply_fallback(self, entropy_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Force low-risk plans for high entropy scenarios."""
        try:
            fallbacks = []
            for _, row in entropy_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                entropy = float(row.get("entropy", 0.0))

                if entropy > self.entropy_threshold:
                    fallback = {
                        "type": "fallback_plan",
                        "symbol": symbol,
                        "entropy": entropy,
                        "risk_level": self.fallback_risk_level,
                        "timestamp": int(time.time()),
                        "description": f"Applied fallback plan for {symbol}: Entropy {entropy:.2f}, Risk level {self.fallback_risk_level:.2%}"
                    }
                    fallbacks.append(fallback)
                    self.logger.log_issue(fallback)
                    self.cache.store_incident(fallback)
                    self.redis_client.set(f"risk_management:fallback:{symbol}", str(fallback), ex=3600)
                    await self.notify_execution(fallback)
                else:
                    fallback = {
                        "type": "fallback_plan",
                        "symbol": symbol,
                        "entropy": entropy,
                        "risk_level": None,
                        "timestamp": int(time.time()),
                        "description": f"No fallback needed for {symbol}: Entropy {entropy:.2f}"
                    }
                    fallbacks.append(fallback)
                    self.logger.log_issue(fallback)
                    self.cache.store_incident(fallback)

            summary = {
                "type": "fallback_summary",
                "fallback_count": len([f for f in fallbacks if f["risk_level"] is not None]),
                "timestamp": int(time.time()),
                "description": f"Applied {len([f for f in fallbacks if f['risk_level'] is not None])} fallback plans"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return fallbacks
        except Exception as e:
            self.logger.log(f"Error applying fallback plans: {e}")
            self.cache.store_incident({
                "type": "graceful_fallback_error",
                "timestamp": int(time.time()),
                "description": f"Error applying fallback plans: {str(e)}"
            })
            return []

    async def notify_execution(self, fallback: Dict[str, Any]):
        """Notify Executions Agent of applied fallback plans."""
        self.logger.log(f"Notifying Executions Agent: {fallback.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(fallback))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of fallback plan results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))