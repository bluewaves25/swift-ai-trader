from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class BreakoutStrategy:
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
        self.breakout_threshold = config.get("breakout_threshold", 0.02)  # 2% breakout level

    async def detect_breakout(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect breakout opportunities after volatility contraction."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                high = float(row.get("high", 0.0))
                low = float(row.get("low", 0.0))
                prev_high = float(row.get("prev_high", 0.0))
                prev_low = float(row.get("prev_low", 0.0))

                range_ratio = (high - low) / prev_high if prev_high != 0 else 0.0
                if range_ratio > self.breakout_threshold and high > prev_high:
                    opportunity = {
                        "type": "breakout_strategy",
                        "symbol": symbol,
                        "breakout_level": high,
                        "timestamp": int(time.time()),
                        "description": f"Breakout detected for {symbol}: Level {high:.2f}, Ratio {range_ratio:.4f}"
                    }
                    opportunities.append(opportunity)
                    self.logger.log_issue(opportunity)
                    self.cache.store_incident(opportunity)
                    self.redis_client.set(f"strategy_engine:breakout:{symbol}", str(opportunity), ex=3600)
                    await self.notify_execution(opportunity)

            summary = {
                "type": "breakout_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} breakout opportunities"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting breakout: {e}")
            self.cache.store_incident({
                "type": "breakout_strategy_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting breakout: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of breakout opportunity."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of breakout results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))