from typing import Dict, Any, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class SentimentProcessor:
    def __init__(self, logger: FailureAgentLogger, cache: IncidentCache):
        self.analyzer = SentimentIntensityAnalyzer()
        self.logger = logger
        self.cache = cache

    def process_sentiment(self, social_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment of social media data and assign risk scores."""
        try:
            processed_data = []
            for item in social_data:
                text = item.get("text", "") or item.get("title", "")
                if not text:
                    continue
                sentiment = self.analyzer.polarity_scores(text)
                risk_score = -sentiment["compound"]  # Negative sentiment = higher risk
                processed = {
                    "source": item.get("source", "unknown"),
                    "keyword": item.get("keyword", ""),
                    "type": "processed_sentiment",
                    "risk_score": max(min(risk_score, 1.0), -1.0),  # Normalize to -1 to 1
                    "timestamp": item["timestamp"],
                    "description": f"Sentiment analysis for {item.get('keyword', 'unknown')}: {text[:50]}..."
                }
                self.cache.store_incident(processed)
                self.logger.log(f"Processed sentiment: {processed['description']}, risk_score: {processed['risk_score']}")
                processed_data.append(processed)
            return processed_data
        except Exception as e:
            self.logger.log(f"Error processing sentiment: {e}")
            return []