from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class AbnormalPatterns:
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
        self.pattern_confidence = config.get("pattern_confidence", 0.6)  # Confidence threshold

    async def detect_abnormal_patterns(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect weird market moves using AI pattern matching."""
        try:
            patterns = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                pattern_score = float(data.get("pattern_score", 0.0))

                if pattern_score > self.pattern_confidence:
                    pattern = {
                        "type": "abnormal_pattern",
                        "symbol": symbol,
                        "pattern_score": pattern_score,
                        "timestamp": int(time.time()),
                        "description": f"Abnormal pattern for {symbol}: score {pattern_score:.2f}"
                    }
                    patterns.append(pattern)
                    self.logger.log_issue(pattern)
                    self.cache.store_incident(pattern)
                    self.redis_client.set(f"market_conditions:pattern:{symbol}", str(pattern), ex=604800)  # Expire after 7 days

            summary = {
                "type": "abnormal_pattern_summary",
                "pattern_count": len(patterns),
                "timestamp": int(time.time()),
                "description": f"Detected {len(patterns)} abnormal patterns"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return patterns
        except Exception as e:
            self.logger.log(f"Error detecting abnormal patterns: {e}")
            self.cache.store_incident({
                "type": "abnormal_pattern_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting abnormal patterns: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of abnormal pattern results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))