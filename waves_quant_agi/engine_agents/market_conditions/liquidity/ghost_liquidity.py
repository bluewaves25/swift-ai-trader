from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class GhostLiquidityDetector:
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
        self.ghost_threshold = config.get("ghost_threshold", 0.5)  # 50% withdrawal rate

    async def detect_ghost_liquidity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect fake or pulled liquidity in the market."""
        try:
            ghost_pools = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                order_volume = float(data.get("order_volume", 0.0))
                executed_volume = float(data.get("executed_volume", 0.0))

                withdrawal_rate = (order_volume - executed_volume) / order_volume if order_volume > 0 else 0.0
                if withdrawal_rate > self.ghost_threshold:
                    ghost = {
                        "type": "ghost_liquidity",
                        "symbol": symbol,
                        "withdrawal_rate": withdrawal_rate,
                        "timestamp": int(time.time()),
                        "description": f"Ghost liquidity detected for {symbol}: withdrawal rate {withdrawal_rate:.2f}"
                    }
                    ghost_pools.append(ghost)
                    self.logger.log_issue(ghost)
                    self.cache.store_incident(ghost)
                    self.redis_client.set(f"market_conditions:ghost_liquidity:{symbol}", str(ghost), ex=604800)  # Expire after 7 days

            summary = {
                "type": "ghost_liquidity_summary",
                "ghost_count": len(ghost_pools),
                "timestamp": int(time.time()),
                "description": f"Detected {len(ghost_pools)} ghost liquidity instances"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return ghost_pools
        except Exception as e:
            self.logger.log(f"Error detecting ghost liquidity: {e}")
            self.cache.store_incident({
                "type": "ghost_liquidity_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting ghost liquidity: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of ghost liquidity results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))