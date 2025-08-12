from typing import Dict, Any, List
import time
import pandas as pd

class LatencyOptimizer:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
        self.latency_threshold = config.get("latency_threshold", 10.0)  # 10ms max latency
        self.exchange_priority = config.get("exchange_priority", ["binance", "kraken"])  # Preferred exchanges

    async def optimize_execution(self, trade_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Minimize execution delays in HFT by selecting optimal exchange."""
        try:
            optimizations = []
            for _, row in trade_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                latency = float(row.get("exchange_latency", 0.0))
                current_exchange = row.get("exchange", "binance")

                optimal_exchange = current_exchange
                if latency > self.latency_threshold:
                    for exchange in self.exchange_priority:
                        if exchange != current_exchange:
                            # Placeholder: Check latency for alternative exchange
                            redis_client = await self.connection_manager.get_redis_client()
                            if redis_client:
                                new_latency = float(redis_client.get(f"exchange:{exchange}:latency") or latency)
                            else:
                                new_latency = latency
                            if new_latency < self.latency_threshold:
                                optimal_exchange = exchange
                                break

                    if optimal_exchange != current_exchange:
                        optimization = {
                            "type": "latency_optimization",
                            "symbol": symbol,
                            "original_exchange": current_exchange,
                            "optimal_exchange": optimal_exchange,
                            "latency": latency,
                            "timestamp": int(time.time()),
                            "description": f"Switched {symbol} to {optimal_exchange} due to latency {latency:.2f}ms"
                        }
                        optimizations.append(optimization)
                        # Store optimization in Redis using connection manager
                        redis_client = await self.connection_manager.get_redis_client()
                        if redis_client:
                            redis_client.set(f"risk_management:latency:{symbol}", str(optimization), ex=3600)
                            await self.notify_execution(optimization)

            summary = {
                "type": "latency_optimization_summary",
                "optimization_count": len(optimizations),
                "timestamp": int(time.time()),
                "description": f"Optimized latency for {len(optimizations)} trades"
            }
            await self.notify_core(summary)
            return optimizations
        except Exception as e:
            print(f"Error in latency optimizer: {e}")
            return []

    async def notify_execution(self, optimization: Dict[str, Any]):
        """Notify Executions Agent of latency optimizations."""
        print(f"Notifying Executions Agent: {optimization.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("execution_agent", str(optimization))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of latency optimization results."""
        print(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))