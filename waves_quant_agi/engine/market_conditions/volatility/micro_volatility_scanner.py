from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class MicroVolatilityScanner:
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
        self.micro_threshold = config.get("micro_threshold", 0.005)  # 0.5% intra-minute change

    async def scan_micro_volatility(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect intra-minute or micro-trend volatility shifts."""
        try:
            micro_shifts = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                price_change = float(data.get("intra_minute_price_change", 0.0))

                if abs(price_change) > self.micro_threshold:
                    shift = {
                        "type": "micro_volatility",
                        "symbol": symbol,
                        "price_change": price_change,
                        "timestamp": int(time.time()),
                        "description": f"Micro-volatility shift for {symbol}: price change {price_change:.4f}"
                    }
                    micro_shifts.append(shift)
                    self.logger.log_issue(shift)
                    self.cache.store_incident(shift)
                    self.redis_client.set(f"market_conditions:micro_volatility:{symbol}", str(shift), ex=604800)  # Expire after 7 days

            summary = {
                "type": "micro_volatility_summary",
                "shift_count": len(micro_shifts),
                "timestamp": int(time.time()),
                "description": f"Detected {len(micro_shifts)} micro-volatility shifts"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return micro_shifts
        except Exception as e:
            self.logger.log(f"Error scanning micro-volatility: {e}")
            self.cache.store_incident({
                "type": "micro_volatility_error",
                "timestamp": int(time.time()),
                "description": f"Error scanning micro-volatility: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of micro-volatility results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))