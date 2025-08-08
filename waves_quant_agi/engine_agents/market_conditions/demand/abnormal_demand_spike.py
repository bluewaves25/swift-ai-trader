from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class AbnormalDemandSpike:
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
        self.spike_threshold = config.get("spike_threshold", 2.0)  # 2x standard deviation

    async def detect_demand_spike(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect large, hidden, or stealth demand spikes."""
        try:
            spikes = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                buy_volume = float(data.get("buy_volume", 0.0))
                avg_buy_volume = float(data.get("avg_buy_volume", 1.0))
                std_buy_volume = float(data.get("std_buy_volume", 0.1))

                if buy_volume > avg_buy_volume + self.spike_threshold * std_buy_volume:
                    spike_type = self._classify_spike(data)
                    spike = {
                        "type": "demand_spike",
                        "symbol": symbol,
                        "spike_type": spike_type,
                        "buy_volume": buy_volume,
                        "timestamp": int(time.time()),
                        "description": f"Demand spike for {symbol}: {spike_type} (volume: {buy_volume:.2f})"
                    }
                    spikes.append(spike)
                    self.logger.log_issue(spike)
                    self.cache.store_incident(spike)
                    self.redis_client.set(f"market_conditions:spike:{symbol}", str(spike), ex=604800)  # Expire after 7 days

            summary = {
                "type": "demand_spike_summary",
                "spike_count": len(spikes),
                "timestamp": int(time.time()),
                "description": f"Detected {len(spikes)} demand spikes"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return spikes
        except Exception as e:
            self.logger.log(f"Error detecting demand spikes: {e}")
            self.cache.store_incident({
                "type": "demand_spike_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting demand spikes: {str(e)}"
            })
            return []

    def _classify_spike(self, data: Dict[str, Any]) -> str:
        """Classify demand spike type (placeholder)."""
        # Mock: High order count suggests stealth, high volume suggests large
        return "stealth" if data.get("order_count", 1) > 10 else "large"

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of demand spike results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))