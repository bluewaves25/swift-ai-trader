from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from ..broker_fee_models.model_loader import ModelLoader

class FeeStrategyMap:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, model_loader: ModelLoader):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.model_loader = model_loader
        self.strategy_mappings = config.get("strategy_mappings", {
            "scalping": {"max_commission": 0.001, "max_spread": 0.0002},
            "swing": {"max_commission": 0.002, "max_spread": 0.0005}
        })

    async def map_strategy_to_broker(self, strategy: str, trade: Dict[str, Any]) -> str:
        """Map trading strategy to optimal broker based on fee constraints."""
        try:
            constraints = self.strategy_mappings.get(strategy, {})
            if not constraints:
                self.logger.log(f"No constraints for strategy {strategy}")
                return trade.get("broker", "unknown")

            best_broker = None
            min_cost = float("inf")
            for broker in self.model_loader.fee_models:
                fee_model = self.model_loader.get_fee_model(broker)
                commission = float(fee_model.get("fees", {}).get("commission", 0.0))
                spread = float(fee_model.get("fees", {}).get("spread", 0.0))
                
                if (commission <= constraints.get("max_commission", float("inf")) and
                    spread <= constraints.get("max_spread", float("inf"))):
                    cost = commission + spread
                    if cost < min_cost:
                        min_cost = cost
                        best_broker = broker

            if not best_broker:
                self.logger.log(f"No suitable broker for strategy {strategy}")
                return trade.get("broker", "unknown")

            issue = {
                "type": "strategy_broker_mapping",
                "strategy": strategy,
                "broker": best_broker,
                "symbol": trade.get("symbol", "unknown"),
                "timestamp": int(time.time()),
                "description": f"Mapped {strategy} to broker {best_broker} for {trade.get('symbol')}"
            }
            self.logger.log_issue(issue)
            self.cache.store_incident(issue)
            await self.notify_core(issue)
            return best_broker
        except Exception as e:
            self.logger.log(f"Error mapping strategy {strategy}: {e}")
            self.cache.store_incident({
                "type": "strategy_mapping_error",
                "timestamp": int(time.time()),
                "description": f"Error mapping strategy {strategy}: {str(e)}"
            })
            return trade.get("broker", "unknown")

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of strategy-broker mappings."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent