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

    async def fuse_signals(self, signal_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Aggregate multi-model execution signals."""
        try:
            fused_signals = []
            for symbol in signal_data["symbol"].unique():
                symbol_data = signal_data[signal_data["symbol"] == symbol]
                confidence_scores = symbol_data["confidence_score"].values
                fused_score = float(confidence_scores.mean()) if len(confidence_scores) > 0 else 0.0

                if fused_score >= self.fusion_threshold:
                    signal = {
                        "type": "fused_signal",
                        "symbol": symbol,
                        "fused_score": fused_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Fused execution signal for {symbol}: Score {fused_score:.2f}"
                    }
                    fused_signals.append(signal)
                    self.redis_client.set(f"execution:fused_signal:{symbol}", json.dumps(signal), ex=604800)
                    await self.notify_execution(signal)

            summary = {
                "type": "fusion_summary",
                "signal_count": len(fused_signals),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Fused {len(fused_signals)} execution signals"
            }
            self.redis_client.set("execution:fusion_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return fused_signals
        except Exception as e:
            self.redis_client.lpush("execution:errors", json.dumps({
                "type": "agent_fusion_engine_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error fusing signals: {str(e)}"
            }))
            return []

    async def notify_execution(self, signal: Dict[str, Any]):
        """Notify Execution Logic of fused signals."""
        self.redis_client.publish("execution_logic", json.dumps(signal))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of signal fusion results."""
        self.redis_client.publish("execution_output", json.dumps(issue))