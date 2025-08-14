from typing import Dict, Any
from ..logs.core_agent_logger import CoreAgentLogger

class SystemSignalFilter:
    """System coordination signal filter - focused ONLY on system coordination."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = CoreAgentLogger("system_signal_filter")
        
        # System coordination signal types only
        self.valid_system_signals = {
            "health_check", "timing_sync", "agent_status", 
            "system_command", "coordination_event"
        }
        
        # Required fields for system signals
        self.required_fields = {
            "signal_id": str, 
            "signal_type": str, 
            "timestamp": float,
            "source_agent": str
        }

    def validate_system_signal(self, signal: Dict[str, Any]) -> bool:
        """Validate system coordination signal format and content."""
        try:
            # Check required fields and types
            for field, expected_type in self.required_fields.items():
                if field not in signal or not isinstance(signal[field], expected_type):
                    self.logger.log_action("validate_system_signal", {
                        "result": "failed", 
                        "reason": f"Invalid {field}"
                    })
                    return False
            
            # Check signal type validity
            if signal["signal_type"] not in self.valid_system_signals:
                self.logger.log_action("validate_system_signal", {
                    "result": "failed", 
                    "reason": f"Invalid system signal type: {signal['signal_type']}"
                })
                return False
            
            self.logger.log_action("validate_system_signal", {"result": "passed"})
            return True
            
        except Exception as e:
            self.logger.log_action("validate_system_signal", {
                "result": "failed", 
                "reason": str(e)
            })
            return False