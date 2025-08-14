import time
from typing import Dict, Any, List
import redis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ....logs.failure_agent_logger import FailureAgentLogger
from ....logs.incident_cache import IncidentCache

class AIFinancialPress:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.sentiment_threshold = config.get("sentiment_threshold", 0.4)  # Sentiment score threshold

    async def analyze_financial_press(self, press_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze tone of financial press for market signals."""
        try:
            analyzer = SentimentIntensityAnalyzer()
            sentiments = []
            for data in press_data:
                symbol = data.get("symbol", "unknown")
                text = data.get("text", "")
                source = data.get("source", "unknown")

                sentiment = analyzer.polarity_scores(text)
                if abs(sentiment["compound"]) > self.sentiment_threshold:
                    signal = {
                        "type": "financial_press_signal",
                        "symbol": symbol,
                        "source": source,
                        "sentiment_score": sentiment["compound"],
                        "timestamp": int(time.time()),
                        "description": f"Financial press signal for {symbol} from {source}: score {sentiment['compound']:.2f}"
                    }
                    sentiments.append(signal)
                    self.logger.log_issue(signal)
                    self.cache.store_incident(signal)
                    self.redis_client.set(f"market_conditions:press:{symbol}", str(signal), ex=604800)  # Expire after 7 days

            summary = {
                "type": "financial_press_summary",
                "signal_count": len(sentiments),
                "timestamp": int(time.time()),
                "description": f"Analyzed {len(sentiments)} financial press signals"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return sentiments
        except Exception as e:
            self.logger.log(f"Error analyzing financial press: {e}")
            self.cache.store_incident({
                "type": "financial_press_error",
                "timestamp": int(time.time()),
                "description": f"Error analyzing financial press: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of financial press analysis results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))