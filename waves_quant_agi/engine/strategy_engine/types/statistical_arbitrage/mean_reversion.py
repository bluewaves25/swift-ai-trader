from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class MeanReversion:
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
        self.bollinger_threshold = config.get("bollinger_threshold", 2.0)  # 2 standard deviations

    async def detect_reversion(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect mean reversion opportunities using Bollinger Bands."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "USD/CHF")
                price = float(row.get("price", 0.0))
                bollinger_upper = float(row.get("bollinger_upper", 0.0))
                bollinger_lower = float(row.get("bollinger_lower", 0.0))

                if price > bollinger_upper:
                    signal = "sell"
                    description = f"Mean reversion sell for {symbol}: Price {price:.4f} above upper Bollinger {bollinger_upper:.4f}"
                elif price < bollinger_lower:
                    signal = "buy"
                    description = f"Mean reversion buy for {symbol}: Price {price:.4f} below lower Bollinger {bollinger_lower:.4f}"
                else:
                    continue

                opportunity = {
                    "type": "mean_reversion",
                    "symbol": symbol,
                    "signal": signal,
                    "price": price,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                self.logger.log_issue(opportunity)
                self.cache.store_incident(opportunity)
                self.redis_client.set(f"strategy_engine:mean_reversion:{symbol}", str(opportunity), ex=3600)
                await self.notify_execution(opportunity)

            summary = {
                "type": "mean_reversion_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} mean reversion opportunities"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting mean reversion: {e}")
            self.cache.store_incident({
                "type": "mean_reversion_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting mean reversion: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of mean reversion signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of mean reversion results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))