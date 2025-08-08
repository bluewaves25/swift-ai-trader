from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class ArchitectureMonitor:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.stability_threshold = config.get("stability_threshold", 0.9)  # 90% stability score

    async def monitor_stability(self, system_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Monitor system stability for risk management."""
        try:
            stability_results = []
            for _, row in system_data.iterrows():
                component = row.get("component", "unknown")
                stability_score = float(row.get("stability_score", 0.0))

                if stability_score < self.stability_threshold:
                    result = {
                        "type": "stability_monitor",
                        "component": component,
                        "stability_score": stability_score,
                        "timestamp": int(time.time()),
                        "description": f"Unstable component {component}: Stability {stability_score:.2f}"
                    }
                    stability_results.append(result)
                    self.logger.log_risk_assessment("assessment", result)
                    self.redis_client.set(f"risk_management:stability:{component}", str(result), ex=3600)
                    await self.notify_maintenance(result)
                else:
                    result = {
                        "type": "stability_monitor",
                        "component": component,
                        "stability_score": stability_score,
                        "timestamp": int(time.time()),
                        "description": f"Stable component {component}: Stability {stability_score:.2f}"
                    }
                    stability_results.append(result)
                    self.logger.log_risk_assessment("assessment", result)

            summary = {
                "type": "stability_monitor_summary",
                "result_count": len(stability_results),
                "timestamp": int(time.time()),
                "description": f"Monitored stability for {len(stability_results)} components"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return stability_results
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_maintenance(self, result: Dict[str, Any]):
        """Notify Maintenance System of unstable components."""
        self.logger.log(f"Notifying Maintenance System: {result.get('description', 'unknown')}")
        self.redis_client.publish("maintenance_system", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of stability monitoring results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))