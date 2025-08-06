from typing import Dict, Any, List
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class ThreatCorrelator:
    def __init__(self, logger: FailureAgentLogger, cache: IncidentCache):
        self.logger = logger
        self.cache = cache
        self.risk_mapping = {
            "outage": ["broker_breaker", "network_guard"],
            "crash": ["strategy_breaker", "data_integrity_checker"],
            "api": ["dependency_health", "broker_breaker"],
            "failure": ["agent_supervisor", "data_integrity_checker"]
        }

    def correlate_threats(self, external_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map external signals to internal risks."""
        try:
            correlated = []
            for item in external_data:
                description = item.get("description", "").lower()
                risk_score = item.get("risk_score", 0.0) or 0.5  # Default to moderate risk
                related_components = []
                for keyword, components in self.risk_mapping.items():
                    if keyword in description:
                        related_components.extend(components)
                if related_components:
                    threat = {
                        "source": item.get("source", "unknown"),
                        "type": "correlated_threat",
                        "risk_score": risk_score,
                        "components": list(set(related_components)),
                        "timestamp": item["timestamp"],
                        "description": f"Correlated threat: {item.get('description', '')[:50]}... affects {related_components}"
                    }
                    self.cache.store_incident(threat)
                    self.logger.log(f"Correlated threat: {threat['description']}")
                    correlated.append(threat)
            return correlated
        except Exception as e:
            self.logger.log(f"Error correlating threats: {e}")
            return []