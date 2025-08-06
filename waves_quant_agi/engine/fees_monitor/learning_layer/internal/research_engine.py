from typing import Dict, Any, List
import statistics
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class ResearchEngine:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.pattern_threshold = config.get("pattern_threshold", 0.01)  # 1% fee impact

    async def analyze_cost_patterns(self, key_pattern: str = "*") -> Dict[str, Any]:
        """Analyze cost patterns from historical trade incidents."""
        try:
            incidents = self.cache.retrieve_incidents(f"fees_monitor:{key_pattern}")
            patterns = {
                "by_broker": {},
                "by_symbol": {},
                "high_fee_patterns": []
            }

            for incident in incidents:
                if incident.get("type") in ["pnl_adjusted", "hidden_fee_detected"]:
                    broker = incident.get("broker", "unknown")
                    symbol = incident.get("symbol", "unknown")
                    fee_impact = incident.get("total_fees", 0.0) / float(incident.get("trade_value", 1.0) or 1.0)

                    patterns["by_broker"].setdefault(broker, []).append(fee_impact)
                    patterns["by_symbol"].setdefault(symbol, []).append(fee_impact)

                    if fee_impact > self.pattern_threshold:
                        patterns["high_fee_patterns"].append({
                            "broker": broker,
                            "symbol": symbol,
                            "fee_impact": fee_impact,
                            "description": incident.get("description", "")
                        })

            for broker in patterns["by_broker"]:
                patterns["by_broker"][broker] = statistics.mean(patterns["by_broker"][broker]) if patterns["by_broker"][broker] else 0.0
            for symbol in patterns["by_symbol"]:
                patterns["by_symbol"][symbol] = statistics.mean(patterns["by_symbol"][symbol]) if patterns["by_symbol"][symbol] else 0.0

            result = {
                "type": "cost_pattern_analysis",
                "patterns": patterns,
                "timestamp": int(time.time()),
                "description": f"Analyzed cost patterns: {len(patterns['high_fee_patterns'])} high-fee patterns found"
            }
            self.logger.log_issue(result)
            self.cache.store_incident(result)
            await self.notify_core(result)
            return patterns
        except Exception as e:
            self.logger.log(f"Error analyzing cost patterns: {e}")
            self.cache.store_incident({
                "type": "cost_pattern_error",
                "timestamp": int(time.time()),
                "description": f"Error analyzing cost patterns: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of cost pattern analysis."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent