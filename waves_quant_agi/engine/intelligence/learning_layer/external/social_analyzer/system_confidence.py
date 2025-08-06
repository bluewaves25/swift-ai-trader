from typing import Dict, Any, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class SystemConfidence:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.analyzer = SentimentIntensityAnalyzer()
        self.confidence_threshold = config.get("confidence_threshold", 0.3)  # Positive sentiment threshold

    async def measure_confidence(self, social_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Measure public trust in the AI system based on social feedback."""
        try:
            confidence_scores = []
            for data in social_data:
                text = data.get("text", "")
                if not text:
                    continue

                sentiment = self.analyzer.polarity_scores(text)
                score = sentiment["compound"]
                confidence_scores.append(score)
                if score < self.confidence_threshold:
                    issue = {
                        "type": "low_system_confidence",
                        "source": data.get("source", "unknown"),
                        "sentiment_score": score,
                        "timestamp": int(time.time()),
                        "description": f"Low system confidence from {data.get('source')}: {text[:50]}"
                    }
                    self.logger.log_issue(issue)
                    self.cache.store_incident(issue)

            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            result = {
                "type": "system_confidence",
                "average_score": avg_confidence,
                "data_points": len(confidence_scores),
                "timestamp": int(time.time()),
                "description": f"System confidence score: {avg_confidence:.4f} from {len(confidence_scores)} data points"
            }
            self.logger.log_issue(result)
            self.cache.store_incident(result)
            await self.notify_core(result)
            return result
        except Exception as e:
            self.logger.log(f"Error measuring system confidence: {e}")
            self.cache.store_incident({
                "type": "system_confidence_error",
                "timestamp": int(time.time()),
                "description": f"Error measuring system confidence: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of system confidence results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish to Core Agent