from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class ResearchEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.error_threshold = config.get("error_threshold", 0.1)  # 10% error rate

    async def analyze_failures(self, validation_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze past validation failures to improve rules."""
        try:
            failure_reports = []
            for _, row in validation_data.iterrows():
                symbol = row.get("symbol", "unknown")
                reason = row.get("reason", "unknown")
                status = row.get("status", "reject")
                timestamp = int(row.get("timestamp", pd.Timestamp.now().timestamp()))

                if status == "reject":
                    report = {
                        "type": "validation_failure",
                        "symbol": symbol,
                        "reason": reason,
                        "timestamp": timestamp,
                        "description": f"Validation failure for {symbol}: {reason}"
                    }
                    failure_reports.append(report)
                    self.redis_client.lpush(f"validation:failures:{symbol}", json.dumps(report), ex=604800)

            error_rate = len(failure_reports) / len(validation_data) if len(validation_data) > 0 else 0.0
            summary = {
                "type": "failure_summary",
                "failure_count": len(failure_reports),
                "error_rate": error_rate,
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Analyzed {len(failure_reports)} validation failures, error rate {error_rate:.2%}"
            }
            self.redis_client.set("validation:failure_summary", json.dumps(summary), ex=604800)
            if error_rate > self.error_threshold:
                await self.notify_retraining(summary)
            await self.notify_core(summary)
            return failure_reports
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "research_engine_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error analyzing failures: {str(e)}"
            }))
            return []

    async def notify_retraining(self, summary: Dict[str, Any]):
        """Notify retraining loop of high error rate."""
        self.redis_client.publish("retraining_loop", json.dumps(summary))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of analysis results."""
        self.redis_client.publish("validation_output", json.dumps(issue))