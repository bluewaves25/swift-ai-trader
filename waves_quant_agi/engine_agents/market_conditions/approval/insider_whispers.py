import time
from typing import Dict, Any, List
import redis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ..logs.failure_agent_logger import FailureAgentLogger
from ..logs.incident_cache import IncidentCache

class InsiderWhispers:
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
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.insider_threshold = config.get("insider_threshold", 0.4)  # Sentiment score threshold

    async def detect_insider_signals(self, social_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect insider signals using NLP and data fusion."""
        try:
            signals = []
            for data in social_data:
                symbol = data.get("symbol", "unknown")
                text = data.get("text", "")
                source = data.get("source", "unknown")

                sentiment = self.sentiment_analyzer.polarity_scores(text)
                if abs(sentiment["compound"]) > self.insider_threshold:
                    signal = {
                        "type": "insider_signal",
                        "symbol": symbol,
                        "source": source,
                        "sentiment_score": sentiment["compound"],
                        "timestamp": int(time.time()),
                        "description": f"Insider signal for {symbol} from {source}: {text[:50]} (score: {sentiment['compound']:.2f})"
                    }
                    signals.append(signal)
                    self.logger.log_issue(signal)
                    self.cache.store_incident(signal)
                    self.redis_client.set(f"market_conditions:insider:{symbol}", str(signal), ex=604800)  # Expire after 7 days

            summary = {
                "type": "insider_signal_summary",
                "signal_count": len(signals),
                "timestamp": int(time.time()),
                "description": f"Detected {len(signals)} insider signals"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return signals
        except Exception as e:
            self.logger.log(f"Error detecting insider signals: {e}")
            self.cache.store_incident({
                "type": "insider_whispers_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting insider signals: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of insider signal results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))