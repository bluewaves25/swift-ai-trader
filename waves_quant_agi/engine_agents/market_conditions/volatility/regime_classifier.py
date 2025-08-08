from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class RegimeClassifier:
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
        self.volatility_threshold = config.get("volatility_threshold", 0.015)  # 1.5% price change

    async def classify_regime(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify market as stable, volatile, or noisy."""
        try:
            regimes = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                price_change = float(data.get("price_change", 0.0))
                volume_spike = float(data.get("volume_spike", 0.0))

                regime = self._classify_regime(price_change, volume_spike)
                result = {
                    "type": "market_regime",
                    "symbol": symbol,
                    "regime": regime,
                    "price_change": price_change,
                    "timestamp": int(time.time()),
                    "description": f"Market regime for {symbol}: {regime} (price change: {price_change:.4f})"
                }
                regimes.append(result)
                self.logger.log_issue(result)
                self.cache.store_incident(result)
                self.redis_client.set(f"market_conditions:regime:{symbol}", str(result), ex=604800)  # Expire after 7 days

            summary = {
                "type": "regime_summary",
                "regime_count": len(regimes),
                "timestamp": int(time.time()),
                "description": f"Classified {len(regimes)} market regimes"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return regimes
        except Exception as e:
            self.logger.log(f"Error classifying regimes: {e}")
            self.cache.store_incident({
                "type": "regime_classifier_error",
                "timestamp": int(time.time()),
                "description": f"Error classifying regimes: {str(e)}"
            })
            return []

    def _classify_regime(self, price_change: float, volume_spike: float) -> str:
        """Classify market regime (placeholder)."""
        # Mock: High price change with low volume suggests noise
        if abs(price_change) > self.volatility_threshold and volume_spike < 100:
            return "noisy"
        elif abs(price_change) > self.volatility_threshold:
            return "volatile"
        return "stable"

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of regime classification results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))