from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class VolatilityResponsiveMM:
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
        self.volatility_threshold = config.get("volatility_threshold", 0.3)  # Volatility trigger

    async def generate_mm_signal(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate market-making signals based on volatility levels."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "EUR/USD")
                volatility = float(row.get("volatility", 0.0))
                mid_price = float(row.get("mid_price", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                spread_factor = 0.002 if volatility < self.volatility_threshold else 0.005
                bid_price = mid_price * (1 - spread_factor)
                ask_price = mid_price * (1 + spread_factor)

                if bid_price > 0 and ask_price > bid_price + fee_score:
                    opportunity = {
                        "type": "volatility_responsive_mm",
                        "symbol": symbol,
                        "bid_price": bid_price,
                        "ask_price": ask_price,
                        "volatility": volatility,
                        "timestamp": int(time.time()),
                        "description": f"Volatility-responsive MM for {symbol}: Bid {bid_price:.2f}, Ask {ask_price:.2f}"
                    }
                    opportunities.append(opportunity)
                    self.logger.log_issue(opportunity)
                    self.cache.store_incident(opportunity)
                    self.redis_client.set(f"strategy_engine:volatility_mm:{symbol}", str(opportunity), ex=3600)
                    await self.notify_execution(opportunity)

            summary = {
                "type": "volatility_mm_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Generated {len(opportunities)} volatility-responsive MM signals"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error generating volatility MM signal: {e}")
            self.cache.store_incident({
                "type": "volatility_mm_error",
                "timestamp": int(time.time()),
                "description": f"Error generating volatility MM signal: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of market-making signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of market-making results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))