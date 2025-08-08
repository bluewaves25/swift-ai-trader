from typing import Dict, Any, List
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class PredictiveAlerts:
    def __init__(self, logger: FailureAgentLogger, cache: IncidentCache, risk_threshold: float = 0.7):
        self.logger = logger
        self.cache = cache
        self.risk_threshold = risk_threshold

    def generate_alerts(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate predictive alerts based on synthesized patterns."""
        try:
            alerts = []
            for pattern in patterns:
                if pattern.get("risk_score", 0.0) >= self.risk_threshold:
                    alert = {
                        "type": "predictive_alert",
                        "internal_type": pattern.get("internal_type", "unknown"),
                        "external_type": pattern.get("external_type", "unknown"),
                        "risk_score": pattern["risk_score"],
                        "timestamp": pattern["timestamp"],
                        "description": f"Alert: High risk of {pattern['internal_type']} due to {pattern['description'][:50]}..."
                    }
                    self.cache.store_incident(alert)
                    self.logger.log(f"Generated alert: {alert['description']}")
                    alerts.append(alert)
            return alerts
        except Exception as e:
            self.logger.log(f"Error generating predictive alerts: {e}")
            return []