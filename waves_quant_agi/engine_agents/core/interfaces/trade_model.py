from typing import Dict, Any, Optional
from dataclasses import dataclass
from ..logs.core_agent_logger import CoreAgentLogger

@dataclass
class TradeCommand:
    signal_id: str
    strategy: str
    params: Dict[str, Any]
    metadata: Dict[str, Any]

    def __post_init__(self):
        self.logger = CoreAgentLogger("trade_model")
        self.logger.log_action("create_trade_command", {"signal_id": self.signal_id, "strategy": self.strategy})

    def to_dict(self) -> Dict[str, Any]:
        """Convert TradeCommand to dictionary."""
        return {
            "signal_id": self.signal_id,
            "strategy": self.strategy,
            "params": self.params,
            "metadata": self.metadata
        }

    def validate(self) -> bool:
        """Validate TradeCommand fields."""
        required = {"signal_id": str, "strategy": str, "params": dict, "metadata": dict}
        try:
            for field, expected_type in required.items():
                if not isinstance(getattr(self, field), expected_type):
                    self.logger.log_action("validate_trade_command", {"result": "failed", "reason": f"Invalid {field}"})
                    return False
            return True
        except Exception as e:
            self.logger.log_action("validate_trade_command", {"result": "failed", "reason": str(e)})
            return False