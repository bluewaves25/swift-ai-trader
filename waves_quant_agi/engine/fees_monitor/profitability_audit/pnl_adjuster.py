from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from ..broker_fee_models.model_loader import ModelLoader

class PnlAdjuster:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, model_loader: ModelLoader):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.model_loader = model_loader

    async def adjust_pnl(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust trade PnL to account for all fees and slippage."""
        try:
            broker = trade.get("broker", "unknown")
            fee_model = self.model_loader.get_fee_model(broker)
            if not fee_model:
                self.logger.log(f"No fee model for {broker}")
                return trade

            gross_pnl = float(trade.get("gross_pnl", 0.0))
            trade_value = float(trade.get("price", 0.0)) * float(trade.get("size", 1.0))
            commission = float(fee_model.get("fees", {}).get("commission", 0.0)) * trade_value
            swap = float(fee_model.get("fees", {}).get("swap", 0.0)) * trade_value
            slippage = float(trade.get("slippage", 0.0)) * trade_value

            total_fees = commission + swap
            net_pnl = gross_pnl - total_fees - slippage

            adjusted = {
                "type": "pnl_adjusted",
                "broker": broker,
                "symbol": trade.get("symbol", "unknown"),
                "gross_pnl": gross_pnl,
                "net_pnl": net_pnl,
                "total_fees": total_fees,
                "slippage_cost": slippage,
                "timestamp": int(time.time()),
                "description": f"Adjusted PnL for {broker}/{trade.get('symbol')}: gross {gross_pnl:.2f} to net {net_pnl:.2f}"
            }
            self.logger.log_issue(adjusted)
            self.cache.store_incident(adjusted)
            await self.notify_core(adjusted)
            return adjusted
        except Exception as e:
            self.logger.log(f"Error adjusting PnL: {e}")
            self.cache.store_incident({
                "type": "pnl_adjuster_error",
                "timestamp": int(time.time()),
                "description": f"Error adjusting PnL: {str(e)}"
            })
            return trade

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of PnL adjustments."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent