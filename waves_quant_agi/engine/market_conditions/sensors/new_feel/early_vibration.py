from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class EarlyVibration:
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
        self.vibration_threshold = config.get("vibration_threshold", 0.01)  # 1% signal deviation

    async def detect_early_vibration(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect latent market shifts using quantum-inspired early feelers."""
        try:
            vibrations = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                signal_deviation = float(data.get("signal_deviation", 0.0))

                if abs(signal_deviation) > self.vibration_threshold:
                    vibration = {
                        "type": "early_vibration",
                        "symbol": symbol,
                        "signal_deviation": signal_deviation,
                        "timestamp": int(time.time()),
                        "description": f"Early vibration for {symbol}: deviation {signal_deviation:.4f}"
                    }
                    vibrations.append(vibration)
                    self.logger.log_issue(vibration)
                    self.cache.store_incident(vibration)
                    self.redis_client.set(f"market_conditions:vibration:{symbol}", str(vibration), ex=604800)  # Expire after 7 days

            summary = {
                "type": "early_vibration_summary",
                "vibration_count": len(vibrations),
                "timestamp": int(time.time()),
                "description": f"Detected {len(vibrations)} early vibrations"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return vibrations
        except Exception as e:
            self.logger.log(f"Error detecting early vibrations: {e}")
            self.cache.store_incident({
                "type": "early_vibration_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting early vibrations: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of early vibration results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))