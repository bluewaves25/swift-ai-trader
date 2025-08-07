from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class EdgeCaseCollector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.rarity_threshold = config.get("rarity_threshold", 0.01)  # 1% rarity

    async def collect_edge_cases(self, validation_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Collect rare validation misses."""
        try:
            edge_cases = []
            for _, row in validation_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                status = row.get("status", "unknown")
                rarity_score = float(row.get("rarity_score", 0.0))

                if rarity_score <= self.rarity_threshold and status == "reject":
                    edge_case = {
                        "type": "edge_case",
                        "symbol": symbol,
                        "rarity_score": rarity_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Edge case detected for {symbol}: Rarity {rarity_score:.4f}"
                    }
                    edge_cases.append(edge_case)
                    self.redis_client.lpush(f"validation:edge_case:{symbol}", json.dumps(edge_case), ex=604800)
                    await self.notify_retraining(edge_case)

            summary = {
                "type": "edge_case_summary",
                "edge_case_count": len(edge_cases),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Collected {len(edge_cases)} edge cases"
            }
            self.redis_client.set("validation:edge_case_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return edge_cases
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "edge_case_collector_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error collecting edge cases: {str(e)}"
            }))
            return []

    async def notify_retraining(self, edge_case: Dict[str, Any]):
        """Notify retraining loop of edge cases."""
        self.redis_client.publish("retraining_loop", json.dumps(edge_case))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of edge case results."""
        self.redis_client.publish("validation_output", json.dumps(issue))