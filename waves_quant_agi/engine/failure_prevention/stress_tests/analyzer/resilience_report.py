from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from .failure_classifier import FailureClassifier

class ResilienceReport:
    def __init__(self, logger: FailureAgentLogger, cache: IncidentCache, classifier: FailureClassifier):
        self.logger = logger
        self.cache = cache
        self.classifier = classifier

    def generate_report(self, key_pattern: str = "*") -> Dict[str, Any]:
        """Generate resilience report based on classified failures and incidents."""
        try:
            classification = self.classifier.classify_failures(key_pattern)
            incidents = self.cache.retrieve_incidents(key_pattern)
            
            report = {
                "timestamp": int(time.time()),
                "total_incidents": classification["total_incidents"],
                "category_breakdown": classification["categories"],
                "unclassified": classification["unclassified"],
                "recommendations": [],
                "critical_incidents": 0
            }

            # Analyze incidents for critical issues and recommendations
            for incident in incidents:
                if "critical" in incident.get("description", "").lower():
                    report["critical_incidents"] += 1
                category = self.classifier.failure_categories.get(incident.get("type", "unknown"), "unclassified")
                if category in ["infrastructure", "network"]:
                    report["recommendations"].append(f"Review {category} capacity: {incident.get('description', '')[:50]}...")
                elif category in ["agent", "strategy"]:
                    report["recommendations"].append(f"Optimize {category} logic: {incident.get('description', '')[:50]}...")
                elif category == "data":
                    report["recommendations"].append(f"Enhance data validation: {incident.get('description', '')[:50]}...")

            self.logger.log(f"Generated resilience report: {report['category_breakdown']}, {report['critical_incidents']} critical")
            self.cache.store_incident({
                "type": "resilience_report",
                "timestamp": report["timestamp"],
                "description": f"Resilience report: {len(report['recommendations'])} recommendations"
            })
            return report
        except Exception as e:
            self.logger.log(f"Error generating resilience report: {e}")
            self.cache.store_incident({
                "type": "report_error",
                "timestamp": int(time.time()),
                "description": f"Error generating resilience report: {str(e)}"
            })
            return {"status": "error", "error": str(e)}