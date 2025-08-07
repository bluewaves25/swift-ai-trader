from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class OrchestrationCases:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.orchestration_threshold = config.get("orchestration_threshold", 0.75)  # 75% confidence

    async def coordinate_execution_strategies(self, insight_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Coordinate execution strategies based on external insights."""
        try:
            strategies = []
            for _, row in insight_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                insight_score = float(row.get("insight_score", 0.0))
                strategy_type = row.get("strategy_type", "default")

                if insight_score >= self.orchestration_threshold:
                    strategy = {
                        "type": "execution_strategy",
                        "symbol": symbol,
                        "strategy_type": strategy_type,
                        "insight_score": insight_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Coordinated {strategy_type} strategy for {symbol}: Score {insight_score:.2f}"
                    }
                    strategies.append(strategy)
                    self.redis_client.set(f"execution:strategy:{symbol}:{strategy_type}", json.dumps(strategy), ex=604800)
                    await self.notify_execution(strategy)

            summary = {
                "type": "strategy_coordination_summary",
                "strategy_count": len(strategies),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Coordinated {len(strategies)} execution strategies"
            }
            self.redis_client.set("execution:strategy_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return strategies
        except Exception as e:
            self.redis_client.lpush("execution:errors", json.dumps({
                "type": "orchestration_cases_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error coordinating strategies: {str(e)}"
            }))
            return []

    async def notify_execution(self, strategy: Dict[str, Any]):
        """Notify Execution Logic of coordinated strategies."""
        self.redis_client.publish("execution_logic", json.dumps(strategy))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of coordination results."""
        self.redis_client.publish("execution_output", json.dumps(issue))