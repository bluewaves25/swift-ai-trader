from typing import Dict, Any, List
import pandas as pd
import time

class CapitalAllocator:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
                self.max_allocation = config.get("max_allocation", 0.2)  # Max 20% per strategy
        self.total_capital = config.get("total_capital", 1000000.0)  # Default $1M

    async def allocate_capital(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """Dynamically allocate capital based on market conditions."""
        try:
            allocations = {}
            for _, row in market_data.iterrows():
                strategy_id = row.get("strategy_id", "unknown")
                symbol = row.get("symbol", "BTC/USD")
                sharpe_ratio = float(row.get("sharpe_ratio", 0.0))

                # Allocate based on Sharpe ratio (placeholder)
                allocation_ratio = min(self.max_allocation, sharpe_ratio / self.config.get("sharpe_threshold", 2.0))
                allocated_capital = self.total_capital * allocation_ratio

                allocations[strategy_id] = {
                    "symbol": symbol,
                    "allocated_capital": allocated_capital,
                    "sharpe_ratio": sharpe_ratio
                }
                redis_client = await self.connection_manager.get_redis_client()
                        if redis_client:
                            redis_client.set(f"risk_management:allocation:{strategy_id}", str(allocations[strategy_id]), ex=3600)

            summary = {
                "type": "capital_allocation_summary",
                "allocated_strategies": len(allocations),
                "timestamp": int(time.time()),
                "description": f"Allocated capital to {len(allocations)} strategies"
            }
            self.logger.log_risk_assessment("capital_allocation_summary", summary)
            await self.notify_core(summary)
            return {
                "allocations": allocations,
                "available_capital": self.total_capital - sum(a["allocated_capital"] for a in allocations.values())
            }
        except Exception as e:
            print(f"Error in {os.path.basename(file_path)}: {e}")
            return {"allocations": {}, "available_capital": self.total_capital}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of allocation results."""
        }")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))