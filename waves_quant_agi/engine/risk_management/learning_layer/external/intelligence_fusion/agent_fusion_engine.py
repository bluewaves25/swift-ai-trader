from typing import Dict, Any, List
import redis
import pandas as pd
import numpy as np
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
                    self.logger.log_issue(signal)
                    self.cache.store_incident(signal)
                    self.redis_client.set(f"risk_management:fused_signal:{symbol}", str(signal), ex=3600)
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
                    self.logger.log_issue(signal)
                    self.cache.store_incident(signal)

            summary = {
                "type": "fused_signal_summary",
                "signal_count": len(fused_signals),
                "timestamp": int(time.time()),
                "description": f"Fused {len(fused_signals)} risk signals across agents"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return fused_signals
        except Exception as e:
            self.logger.log(f"Error fusing agent signals: {e}")
            self.cache.store_incident({
                "type": "agent_fusion_engine_error",
                "timestamp": int(time.time()),
                "description": f"Error fusing agent signals: {str(e)}"
            })
            return []

    async def notify_execution(self, signal: Dict[str, Any]):
        """Notify Executions Agent of approved fused signals."""
        self.logger.log(f"Notifying Executions Agent: {signal.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(signal))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of fused signal results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))