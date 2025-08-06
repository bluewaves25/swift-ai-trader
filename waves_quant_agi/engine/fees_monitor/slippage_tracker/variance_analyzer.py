from typing import Dict, Any, List
import statistics
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class VarianceAnalyzer:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.variance_threshold = config.get("variance_threshold", 0.002)  # 0.2% variance

    async def analyze_slippage_variance(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze variance in slippage across trades for a broker or symbol."""
        try:
            slippages = [float(trade.get("slippage", 0.0)) for trade in trades if trade.get("slippage", 0.0) > 0]
            if not slippages or len(slippages) < 2:
                self.logger.log("Insufficient trade data for variance analysis")
                return {}

            variance = statistics.variance(slippages)
            mean_slippage = statistics.mean(slippages)
            broker = trades[0].get("broker", "unknown")
            symbol = trades[0].get("symbol", "unknown")

            if variance > self.variance_threshold:
                issue = {
                    "type": "high_slippage_variance",
                    "broker": broker,
                    "symbol": symbol,
                    "variance": variance,
                    "mean_slippage": mean_slippage,
                    "threshold": self.variance_threshold,
                    "timestamp": int(time.time()),
                    "description": f"High slippage variance {variance:.4f} for {broker}/{symbol}, mean {mean_slippage:.4f}"
                }
                self.logger.log_issue(issue)
                self.cache.store_incident(issue)
                await self.notify_core(issue)
                return issue
            return {}
        except Exception as e:
            self.logger.log(f"Error analyzing slippage variance: {e}")
            self.cache.store_incident({
                "type": "variance_analysis_error",
                "timestamp": int(time.time()),
                "description": f"Error analyzing slippage variance: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of variance issues."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent