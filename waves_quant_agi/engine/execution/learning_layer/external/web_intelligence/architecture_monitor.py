from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class ArchitectureMonitor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.stability_threshold = config.get("stability_threshold", 0.9)  # 90% stability score

    async def monitor_stability(self, system_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Monitor system stability for execution reliability."""
        try:
            stability_reports = []
            for _, row in system_data.iterrows():
                component = row.get("component", "unknown")
                stability_score = float(row.get("stability_score", 0.0))
                symbol = row.get("symbol", "BTC/USD")

                if stability_score < self.stability_threshold:
                    report = {
                        "type": "stability_alert",
                        "component": component,
                        "symbol": symbol,
                        "stability_score": stability_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Unstable component {component} for {symbol}: Score {stability_score:.2f}"
                    }
                    stability_reports.append(report)
                    self.redis_client.set(f"execution:stability:{component}:{symbol}", json.dumps(report), ex=604800)
                    await self.notify_execution(report)

            summary = {
                "type": "stability_summary",
                "report_count": len(stability_reports),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Generated {len(stability_reports)} stability alerts"
            }
            self.redis_client.set("execution:stability_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return stability_reports
        except Exception as e:
            self.redis_client.lpush("execution:errors", json.dumps({
                "type": "architecture_monitor_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error monitoring stability: {str(e)}"
            }))
            return []

    async def notify_execution(self, report: Dict[str, Any]):
        """Notify Execution Logic of stability alerts."""
        self.redis_client.publish("execution_logic", json.dumps(report))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of stability monitoring results."""
        self.redis_client.publish("execution_output", json.dumps(issue))