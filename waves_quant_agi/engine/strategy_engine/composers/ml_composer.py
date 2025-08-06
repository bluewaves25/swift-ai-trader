from typing import Dict, Any, List
import redis
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from ...market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ...market_conditions.memory.incident_cache import IncidentCache

class MLComposer:
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
        self.model = RandomForestClassifier(n_estimators=config.get("n_estimators", 100))
        self.confidence_threshold = config.get("confidence_threshold", 0.7)

    async def compose_strategy(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate ML-based strategy blueprints based on market conditions."""
        try:
            strategies = []
            features = self._extract_features(market_data)
            predictions = self.model.predict_proba(features)[:, 1]  # Probability of strategy success

            for data, pred in zip(market_data, predictions):
                symbol = data.get("symbol", "unknown")
                if pred > self.confidence_threshold:
                    strategy = {
                        "type": "ml_strategy",
                        "symbol": symbol,
                        "strategy_type": self._map_prediction_to_strategy(pred),
                        "confidence": float(pred),
                        "timestamp": int(time.time()),
                        "description": f"ML-composed strategy for {symbol}: confidence {pred:.2f}"
                    }
                    strategies.append(strategy)
                    self.logger.log_issue(strategy)
                    self.cache.store_incident(strategy)
                    self.redis_client.set(f"strategy_engine:ml_strategy:{symbol}", str(strategy), ex=604800)

            summary = {
                "type": "ml_composer_summary",
                "strategy_count": len(strategies),
                "timestamp": int(time.time()),
                "description": f"Composed {len(strategies)} ML-based strategies"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return strategies
        except Exception as e:
            self.logger.log(f"Error composing ML strategies: {e}")
            self.cache.store_incident({
                "type": "ml_composer_error",
                "timestamp": int(time.time()),
                "description": f"Error composing ML strategies: {str(e)}"
            })
            return []

    def _extract_features(self, market_data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features for ML model (placeholder)."""
        return np.array([[data.get("volatility", 0.0), data.get("trend_score", 0.0)] for data in market_data])

    def _map_prediction_to_strategy(self, prediction: float) -> str:
        """Map ML prediction to strategy type."""
        if prediction > 0.9: return "trend_following"
        if prediction > 0.8: return "news_driven"
        if prediction > 0.7: return "statistical_arbitrage"
        return "market_making"

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of composed strategies."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))