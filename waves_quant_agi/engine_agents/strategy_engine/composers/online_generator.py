from typing import Dict, Any, List
import time
import redis
from ..logs.strategy_engine_logger import StrategyEngineLogger

class OnlineGenerator:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.strategy_threshold = config.get("strategy_threshold", 0.7)

    async def generate_strategy(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate adaptive strategies based on real-time market conditions."""
        try:
            strategies = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                condition_score = float(data.get("condition_score", 0.0))

                if condition_score > self.strategy_threshold:
                    strategy_type = self._determine_strategy_type(data)
                    strategy = {
                        "type": "online_strategy",
                        "symbol": symbol,
                        "strategy_type": strategy_type,
                        "condition_score": condition_score,
                        "timestamp": int(time.time()),
                        "description": f"Online strategy for {symbol}: type {strategy_type}, score {condition_score:.2f}"
                    }
                    strategies.append(strategy)
                    self.logger.log_strategy_deployment("online_strategy", strategy)
                    self.redis_client.set(f"strategy_engine:online_strategy:{symbol}", str(strategy), ex=604800)

            summary = {
                "type": "online_generator_summary",
                "strategy_count": len(strategies),
                "timestamp": int(time.time()),
                "description": f"Generated {len(strategies)} online strategies"
            }
            self.logger.log_strategy_deployment("online_generator_summary", summary)
            await self.notify_core(summary)
            return strategies
        except Exception as e:
            self.logger.log_error(f"Error generating online strategies: {e}")
            return []

    def _determine_strategy_type(self, data: Dict[str, Any]) -> str:
        """Determine strategy type based on market conditions."""
        if data.get("volatility", 0.0) < 0.3: return "market_making"
        if data.get("trend_strength", 0.0) > 0.8: return "trend_following"
        if data.get("news_impact", 0.0) > 0.7: return "news_driven"
        return "statistical_arbitrage"

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of generated strategies."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))