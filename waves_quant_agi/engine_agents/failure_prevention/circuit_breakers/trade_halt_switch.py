# failure_prevention/circuit_breakers/trade_halt_switch.py
"""
Trade Halt Switch - Emergency stop mechanism for all trading
"""

import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from ..logs.failure_agent_logger import FailureAgentLogger

class TradeHaltSwitch:
    """Emergency halt mechanism for trading operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = FailureAgentLogger("TradeHaltSwitch")
        
        self.is_halted = False
        self.halt_reason = None
        self.halt_timestamp = None
        self.emergency_callbacks: list = []
        
    def register_emergency_callback(self, callback: Callable):
        """Register callback to be called during emergency halt"""
        self.emergency_callbacks.append(callback)
    
    async def emergency_stop(self, reason: str = "Emergency halt activated"):
        """Immediately halt all trading operations"""
        self.logger.critical(f"EMERGENCY HALT: {reason}")
        
        self.is_halted = True
        self.halt_reason = reason
        self.halt_timestamp = datetime.now()
        
        # Execute all emergency callbacks
        for callback in self.emergency_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(reason)
                else:
                    callback(reason)
            except Exception as e:
                self.logger.error(f"Error executing emergency callback: {e}")
    
    async def resume_trading(self, authorization_code: str = None):
        """Resume trading operations (requires authorization)"""
        # In production, this would require proper authorization
        if authorization_code != self.config.get('resume_code', 'RESUME_TRADING_AUTH'):
            self.logger.warning("Unauthorized attempt to resume trading")
            return False
        
        self.logger.info("Resuming trading operations")
        self.is_halted = False
        self.halt_reason = None
        self.halt_timestamp = None
        return True
    
    def is_trading_halted(self) -> bool:
        """Check if trading is currently halted"""
        return self.is_halted
    
    def get_halt_status(self) -> Dict[str, Any]:
        """Get current halt status"""
        return {
            'is_halted': self.is_halted,
            'halt_reason': self.halt_reason,
            'halt_timestamp': self.halt_timestamp,
            'duration_seconds': (datetime.now() - self.halt_timestamp).total_seconds() if self.halt_timestamp else None
        }
