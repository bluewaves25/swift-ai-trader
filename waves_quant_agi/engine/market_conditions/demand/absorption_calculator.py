from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class AbsorptionCalculator:
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
        self.absorption_threshold = config.get("absorption_threshold", 0.8)  # 80% absorption rate

    async def calculate_absorption(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate how much supply is absorbed by demand in real-time."""
        try:
            absorptions = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                buy_volume = float(data.get("buy_volume", 0.0))
                supply_volume = float(data.get("supply_volume", 1.0))

                absorption_rate = buy_volume / supply_volume if supply_volume > 0 else 0.0
                status = "high_absorption" if absorption_rate > self.absorption_threshold else "low_absorption"

                result = {
                    "type": "demand_absorption",
                    "symbol": symbol,
                    "absorption_rate": absorption_rate,
                    "status": status,
                    "timestamp": int(time.time()),
                    "description": f"Absorption for {symbol}: {status} (rate: {absorption_rate:.2f})"
                }
                absorptions.append(result)
                self.logger.log_issue(result)
                self.cache.store_incident(result)
                self.redis_client.set(f"market_conditions:absorption:{symbol}", str(result), ex=604800)  # Expire after 7 days

            summary = {
                "type": "absorption_summary",
                "absorption_count": len(absorptions),
                "timestamp": int(time.time()),
                "description": f"Calculated absorption for {len(absorptions)} symbols"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return absorptions
        except Exception as e:
            self.logger.log(f"Error calculating absorption: {e}")
            self.cache.store_incident({
                "type": "absorption_error",
                "timestamp": int(time.time()),
                "description": f"Error calculating absorption: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of absorption results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))