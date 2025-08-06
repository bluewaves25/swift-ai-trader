from typing import Dict, Any, List
import redis
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class TriangularArbitrage:
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
        self.spread_threshold = config.get("spread_threshold", 0.005)  # 0.5% minimum spread

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect triangular arbitrage opportunities across three currency pairs."""
        try:
            opportunities = []
            for data in market_data:
                pair1 = data.get("pair1", "EUR/USD")
                pair2 = data.get("pair2", "USD/JPY")
                pair3 = data.get("pair3", "EUR/JPY")
                price1 = float(data.get("price1", 1.0))
                price2 = float(data.get("price2", 1.0))
                price3 = float(data.get("price3", 1.0))

                # Calculate triangular arbitrage profit
                implied_rate = price1 * price2
                spread = (implied_rate / price3 - 1) if price3 != 0 else 0.0

                if abs(spread) > self.spread_threshold:
                    opportunity = {
                        "type": "triangular_arbitrage",
                        "pairs": [pair1, pair2, pair3],
                        "spread": spread,
                        "timestamp": int(time.time()),
                        "description": f"Triangular arbitrage opportunity: {pair1}, {pair2}, {pair3}, Spread {spread:.4f}"
                    }
                    opportunities.append(opportunity)
                    self.logger.log_issue(opportunity)
                    self.cache.store_incident(opportunity)
                    self.redis_client.set(f"strategy_engine:triangular_arbitrage:{pair1}", str(opportunity), ex=3600)  # 1-hour expiration
                    await self.notify_execution(opportunity)

            summary = {
                "type": "triangular_arbitrage_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} triangular arbitrage opportunities"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting triangular arbitrage: {e}")
            self.cache.store_incident({
                "type": "triangular_arbitrage_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting triangular arbitrage: {str(e)}"
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