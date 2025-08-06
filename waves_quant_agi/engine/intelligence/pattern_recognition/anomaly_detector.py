from typing import Dict, Any, List
import statistics
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class AnomalyDetector:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.anomaly_threshold = config.get("anomaly_threshold", 2.0)  # 2 standard deviations

    async def detect_anomalies(self, agent_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in agent performance metrics."""
        try:
            anomalies = []
            for metric_type in ["speed", "accuracy", "cost", "error_rate"]:
                values = [float(m.get(metric_type, 0.0)) for m in agent_metrics if m.get(metric_type, 0.0) > 0]
                if not values or len(values) < 2:
                    continue

                mean = statistics.mean(values)
                stdev = statistics.stdev(values) if len(values) > 1 else 0
                threshold = mean + self.anomaly_threshold * stdev

                for metric in agent_metrics:
                    value = float(metric.get(metric_type, 0.0))
                    if value > threshold:
                        anomaly = {
                            "type": "agent_anomaly",
                            "agent": metric.get("agent", "unknown"),
                            "metric_type": metric_type,
                            "value": value,
                            "threshold": threshold,
                            "timestamp": int(time.time()),
                            "description": f"Anomaly in {metric_type} for {metric.get('agent')}: {value:.4f} exceeds {threshold:.4f}"
                        }
                        anomalies.append(anomaly)
                        self.logger.log_issue(anomaly)
                        self.cache.store_incident(anomaly)

            result = {
                "type": "anomaly_detection",
                "anomaly_count": len(anomalies),
                "timestamp": int(time.time()),
                "description": f"Detected {len(anomalies)} agent performance anomalies"
            }
            self.cache.store_incident(result)
            await self.notify_core(result)
            return anomalies
        except Exception as e:
            self.logger.log(f"Error detecting anomalies: {e}")
            self.cache.store_incident({
                "type": "anomaly_detector_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting anomalies: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of anomaly detections."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish to Core Agent