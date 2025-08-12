from typing import Dict, Any
from ..logs.core_agent_logger import CoreAgentLogger

class SignalFilter:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = CoreAgentLogger("signal_filter")
        self.required_fields = {"signal_id": str, "strategy": str, "params": dict, "timestamp": float}
        self.valid_strategies = {"momentum", "mean_reversion", "arbitrage"}

    def validate_signal(self, signal: Dict[str, Any]) -> bool:
        """Validate signal format and content."""
        try:
            # Check required fields and types
            for field, expected_type in self.required_fields.items():
                if field not in signal or not isinstance(signal[field], expected_type):
                    self.logger.log_action("validate_signal", {"result": "failed", "reason": f"Invalid {field}"})
                    return False
            
            # Check strategy validity
            if signal["strategy"] not in self.valid_strategies:
                self.logger.log_action("validate_signal", {"result": "failed", "reason": f"Invalid strategy: {signal['strategy']}"})
                return False
            
            # Check params content
            params = signal["params"]
            if not all(key in params for key in ["amount", "base", "quote"]):
                self.logger.log_action("validate_signal", {"result": "failed", "reason": "Missing required params"})
                return False
            
            self.logger.log_action("validate_signal", {"result": "passed"})
            return True
        except Exception as e:
            self.logger.log_action("validate_signal", {"result": "failed", "reason": str(e)})
            return False