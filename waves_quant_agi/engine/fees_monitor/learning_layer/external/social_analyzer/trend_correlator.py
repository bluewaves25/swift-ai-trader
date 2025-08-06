from typing import Dict, Any, List
import statistics
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class TrendCorrelator:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.complaint_spike_threshold = config.get("complaint_spike_threshold", 5)  # Min complaints for spike

    async def correlate_trends(self, complaints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Correlate spikes in fee complaints with brokers or market conditions."""
        try:
            broker_complaints = {}
            for complaint in complaints:
                broker = complaint.get("broker", "unknown")
                broker_complaints[broker] = broker_complaints.get(broker, 0) + 1

            trends = {
                "type": "complaint_trend",
                "spikes": [],
                "timestamp": int(time.time()),
                "description": ""
            }
            for broker, count in broker_complaints.items():
                if count >= self.complaint_spike_threshold:
                    trends["spikes"].append({
                        "broker": broker,
                        "complaint_count": count,
                        "description": f"Spike in complaints for {broker}: {count} reports"
                    })

            if trends["spikes"]:
                trends["description"] = f"Detected {len(trends['spikes'])} complaint spikes"
                self.logger.log_issue(trends)
                self.cache.store_incident(trends)
                await self.notify_core(trends)
            return trends
        except Exception as e:
            self.logger.log(f"Error correlating trends: {e}")
            self.cache.store_incident({
                "type": "trend_correlator_error",
                "timestamp": int(time.time()),
                "description": f"Error correlating trends: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of complaint trend correlations."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent