from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class MomentumRider:
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
        self.momentum_threshold = config.get("momentum_threshold", 0.03)  # 3% momentum strength
        self.rsi_threshold = config.get("rsi_threshold", 70)  # RSI overbought/oversold

    async def detect_momentum(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect sustained momentum with RSI and volume filters."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                momentum = float(row.get("momentum", 0.0))
                rsi = float(row.get("rsi", 50.0))
                volume = float(row.get("volume", 0.0))
                prev_volume = float(row.get("prev_volume", 0.0))

                if momentum > self.momentum_threshold and rsi < self.rsi_threshold and volume > prev_volume:
                    signal = "buy"
                    description = f"Bullish momentum for {symbol}: Momentum {momentum:.4f}, RSI {rsi:.2f}"
                elif momentum < -self.momentum_threshold and rsi > (100 - self.rsi_threshold) and volume > prev_volume:
                    signal = "sell"
                    description = f"Bearish momentum for {symbol}: Momentum {momentum:.4f}, RSI {rsi:.2f}"
                else:
                    continue

                opportunity = {
                    "type": "momentum_rider",
                    "symbol": symbol,
                    "signal": signal,
                    "momentum": momentum,
                    "rsi": rsi,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                self.logger.log_issue(opportunity)
                self.cache.store_incident(opportunity)
                self.redis_client.set(f"strategy_engine:momentum_rider:{symbol}", str(opportunity), ex=3600)
                await self.notify_execution(opportunity)

            summary = {
                "type": "momentum_rider_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} momentum signals"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting momentum: {e}")
            self.cache.store_incident({
                "type": "momentum_rider_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting momentum: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of momentum signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of momentum results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))