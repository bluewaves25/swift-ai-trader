import time
from typing import Dict, Any, List
import redis
from ....logs.failure_agent_logger import FailureAgentLogger
from ....logs.incident_cache import IncidentCache

class RatePolicyShockPredictor:
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
        self.shock_threshold = config.get("shock_threshold", 0.6)  # Confidence threshold for shocks

    async def predict_rate_shocks(self, macro_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict shocks from interest rate or policy changes."""
        try:
            shocks = []
            for data in macro_data:
                symbol = data.get("symbol", "unknown")
                shock_probability = float(data.get("shock_probability", 0.0))
                source = data.get("source", "unknown")

                if shock_probability > self.shock_threshold:
                    shock = {
                        "type": "rate_policy_shock",
                        "symbol": symbol,
                        "source": source,
                        "shock_probability": shock_probability,
                        "timestamp": int(time.time()),
                        "description": f"Rate policy shock for {symbol} from {source}: probability {shock_probability:.2f}"
                    }
                    shocks.append(shock)
                    self.logger.log_issue(shock)
                    self.cache.store_incident(shock)
                    self.redis_client.set(f"market_conditions:rate_shock:{symbol}", str(shock), ex=604800)  # Expire after 7 days

            summary = {
                "type": "rate_shock_summary",
                "shock_count": len(shocks),
                "timestamp": int(time.time()),
                "description": f"Predicted {len(shocks)} rate policy shocks"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return shocks
        except Exception as e:
            self.logger.log(f"Error predicting rate policy shocks: {e}")
            self.cache.store_incident({
                "type": "rate_shock_error",
                "timestamp": int(time.time()),
                "description": f"Error predicting rate policy shocks: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of rate policy shock predictions."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))