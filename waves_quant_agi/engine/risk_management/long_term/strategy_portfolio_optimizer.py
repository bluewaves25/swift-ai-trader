from typing import Dict, Any, List
import redis
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from ..market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ..market_conditions.memory.incident_cache import IncidentCache

class StrategyPortfolioOptimizer:
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
        self.model = RandomForestRegressor(n_estimators=config.get("n_estimators", 100))
        self.sharpe_threshold = config.get("sharpe_threshold", 2.0)

    async def optimize_portfolio(self, strategy_data: pd.DataFrame) -> Dict[str, Any]:
        """Balance alpha across strategies for optimal risk-reward."""
        try:
            features = strategy_data[["sharpe_ratio", "volatility", "win_rate"]].fillna(0).values
            targets = strategy_data["returns"].fillna(0).values
            self.model.fit(features, targets)

            allocations = {}
            for _, row in strategy_data.iterrows():
                strategy_id = row.get("strategy_id", "unknown")
                symbol = row.get("symbol", "BTC/USD")
                sharpe_ratio = float(row.get("sharpe_ratio", 0.0))

                predicted_return = float(self.model.predict([[sharpe_ratio, row.get("volatility", 0.0), row.get("win_rate", 0.0)]])[0])
                allocation_weight = min(0.3, predicted_return / self.sharpe_threshold)  # Max 30% per strategy

                allocations[strategy_id] = {
                    "symbol": symbol,
                    "allocation_weight": allocation_weight,
                    "predicted_return": predicted_return,
                    "timestamp": int(time.time())
                }
                self.redis_client.set(f"risk_management:portfolio:{strategy_id}", str(allocations[strategy_id]), ex=3600)

            summary = {
                "type": "portfolio_optimization_summary",
                "allocated_strategies": len(allocations),
                "timestamp": int(time.time()),
                "description": f"Optimized portfolio for {len(allocations)} strategies"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return allocations
        except Exception as e:
            self.logger.log(f"Error optimizing portfolio: {e}")
            self.cache.store_incident({
                "type": "strategy_portfolio_optimizer_error",
                "timestamp": int(time.time()),
                "description": f"Error optimizing portfolio: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of portfolio optimization results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))