from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class SupplyDetector:
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
        self.volume_threshold = config.get("volume_threshold", 1.5)  # 1.5x average volume

    async def classify_supply_behavior(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Classify real-time supply behavior based on volume and offers."""
        try:
            behaviors = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                volume = float(data.get("volume", 0.0))
                offers = float(data.get("offers", 0.0))
                avg_volume = float(data.get("avg_volume", 1.0))

                behavior = "normal"
                if volume > self.volume_threshold * avg_volume:
                    behavior = "high_supply"
                elif volume < 0.5 * avg_volume:
                    behavior = "low_supply"

                result = {
                    "type": "supply_behavior",
                    "symbol": symbol,
                    "behavior": behavior,
                    "volume": volume,
                    "offers": offers,
                    "timestamp": int(time.time()),
                    "description": f"Supply behavior for {symbol}: {behavior} (volume: {volume}, offers: {offers})"
                }
                behaviors.append(result)
                self.logger.log_issue(result)
                self.cache.store_incident(result)
                self.redis_client.set(f"market_conditions:supply:{symbol}", str(result), ex=604800)  # Expire after 7 days

            summary = {
                "type": "supply_behavior_summary",
                "behavior_count": len(behaviors),
                "timestamp": int(time.time()),
                "description": f"Classified supply behavior for {len(behaviors)} symbols"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return summary
        except Exception as e:
            self.logger.log(f"Error classifying supply behavior: {e}")
            self.cache.store_incident({
                "type": "supply_detector_error",
                "timestamp": int(time.time()),
                "description": f"Error classifying supply behavior: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of supply behavior results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))