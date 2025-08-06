from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class SpikeDetector:
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
        self.spike_threshold = config.get("spike_threshold", 3.0)  # 3x standard deviation

    async def detect_volatility_spike(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect sudden explosions in price or volume."""
        try:
            spikes = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                price_change = float(data.get("price_change", 0.0))
                volume = float(data.get("volume", 0.0))
                avg_volume = float(data.get("avg_volume", 1.0))
                std_volume = float(data.get("std_volume", 0.1))

                if abs(price_change) > self.spike_threshold or volume > avg_volume + self.spike_threshold * std_volume:
                    spike_type = "price" if abs(price_change) > self.spike_threshold else "volume"
                    spike = {
                        "type": "volatility_spike",
                        "symbol": symbol,
                        "spike_type": spike_type,
                        "value": price_change if spike_type == "price" else volume,
                        "timestamp": int(time.time()),
                        "description": f"{spike_type.capitalize()} spike for {symbol}: {spike_type} {spike['value']:.2f}"
                    }
                    spikes.append(spike)
                    self.logger.log_issue(spike)
                    self.cache.store_incident(spike)
                    self.redis_client.set(f"market_conditions:spike:{symbol}", str(spike), ex=604800)  # Expire after 7 days

            summary = {
                "type": "volatility_spike_summary",
                "spike_count": len(spikes),
                "timestamp": int(time.time()),
                "description": f"Detected {len(spikes)} volatility spikes"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return spikes
        except Exception as e:
            self.logger.log(f"Error detecting volatility spikes: {e}")
            self.cache.store_incident({
                "type": "spike_detector_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting volatility spikes: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of volatility spike results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))