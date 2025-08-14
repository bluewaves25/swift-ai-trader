import time
from typing import Dict, Any, List
import random
import redis
from ..logs.failure_agent_logger import FailureAgentLogger
from ..logs.incident_cache import IncidentCache

class PressureBuilder:
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
        self.pressure_variation = config.get("pressure_variation", 0.4)  # 40% variation

    async def simulate_pressure(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simulate conditions that may cause market shifts."""
        try:
            pressures = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                base_volume = float(data.get("volume", 100.0))
                base_imbalance = float(data.get("imbalance_ratio", 0.0))

                # Generate synthetic pressure conditions
                volume = base_volume * (1 + random.uniform(-self.pressure_variation, self.pressure_variation))
                imbalance = base_imbalance + random.uniform(-self.pressure_variation, self.pressure_variation)
                pressure = {
                    "type": "pressure_simulation",
                    "symbol": symbol,
                    "volume": volume,
                    "imbalance": imbalance,
                    "timestamp": int(time.time()),
                    "description": f"Simulated pressure for {symbol}: volume {volume:.2f}, imbalance {imbalance:.2f}"
                }
                pressures.append(pressure)
                self.logger.log_issue(pressure)
                self.cache.store_incident(pressure)
                self.redis_client.set(f"market_conditions:pressure:{symbol}", str(pressure), ex=604800)  # Expire after 7 days

            summary = {
                "type": "pressure_summary",
                "pressure_count": len(pressures),
                "timestamp": int(time.time()),
                "description": f"Simulated {len(pressures)} pressure scenarios"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return pressures
        except Exception as e:
            self.logger.log(f"Error simulating pressure: {e}")
            self.cache.store_incident({
                "type": "pressure_builder_error",
                "timestamp": int(time.time()),
                "description": f"Error simulating pressure: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of pressure simulation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))