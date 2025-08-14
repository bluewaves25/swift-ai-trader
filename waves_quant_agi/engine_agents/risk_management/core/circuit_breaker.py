#!/usr/bin/env python3
"""
Circuit Breaker - Automatic error recovery and graceful degradation
Implements circuit breaker pattern to prevent cascading failures
Provides automatic fallback and recovery mechanisms
"""

import time
import asyncio
from typing import Dict, Any, Callable, Optional, Union
from enum import Enum

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Circuit is open, calls fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service is recovered

class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception,
                 name: str = "default"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name
        
        # Circuit state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        
        # Statistics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.circuit_opens = 0
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        self.total_calls += 1
        
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                self.failed_calls += 1
                raise Exception(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset failure count
            self._on_success()
            return result
            
        except self.expected_exception as e:
            # Expected failure - increment failure count
            self._on_failure()
            raise e
        except Exception as e:
            # Unexpected failure - also increment failure count
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        return time.time() - self.last_failure_time > self.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        self.successful_calls += 1
        
        if self.state == CircuitState.HALF_OPEN:
            # Service recovered, close circuit
            self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.failed_calls += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            # Open circuit
            self.state = CircuitState.OPEN
            self.circuit_opens += 1
    
    def force_open(self):
        """Manually open the circuit."""
        self.state = CircuitState.OPEN
        self.circuit_opens += 1
    
    def force_close(self):
        """Manually close the circuit."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
    
    def force_half_open(self):
        """Manually set circuit to half-open state."""
        self.state = CircuitState.HALF_OPEN
    
    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self.state
    
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED
    
    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)."""
        return self.state == CircuitState.OPEN
    
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self.state == CircuitState.HALF_OPEN
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout,
            'last_failure_time': self.last_failure_time,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'circuit_opens': self.circuit_opens,
            'success_rate': self.successful_calls / max(self.total_calls, 1),
            'failure_rate': self.failed_calls / max(self.total_calls, 1)
        }
    
    def reset_stats(self):
        """Reset all statistics."""
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.circuit_opens = 0

class CircuitBreakerManager:
    """Manager for multiple circuit breakers."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def create_circuit_breaker(self, 
                              name: str,
                              failure_threshold: int = 5,
                              recovery_timeout: int = 60,
                              expected_exception: type = Exception) -> CircuitBreaker:
        """Create a new circuit breaker."""
        if name in self.circuit_breakers:
            raise ValueError(f"Circuit breaker '{name}' already exists")
        
        circuit_breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            name=name
        )
        
        self.circuit_breakers[name] = circuit_breaker
        return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get an existing circuit breaker."""
        return self.circuit_breakers.get(name)
    
    def remove_circuit_breaker(self, name: str) -> bool:
        """Remove a circuit breaker."""
        if name in self.circuit_breakers:
            del self.circuit_breakers[name]
            return True
        return False
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        return {name: cb.get_stats() for name, cb in self.circuit_breakers.items()}
    
    def force_open_all(self):
        """Force all circuit breakers to open state."""
        for cb in self.circuit_breakers.values():
            cb.force_open()
    
    def force_close_all(self):
        """Force all circuit breakers to close state."""
        for cb in self.circuit_breakers.values():
            cb.force_close()
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all circuit breakers."""
        total_circuits = len(self.circuit_breakers)
        open_circuits = sum(1 for cb in self.circuit_breakers.values() if cb.is_open())
        half_open_circuits = sum(1 for cb in self.circuit_breakers.values() if cb.is_half_open())
        closed_circuits = sum(1 for cb in self.circuit_breakers.values() if cb.is_closed())
        
        return {
            'total_circuits': total_circuits,
            'open_circuits': open_circuits,
            'half_open_circuits': half_open_circuits,
            'closed_circuits': closed_circuits,
            'health_score': closed_circuits / max(total_circuits, 1),
            'timestamp': time.time()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers."""
        return {
            name: {
                'state': cb.state.value,
                'failure_count': cb.failure_count,
                'is_open': cb.is_open(),
                'is_closed': cb.is_closed(),
                'is_half_open': cb.is_half_open()
            }
            for name, cb in self.circuit_breakers.items()
        }
