from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class SystemConfidence:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.confidence_threshold = config.get("confidence_threshold", 0.8)  # 80% confidence

    async def evaluate_confidence(self, execution_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate public confidence in unchecked execution."""
        try:
            confidences = []
            for _, row in execution_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                confidence_score = float(row.get("confidence_score", 0.0))

                if confidence_score < self.confidence_threshold:
                    confidence = {
                        "type": "confidence_alert",
                        "symbol": symbol,
                        "confidence_score": confidence_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Low confidence in execution for {symbol}: Score {confidence_score:.2f}"
                    }
                    confidences.append(confidence)
                    self.redis_client.set(f"validation:confidence:{symbol}", json.dumps(confidence), ex=604800)
                    await self.notify_core(confidence)

            summary = {
                "type": "confidence_summary",
                "confidence_count": len(confidences),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Evaluated {len(confidences)} confidence alerts"
            }
            self.redis_client.set("validation:confidence_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return confidences
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "system_confidence_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error evaluating confidence: {str(e)}"
            }))
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of confidence evaluation results."""
        self.redis_client.publish("validation_output", json.dumps(issue))