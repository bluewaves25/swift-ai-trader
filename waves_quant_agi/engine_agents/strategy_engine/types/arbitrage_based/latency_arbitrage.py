from typing import Dict, Any, List
import time
import redis
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class LatencyArbitrage:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
                self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.price_diff_threshold = config.get("price_diff_threshold", 0.005)  # 0.5% price difference

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect latency arbitrage opportunities across exchanges."""
        try:
            opportunities = []
            for data in market_data:
                symbol = data.get("symbol", "BTC/USD")
                exchange1_price = float(data.get("exchange1_price", 0.0))
                exchange2_price = float(data.get("exchange2_price", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                price_diff = abs(exchange1_price - exchange2_price) / exchange1_price if exchange1_price != 0 else 0.0
                if price_diff > self.price_diff_threshold and price_diff > fee_score:
                    opportunity = {
                        "type": "latency_arbitrage",
                        "symbol": symbol,
                        "price_diff": price_diff,
                        "exchange1_price": exchange1_price,
                        "exchange2_price": exchange2_price,
                        "timestamp": int(time.time()),
                        "description": f"Latency arbitrage for {symbol}: Diff {price_diff:.4f}"
                    }
                    opportunities.append(opportunity)
                    self.logger.log_strategy_deployment("deployment", opportunity)
                    opportunity)
                    self.redis_client.set(f"strategy_engine:latency_arbitrage:{symbol}", str(opportunity), ex=3600)
                    await self.notify_execution(opportunity)

            summary = {
                "type": "latency_arbitrage_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} latency arbitrage opportunities"
            }
            self.logger.log_strategy_deployment("deployment", summary)
            summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting latency arbitrage: {e}")
            {
                "type": "latency_arbitrage_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting latency arbitrage: {str(e)}"
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