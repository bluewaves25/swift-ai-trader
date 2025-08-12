from typing import Dict, Any, List
from ....logs.failure_agent_logger import FailureAgentLogger
from ....memory.incident_cache import IncidentCache
from ...internal.research_engine import ResearchEngine

class CostPatternSynthesizer:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, research_engine: ResearchEngine):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.research_engine = research_engine
        self.fee_impact_threshold = config.get("fee_impact_threshold", 0.01)  # 1% fee impact

    async def synthesize_patterns(self, internal_patterns: Dict[str, Any], external_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesize internal and external cost patterns for comprehensive insights."""
        try:
            synthesized = []
            internal_brokers = internal_patterns.get("by_broker", {})
            internal_symbols = internal_patterns.get("by_symbol", {})

            for data in external_data:
                broker = data.get("broker", "unknown")
                internal_fee_impact = internal_brokers.get(broker, 0.0)
                if internal_fee_impact > self.fee_impact_threshold or data.get("type") in ["negative_fee_sentiment", "regulatory_change"]:
                    pattern = {
                        "broker": broker,
                        "symbol": data.get("symbol", internal_symbols.get("symbol", "unknown")),
                        "internal_fee_impact": internal_fee_impact,
                        "external_source": data.get("source", "unknown"),
                        "description": f"Synthesized pattern: {broker} with {internal_fee_impact:.4f} internal impact, {data.get('description', '')[:50]}"
                    }
                    synthesized.append(pattern)
                    self.logger.log(f"Synthesized pattern: {pattern['description']}")
                    self.cache.store_incident({
                        "type": "synthesized_cost_pattern",
                        "broker": broker,
                        "timestamp": int(time.time()),
                        "description": pattern["description"]
                    })

            result = {
                "type": "pattern_synthesis",
                "pattern_count": len(synthesized),
                "timestamp": int(time.time()),
                "description": f"Synthesized {len(synthesized)} cost patterns"
            }
            self.logger.log_issue(result)
            self.cache.store_incident(result)
            await self.notify_core(result)
            return synthesized
        except Exception as e:
            self.logger.log(f"Error synthesizing patterns: {e}")
            self.cache.store_incident({
                "type": "pattern_synthesizer_error",
                "timestamp": int(time.time()),
                "description": f"Error synthesizing patterns: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of synthesized patterns."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent