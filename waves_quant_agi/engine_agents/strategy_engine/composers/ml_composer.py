from typing import Dict, Any, List
import redis
import numpy as np
import time
from sklearn.ensemble import RandomForestClassifier
from ..logs.strategy_engine_logger import StrategyEngineLogger

class MLComposer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = self._init_redis()
        self.logger = StrategyEngineLogger("ml_composer", self.redis_client)
        self.model = RandomForestClassifier(n_estimators=config.get("n_estimators", 100))
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        self.stats = {
            "strategies_composed": 0,
            "high_confidence_strategies": 0,
            "model_predictions": 0,
            "errors": 0,
            "start_time": time.time()
        }

    def _init_redis(self) -> redis.Redis:
        """Initialize Redis connection."""
        try:
            redis_url = self.config.get("redis_url", "redis://localhost:6379")
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            self.logger.log("Redis connection established", "info")
            return client
        except Exception as e:
            self.logger.log_error(f"Failed to connect to Redis: {e}")
            raise

    async def compose_strategy(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate ML-based strategy blueprints based on market conditions."""
        try:
            strategies = []
            features = self._extract_features(market_data)
            predictions = self.model.predict_proba(features)[:, 1]  # Probability of strategy success

            for data, pred in zip(market_data, predictions):
                symbol = data.get("symbol", "unknown")
                self.stats["model_predictions"] += 1
                
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
                    
                    # Log strategy composition
                    self.logger.log_strategy_composition("ml_composer", strategy)
                    
                    # Store in Redis
                    self.redis_client.set(f"strategy_engine:ml_strategy:{symbol}", str(strategy), ex=604800)
                    
                    # Update stats
                    self.stats["strategies_composed"] += 1
                    if pred > 0.8:
                        self.stats["high_confidence_strategies"] += 1

            summary = {
                "type": "ml_composer_summary",
                "strategy_count": len(strategies),
                "timestamp": int(time.time()),
                "description": f"Composed {len(strategies)} ML-based strategies"
            }
            self.logger.log_strategy_composition("ml_composer_summary", summary)
            await self.notify_core(summary)
            return strategies
        except Exception as e:
            self.logger.log_error(f"Error composing ML strategies: {e}")
            self.stats["errors"] += 1
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

    def get_composer_stats(self) -> Dict[str, Any]:
        """Get ML composer statistics."""
        return {
            **self.stats,
            "uptime": time.time() - self.stats["start_time"]
        }

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of composed strategies."""
        try:
            self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}", "info")
            self.redis_client.publish("strategy_engine_output", str(issue))
        except Exception as e:
            self.logger.log_error(f"Error notifying core: {e}")
            self.stats["errors"] += 1