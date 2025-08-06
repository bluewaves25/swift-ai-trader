from typing import Dict, Any, List
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class TrueProfitReporter:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.report_interval = config.get("report_interval", 604800)  # Weekly in seconds

    async def generate_profit_report(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate true profitability report after fees and slippage."""
        try:
            total_gross_pnl = sum(float(trade.get("gross_pnl", 0.0)) for trade in trades)
            total_net_pnl = sum(float(trade.get("net_pnl", trade.get("gross_pnl", 0.0))) for trade in trades)
            total_fees = sum(float(trade.get("total_fees", 0.0)) for trade in trades)
            total_slippage = sum(float(trade.get("slippage_cost", 0.0)) for trade in trades)

            report = {
                "type": "profit_report",
                "total_trades": len(trades),
                "gross_pnl": total_gross_pnl,
                "net_pnl": total_net_pnl,
                "total_fees": total_fees,
                "total_slippage": total_slippage,
                "timestamp": int(time.time()),
                "description": f"Profit report: {len(trades)} trades, gross {total_gross_pnl:.2f}, net {total_net_pnl:.2f}, fees {total_fees:.2f}"
            }
            self.logger.log_issue(report)
            self.cache.store_incident(report)
            await self.notify_core(report)
            return report
        except Exception as e:
            self.logger.log(f"Error generating profit report: {e}")
            self.cache.store_incident({
                "type": "profit_report_error",
                "timestamp": int(time.time()),
                "description": f"Error generating profit report: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of profit reports."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent