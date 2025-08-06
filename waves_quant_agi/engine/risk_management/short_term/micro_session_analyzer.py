from typing import Dict, Any, List
import redis
import pandas as pd
from ..market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ..market_conditions.memory.incident_cache import IncidentCache

class MicroSessionAnalyzer:
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
        self.micro_session_size = config.get("micro_session_size", 100)  # 100 trades or 1 sec
        self.loss_threshold = config.get("loss_threshold", 0.02)  # 2% loss per micro-session
        self.consecutive_loss_limit = config.get("consecutive_loss_limit", 3)  # 3 bad micro-sessions

    async def analyze_micro_sessions(self, trade_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate HFT micro-sessions (1-sec or 100-trade buckets)."""
        try:
            alerts = []
            micro_sessions = trade_data.groupby(pd.Grouper(key="timestamp", freq="1s"))
            consecutive_losses = 0

            for _, session in micro_sessions:
                if len(session) >= self.micro_session_size:
                    symbol = session["symbol"].iloc[0] if "symbol" in session else "BTC/USD"
                    session_pnl = float(session["pnl"].sum())
                    session_loss = -session_pnl / session["capital"].iloc[0] if session["capital"].iloc[0] else 0.0

                    if session_loss > self.loss_threshold:
                        consecutive_losses += 1
                        alert = {
                            "type": "micro_session_alert",
                            "symbol": symbol,
                            "session_loss": session_loss,
                            "consecutive_losses": consecutive_losses,
                            "timestamp": int(time.time()),
                            "description": f"Micro-session loss for {symbol}: {session_loss:.2%}"
                        }
                        alerts.append(alert)
                        self.logger.log_issue(alert)
                        self.cache.store_incident(alert)
                        self.redis_client.set(f"risk_management:micro_session:{symbol}", str(alert), ex=3600)
                        if consecutive_losses >= self.consecutive_loss_limit:
                            await self.notify_execution({"type": "lockout", "symbol": symbol, "description": f"Lockout triggered: {consecutive_losses} bad micro-sessions"})
                    else:
                        consecutive_losses = 0

            summary = {
                "type": "micro_session_summary",
                "alert_count": len(alerts),
                "timestamp": int(time.time()),
                "description": f"Analyzed {len(micro_sessions)} micro-sessions, {len(alerts)} alerts"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return alerts
        except Exception as e:
            self.logger.log(f"Error analyzing micro-sessions: {e}")
            self.cache.store_incident({
                "type": "micro_session_analyzer_error",
                "timestamp": int(time.time()),
                "description": f"Error analyzing micro-sessions: {str(e)}"
            })
            return []

    async def notify_execution(self, alert: Dict[str, Any]):
        """Notify Executions Agent of micro-session alerts or lockouts."""
        self.logger.log(f"Notifying Executions Agent: {alert.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(alert))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of micro-session analysis results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))