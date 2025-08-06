from typing import Dict, Any, List
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class FailureClassifier:
    def __init__(self, logger: FailureAgentLogger, cache: IncidentCache):
        self.logger = logger
        self.cache = cache
        self.failure_categories = {
            "cpu_overload": "infrastructure",
            "memory_overload": "infrastructure",
            "queue_lag": "infrastructure",
            "agent_response_delay": "agent",
            "data_corruption": "data",
            "data_value_error": "data",
            "broker_breaker_triggered": "broker",
            "strategy_breaker_triggered": "strategy",
            "trade_halt_triggered": "system",
            "network_latency": "network",
            "api_failure": "dependency",
            "redis_failure": "dependency"
        }

    def classify_failures(self, key_pattern: str = "*") -> Dict[str, Any]:
        """Classify failures from incident cache into categories."""
        try:
            incidents = self.cache.retrieve_incidents(key_pattern)
            classification = {
                "total_incidents": len(incidents),
                "categories": {},
                "unclassified": 0
            }

            for incident in incidents:
                failure_type = incident.get("type", "unknown")
                category = self.failure_categories.get(failure_type, "unclassified")
                classification["categories"][category] = classification["categories"].get(category, 0) + 1
                if category == "unclassified":
                    classification["unclassified"] += 1

            self.logger.log(f"Classified {len(incidents)} incidents: {classification['categories']}")
            self.cache.store_incident({
                "type": "failure_classification",
                "timestamp": int(time.time()),
                "description": f"Failure classification: {classification['categories']}"
            })
            return classification
        except Exception as e:
            self.logger.log(f"Error classifying failures: {e}")
            self.cache.store_incident({
                "type": "classification_error",
                "timestamp": int(time.time()),
                "description": f"Error classifying failures: {str(e)}"
            })
            return {"status": "error", "error": str(e)}