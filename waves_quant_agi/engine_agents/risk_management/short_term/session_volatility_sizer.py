from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ..logs.risk_management_logger import RiskManagementLogger

class SessionVolatilitySizer:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.volatility_scaling_factor = config.get("volatility_scaling_factor", 0.5)  # Reduce size with volatility
        self.max_position_size = config.get("max_position_size", 0.05)  # 5% of capital

    async def adjust_trade_size(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Adjust trade sizes based on session volatility."""
        try:
            adjustments = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                volatility = float(row.get("volatility", 0.0))
                base_position_size = float(row.get("base_position_size", self.max_position_size))

                # Scale position size inversely with volatility
                adjusted_size = min(self.max_position_size, base_position_size * (1.0 / (1.0 + self.volatility_scaling_factor * volatility)))

                adjustment = {
                    "type": "trade_size_adjustment",
                    "symbol": symbol,
                    "adjusted_size": adjusted_size,
                    "volatility": volatility,
                    "timestamp": int(time.time()),
                    "description": f"Adjusted trade size for {symbol}: {adjusted_size:.4f} (Volatility {volatility:.2f})"
                }
                adjustments.append(adjustment)
                self.logger.log_risk_assessment("assessment", adjustment)
                self.redis_client.set(f"risk_management:trade_size:{symbol}", str(adjustment), ex=3600)
                await self.notify_execution(adjustment)

            summary = {
                "type": "volatility_sizer_summary",
                "adjustment_count": len(adjustments),
                "timestamp": int(time.time()),
                "description": f"Adjusted trade sizes for {len(adjustments)} positions"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return adjustments
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, adjustment: Dict[str, Any]):
        """Notify Executions Agent of trade size adjustments."""
        self.logger.log(f"Notifying Executions Agent: {adjustment.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(adjustment))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of trade size adjustment results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))