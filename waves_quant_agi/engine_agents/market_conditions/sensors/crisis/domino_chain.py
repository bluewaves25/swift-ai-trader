import time
from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...logs.incident_cache import IncidentCache

class DominoChain:
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
        self.chain_threshold = config.get("chain_threshold", 0.7)  # Confidence for chain reaction

    async def predict_domino_chain(self, crisis_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict chain reactions from initial crisis signs."""
        try:
            chains = []
            for data in crisis_data:
                symbol = data.get("symbol", "unknown")
                crisis_score = float(data.get("crisis_score", 0.0))

                if crisis_score > self.chain_threshold:
                    chain = {
                        "type": "domino_chain",
                        "symbol": symbol,
                        "crisis_score": crisis_score,
                        "predicted_impact": self._predict_impact(crisis_score),
                        "timestamp": int(time.time()),
                        "description": f"Domino chain predicted for {symbol}: score {crisis_score:.2f}"
                    }
                    chains.append(chain)
                    self.logger.log_issue(chain)
                    self.cache.store_incident(chain)
                    self.redis_client.set(f"market_conditions:domino_chain:{symbol}", str(chain), ex=604800)  # Expire after 7 days

            summary = {
                "type": "domino_chain_summary",
                "chain_count": len(chains),
                "timestamp": int(time.time()),
                "description": f"Predicted {len(chains)} domino chain reactions"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return chains
        except Exception as e:
            self.logger.log(f"Error predicting domino chains: {e}")
            self.cache.store_incident({
                "type": "domino_chain_error",
                "timestamp": int(time.time()),
                "description": f"Error predicting domino chains: {str(e)}"
            })
            return []

    def _predict_impact(self, crisis_score: float) -> str:
        """Predict impact of crisis (placeholder)."""
        return "high" if crisis_score > 0.8 else "moderate"

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of domino chain predictions."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))