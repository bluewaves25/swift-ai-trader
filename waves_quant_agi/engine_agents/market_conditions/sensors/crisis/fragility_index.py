from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class FragilityIndex:
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
        self.fragility_threshold = config.get("fragility_threshold", 0.7)  # Fragility score threshold

    async def measure_fragility(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Measure how fragile the current market structure is."""
        try:
            fragilities = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                liquidity_depth = float(data.get("liquidity_depth", 1.0))
                volatility = float(data.get("volatility", 0.0))

                fragility_score = self._calculate_fragility(liquidity_depth, volatility)
                if fragility_score > self.fragility_threshold:
                    fragility = {
                        "type": "fragility_index",
                        "symbol": symbol,
                        "fragility_score": fragility_score,
                        "timestamp": int(time.time()),
                        "description": f"Fragility for {symbol}: score {fragility_score:.2f}"
                    }
                    fragilities.append(fragility)
                    self.logger.log_issue(fragility)
                    self.cache.store_incident(fragility)
                    self.redis_client.set(f"market_conditions:fragility:{symbol}", str(fragility), ex=604800)  # Expire after 7 days

            summary = {
                "type": "fragility_summary",
                "fragility_count": len(fragilities),
                "timestamp": int(time.time()),
                "description": f"Measured {len(fragilities)} fragile market conditions"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return fragilities
        except Exception as e:
            self.logger.log(f"Error measuring fragility: {e}")
            self.cache.store_incident({
                "type": "fragility_index_error",
                "timestamp": int(time.time()),
                "description": f"Error measuring fragility: {str(e)}"
            })
            return []

    def _calculate_fragility(self, liquidity_depth: float, volatility: float) -> float:
        """Calculate fragility score (placeholder)."""
        # Mock: High volatility and low liquidity suggest fragility
        return min(1.0, volatility / liquidity_depth if liquidity_depth > 0 else 0.8)

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of fragility results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))