from typing import Dict, Any, List
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache
from ..internal.research_engine import ResearchEngine

class PatternSynthesizer:
    def __init__(self, internal_engine: ResearchEngine, logger: FailureAgentLogger, cache: IncidentCache):
        self.internal_engine = internal_engine
        self.logger = logger
        self.cache = cache

    def synthesize_patterns(self, internal_data: List[Dict[str, Any]], external_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine internal and external patterns to identify cross-system risks."""
        try:
            synthesized = []
            internal_patterns = self.internal_engine.analyze_failure_patterns()
            internal_types = internal_patterns.get("types", {})
            
            for ext_item in external_data:
                ext_type = ext_item.get("type", "unknown")
                ext_description = ext_item.get("description", "").lower()
                risk_score = ext_item.get("risk_score", 0.5)
                
                # Match external issues to internal patterns
                for int_type in internal_types:
                    if int_type in ext_description or ext_type in ["technical_issue", "market_sentiment", "industry_incident"]:
                        pattern = {
                            "type": "synthesized_pattern",
                            "internal_type": int_type,
                            "external_type": ext_type,
                            "risk_score": risk_score,
                            "timestamp": ext_item["timestamp"],
                            "description": f"Pattern: {int_type} linked to {ext_description[:50]}..."
                        }
                        self.cache.store_incident(pattern)
                        self.logger.log(f"Synthesized pattern: {pattern['description']}")
                        synthesized.append(pattern)
            return synthesized
        except Exception as e:
            self.logger.log(f"Error synthesizing patterns: {e}")
            return []