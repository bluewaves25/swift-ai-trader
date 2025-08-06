from typing import Dict, Any, List
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from ..broker_fee_models.model_loader import ModelLoader

class HiddenFeeDetector:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, model_loader: ModelLoader):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.model_loader = model_loader
        self.discrepancy_threshold = config.get("discrepancy_threshold", 0.005)  # 0.5% of trade value

    async def detect_hidden_fees(self, trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect hidden fees by comparing expected vs. actual costs."""
        try:
            hidden_fees = []
            for trade in trades:
                broker = trade.get("broker", "unknown")
                fee_model = self.model_loader.get_fee_model(broker)
                if not fee_model:
                    continue

                trade_value = float(trade.get("price", 0.0)) * float(trade.get("size", 1.0))
                expected_fees = float(fee_model.get("fees", {}).get("commission", 0.0)) * trade_value
                expected_fees += float(fee_model.get("fees", {}).get("swap", 0.0)) * trade_value
                actual_fees = float(trade.get("actual_fees", 0.0))

                discrepancy = abs(actual_fees - expected_fees) / trade_value if trade_value > 0 else 0
                if discrepancy > self.discrepancy_threshold:
                    issue = {
                        "type": "hidden_fee_detected",
                        "broker": broker,
                        "symbol": trade.get("symbol", "unknown"),
                        "discrepancy": discrepancy,
                        "expected_fees": expected_fees,
                        "actual_fees": actual_fees,
                        "timestamp": int(time.time()),
                        "description": f"Hidden fee detected for {broker}/{trade.get('symbol')}: discrepancy {discrepancy:.4f}"
                    }
                    self.logger.log_issue(issue)
                    self.cache.store_incident(issue)
                    hidden_fees.append(issue)
                    await self.notify_core(issue)
            return hidden_fees
        except Exception as e:
            self.logger.log(f"Error detecting hidden fees: {e}")
            self.cache.store_incident({
                "type": "hidden_fee_detector_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting hidden fees: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of hidden fee detections."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent