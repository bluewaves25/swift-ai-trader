from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class SyncValidator:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.sync_threshold = config.get("sync_threshold", 0.1)  # Max allowed sync lag (seconds)

    async def check_sync(self, primary_data: Dict[str, Any], mirror_data: Dict[str, Any]):
        """Validate synchronization between primary and mirror systems."""
        try:
            primary_ts = primary_data.get("timestamp", 0.0)
            mirror_ts = mirror_data.get("timestamp", 0.0)
            sync_lag = abs(primary_ts - mirror_ts)

            if sync_lag > self.sync_threshold:
                issue = {
                    "type": "sync_failure",
                    "primary_id": primary_data.get("id", "unknown"),
                    "mirror_id": mirror_data.get("id", "unknown"),
                    "sync_lag": sync_lag,
                    "timestamp": int(time.time()),
                    "description": f"Sync lag {sync_lag}s exceeds threshold {self.sync_threshold}s"
                }
                self.logger.log_issue(issue)
                self.cache.store_incident(issue)
                await self.notify_core(issue)
                return False
            return True
        except Exception as e:
            self.logger.log(f"Error checking sync: {e}")
            self.cache.store_incident({
                "type": "sync_validator_error",
                "timestamp": int(time.time()),
                "description": f"Error checking sync: {str(e)}"
            })
            return False

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of sync issues."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent