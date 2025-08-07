from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class AuditMemory:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.accuracy_threshold = config.get("accuracy_threshold", 0.9)  # 90% accuracy

    async def store_validation(self, validation_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Store validation scores, accuracy, and patterns."""
        try:
            audits = []
            for _, row in validation_data.iterrows():
                status = row.get("status", "unknown")
                symbol = row.get("symbol", "unknown")
                reason = row.get("reason", "unknown")
                timestamp = int(row.get("timestamp", pd.Timestamp.now().timestamp()))

                audit = {
                    "type": "validation_audit",
                    "status": status,
                    "symbol": symbol,
                    "reason": reason,
                    "timestamp": timestamp,
                    "description": f"Validation audit for {symbol}: {status} - {reason}"
                }
                audits.append(audit)
                self.redis_client.lpush(f"validation:audit:{symbol}", json.dumps(audit), ex=604800)

            valid_count = len(validation_data[validation_data["status"] == "valid"])
            accuracy = valid_count / len(validation_data) if len(validation_data) > 0 else 0.0
            summary = {
                "type": "audit_summary",
                "audit_count": len(audits),
                "accuracy": accuracy,
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Stored {len(audits)} validation audits, accuracy {accuracy:.2%}"
            }
            self.redis_client.set("validation:audit_summary", json.dumps(summary), ex=604800)
            if accuracy < self.accuracy_threshold:
                await self.notify_retraining(summary)
            await self.notify_core(summary)
            return audits
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "audit_memory_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error storing validation audits: {str(e)}"
            }))
            return []

    async def notify_retraining(self, summary: Dict[str, Any]):
        """Notify retraining loop of low accuracy."""
        self.redis_client.publish("retraining_loop", json.dumps(summary))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of audit results."""
        self.redis_client.publish("validation_output", json.dumps(issue))