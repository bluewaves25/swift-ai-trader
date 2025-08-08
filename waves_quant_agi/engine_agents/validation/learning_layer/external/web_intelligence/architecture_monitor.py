from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class ArchitectureMonitor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.stability_threshold = config.get("stability_threshold", 0.9)  # 90% stability score

    async def monitor_architecture(self, system_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Track validation logic shifts in other systems."""
        try:
            shifts = []
            for _, row in system_data.iterrows():
                component = row.get("component", "unknown")
                stability_score = float(row.get("stability_score", 0.0))
                symbol = row.get("symbol", "BTC/USD")

                if stability_score < self.stability_threshold:
                    shift = {
                        "type": "architecture_shift",
                        "component": component,
                        "symbol": symbol,
                        "stability_score": stability_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Validation logic shift in {component} for {symbol}: Score {stability_score:.2f}"
                    }
                    shifts.append(shift)
                    self.redis_client.set(f"validation:shift:{component}:{symbol}", json.dumps(shift), ex=604800)
                    await self.notify_core(shift)

            summary = {
                "type": "shift_summary",
                "shift_count": len(shifts),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Detected {len(shifts)} validation logic shifts"
            }
            self.redis_client.set("validation:shift_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return shifts
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "architecture_monitor_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error monitoring architecture: {str(e)}"
            }))
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of architecture monitoring results."""
        self.redis_client.publish("validation_output", json.dumps(issue))