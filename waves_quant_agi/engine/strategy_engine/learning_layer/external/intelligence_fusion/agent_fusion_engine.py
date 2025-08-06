from typing import Dict, Any, List
import redis
import pandas as pd
from .....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from .....market_conditions.memory.incident_cache import IncidentCache

class AgentFusionEngine:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.fusion_threshold = config.get("fusion_threshold", 0.8)  # Agent signal agreement

    async def fuse_signals(self, agent_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Fuse signals from multiple agents for unified strategies."""
        try:
            fused_signals = []
            for _, row in agent_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                agent_scores = row.get("agent_scores", [])
                avg_score = float(sum(agent_scores) / len(agent_scores)) if agent_scores else 0.0

                if abs(avg_score) > self.fusion_threshold:
                    signal = "buy" if avg_score > 0 else "sell"
                    description = f"Fused signal for {symbol}: Avg Score {avg_score:.2f}"
                    fused_signal = {
                        "type": "agent_fusion",
                        "symbol": symbol,
                        "signal": signal,
                        "avg_score": avg_score,
                        "timestamp": int(time.time()),
                        "description": description
                    }
                    fused_signals.append(fused_signal)
                    self.logger.log_issue(fused_signal)
                    self.cache.store_incident(fused_signal)
                    self.redis_client.set(f"strategy_engine:fusion:{symbol}", str(fused_signal), ex=3600)
                    await self.notify_execution(fused_signal)

            summary = {
                "type": "agent_fusion_summary",
                "signal_count": len(fused_signals),
                "timestamp": int(time.time()),
                "description": f"Fused {len(fused_signals)} agent signals"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return fused_signals
        except Exception as e:
            self.logger.log(f"Error fusing agent signals: {e}")
            self.cache.store_incident({
                "type": "agent_fusion_error",
                "timestamp": int(time.time()),
                "description": f"Error fusing agent signals: {str(e)}"
            })
            return []

    async def notify_execution(self, signal: Dict[str, Any]):
        """Notify Executions Agent of fused signal."""
        self.logger.log(f"Notifying Executions Agent: {signal.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(signal))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of fusion results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))