from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

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

    async def generate_predictions(self, fused_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate composite execution predictions."""
        try:
            predictions = []
            for _, row in fused_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                fused_score = float(row.get("fused_score", 0.0))
                prediction_type = row.get("prediction_type", "default")

                if fused_score >= self.prediction_threshold:
                    prediction = {
                        "type": "execution_prediction",
                        "symbol": symbol,
                        "prediction_type": prediction_type,
                        "confidence_score": fused_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Execution prediction for {symbol}: {prediction_type} with score {fused_score:.2f}"
                    }
                    predictions.append(prediction)
                    self.redis_client.set(f"execution:prediction:{symbol}:{prediction_type}", json.dumps(prediction), ex=604800)
                    await self.notify_execution(prediction)

            summary = {
                "type": "prediction_summary",
                "prediction_count": len(predictions),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Generated {len(predictions)} execution predictions"
            }
            self.redis_client.set("execution:prediction_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return predictions
        except Exception as e:
            self.redis_client.lpush("execution:errors", json.dumps({
                "type": "system_predictor_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error generating predictions: {str(e)}"
            }))
            return []

    async def notify_execution(self, prediction: Dict[str, Any]):
        """Notify Execution Logic of predictions."""
        self.redis_client.publish("execution_logic", json.dumps(prediction))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of prediction results."""
        self.redis_client.publish("execution_output", json.dumps(issue))