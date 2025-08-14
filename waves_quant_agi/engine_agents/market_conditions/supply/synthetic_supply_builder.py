import time
from typing import Dict, Any, List
import random
import redis
from ..logs.failure_agent_logger import FailureAgentLogger
from ..logs.incident_cache import IncidentCache

class SyntheticSupplyBuilder:
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
        self.variation_range = config.get("variation_range", 0.3)  # 30% variation

    async def generate_synthetic_supply(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simulate supply conditions for testing reactions."""
        try:
            synthetic_data = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                base_volume = float(data.get("volume", 100.0))
                base_offers = float(data.get("offers", 50.0))

                # Generate synthetic variations
                volume = base_volume * (1 + random.uniform(-self.variation_range, self.variation_range))
                offers = base_offers * (1 + random.uniform(-self.variation_range, self.variation_range))
                synthetic = {
                    "type": "synthetic_supply",
                    "symbol": symbol,
                    "volume": volume,
                    "offers": offers,
                    "timestamp": int(time.time()),
                    "description": f"Synthetic supply for {symbol}: volume {volume:.2f}, offers {offers:.2f}"
                }
                synthetic_data.append(synthetic)
                self.logger.log_issue(synthetic)
                self.cache.store_incident(synthetic)
                self.redis_client.set(f"market_conditions:synthetic:{symbol}", str(synthetic), ex=604800)  # Expire after 7 days

            summary = {
                "type": "synthetic_supply_summary",
                "data_count": len(synthetic_data),
                "timestamp": int(time.time()),
                "description": f"Generated {len(synthetic_data)} synthetic supply scenarios"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return synthetic_data
        except Exception as e:
            self.logger.log(f"Error generating synthetic supply: {e}")
            self.cache.store_incident({
                "type": "synthetic_supply_error",
                "timestamp": int(time.time()),
                "description": f"Error generating synthetic supply: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of synthetic supply results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))