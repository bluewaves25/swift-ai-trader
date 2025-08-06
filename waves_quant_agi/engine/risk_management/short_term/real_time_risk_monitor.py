from typing import Dict, Any, List
import redis
import pandas as pd
from ..market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ..market_conditions.memory.incident_cache import IncidentCache

class RealTimeRiskMonitor:
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
        self.exposure_threshold = config.get("exposure_threshold", 0.1)  # 10% max exposure
        self.anomaly_threshold = config.get("anomaly_threshold", 2.5)  # 2.5 std dev for anomalies

    async def assess_risk(self, position_data: pd.DataFrame) -> float:
        """Monitor live position exposure and detect anomalies."""
        try:
            total_exposure = 0.0
            alerts = []
            for _, row in position_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                exposure = float(row.get("exposure", 0.0))
                volatility = float(row.get("volatility", 0.0))
                historical_vol = float(row.get("historical_volatility", 1.0))

                total_exposure += exposure
                volatility_z_score = (volatility - historical_vol) / historical_vol if historical_vol else 0.0

                if volatility_z_score > self.anomaly_threshold:
                    alert = {
                        "type": "anomaly_alert",
                        "symbol": symbol,
                        "volatility_z_score": volatility_z_score,
                        "timestamp": int(time.time()),
                        "description": f"Anomaly detected for {symbol}: Volatility z-score {volatility_z_score:.2f}"
                    }
                    alerts.append(alert)
                    self.logger.log_issue(alert)
                    self.cache.store_incident(alert)
                    self.redis_client.set(f"risk_management:anomaly:{symbol}", str(alert), ex=3600)
                    await self.notify_execution(alert)

            if total_exposure > self.exposure_threshold:
                exposure_alert = {
                    "type": "exposure_alert",
                    "total_exposure": total_exposure,
                    "timestamp": int(time.time()),
                    "description": f"Total exposure exceeded: {total_exposure:.2%}"
                }
                alerts.append(exposure_alert)
                self.logger.log_issue(exposure_alert)
                self.cache.store_incident(exposure_alert)
                self.redis_client.set("risk_management:exposure", str(exposure_alert), ex=3600)
                await self.notify_execution(exposure_alert)

            summary = {
                "type": "risk_monitor_summary",
                "alert_count": len(alerts),
                "total_exposure": total_exposure,
                "timestamp": int(time.time()),
                "description": f"Monitored {len(position_data)} positions, {len(alerts)} alerts"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return total_exposure
        except Exception as e:
            self.logger.log(f"Error monitoring risk: {e}")
            self.cache.store_incident({
                "type": "real_time_risk_monitor_error",
                "timestamp": int(time.time()),
                "description": f"Error monitoring risk: {str(e)}"
            })
            return 0.0

    async def notify_execution(self, alert: Dict[str, Any]):
        """Notify Executions Agent of risk alerts."""
        self.logger.log(f"Notifying Executions Agent: {alert.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(alert))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of risk monitoring results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))