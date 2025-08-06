from typing import Dict, Any, List
import redis
import pandas as pd
from ..market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ..market_conditions.memory.incident_cache import IncidentCache

class CapitalAllocator:
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
                self.redis_client.set(f"risk_management:allocation:{strategy_id}", str(allocations[strategy_id]), ex=3600)

            summary = {
                "type": "capital_allocation_summary",
                "allocated_strategies": len(allocations),
                "timestamp": int(time.time()),
                "description": f"Allocated capital to {len(allocations)} strategies"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return {
                "allocations": allocations,
                "available_capital": self.total_capital - sum(a["allocated_capital"] for a in allocations.values())
            }
        except Exception as e:
            self.logger.log(f"Error allocating capital: {e}")
            self.cache.store_incident({
                "type": "capital_allocator_error",
                "timestamp": int(time.time()),
                "description": f"Error allocating capital: {str(e)}"
            })
            return {"allocations": {}, "available_capital": self.total_capital}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of allocation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))