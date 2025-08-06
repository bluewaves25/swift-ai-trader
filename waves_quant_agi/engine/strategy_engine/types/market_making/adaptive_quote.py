from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class AdaptiveQuote:
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
        self.quote_adjustment_factor = config.get("quote_adjustment_factor", 0.01)  # 1% adjustment

    async def generate_quote(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate adaptive bid-ask quotes based on market conditions."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "ETH/USD")
                mid_price = float(row.get("mid_price", 0.0))
                liquidity = float(row.get("liquidity", 1.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                bid_adjustment = self.quote_adjustment_factor * (1 / liquidity)
                ask_adjustment = self.quote_adjustment_factor * (1 / liquidity)
                bid_price = mid_price * (1 - bid_adjustment)
                ask_price = mid_price * (1 + ask_adjustment)

                if bid_price > 0 and ask_price > bid_price + fee_score:
                    opportunity = {
                        "type": "adaptive_quote",
                        "symbol": symbol,
                        "bid_price": bid_price,
                        "ask_price": ask_price,
                        "timestamp": int(time.time()),
                        "description": f"Adaptive quote for {symbol}: Bid {bid_price:.2f}, Ask {ask_price:.2f}"
                    }
                    opportunities.append(opportunity)
                    self.logger.log_issue(opportunity)
                    self.cache.store_incident(opportunity)
                    self.redis_client.set(f"strategy_engine:adaptive_quote:{symbol}", str(opportunity), ex=3600)
                    await self.notify_execution(opportunity)

            summary = {
                "type": "adaptive_quote_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Generated {len(opportunities)} adaptive quotes"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error generating adaptive quote: {e}")
            self.cache.store_incident({
                "type": "adaptive_quote_error",
                "timestamp": int(time.time()),
                "description": f"Error generating adaptive quote: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of adaptive quote."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of adaptive quote results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))