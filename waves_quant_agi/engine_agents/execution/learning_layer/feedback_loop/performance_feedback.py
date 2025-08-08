from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class PerformanceFeedback:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.performance_threshold = config.get("performance_threshold", 0.9)  # 90% performance score

    async def evaluate_performance(self, execution_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate execution outcomes and suggest parameter tweaks."""
        try:
            feedback_list = []
            for _, row in execution_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                latency = float(row.get("latency", 0.0))
                slippage_bps = float(row.get("slippage_bps", 0.0))
                performance_score = 1.0 - (latency / 10000 + slippage_bps / 1000)  # Simplified scoring

                if performance_score < self.performance_threshold:
                    feedback = {
                        "type": "performance_feedback",
                        "symbol": symbol,
                        "performance_score": performance_score,
                        "suggested_slippage_bps": slippage_bps * 1.1,  # Increase by 10%
                        "suggested_latency_ms": latency * 0.9,  # Reduce by 10%
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Suboptimal performance for {symbol}: Score {performance_score:.2f}"
                    }
                    feedback_list.append(feedback)
                    self.redis_client.set(f"execution:feedback:{symbol}", json.dumps(feedback), ex=604800)
                    await self.notify_execution(feedback)

            summary = {
                "type": "performance_summary",
                "feedback_count": len(feedback_list),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Generated {len(feedback_list)} performance feedback items"
            }
            self.redis_client.set("execution:performance_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return feedback_list
        except Exception as e:
            self.redis_client.lpush("execution:errors", json.dumps({
                "type": "performance_feedback_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error evaluating performance: {str(e)}"
            }))
            return []

    async def notify_execution(self, feedback: Dict[str, Any]):
        """Notify Execution Logic of performance feedback."""
        self.redis_client.publish("execution_logic", json.dumps(feedback))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of performance feedback results."""
        self.redis_client.publish("execution_output", json.dumps(issue))