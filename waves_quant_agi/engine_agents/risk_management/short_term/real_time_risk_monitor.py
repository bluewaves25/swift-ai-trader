from typing import Dict, Any, List
import time
import pandas as pd

class RealTimeRiskMonitor:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
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
                    # Store alert in Redis using connection manager
                    redis_client = await self.connection_manager.get_redis_client()
                    if redis_client:
                        redis_client.set(f"risk_management:anomaly:{symbol}", str(alert), ex=3600)
                        await self.notify_execution(alert)

            if total_exposure > self.exposure_threshold:
                exposure_alert = {
                    "type": "exposure_alert",
                    "total_exposure": total_exposure,
                    "timestamp": int(time.time()),
                    "description": f"Total exposure exceeded: {total_exposure:.2%}"
                }
                alerts.append(exposure_alert)
                # Store exposure alert in Redis using connection manager
                redis_client = await self.connection_manager.get_redis_client()
                if redis_client:
                    redis_client.set("risk_management:exposure", str(exposure_alert), ex=3600)
                    await self.notify_execution(exposure_alert)

            summary = {
                "type": "risk_monitor_summary",
                "alert_count": len(alerts),
                "total_exposure": total_exposure,
                "timestamp": int(time.time()),
                "description": f"Monitored {len(position_data)} positions, {len(alerts)} alerts"
            }
            await self.notify_core(summary)
            return total_exposure
        except Exception as e:
            print(f"Error in real-time risk monitor: {e}")
            return 0.0

    async def notify_execution(self, alert: Dict[str, Any]):
        """Notify Executions Agent of risk alerts."""
        print(f"Notifying Executions Agent: {alert.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("execution_agent", str(alert))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of risk monitoring results."""
        print(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))