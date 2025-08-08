from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class SlippageDetector:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.slippage_threshold = config.get("slippage_threshold", 0.001)  # 0.1% price deviation

    async def detect_slippage(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Detect slippage by comparing expected and executed prices."""
        try:
            expected_price = float(trade.get("expected_price", 0.0))
            executed_price = float(trade.get("executed_price", 0.0))
            if expected_price <= 0 or executed_price <= 0:
                self.logger.log(f"Invalid trade prices: {trade}")
                return {}

            slippage = abs(executed_price - expected_price) / expected_price
            if slippage > self.slippage_threshold:
                issue = {
                    "type": "slippage_detected",
                    "broker": trade.get("broker", "unknown"),
                    "symbol": trade.get("symbol", "unknown"),
                    "slippage": slippage,
                    "threshold": self.slippage_threshold,
                    "timestamp": int(time.time()),
                    "description": f"Slippage {slippage:.4f} exceeds threshold {self.slippage_threshold} for {trade.get('symbol')}"
                }
                self.logger.log_issue(issue)
                self.cache.store_incident(issue)
                await self.notify_core(issue)
                return issue
            return {}
        except Exception as e:
            self.logger.log(f"Error detecting slippage: {e}")
            self.cache.store_incident({
                "type": "slippage_detector_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting slippage: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of slippage issues."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent