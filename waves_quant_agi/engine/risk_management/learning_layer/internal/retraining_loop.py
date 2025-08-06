from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class RetrainingLoop:
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
        self.anomaly_threshold = config.get("anomaly_threshold", 0.15)  # 15% anomaly rate
        self.retraining_interval = config.get("retraining_interval", 604800)  # 1 week in seconds

    async def trigger_retraining(self, incident_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Trigger periodic or anomaly-based retraining."""
        try:
            retraining_triggers = []
            current_time = int(time.time())
            for risk_type in incident_data["type"].unique():
                type_data = incident_data[incident_data["type"] == risk_type]
                anomaly_rate = len(type_data[type_data["description"].str.contains("error|failed")]) / len(type_data) if len(type_data) > 0 else 0.0
                last_retrained = float(self.redis_client.get(f"risk_management:last_retrained:{risk_type}") or 0)

                if anomaly_rate > self.anomaly_threshold or (current_time - last_retrained) > self.retraining_interval:
                    trigger = {
                        "type": "retraining_trigger",
                        "risk_type": risk_type,
                        "anomaly_rate": anomaly_rate,
                        "last_retrained": last_retrained,
                        "timestamp": current_time,
                        "description": f"Retraining triggered for {risk_type}: Anomaly rate {anomaly_rate:.2%}, Last retrained {last_retrained}"
                    }
                    retraining_triggers.append(trigger)
                    self.logger.log_issue(trigger)
                    self.cache.store_incident(trigger)
                    self.redis_client.set(f"risk_management:last_retrained:{risk_type}", str(current_time), ex=604800)
                    await self.notify_training_module(trigger)

            summary = {
                "type": "retraining_summary",
                "trigger_count": len(retraining_triggers),
                "timestamp": current_time,
                "description": f"Triggered {len(retraining_triggers)} retraining processes"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return retraining_triggers
        except Exception as e:
            self.logger.log(f"Error triggering retraining: {e}")
            self.cache.store_incident({
                "type": "retraining_loop_error",
                "timestamp": int(time.time()),
                "description": f"Error triggering retraining: {str(e)}"
            })
            return []

    async def notify_training_module(self, trigger: Dict[str, Any]):
        """Notify Training Module of retraining triggers."""
        self.logger.log(f"Notifying Training Module: {trigger.get('description', 'unknown')}")
        self.redis_client.publish("training_module", str(trigger))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of retraining trigger results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))