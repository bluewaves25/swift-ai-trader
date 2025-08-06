from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class MovingAverageCrossover:
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
        self.ma_short_period = config.get("ma_short_period", 50)
        self.ma_long_period = config.get("ma_long_period", 200)

    async def detect_crossover(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect moving average crossover signals for trend following."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "EUR/USD")
                ma_short = float(row.get("ma_short", 0.0))
                ma_long = float(row.get("ma_long", 0.0))
                prev_ma_short = float(row.get("prev_ma_short", 0.0))
                prev_ma_long = float(row.get("prev_ma_long", 0.0))

                if ma_short > ma_long and prev_ma_short <= prev_ma_long:
                    signal = "buy"
                    description = f"Bullish crossover for {symbol}: MA{self.ma_short_period} crossed above MA{self.ma_long_period}"
                elif ma_short < ma_long and prev_ma_short >= prev_ma_long:
                    signal = "sell"
                    description = f"Bearish crossover for {symbol}: MA{self.ma_short_period} crossed below MA{self.ma_long_period}"
                else:
                    continue

                opportunity = {
                    "type": "ma_crossover",
                    "symbol": symbol,
                    "signal": signal,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                self.logger.log_issue(opportunity)
                self.cache.store_incident(opportunity)
                self.redis_client.set(f"strategy_engine:ma_crossover:{symbol}", str(opportunity), ex=3600)
                await self.notify_execution(opportunity)

            summary = {
                "type": "ma_crossover_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} MA crossover signals"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting MA crossover: {e}")
            self.cache.store_incident({
                "type": "ma_crossover_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting MA crossover: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of crossover signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of crossover results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))