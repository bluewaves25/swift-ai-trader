import time
from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class HedgeFundMonitor:
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
        self.activity_threshold = config.get("activity_threshold", 0.6)  # Confidence threshold for activity

    async def monitor_hedgefund_activity(self, external_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Watch large fund rebalancing or strategic moves."""
        try:
            activities = []
            for data in external_data:
                symbol = data.get("symbol", "unknown")
                activity_score = float(data.get("activity_score", 0.0))
                source = data.get("source", "unknown")

                if activity_score > self.activity_threshold:
                    activity = {
                        "type": "hedgefund_activity",
                        "symbol": symbol,
                        "source": source,
                        "activity_score": activity_score,
                        "timestamp": int(time.time()),
                        "description": f"Hedge fund activity for {symbol} from {source}: score {activity_score:.2f}"
                    }
                    activities.append(activity)
                    self.logger.log_issue(activity)
                    self.cache.store_incident(activity)
                    self.redis_client.set(f"market_conditions:hedgefund:{symbol}", str(activity), ex=604800)  # Expire after 7 days

            summary = {
                "type": "hedgefund_activity_summary",
                "activity_count": len(activities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(activities)} hedge fund activities"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return activities
        except Exception as e:
            self.logger.log(f"Error monitoring hedge fund activity: {e}")
            self.cache.store_incident({
                "type": "hedgefund_monitor_error",
                "timestamp": int(time.time()),
                "description": f"Error monitoring hedge fund activity: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of hedge fund activity results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))