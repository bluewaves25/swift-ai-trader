from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class OutlierDetector:
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
        self.outlier_threshold = config.get("outlier_threshold", 0.8)  # Outlier detection threshold

    async def detect_outliers(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect market behaviors outside historical or expected bounds."""
        try:
            outliers = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                outlier_score = float(data.get("outlier_score", 0.0))

                if outlier_score > self.outlier_threshold:
                    outlier = {
                        "type": "outlier_detected",
                        "symbol": symbol,
                        "outlier_score": outlier_score,
                        "timestamp": int(time.time()),
                        "description": f"Outlier detected for {symbol}: score {outlier_score:.2f}"
                    }
                    outliers.append(outlier)
                    self.logger.log_issue(outlier)
                    self.cache.store_incident(outlier)
                    self.redis_client.set(f"market_conditions:outlier:{symbol}", str(outlier), ex=604800)  # Expire after 7 days

            summary = {
                "type": "outlier_summary",
                "outlier_count": len(outliers),
                "timestamp": int(time.time()),
                "description": f"Detected {len(outliers)} market outliers"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return outliers
        except Exception as e:
            self.logger.log(f"Error detecting outliers: {e}")
            self.cache.store_incident({
                "type": "outlier_detector_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting outliers: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of outlier detection results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))