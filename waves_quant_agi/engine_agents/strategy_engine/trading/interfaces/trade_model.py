from typing import Dict, Any, Optional
from dataclasses import dataclass
from ...logs.strategy_engine_logger import StrategyEngineLogger
import time

@dataclass
class TradeCommand:
    """Trade command model - consolidated from Core Agent."""
    
    command_id: str
    symbol: str
    action: str  # "buy", "sell", "close"
    amount: float
    price: float
    signal_id: str
    strategy_id: str
    timestamp: float
    risk_score: float = 0.5
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        self.logger = StrategyEngineLogger("trade_model")
        self.logger.log_action("create_trade_command", {
            "command_id": self.command_id, 
            "symbol": self.symbol, 
            "action": self.action
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert TradeCommand to dictionary."""
        return {
            "command_id": self.command_id,
            "symbol": self.symbol,
            "action": self.action,
            "amount": self.amount,
            "price": self.price,
            "signal_id": self.signal_id,
            "strategy_id": self.strategy_id,
            "timestamp": self.timestamp,
            "risk_score": self.risk_score,
            "metadata": self.metadata
        }

    def validate(self) -> bool:
        """Validate TradeCommand fields."""
        required = {
            "command_id": str, 
            "symbol": str, 
            "action": str, 
            "amount": (int, float), 
            "price": (int, float),
            "signal_id": str,
            "strategy_id": str,
            "timestamp": (int, float)
        }
        
        try:
            for field, expected_type in required.items():
                value = getattr(self, field)
                if not isinstance(value, expected_type):
                    self.logger.log_action("validate_trade_command", {
                        "result": "failed", 
                        "reason": f"Invalid {field} type: {type(value)}"
                    })
                    return False
            
            # Validate action values
            if self.action not in ["buy", "sell", "close"]:
                self.logger.log_action("validate_trade_command", {
                    "result": "failed", 
                    "reason": f"Invalid action: {self.action}"
                })
                return False
            
            # Validate numeric values
            if self.amount <= 0:
                self.logger.log_action("validate_trade_command", {
                    "result": "failed", 
                    "reason": "Amount must be positive"
                })
                return False
            
            if self.price <= 0:
                self.logger.log_action("validate_trade_command", {
                    "result": "failed", 
                    "reason": "Price must be positive"
                })
                return False
            
            # Validate risk score
            if not 0.0 <= self.risk_score <= 1.0:
                self.logger.log_action("validate_trade_command", {
                    "result": "failed", 
                    "reason": f"Risk score must be between 0 and 1: {self.risk_score}"
                })
                return False
            
            self.logger.log_action("validate_trade_command", {"result": "passed"})
            return True
            
        except Exception as e:
            self.logger.log_action("validate_trade_command", {
                "result": "failed", 
                "reason": str(e)
            })
            return False

    def get_exposure(self) -> float:
        """Calculate total exposure for this trade command."""
        return self.amount * self.price

    def get_risk_adjusted_amount(self) -> float:
        """Get risk-adjusted position amount."""
        # Reduce position size based on risk score
        risk_multiplier = 1.0 - self.risk_score
        return self.amount * risk_multiplier

    def is_high_risk(self) -> bool:
        """Check if this is a high-risk trade command."""
        return self.risk_score > 0.7

    def is_low_risk(self) -> bool:
        """Check if this is a low-risk trade command."""
        return self.risk_score < 0.3

    def get_execution_priority(self) -> int:
        """Get execution priority based on risk and timing."""
        # Higher priority for lower risk and more recent commands
        risk_factor = 1.0 - self.risk_score
        time_factor = min(1.0, (time.time() - self.timestamp) / 3600)  # 1 hour max
        priority = (risk_factor * 0.7) + (time_factor * 0.3)
        return int(priority * 100)  # Scale to 0-100

    def add_metadata(self, key: str, value: Any):
        """Add metadata to the trade command."""
        self.metadata[key] = value
        self.logger.log_action("add_metadata", {"key": key, "value": value})

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)

    def update_price(self, new_price: float):
        """Update the price of the trade command."""
        old_price = self.price
        self.price = new_price
        self.logger.log_action("update_price", {
            "old_price": old_price, 
            "new_price": new_price
        })

    def update_amount(self, new_amount: float):
        """Update the amount of the trade command."""
        old_amount = self.amount
        self.amount = new_amount
        self.logger.log_action("update_amount", {
            "old_amount": old_amount, 
            "new_amount": new_amount
        })

    def clone(self) -> 'TradeCommand':
        """Create a clone of this trade command."""
        return TradeCommand(
            command_id=f"{self.command_id}_clone_{int(time.time())}",
            symbol=self.symbol,
            action=self.action,
            amount=self.amount,
            price=self.price,
            signal_id=self.signal_id,
            strategy_id=self.strategy_id,
            timestamp=time.time(),
            risk_score=self.risk_score,
            metadata=self.metadata.copy()
        )

    def __str__(self) -> str:
        """String representation of TradeCommand."""
        return f"TradeCommand({self.command_id}: {self.action} {self.amount} {self.symbol} @ {self.price})"

    def __repr__(self) -> str:
        """Detailed representation of TradeCommand."""
        return f"TradeCommand(command_id='{self.command_id}', symbol='{self.symbol}', action='{self.action}', amount={self.amount}, price={self.price}, signal_id='{self.signal_id}', strategy_id='{self.strategy_id}', timestamp={self.timestamp}, risk_score={self.risk_score}, metadata={self.metadata})"
