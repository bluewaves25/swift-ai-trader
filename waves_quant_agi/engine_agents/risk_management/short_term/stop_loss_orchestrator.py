from typing import Dict, Any, List
import time
import pandas as pd

class StopLossOrchestrator:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
                self.static_stop_threshold = config.get("static_stop_threshold", 0.02)  # 2% static stop
        self.dynamic_stop_factor = config.get("dynamic_stop_factor", 1.5)  # Volatility multiplier
        self.volatility_window = config.get("volatility_window", 60)  # 60 seconds

    async def apply_stop_loss(self, position_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Apply multi-layered stop-loss logic: static, dynamic, volatility-aware."""
        try:
            stop_decisions = []
            for _, row in position_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                position_value = float(row.get("position_value", 0.0))
                entry_price = float(row.get("entry_price", 0.0))
                current_price = float(row.get("current_price", 0.0))
                volatility = float(row.get("volatility", 0.0))

                # Static stop-loss
                price_change = (current_price - entry_price) / entry_price
                static_stop_triggered = abs(price_change) > self.static_stop_threshold

                # Dynamic volatility-aware stop-loss
                dynamic_stop = self.dynamic_stop_factor * volatility
                dynamic_stop_triggered = abs(price_change) > dynamic_stop

                if static_stop_triggered or dynamic_stop_triggered:
                    decision = {
                        "type": "stop_loss",
                        "symbol": symbol,
                        "price_change": price_change,
                        "volatility": volatility,
                        "timestamp": int(time.time()),
                        "description": f"Stop-loss triggered for {symbol}: Price change {price_change:.2%}, Volatility {volatility:.2f}"
                    }
                    stop_decisions.append(decision)
                    
                    redis_client = await self.connection_manager.get_redis_client()
                        if redis_client:
                            redis_client.set(f"risk_management:stop_loss:{symbol}", str(decision), ex=3600)
                    await self.notify_execution(decision)

            summary = {
                "type": "stop_loss_summary",
                "stop_count": len(stop_decisions),
                "timestamp": int(time.time()),
                "description": f"Applied {len(stop_decisions)} stop-loss decisions"
            }
            
            await self.notify_core(summary)
            return stop_decisions
        except Exception as e:
            print(f"Error in {os.path.basename(file_path)}: {e}")
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of stop-loss triggers."""
        }")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of stop-loss results."""
        }")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))