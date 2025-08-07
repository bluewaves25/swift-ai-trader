from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class OrchestrationTrainer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.training_threshold = config.get("training_threshold", 0.85)  # 85% accuracy

    async def train_orchestration(self, strategy_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Train orchestration logic for execution strategies."""
        try:
            trained_strategies = []
            for _, row in strategy_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                strategy_type = row.get("strategy_type", "default")
                accuracy = float(row.get("accuracy", 0.0))

                if accuracy >= self.training_threshold:
                    strategy = {
                        "type": "orchestration_training",
                        "symbol": symbol,
                        "strategy_type": strategy_type,
                        "accuracy": accuracy,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Trained orchestration for {symbol} ({strategy_type}): Accuracy {accuracy:.2%}"
                    }
                    trained_strategies.append(strategy)
                    self.redis_client.set(f"execution:orchestration:{symbol}:{strategy_type}", json.dumps(strategy), ex=604800)
                    await self.notify_execution(strategy)

            summary = {
                "type": "orchestration_summary",
                "strategy_count": len(trained_strategies),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Trained {len(trained_strategies)} orchestration strategies"
            }
            self.redis_client.set("execution:orchestration_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return trained_strategies
        except Exception as e:
            self.redis_client.lpush("execution:errors", json.dumps({
                "type": "orchestration_trainer_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error training orchestration: {str(e)}"
            }))
            return []

    async def notify_execution(self, strategy: Dict[str, Any]):
        """Notify Execution Logic of trained strategies."""
        self.redis_client.publish("execution_logic", json.dumps(strategy))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of training results."""
        self.redis_client.publish("execution_output", json.dumps(issue))