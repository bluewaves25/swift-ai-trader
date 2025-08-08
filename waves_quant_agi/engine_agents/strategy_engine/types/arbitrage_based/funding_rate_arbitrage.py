from typing import Dict, Any, List
import time
import redis
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class FundingRateArbitrage:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
                self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.funding_threshold = config.get("funding_threshold", 0.01)  # 1% funding rate difference

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect funding rate arbitrage opportunities in crypto perpetuals."""
        try:
            opportunities = []
            for data in market_data:
                symbol = data.get("symbol", "BTC/USD")
                exchange1_rate = float(data.get("funding_rate_exchange1", 0.0))
                exchange2_rate = float(data.get("funding_rate_exchange2", 0.0))

                rate_diff = abs(exchange1_rate - exchange2_rate)
                if rate_diff > self.funding_threshold:
                    opportunity = {
                        "type": "funding_rate_arbitrage",
                        "symbol": symbol,
                        "rate_diff": rate_diff,
                        "exchange1_rate": exchange1_rate,
                        "exchange2_rate": exchange2_rate,
                        "timestamp": int(time.time()),
                        "description": f"Funding rate arbitrage for {symbol}: Diff {rate_diff:.4f}"
                    }
                    opportunities.append(opportunity)
                    self.logger.log_strategy_deployment("deployment", opportunity)
                    opportunity)
                    self.redis_client.set(f"strategy_engine:funding_rate_arbitrage:{symbol}", str(opportunity), ex=3600)
                    await self.notify_execution(opportunity)

            summary = {
                "type": "funding_rate_arbitrage_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} funding rate arbitrage opportunities"
            }
            self.logger.log_strategy_deployment("deployment", summary)
            summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting funding rate arbitrage: {e}")
            {
                "type": "funding_rate_arbitrage_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting funding rate arbitrage: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of arbitrage opportunity."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of arbitrage results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))