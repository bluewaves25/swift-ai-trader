import time
from typing import Dict, Any, List
import redis
from ..logs.failure_agent_logger import FailureAgentLogger
from ..logs.incident_cache import IncidentCache

class RegulatoryEventMonitor:
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
        self.event_confidence = config.get("event_confidence", 0.6)  # Confidence threshold

    async def monitor_regulatory_events(self, event_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Monitor scheduled and unplanned regulatory events."""
        try:
            events = []
            for data in event_data:
                symbol = data.get("symbol", "unknown")
                event_type = data.get("event_type", "unknown")
                confidence = float(data.get("confidence", 0.5))

                if confidence > self.event_confidence:
                    event = {
                        "type": "regulatory_event",
                        "symbol": symbol,
                        "event_type": event_type,
                        "confidence": confidence,
                        "timestamp": int(time.time()),
                        "description": f"Regulatory event for {symbol}: {event_type} (confidence: {confidence:.2f})"
                    }
                    events.append(event)
                    self.logger.log_issue(event)
                    self.cache.store_incident(event)
                    self.redis_client.set(f"market_conditions:regulatory:{symbol}", str(event), ex=604800)  # Expire after 7 days

            summary = {
                "type": "regulatory_event_summary",
                "event_count": len(events),
                "timestamp": int(time.time()),
                "description": f"Detected {len(events)} regulatory events"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return events
        except Exception as e:
            self.logger.log(f"Error monitoring regulatory events: {e}")
            self.cache.store_incident({
                "type": "regulatory_event_error",
                "timestamp": int(time.time()),
                "description": f"Error monitoring regulatory events: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of regulatory event results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))