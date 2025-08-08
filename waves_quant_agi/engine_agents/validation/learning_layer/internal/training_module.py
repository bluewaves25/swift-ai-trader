from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio
from sklearn.ensemble import IsolationForest

class TrainingModule:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.accuracy_threshold = config.get("accuracy_threshold", 0.85)  # 85% accuracy

    async def train_model(self, failure_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Train models to detect subtle validation issues."""
        try:
            features = failure_data[["size", "leverage", "slippage_bps", "timestamp"]].fillna(0)
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(features)
            predictions = model.predict(features)
            accuracy = sum(predictions == 1) / len(predictions) if len(predictions) > 0 else 0.0

            if accuracy < self.accuracy_threshold:
                report = {
                    "type": "training_report",
                    "accuracy": accuracy,
                    "timestamp": int(pd.Timestamp.now().timestamp()),
                    "description": f"Model trained with accuracy {accuracy:.2%}, below threshold {self.accuracy_threshold:.2%}"
                }
                self.redis_client.lpush("validation:training_reports", json.dumps(report), ex=604800)
                return [report]

            model_data = {
                "type": "model_update",
                "model_type": "isolation_forest",
                "accuracy": accuracy,
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Trained validation model with accuracy {accuracy:.2%}"
            }
            self.redis_client.set("validation:model:latest", json.dumps(model_data), ex=604800)
            await self.notify_core(model_data)
            return [model_data]
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "training_module_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error training model: {str(e)}"
            }))
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of training results."""
        self.redis_client.publish("validation_output", json.dumps(issue))