from typing import Dict, Any, List
import pandas as pd
import redis
import json
import asyncio

class RetrainingLoop:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.anomaly_threshold = config.get("anomaly_threshold", 0.15)  # 15% anomaly rate
        self.retrain_interval = config.get("retrain_interval", 604800)  # 7 days in seconds

    async def run_retraining_loop(self, execution_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Manage adaptive retraining for execution strategies."""
        try:
            retrain_results = []
            for symbol in execution_data["symbol"].unique():
                symbol_data = execution_data[execution_data["symbol"] == symbol]
                anomaly_rate = symbol_data["error_rate"].mean() if "error_rate" in symbol_data else 0.0

                if anomaly_rate >= self.anomaly_threshold:
                    result = {
                        "type": "retraining_trigger",
                        "symbol": symbol,
                        "anomaly_rate": anomaly_rate,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Triggered retraining for {symbol}: Anomaly rate {anomaly_rate:.2%}"
                    }
                    retrain_results.append(result)
                    self.redis_client.set(f"execution:retraining:{symbol}", json.dumps(result), ex=604800)
                    await self.notify_training(result)

            summary = {
                "type": "retraining_summary",
                "retrain_count": len(retrain_results),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Triggered {len(retrain_results)} retraining processes"
            }
            self.redis_client.set("execution:retraining_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return retrain_results
        except Exception as e:
            self.redis_client.lpush("execution:errors", json.dumps({
                "type": "retraining_loop_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error in retraining loop: {str(e)}"
            }))
            return []

    async def notify_training(self, result: Dict[str, Any]):
        """Notify Training Module of retraining triggers."""
        self.redis_client.publish("training_module", json.dumps(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of retraining results."""
        self.redis_client.publish("execution_output", json.dumps(issue))