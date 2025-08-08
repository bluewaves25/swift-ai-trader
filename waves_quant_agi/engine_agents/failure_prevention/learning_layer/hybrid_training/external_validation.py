from typing import Dict, Any, List
from ...memory.incident_cache import IncidentCache
from ...logs.failure_agent_logger import FailureAgentLogger
from ..internal.research_engine import ResearchEngine

class ExternalValidation:
    def __init__(self, internal_engine: ResearchEngine, logger: FailureAgentLogger, cache: IncidentCache):
        self.internal_engine = internal_engine
        self.logger = logger
        self.cache = cache

    def validate_patterns(self, internal_pattern: str = "*", external_pattern: str = "*") -> List[Dict[str, Any]]:
        """Validate internal failure patterns against external data."""
        try:
            internal_patterns = self.internal_engine.analyze_failure_patterns(internal_pattern)
            external_data = self.cache.retrieve_incidents(external_pattern)
            validated = []

            internal_types = internal_patterns.get("types", {})
            for ext_item in external_data:
                ext_description = ext_item.get("description", "").lower()
                for int_type in internal_types:
                    if int_type in ext_description or ext_item.get("type") in ["technical_issue", "market_sentiment", "industry_incident"]:
                        validation = {
                            "type": "validated_pattern",
                            "internal_type": int_type,
                            "external_type": ext_item.get("type", "unknown"),
                            "confidence": min(1.0, internal_types[int_type] / max(1, len(external_data))),
                            "timestamp": ext_item["timestamp"],
                            "description": f"Validated {int_type} with {ext_item.get('description', '')[:50]}..."
                        }
                        self.cache.store_incident(validation)
                        self.logger.log(f"Validated pattern: {validation['description']}")
                        validated.append(validation)
            return validated
        except Exception as e:
            self.logger.log(f"Error validating patterns: {e}")
            return []