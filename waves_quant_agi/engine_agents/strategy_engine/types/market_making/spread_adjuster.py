from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class SpreadAdjuster:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
                self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.spread_multiplier = config.get("spread_multiplier", 1.5)  # Spread adjustment factor

    async def adjust_spread(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Adjust bid-ask spreads dynamically for market making."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                base_spread = float(row.get("base_spread", 0.001))
                volatility = float(row.get("volatility", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                adjusted_spread = base_spread * self.spread_multiplier * (1 + volatility)
                if adjusted_spread > fee_score:
                    opportunity = {
                        "type": "spread_adjuster",
                        "symbol": symbol,
                        "adjusted_spread": adjusted_spread,
                        "timestamp": int(time.time()),
                        "description": f"Spread adjustment for {symbol}: Adjusted spread {adjusted_spread:.4f}"
                    }
                    opportunities.append(opportunity)
                    self.logger.log_strategy_deployment("deployment", opportunity)
                    opportunity)
                    self.redis_client.set(f"strategy_engine:spread_adjuster:{symbol}", str(opportunity), ex=3600)
                    await self.notify_execution(opportunity)

            summary = {
                "type": "spread_adjuster_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Adjusted spreads for {len(opportunities)} symbols"
            }
            self.logger.log_strategy_deployment("deployment", summary)
            summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error adjusting spread: {e}")
            {
                "type": "spread_adjuster_error",
                "timestamp": int(time.time()),
                "description": f"Error adjusting spread: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of spread adjustment."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of spread adjustment results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))