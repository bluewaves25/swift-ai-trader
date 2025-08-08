from typing import Dict, Any, List
import redis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class SocialWarningSystem:
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
        self.warning_threshold = config.get("warning_threshold", 0.5)  # Sentiment score threshold

    async def detect_social_warnings(self, social_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect spikes in trader concerns or rumors."""
        try:
            warnings = []
            analyzer = SentimentIntensityAnalyzer()
            for data in social_data:
                symbol = data.get("symbol", "unknown")
                text = data.get("text", "")
                source = data.get("source", "unknown")

                sentiment = analyzer.polarity_scores(text)
                if sentiment["compound"] < -self.warning_threshold:
                    warning = {
                        "type": "social_warning",
                        "symbol": symbol,
                        "source": source,
                        "sentiment_score": sentiment["compound"],
                        "timestamp": int(time.time()),
                        "description": f"Social warning for {symbol} from {source}: {text[:50]} (score: {sentiment['compound']:.2f})"
                    }
                    warnings.append(warning)
                    self.logger.log_issue(warning)
                    self.cache.store_incident(warning)
                    self.redis_client.set(f"market_conditions:social_warning:{symbol}", str(warning), ex=604800)  # Expire after 7 days

            summary = {
                "type": "social_warning_summary",
                "warning_count": len(warnings),
                "timestamp": int(time.time()),
                "description": f"Detected {len(warnings)} social warnings"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return warnings
        except Exception as e:
            self.logger.log(f"Error detecting social warnings: {e}")
            self.cache.store_incident({
                "type": "social_warning_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting social warnings: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of social warning results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))