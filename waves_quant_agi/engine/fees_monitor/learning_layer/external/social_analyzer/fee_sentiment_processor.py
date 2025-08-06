from typing import Dict, Any, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class FeeSentimentProcessor:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.analyzer = SentimentIntensityAnalyzer()
        self.sentiment_threshold = config.get("sentiment_threshold", -0.5)  # Negative sentiment threshold

    async def process_sentiment(self, complaints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment of fee-related complaints from forums."""
        try:
            sentiment_results = []
            for complaint in complaints:
                text = complaint.get("description", "")
                if not text:
                    continue

                sentiment = self.analyzer.polarity_scores(text)
                if sentiment["compound"] < self.sentiment_threshold:
                    issue = {
                        "type": "negative_fee_sentiment",
                        "broker": complaint.get("broker", "unknown"),
                        "source": complaint.get("source", "unknown"),
                        "sentiment_score": sentiment["compound"],
                        "timestamp": int(time.time()),
                        "description": f"Negative sentiment for {complaint.get('broker')}: {text[:50]}"
                    }
                    sentiment_results.append(issue)
                    self.logger.log_issue(issue)
                    self.cache.store_incident(issue)
                    await self.notify_core(issue)
            return sentiment_results
        except Exception as e:
            self.logger.log(f"Error processing sentiment: {e}")
            self.cache.store_incident({
                "type": "sentiment_processor_error",
                "timestamp": int(time.time()),
                "description": f"Error processing sentiment: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of sentiment analysis results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent