from typing import Dict, Any, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class AgentSentiment:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.analyzer = SentimentIntensityAnalyzer()
        self.sentiment_threshold = config.get("sentiment_threshold", -0.5)  # Negative sentiment threshold

    async def analyze_sentiment(self, social_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment of crowd feedback on agent performance."""
        try:
            sentiment_results = []
            for data in social_data:
                text = data.get("text", "")
                if not text:
                    continue

                sentiment = self.analyzer.polarity_scores(text)
                if sentiment["compound"] < self.sentiment_threshold:
                    issue = {
                        "type": "negative_agent_sentiment",
                        "agent": data.get("agent", "unknown"),
                        "source": data.get("source", "unknown"),
                        "sentiment_score": sentiment["compound"],
                        "timestamp": int(time.time()),
                        "description": f"Negative sentiment for {data.get('agent')}: {text[:50]}"
                    }
                    sentiment_results.append(issue)
                    self.logger.log_issue(issue)
                    self.cache.store_incident(issue)
                    await self.notify_core(issue)
            return sentiment_results
        except Exception as e:
            self.logger.log(f"Error analyzing agent sentiment: {e}")
            self.cache.store_incident({
                "type": "agent_sentiment_error",
                "timestamp": int(time.time()),
                "description": f"Error analyzing agent sentiment: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of sentiment analysis results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish to Core Agent