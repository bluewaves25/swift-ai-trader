from typing import Dict, Any, List
from ...memory.incident_cache import IncidentCache
from ...logs.failure_agent_logger import FailureAgentLogger

class ResearchEngine:
    def __init__(self, cache: IncidentCache, logger: FailureAgentLogger):
        self.cache = cache
        self.logger = logger

    def analyze_failure_patterns(self, key_pattern: str = "*") -> Dict[str, Any]:
        """Analyze internal failure patterns from incident cache."""
        try:
            incidents = self.cache.retrieve_incidents(key_pattern)
            if not incidents:
                self.logger.log("No incidents found for analysis")
                return {"status": "no_data"}

            analysis = {
                "total_incidents": len(incidents),
                "types": {},
                "symbols": set(),
                "timestamp_range": {
                    "min": float("inf"),
                    "max": 0.0
                }
            }

            for incident in incidents:
                incident_type = incident.get("type", "unknown")
                analysis["types"][incident_type] = analysis["types"].get(incident_type, 0) + 1
                if "symbol" in incident:
                    analysis["symbols"].add(incident["symbol"])
                analysis["timestamp_range"]["min"] = min(analysis["timestamp_range"]["min"], float(incident["timestamp"]))
                analysis["timestamp_range"]["max"] = max(analysis["timestamp_range"]["max"], float(incident["timestamp"]))

            # Calculate failure frequency by type
            analysis["failure_frequency"] = {
                t: count / len(incidents) for t, count in analysis["types"].items()
            }
            
            self.logger.log(f"Failure analysis: {analysis}")
            return analysis
        except Exception as e:
            self.logger.log(f"Error analyzing failure patterns: {e}")
            return {"status": "error", "error": str(e)}

    def collect_training_data(self, key_pattern: str = "*") -> List[Dict[str, Any]]:
        """Collect internal incident data for training."""
        try:
            incidents = self.cache.retrieve_incidents(key_pattern)
            dataset = [
                {
                    "type": incident.get("type", "unknown"),
                    "symbol": incident.get("symbol", "unknown"),
                    "timestamp": float(incident["timestamp"]),
                    "features": {
                        "value": float(incident.get("value", 0.0)),
                        "threshold": float(incident.get("threshold", 0.0)),
                        "description": incident.get("description", "")
                    }
                }
                for incident in incidents
            ]
            self.logger.log(f"Collected {len(dataset)} incidents for training")
            return dataset
        except Exception as e:
            self.logger.log(f"Error collecting training data: {e}")
            return []