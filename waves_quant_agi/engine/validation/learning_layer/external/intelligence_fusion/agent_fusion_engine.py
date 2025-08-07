from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class AgentFusionEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.fusion_threshold = config.get("fusion_threshold", 0.85)  # 85% confidence

    async def fuse_insights(self, insight_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Combine external insights into validator heuristics."""
        try:
            fused_insights = []
            for symbol in insight_data["symbol"].unique():
                symbol_data = insight_data[insight_data["symbol"] == symbol]
                confidence_scores = symbol_data["confidence_score"].values
                fused_score = float(confidence_scores.mean()) if len(confidence_scores) > 0 else 0.0

                if fused_score >= self.fusion_threshold:
                    insight = {
                        "type": "fused_insight",
                        "symbol": symbol,
                        "fused_score": fused_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Fused validation insight for {symbol}: Score {fused_score:.2f}"
                    }
                    fused_insights.append(insight)
                    self.redis_client.set(f"validation:insight:{symbol}", json.dumps(insight), ex=604800)
                    await self.notify_core(insight)

            summary = {
                "type": "insight_summary",
                "insight_count": len(fused_insights),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Fused {len(fused_insights)} validation insights"
            }
            self.redis_client.set("validation:insight_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return fused_insights
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "agent_fusion_engine_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error fusing insights: {str(e)}"
            }))
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of fused insights."""
        self.redis_client.publish("validation_output", json.dumps(issue))