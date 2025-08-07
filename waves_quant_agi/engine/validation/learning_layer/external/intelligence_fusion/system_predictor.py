from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio
from sklearn.linear_model import LogisticRegression

class SystemPredictor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.prediction_threshold = config.get("prediction_threshold", 0.8)  # 80% confidence

    async def predict_failures(self, validation_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Predict potential validation failure points."""
        try:
            predictions = []
            features = validation_data[["size", "leverage", "slippage_bps", "timestamp"]].fillna(0)
            labels = validation_data["status"].apply(lambda x: 1 if x == "reject" else 0)
            model = LogisticRegression(random_state=42)
            model.fit(features, labels)
            probs = model.predict_proba(features)[:, 1]

            for idx, (row, prob) in enumerate(zip(validation_data.itertuples(), probs)):
                symbol = row.symbol
                if prob >= self.prediction_threshold:
                    prediction = {
                        "type": "failure_prediction",
                        "symbol": symbol,
                        "probability": prob,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Predicted validation failure for {symbol}: Probability {prob:.2f}"
                    }
                    predictions.append(prediction)
                    self.redis_client.set(f"validation:prediction:{symbol}:{idx}", json.dumps(prediction), ex=604800)
                    await self.notify_core(prediction)

            summary = {
                "type": "prediction_summary",
                "prediction_count": len(predictions),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Generated {len(predictions)} failure predictions"
            }
            self.redis_client.set("validation:prediction_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return predictions
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "system_predictor_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error predicting failures: {str(e)}"
            }))
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of prediction results."""
        self.redis_client.publish("validation_output", json.dumps(issue))