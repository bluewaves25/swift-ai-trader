from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class GlobalLiquiditySignal:
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
        self.liquidity_threshold = config.get("liquidity_threshold", 0.7)  # Liquidity impact score

    async def detect_liquidity_signal(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect trading signals based on global liquidity conditions."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "USD/JPY")
                liquidity_score = float(row.get("liquidity_score", 0.0))

                if liquidity_score > self.liquidity_threshold:
                    signal = "buy"
                    description = f"Bullish liquidity signal for {symbol}: Score {liquidity_score:.2f}"
                elif liquidity_score < -self.liquidity_threshold:
                    signal = "sell"
                    description = f"Bearish liquidity signal for {symbol}: Score {liquidity_score:.2f}"
                else:
                    continue

                opportunity = {
                    "type": "global_liquidity_signal",
                    "symbol": symbol,
                    "signal": signal,
                    "liquidity_score": liquidity_score,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                self.logger.log_issue(opportunity)
                self.cache.store_incident(opportunity)
                self.redis_client.set(f"strategy_engine:liquidity_signal:{symbol}", str(opportunity), ex=3600)
                await self.notify_execution(opportunity)

            summary = {
                "type": "liquidity_signal_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} liquidity signals"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting liquidity signal: {e}")
            self.cache.store_incident({
                "type": "liquidity_signal_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting liquidity signal: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of liquidity signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of liquidity signal results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))