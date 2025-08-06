# failure_prevention/circuit_breakers/broker_breaker.py
"""
Broker Circuit Breaker - Manages broker connection failures and fallbacks
"""

import asyncio
import time
from typing import Dict, Any, Set, Optional
from datetime import datetime, timedelta
from enum import Enum
from ..logs.failure_agent_logger import FailureLogger
from .. import FailureType, AlertLevel

class BreakerState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit broken, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered

class BrokerBreaker:
    """Circuit breaker for broker connections"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = FailureLogger("BrokerBreaker")
        
        # Circuit breaker settings
        self.failure_threshold = config.get('failure_threshold', 5)
        self.recovery_timeout = config.get('recovery_timeout', 60)  # seconds
        self.half_open_max_calls = config.get('half_open_max_calls', 3)
        
        # Broker states
        self.broker_states: Dict[str, BreakerState] = {}
        self.broker_failures: Dict[str, int] = {}
        self.broker_last_failure: Dict[str, datetime] = {}
        self.blocked_brokers: Set[str] = set()
        self.half_open_calls: Dict[str, int] = {}
        
    async def activate(self, broker_id: str, reason: str = "Circuit breaker activated"):
        """Activate circuit breaker for a broker"""
        self.logger.warning(f"Activating circuit breaker for broker {broker_id}: {reason}")
        
        self.broker_states[broker_id] = BreakerState.OPEN
        self.blocked_brokers.add(broker_id)
        self.broker_last_failure[broker_id] = datetime.now()
        
        # Schedule recovery attempt
        asyncio.create_task(self._schedule_recovery_attempt(broker_id))
    
    async def _schedule_recovery_attempt(self, broker_id: str):
        """Schedule recovery attempt after timeout"""
        await asyncio.sleep(self.recovery_timeout)
        
        if broker_id in self.broker_states and self.broker_states[broker_id] == BreakerState.OPEN:
            self.logger.info(f"Attempting recovery for broker {broker_id}")
            self.broker_states[broker_id] = BreakerState.HALF_OPEN
            self.half_open_calls[broker_id] = 0
    
    def can_execute(self, broker_id: str) -> bool:
        """Check if calls to broker are allowed"""
        state = self.broker_states.get(broker_id, BreakerState.CLOSED)
        
        if state == BreakerState.CLOSED:
            return True
        elif state == BreakerState.OPEN:
            return False
        elif state == BreakerState.HALF_OPEN:
            return self.half_open_calls.get(broker_id, 0) < self.half_open_max_calls
        
        return False
    
    async def record_success(self, broker_id: str):
        """Record successful broker call"""
        state = self.broker_states.get(broker_id, BreakerState.CLOSED)
        
        if state == BreakerState.HALF_OPEN:
            # Success in half-open state - close the circuit
            self.logger.info(f"Broker {broker_id} recovered, closing circuit")
            self.broker_states[broker_id] = BreakerState.CLOSED
            self.broker_failures[broker_id] = 0
            self.blocked_brokers.discard(broker_id)
            self.half_open_calls.pop(broker_id, None)
        elif state == BreakerState.CLOSED:
            # Reset failure count on successful calls
            self.broker_failures[broker_id] = max(0, self.broker_failures.get(broker_id, 0) - 1)
    
    async def record_failure(self, broker_id: str, error: str):
        """Record broker failure"""
        self.broker_failures[broker_id] = self.broker_failures.get(broker_id, 0) + 1
        failure_count = self.broker_failures[broker_id]
        
        state = self.broker_states.get(broker_id, BreakerState.CLOSED)
        
        if state == BreakerState.HALF_OPEN:
            # Failure in half-open state - reopen circuit
            await self.activate(broker_id, f"Failed during recovery: {error}")
        elif state == BreakerState.CLOSED and failure_count >= self.failure_threshold:
            # Too many failures - open circuit
            await self.activate(broker_id, f"Failure threshold reached: {failure_count}")
        
        if state == BreakerState.HALF_OPEN:
            self.half_open_calls[broker_id] = self.half_open_calls.get(broker_id, 0) + 1
    
    def get_broker_status(self, broker_id: str) -> Dict[str, Any]:
        """Get status of a specific broker"""
        return {
            'broker_id': broker_id,
            'state': self.broker_states.get(broker_id, BreakerState.CLOSED).value,
            'failure_count': self.broker_failures.get(broker_id, 0),
            'is_blocked': broker_id in self.blocked_brokers,
            'last_failure': self.broker_last_failure.get(broker_id),
            'can_execute': self.can_execute(broker_id)
        }