from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from ..broker_fee_models.model_loader import ModelLoader

class ExecutionRecommender:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, model_loader: ModelLoader):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.model_loader = model_loader
        self.spread_threshold = config.get("spread_threshold", 0.0005)  # 0.05%

    async def recommend_execution(self, trade: Dict[str, Any]) -> str:
        """Recommend execution method (limit/market) based on fees and spread."""
        try:
            broker = trade.get("broker", "unknown")
            fee_model = self.model_loader.get_fee_model(broker)
            if not fee_model:
                self.logger.log(f"No fee model for {broker}")
                return "market"

            spread = float(fee_model.get("fees", {}).get("spread", 0.0))
            commission = float(fee_model.get("fees", {}).get("commission", 0.0))
            market_depth = float(trade.get("market_depth", 0.0))

            recommendation = "limit" if spread > self.spread_threshold and market_depth > 0 else "market"
            issue = {
                "type": "execution_recommendation",
                "broker": broker,
                "symbol": trade.get("symbol", "unknown"),
                "recommendation": recommendation,
                "spread": spread,
                "timestamp": int(time.time()),
                "description": f"Recommended {recommendation} execution for {broker}/{trade.get('symbol')} (spread: {spread})"
            }
            self.logger.log_issue(issue)
            self.cache.store_incident(issue)
            await self.notify_core(issue)
            return recommendation
        except Exception as e:
            self.logger.log(f"Error recommending execution: {e}")
            self.cache.store_incident({
                "type": "execution_recommender_error",
                "timestamp": int(time.time()),
                "description": f"Error recommending execution: {str(e)}"
            })
            return "market"

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of execution recommendations."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent