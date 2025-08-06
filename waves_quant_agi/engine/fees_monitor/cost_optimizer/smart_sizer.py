from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from ..broker_fee_models.model_loader import ModelLoader

class SmartSizer:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, model_loader: ModelLoader):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.model_loader = model_loader
        self.max_fee_impact = config.get("max_fee_impact", 0.01)  # 1% of trade value

    async def optimize_position_size(self, trade: Dict[str, Any]) -> float:
        """Adjust position size to minimize fee impact."""
        try:
            broker = trade.get("broker", "unknown")
            fee_model = self.model_loader.get_fee_model(broker)
            if not fee_model:
                self.logger.log(f"No fee model for {broker}")
                return trade.get("size", 1.0)

            commission = float(fee_model.get("fees", {}).get("commission", 0.0))
            trade_value = float(trade.get("price", 0.0)) * float(trade.get("size", 1.0))
            if trade_value <= 0:
                self.logger.log(f"Invalid trade value: {trade}")
                return trade.get("size", 1.0)

            fee_impact = (commission * trade_value) / trade_value
            if fee_impact > self.max_fee_impact:
                adjusted_size = trade.get("size", 1.0) * (self.max_fee_impact / fee_impact)
                issue = {
                    "type": "position_size_adjusted",
                    "broker": broker,
                    "symbol": trade.get("symbol", "unknown"),
                    "original_size": trade.get("size", 1.0),
                    "adjusted_size": adjusted_size,
                    "timestamp": int(time.time()),
                    "description": f"Adjusted position size for {broker}/{trade.get('symbol')} from {trade.get('size', 1.0)} to {adjusted_size}"
                }
                self.logger.log_issue(issue)
                self.cache.store_incident(issue)
                await self.notify_core(issue)
                return adjusted_size
            return trade.get("size", 1.0)
        except Exception as e:
            self.logger.log(f"Error optimizing position size: {e}")
            self.cache.store_incident({
                "type": "smart_sizer_error",
                "timestamp": int(time.time()),
                "description": f"Error optimizing position size: {str(e)}"
            })
            return trade.get("size", 1.0)

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of size adjustments."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent