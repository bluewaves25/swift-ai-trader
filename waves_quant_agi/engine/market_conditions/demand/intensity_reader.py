from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class DemandIntensityReader:
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
        self.intensity_threshold = config.get("intensity_threshold", 1.5)  # 1.5x average buy volume

    async def measure_demand_intensity(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Measure urgency and strength of buying in real-time."""
        try:
            intensities = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                buy_volume = float(data.get("buy_volume", 0.0))
                avg_buy_volume = float(data.get("avg_buy_volume", 1.0))

                intensity = "normal"
                if buy_volume > self.intensity_threshold * avg_buy_volume:
                    intensity = "high_demand"
                elif buy_volume < 0.5 * avg_buy_volume:
                    intensity = "low_demand"

                result = {
                    "type": "demand_intensity",
                    "symbol": symbol,
                    "intensity": intensity,
                    "buy_volume": buy_volume,
                    "timestamp": int(time.time()),
                    "description": f"Demand intensity for {symbol}: {intensity} (buy volume: {buy_volume})"
                }
                intensities.append(result)
                self.logger.log_issue(result)
                self.cache.store_incident(result)
                self.redis_client.set(f"market_conditions:demand_intensity:{symbol}", str(result), ex=604800)  # Expire after 7 days

            summary = {
                "type": "demand_intensity_summary",
                "intensity_count": len(intensities),
                "timestamp": int(time.time()),
                "description": f"Measured demand intensity for {len(intensities)} symbols"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return summary
        except Exception as e:
            self.logger.log(f"Error measuring demand intensity: {e}")
            self.cache.store_incident({
                "type": "demand_intensity_error",
                "timestamp": int(time.time()),
                "description": f"Error measuring demand intensity: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of demand intensity results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))