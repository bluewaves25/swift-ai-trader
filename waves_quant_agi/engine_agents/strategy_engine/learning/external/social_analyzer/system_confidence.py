from typing import Dict, Any, List
import time
import redis
import pandas as pd
from .....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from .....market_conditions.memory.incident_cache import IncidentCache

class SystemConfidence:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
                self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.confidence_threshold = config.get("confidence_threshold", 0.75)  # System confidence score

    async def assess_confidence(self, system_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Assess system-wide confidence for trading signals."""
        try:
            opportunities = []
            for _, row in system_data.iterrows():
                symbol = row.get("symbol", "ETH/USD")
                confidence_score = float(row.get("confidence_score", 0.0))

                if confidence_score > self.confidence_threshold:
                    signal = "buy"
                    description = f"High system confidence for {symbol}: Score {confidence_score:.2f}"
                elif confidence_score < -self.confidence_threshold:
                    signal = "sell"
                    description = f"Low system confidence for {symbol}: Score {confidence_score:.2f}"
                else:
                    continue

                opportunity = {
                    "type": "system_confidence",
                    "symbol": symbol,
                    "signal": signal,
                    "confidence_score": confidence_score,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                self.logger.log_strategy_deployment("deployment", opportunity)
                opportunity)
                self.redis_client.set(f"strategy_engine:confidence:{symbol}", str(opportunity), ex=3600)
                await self.notify_execution(opportunity)

            summary = {
                "type": "system_confidence_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} system confidence signals"
            }
            self.logger.log_strategy_deployment("deployment", summary)
            summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error assessing system confidence: {e}")
            {
                "type": "system_confidence_error",
                "timestamp": int(time.time()),
                "description": f"Error assessing system confidence: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of confidence signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of confidence results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))