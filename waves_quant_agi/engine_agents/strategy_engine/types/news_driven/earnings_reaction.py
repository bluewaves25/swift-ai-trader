from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class EarningsReaction:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
                self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.earnings_surprise_threshold = config.get("earnings_surprise_threshold", 0.05)  # 5% surprise

    async def detect_earnings_signal(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect trading signals based on earnings surprises."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "TSLA")
                earnings_surprise = float(row.get("earnings_surprise", 0.0))
                price_change = float(row.get("price_change", 0.0))

                if earnings_surprise > self.earnings_surprise_threshold and price_change > 0:
                    signal = "buy"
                    description = f"Bullish earnings reaction for {symbol}: Surprise {earnings_surprise:.2f}"
                elif earnings_surprise < -self.earnings_surprise_threshold and price_change < 0:
                    signal = "sell"
                    description = f"Bearish earnings reaction for {symbol}: Surprise {earnings_surprise:.2f}"
                else:
                    continue

                opportunity = {
                    "type": "earnings_reaction",
                    "symbol": symbol,
                    "signal": signal,
                    "earnings_surprise": earnings_surprise,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                self.logger.log_strategy_deployment("deployment", opportunity)
                opportunity)
                self.redis_client.set(f"strategy_engine:earnings_reaction:{symbol}", str(opportunity), ex=3600)
                await self.notify_execution(opportunity)

            summary = {
                "type": "earnings_reaction_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} earnings reaction opportunities"
            }
            self.logger.log_strategy_deployment("deployment", summary)
            summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting earnings reaction: {e}")
            {
                "type": "earnings_reaction_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting earnings reaction: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of earnings signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of earnings results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))