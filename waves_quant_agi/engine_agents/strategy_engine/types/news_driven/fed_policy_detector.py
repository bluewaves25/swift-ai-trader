from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class FedPolicyDetector:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
                self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.policy_impact_threshold = config.get("policy_impact_threshold", 0.6)  # Sentiment impact score

    async def detect_policy_signal(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect trading signals based on Fed policy changes."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "USD/JPY")
                policy_impact = float(row.get("policy_impact", 0.0))

                if policy_impact > self.policy_impact_threshold:
                    signal = "buy"
                    description = f"Bullish Fed policy signal for {symbol}: Impact {policy_impact:.2f}"
                elif policy_impact < -self.policy_impact_threshold:
                    signal = "sell"
                    description = f"Bearish Fed policy signal for {symbol}: Impact {policy_impact:.2f}"
                else:
                    continue

                opportunity = {
                    "type": "fed_policy_detector",
                    "symbol": symbol,
                    "signal": signal,
                    "policy_impact": policy_impact,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                self.logger.log_strategy_deployment("deployment", opportunity)
                opportunity)
                self.redis_client.set(f"strategy_engine:fed_policy:{symbol}", str(opportunity), ex=3600)
                await self.notify_execution(opportunity)

            summary = {
                "type": "fed_policy_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} Fed policy signals"
            }
            self.logger.log_strategy_deployment("deployment", summary)
            summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting Fed policy signal: {e}")
            {
                "type": "fed_policy_detector_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting Fed policy signal: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of Fed policy signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of Fed policy results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))