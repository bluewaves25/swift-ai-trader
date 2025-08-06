from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class ImbalanceTracker:
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
        self.imbalance_threshold = config.get("imbalance_threshold", 0.3)  # 30% imbalance ratio

    async def track_imbalance(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Track supply-demand imbalances over time."""
        try:
            imbalances = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                supply_volume = float(data.get("supply_volume", 1.0))
                demand_volume = float(data.get("demand_volume", 1.0))

                imbalance_ratio = (demand_volume - supply_volume) / supply_volume if supply_volume > 0 else 0.0
                status = "imbalanced" if abs(imbalance_ratio) > self.imbalance_threshold else "balanced"

                result = {
                    "type": "imbalance",
                    "symbol": symbol,
                    "imbalance_ratio": imbalance_ratio,
                    "status": status,
                    "timestamp": int(time.time()),
                    "description": f"Imbalance for {symbol}: {status} (ratio: {imbalance_ratio:.2f})"
                }
                imbalances.append(result)
                self.logger.log_issue(result)
                self.cache.store_incident(result)
                self.redis_client.set(f"market_conditions:imbalance:{symbol}", str(result), ex=604800)  # Expire after 7 days

            summary = {
                "type": "imbalance_summary",
                "imbalance_count": len(imbalances),
                "timestamp": int(time.time()),
                "description": f"Tracked imbalances for {len(imbalances)} symbols"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return imbalances
        except Exception as e:
            self.logger.log(f"Error tracking imbalances: {e}")
            self.cache.store_incident({
                "type": "imbalance_tracker_error",
                "timestamp": int(time.time()),
                "description": f"Error tracking imbalances: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of imbalance results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))