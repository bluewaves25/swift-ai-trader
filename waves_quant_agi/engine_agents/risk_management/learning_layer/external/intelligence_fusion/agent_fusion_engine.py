from typing import Dict, Any, List
import time
import pandas as pd
import numpy as np

class AgentFusionEngine:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
        self.fusion_confidence_threshold = config.get("fusion_confidence_threshold", 0.75)  # 75% confidence

    async def fuse_signals(self, agent_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Fuse risk signals across agents."""
        try:
            fused_signals = []
            for symbol in agent_data["symbol"].unique():
                symbol_data = agent_data[agent_data["symbol"] == symbol]
                signals = symbol_data["signal_score"].values
                fused_score = float(np.mean(signals)) if len(signals) > 0 else 0.0

                if fused_score >= self.fusion_confidence_threshold:
                    signal = {
                        "type": "fused_signal",
                        "symbol": symbol,
                        "fused_score": fused_score,
                        "timestamp": int(time.time()),
                        "description": f"Fused signal approved for {symbol}: Score {fused_score:.2f}"
                    }
                    fused_signals.append(signal)
                    # Store signal in Redis using connection manager
                    redis_client = await self.connection_manager.get_redis_client()
                    if redis_client:
                        redis_client.set(f"risk_management:fused_signal:{symbol}", str(signal), ex=3600)
                        await self.notify_execution(signal)
                else:
                    signal = {
                        "type": "fused_signal",
                        "symbol": symbol,
                        "fused_score": fused_score,
                        "timestamp": int(time.time()),
                        "description": f"Fused signal rejected for {symbol}: Score {fused_score:.2f}"
                    }
                    fused_signals.append(signal)

            summary = {
                "type": "fused_signal_summary",
                "signal_count": len(fused_signals),
                "timestamp": int(time.time()),
                "description": f"Fused {len(fused_signals)} risk signals across agents"
            }
            await self.notify_core(summary)
            return fused_signals
        except Exception as e:
            print(f"Error in agent fusion engine: {e}")
            return []

    async def notify_execution(self, signal: Dict[str, Any]):
        """Notify Executions Agent of approved fused signals."""
        print(f"Notifying Executions Agent: {signal.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("execution_agent", str(signal))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of fused signal results."""
        print(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))