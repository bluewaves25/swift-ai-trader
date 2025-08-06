from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class MacroTrendTracker:
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
        self.trend_strength_threshold = config.get("trend_strength_threshold", 0.8)  # Trend strength score

    async def detect_macro_trend(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect long-term macro trends for high time frame trading."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "NAS100")
                trend_score = float(row.get("trend_score", 0.0))
                macro_signal = row.get("macro_signal", "neutral")

                if trend_score > self.trend_strength_threshold and macro_signal == "bullish":
                    signal = "buy"
                    description = f"Bullish macro trend for {symbol}: Score {trend_score:.2f}"
                elif trend_score > self.trend_strength_threshold and macro_signal == "bearish":
                    signal = "sell"
                    description = f"Bearish macro trend for {symbol}: Score {trend_score:.2f}"
                else:
                    continue

                opportunity = {
                    "type": "macro_trend_tracker",
                    "symbol": symbol,
                    "signal": signal,
                    "trend_score": trend_score,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                self.logger.log_issue(opportunity)
                self.cache.store_incident(opportunity)
                self.redis_client.set(f"strategy_engine:macro_trend:{symbol}", str(opportunity), ex=3600)
                await self.notify_execution(opportunity)

            summary = {
                "type": "macro_trend_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} macro trend signals"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting macro trend: {e}")
            self.cache.store_incident({
                "type": "macro_trend_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting macro trend: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of macro trend signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of macro trend results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))