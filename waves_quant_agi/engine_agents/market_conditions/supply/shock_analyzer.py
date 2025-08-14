import time
from typing import Dict, Any, List
import redis
from ..logs.failure_agent_logger import FailureAgentLogger
from ..logs.incident_cache import IncidentCache

class SupplyShockAnalyzer:
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
        self.shock_threshold = config.get("shock_threshold", 2.0)  # 2x standard deviation

    async def detect_supply_shock(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect sudden supply influx or outflow."""
        try:
            shocks = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                volume = float(data.get("volume", 0.0))
                avg_volume = float(data.get("avg_volume", 1.0))
                std_volume = float(data.get("std_volume", 0.1))

                if abs(volume - avg_volume) > self.shock_threshold * std_volume:
                    shock_type = "influx" if volume > avg_volume else "outflow"
                    shock = {
                        "type": "supply_shock",
                        "symbol": symbol,
                        "shock_type": shock_type,
                        "volume": volume,
                        "timestamp": int(time.time()),
                        "description": f"Supply {shock_type} detected for {symbol}: volume {volume:.2f}"
                    }
                    shocks.append(shock)
                    self.logger.log_issue(shock)
                    self.cache.store_incident(shock)
                    self.redis_client.set(f"market_conditions:shock:{symbol}", str(shock), ex=604800)  # Expire after 7 days

            summary = {
                "type": "supply_shock_summary",
                "shock_count": len(shocks),
                "timestamp": int(time.time()),
                "description": f"Detected {len(shocks)} supply shocks"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return shocks
        except Exception as e:
            self.logger.log(f"Error detecting supply shocks: {e}")
            self.cache.store_incident({
                "type": "supply_shock_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting supply shocks: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of supply shock results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))