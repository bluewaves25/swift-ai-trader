# failure_prevention/circuit_breakers/strategy_breaker.py
"""
Strategy Circuit Breaker - Prevents infinite loops and strategy failures
"""

import asyncio
import time
from typing import Dict, Any, Set, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from ..logs.failure_agent_logger import FailureLogger
from .. import FailureType, AlertLevel

class StrategyBreaker:
    """Circuit breaker for trading strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = FailureLogger("StrategyBreaker")
        
        # Strategy monitoring
        self.strategy_calls: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.strategy_errors: Dict[str, int] = defaultdict(int)
        self.blocked_strategies: Set[str] = set()
        self.strategy_timeouts: Dict[str, datetime] = {}
        
        # Thresholds
        self.loop_detection_threshold = config.get('loop_threshold', 10)  # calls per second
        self.error_threshold = config.get('error_threshold', 5)
        self.timeout_minutes = config.get('timeout_minutes', 15)
        
    async def activate(self, strategy_id: str, reason: str = "Strategy circuit breaker activated"):
        """Activate circuit breaker for a strategy"""
        self.logger.warning(f"Blocking strategy {strategy_id}: {reason}")
        
        self.blocked_strategies.add(strategy_id)
        self.strategy_timeouts[strategy_id] = datetime.now() + timedelta(minutes=self.timeout_minutes)
        
        # Schedule automatic unblock
        asyncio.create_task(self._schedule_unblock(strategy_id))
    
    async def _schedule_unblock(self, strategy_id: str):
        """Schedule automatic unblocking of strategy"""
        timeout = self.strategy_timeouts.get(strategy_id)
        if timeout:
            sleep_seconds = (timeout - datetime.now()).total_seconds()
            if sleep_seconds > 0:
                await asyncio.sleep(sleep_seconds)
                await self.unblock_strategy(strategy_id)
    
    async def unblock_strategy(self, strategy_id: str):
        """Manually unblock a strategy"""
        if strategy_id in self.blocked_strategies:
            self.blocked_strategies.remove(strategy_id)
            self.strategy_timeouts.pop(strategy_id, None)
            self.strategy_errors[strategy_id] = 0
            self.logger.info(f"Unblocked strategy {strategy_id}")
    
    def can_execute(self, strategy_id: str) -> bool:
        """Check if strategy can execute"""
        if strategy_id in self.blocked_strategies:
            # Check if timeout has passed
            timeout = self.strategy_timeouts.get(strategy_id)
            if timeout and datetime.now() > timeout:
                asyncio.create_task(self.unblock_strategy(strategy_id))
                return True
            return False
        return True
    
    async def record_strategy_call(self, strategy_id: str, execution_time: float):
        """Record a strategy execution"""
        current_time = time.time()
        self.strategy_calls[strategy_id].append(current_time)
        
        # Check for potential infinite loops
        await self._check_for_loops(strategy_id)
    
    async def record_strategy_error(self, strategy_id: str, error: str):
        """Record a strategy error"""
        self.strategy_errors[strategy_id] += 1
        
        if self.strategy_errors[strategy_id] >= self.error_threshold:
            await self.activate(strategy_id, f"Too many errors: {self.strategy_errors[strategy_id]}")
    
    async def _check_for_loops(self, strategy_id: str):
        """Check for potential infinite loops"""
        calls = self.strategy_calls[strategy_id]
        if len(calls) < self.loop_detection_threshold:
            return
        
        # Check calls in the last second
        current_time = time.time()
        recent_calls = [call for call in calls if current_time - call <= 1.0]
        
        if len(recent_calls) >= self.loop_detection_threshold:
            await self.activate(strategy_id, f"Potential infinite loop detected: {len(recent_calls)} calls/second")
    
    def get_strategy_status(self, strategy_id: str) -> Dict[str, Any]:
        """Get status of a specific strategy"""
        calls = list(self.strategy_calls[strategy_id])
        recent_calls = [call for call in calls if time.time() - call <= 60]  # Last minute
        
        return {
            'strategy_id': strategy_id,
            'is_blocked': strategy_id in self.blocked_strategies,
            'error_count': self.strategy_errors[strategy_id],
            'total_calls': len(calls),
            'recent_calls': len(recent_calls),
            'calls_per_minute': len(recent_calls),
            'timeout_until': self.strategy_timeouts.get(strategy_id),
            'can_execute': self.can_execute(strategy_id)
        }