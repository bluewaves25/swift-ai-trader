from typing import Dict, Any, List
import time
import redis
from .....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from .....market_conditions.memory.incident_cache import IncidentCache

class ArchitectureMonitor:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
                self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.stability_threshold = config.get("stability_threshold", 0.9)  # System stability score

    async def monitor_architecture(self, system_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Monitor system architecture for performance and stability."""
        try:
            alerts = []
            for data in system_data:
                component = data.get("component", "unknown")
                stability_score = float(data.get("stability_score", 0.0))
                latency = float(data.get("latency", 0.0))

                if stability_score < self.stability_threshold or latency > self.config.get("latency_threshold", 0.1):
                    alert = {
                        "type": "architecture_alert",
                        "component": component,
                        "stability_score": stability_score,
                        "latency": latency,
                        "timestamp": int(time.time()),
                        "description": f"Architecture issue for {component}: Stability {stability_score:.2f}, Latency {latency:.2f}"
                    }
                    alerts.append(alert)
                    self.logger.log_strategy_deployment("deployment", alert)
                    alert)
                    self.redis_client.set(f"strategy_engine:architecture:{component}", str(alert), ex=604800)
                    await self.notify_core(alert)

            summary = {
                "type": "architecture_monitor_summary",
                "alert_count": len(alerts),
                "timestamp": int(time.time()),
                "description": f"Generated {len(alerts)} architecture alerts"
            }
            self.logger.log_strategy_deployment("deployment", summary)
            summary)
            await self.notify_core(summary)
            return alerts
        except Exception as e:
            self.logger.log(f"Error monitoring architecture: {e}")
            {
                "type": "architecture_monitor_error",
                "timestamp": int(time.time()),
                "description": f"Error monitoring architecture: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of architecture monitoring results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))