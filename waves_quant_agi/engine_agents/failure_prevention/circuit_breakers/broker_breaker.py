# failure_prevention/circuit_breakers/broker_breaker.py
"""
Broker Circuit Breaker - Manages broker connection failures and fallbacks
"""

import asyncio
import time
import redis
from typing import Dict, Any, Set, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from ..logs.failure_agent_logger import FailureAgentLogger
from .. import FailureType, AlertLevel

class BreakerState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit broken, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered

class BrokerBreaker:
    """Circuit breaker for broker connections"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = FailureAgentLogger()
        
        # Redis configuration
        redis_host = self.config.get('redis_host', 'localhost')
        redis_port = self.config.get('redis_port', 6379)
        redis_db = self.config.get('redis_db', 0)
        
        # Initialize Redis
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=redis_db, 
                decode_responses=True
            )
            self.redis_client.ping()  # Test connection
            self.logger.log_info("BrokerBreaker Redis connection established")
        except Exception as e:
            self.logger.log_error("Redis connection failed", str(e), "BrokerBreaker")
            self.redis_client = None
        
        # Circuit breaker settings
        self.failure_threshold = config.get('failure_threshold', 5)
        self.recovery_timeout = config.get('recovery_timeout', 60)  # seconds
        self.half_open_max_calls = config.get('half_open_max_calls', 3)
        self.monitoring_interval = config.get('monitoring_interval', 30)  # seconds
        
        # Broker states
        self.broker_states: Dict[str, BreakerState] = {}
        self.broker_failures: Dict[str, int] = {}
        self.broker_last_failure: Dict[str, datetime] = {}
        self.blocked_brokers: Set[str] = set()
        self.half_open_calls: Dict[str, int] = {}
        self.broker_stats: Dict[str, Dict[str, Any]] = {}
        
    async def start(self):
        """Start the broker breaker monitoring"""
        self.logger.log_info("BrokerBreaker monitoring started", "BrokerBreaker")
        
        # Start monitoring tasks
        tasks = [
            self._monitor_broker_health(),
            self._report_broker_stats()
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.log_error("Error in broker breaker monitoring", str(e), "BrokerBreaker")
    
    async def stop(self):
        """Stop the broker breaker monitoring"""
        self.logger.log_info("BrokerBreaker monitoring stopped", "BrokerBreaker")
    
    async def activate(self, broker_id: str, reason: str = "Circuit breaker activated"):
        """Activate circuit breaker for a broker"""
        try:
            self.logger.log_circuit_breaker(
                breaker_type="broker",
                target=broker_id,
                action="activate",
                state="open",
                reason=reason
            )
            
            self.broker_states[broker_id] = BreakerState.OPEN
            self.blocked_brokers.add(broker_id)
            self.broker_last_failure[broker_id] = datetime.now()
            
            # Update Redis
            if self.redis_client:
                breaker_data = {
                    'broker_id': broker_id,
                    'state': 'open',
                    'reason': reason,
                    'activated_at': str(datetime.now())
                }
                self.redis_client.hset(f"broker_breaker:states", broker_id, str(breaker_data))
                self.redis_client.publish('broker_breaker:activated', str(breaker_data))
            
            # Schedule recovery attempt
            asyncio.create_task(self._schedule_recovery_attempt(broker_id))
            
        except Exception as e:
            self.logger.log_error(f"Failed to activate circuit breaker for {broker_id}", str(e), "BrokerBreaker")
    
    async def _schedule_recovery_attempt(self, broker_id: str):
        """Schedule recovery attempt after timeout"""
        try:
            await asyncio.sleep(self.recovery_timeout)
            
            if broker_id in self.broker_states and self.broker_states[broker_id] == BreakerState.OPEN:
                self.logger.log_circuit_breaker(
                    breaker_type="broker",
                    target=broker_id,
                    action="recovery_attempt",
                    state="half_open",
                    reason="Recovery timeout reached"
                )
                
                self.broker_states[broker_id] = BreakerState.HALF_OPEN
                self.half_open_calls[broker_id] = 0
                
                # Update Redis
                if self.redis_client:
                    recovery_data = {
                        'broker_id': broker_id,
                        'state': 'half_open',
                        'recovery_attempt_at': str(datetime.now())
                    }
                    self.redis_client.hset(f"broker_breaker:states", broker_id, str(recovery_data))
                    self.redis_client.publish('broker_breaker:recovery_attempt', str(recovery_data))
                    
        except Exception as e:
            self.logger.log_error(f"Failed to schedule recovery for {broker_id}", str(e), "BrokerBreaker")
    
    def can_execute(self, broker_id: str) -> bool:
        """Check if calls to broker are allowed"""
        try:
            state = self.broker_states.get(broker_id, BreakerState.CLOSED)
            
            if state == BreakerState.CLOSED:
                return True
            elif state == BreakerState.OPEN:
                return False
            elif state == BreakerState.HALF_OPEN:
                return self.half_open_calls.get(broker_id, 0) < self.half_open_max_calls
            
            return False
            
        except Exception as e:
            self.logger.log_error(f"Failed to check execution for {broker_id}", str(e), "BrokerBreaker")
            return False
    
    async def record_success(self, broker_id: str):
        """Record successful broker call"""
        try:
            state = self.broker_states.get(broker_id, BreakerState.CLOSED)
            
            if state == BreakerState.HALF_OPEN:
                # Success in half-open state - close the circuit
                self.logger.log_circuit_breaker(
                    breaker_type="broker",
                    target=broker_id,
                    action="recovery_success",
                    state="closed",
                    reason="Successful recovery call"
                )
                
                self.broker_states[broker_id] = BreakerState.CLOSED
                self.broker_failures[broker_id] = 0
                self.blocked_brokers.discard(broker_id)
                self.half_open_calls.pop(broker_id, None)
                
                # Update Redis
                if self.redis_client:
                    success_data = {
                        'broker_id': broker_id,
                        'state': 'closed',
                        'recovered_at': str(datetime.now())
                    }
                    self.redis_client.hset(f"broker_breaker:states", broker_id, str(success_data))
                    self.redis_client.publish('broker_breaker:recovered', str(success_data))
                    
            elif state == BreakerState.CLOSED:
                # Reset failure count on successful calls
                self.broker_failures[broker_id] = max(0, self.broker_failures.get(broker_id, 0) - 1)
            
            # Update stats
            self._update_broker_stats(broker_id, success=True)
            
        except Exception as e:
            self.logger.log_error(f"Failed to record success for {broker_id}", str(e), "BrokerBreaker")
    
    async def record_failure(self, broker_id: str, error: str):
        """Record broker failure"""
        try:
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
            
            # Update stats
            self._update_broker_stats(broker_id, success=False, error=error)
            
            self.logger.log_incident(
                incident_type="broker_failure",
                source=broker_id,
                description=f"Broker failure: {error}",
                failure_count=failure_count,
                metadata={'state': state.value, 'error': error}
            )
            
        except Exception as e:
            self.logger.log_error(f"Failed to record failure for {broker_id}", str(e), "BrokerBreaker")
    
    def _update_broker_stats(self, broker_id: str, success: bool, error: str = None):
        """Update broker statistics"""
        try:
            if broker_id not in self.broker_stats:
                self.broker_stats[broker_id] = {
                    'total_calls': 0,
                    'successful_calls': 0,
                    'failed_calls': 0,
                    'last_call': None,
                    'current_state': 'closed'
                }
            
            stats = self.broker_stats[broker_id]
            stats['total_calls'] += 1
            stats['last_call'] = datetime.now()
            stats['current_state'] = self.broker_states.get(broker_id, BreakerState.CLOSED).value
            
            if success:
                stats['successful_calls'] += 1
            else:
                stats['failed_calls'] += 1
            
            # Store in Redis
            if self.redis_client:
                self.redis_client.hset(f"broker_breaker:stats", broker_id, str(stats))
                
        except Exception as e:
            self.logger.log_error(f"Failed to update stats for {broker_id}", str(e), "BrokerBreaker")
    
    async def _monitor_broker_health(self):
        """Monitor broker health continuously"""
        while True:
            try:
                current_time = datetime.now()
                
                # Check for stale circuit breakers
                for broker_id, last_failure in self.broker_last_failure.items():
                    if broker_id in self.broker_states and self.broker_states[broker_id] == BreakerState.OPEN:
                        time_since_failure = (current_time - last_failure).total_seconds()
                        
                        if time_since_failure > self.recovery_timeout * 2:
                            self.logger.log_alert(
                                alert_type="stale_circuit_breaker",
                                severity="medium",
                                source=broker_id,
                                description=f"Circuit breaker stale for {time_since_failure:.1f}s",
                                metadata={'recovery_timeout': self.recovery_timeout}
                            )
                
                # Log metrics
                open_count = len([b for b in self.broker_states.values() if b == BreakerState.OPEN])
                half_open_count = len([b for b in self.broker_states.values() if b == BreakerState.HALF_OPEN])
                closed_count = len([b for b in self.broker_states.values() if b == BreakerState.CLOSED])
                
                self.logger.log_metric(
                    metric_name="broker_circuit_breakers",
                    value=open_count,
                    tags={'state': 'open', 'total': len(self.broker_states)}
                )
                
                self.logger.log_metric(
                    metric_name="broker_circuit_breakers",
                    value=half_open_count,
                    tags={'state': 'half_open', 'total': len(self.broker_states)}
                )
                
                self.logger.log_metric(
                    metric_name="broker_circuit_breakers",
                    value=closed_count,
                    tags={'state': 'closed', 'total': len(self.broker_states)}
                )
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.log_error("Error in broker health monitoring", str(e), "BrokerBreaker")
                await asyncio.sleep(60)  # Retry after 1 minute
    
    async def _report_broker_stats(self):
        """Report broker statistics periodically"""
        while True:
            try:
                for broker_id, stats in self.broker_stats.items():
                    if stats['total_calls'] > 0:
                        success_rate = (stats['successful_calls'] / stats['total_calls']) * 100
                        
                        self.logger.log_metric(
                            metric_name="broker_success_rate",
                            value=success_rate,
                            tags={'broker_id': broker_id}
                        )
                        
                        self.logger.log_metric(
                            metric_name="broker_total_calls",
                            value=stats['total_calls'],
                            tags={'broker_id': broker_id}
                        )
                
                await asyncio.sleep(300)  # Report every 5 minutes
                
            except Exception as e:
                self.logger.log_error("Error in broker stats reporting", str(e), "BrokerBreaker")
                await asyncio.sleep(60)
    
    def get_broker_status(self, broker_id: str) -> Dict[str, Any]:
        """Get status of a specific broker"""
        try:
            state = self.broker_states.get(broker_id, BreakerState.CLOSED)
            stats = self.broker_stats.get(broker_id, {})
            
            return {
                'broker_id': broker_id,
                'state': state.value,
                'failure_count': self.broker_failures.get(broker_id, 0),
                'last_failure': self.broker_last_failure.get(broker_id),
                'is_blocked': broker_id in self.blocked_brokers,
                'half_open_calls': self.half_open_calls.get(broker_id, 0),
                'stats': stats
            }
            
        except Exception as e:
            self.logger.log_error(f"Failed to get broker status for {broker_id}", str(e), "BrokerBreaker")
            return {'error': str(e)}
    
    def get_all_brokers_status(self) -> Dict[str, Any]:
        """Get status of all brokers"""
        try:
            status = {
                'total_brokers': len(self.broker_states),
                'open_circuits': len([b for b in self.broker_states.values() if b == BreakerState.OPEN]),
                'half_open_circuits': len([b for b in self.broker_states.values() if b == BreakerState.HALF_OPEN]),
                'closed_circuits': len([b for b in self.broker_states.values() if b == BreakerState.CLOSED]),
                'blocked_brokers': list(self.blocked_brokers),
                'brokers': {}
            }
            
            for broker_id in self.broker_states:
                status['brokers'][broker_id] = self.get_broker_status(broker_id)
            
            return status
            
        except Exception as e:
            self.logger.log_error("Failed to get all brokers status", str(e), "BrokerBreaker")
            return {'error': str(e)}
    
    def get_broker_stats(self) -> Dict[str, Any]:
        """Get comprehensive broker statistics"""
        try:
            stats = {
                'total_brokers': len(self.broker_states),
                'broker_stats': self.broker_stats,
                'circuit_breaker_summary': {
                    'open': len([b for b in self.broker_states.values() if b == BreakerState.OPEN]),
                    'half_open': len([b for b in self.broker_states.values() if b == BreakerState.HALF_OPEN]),
                    'closed': len([b for b in self.broker_states.values() if b == BreakerState.CLOSED])
                },
                'redis_connected': self.redis_client is not None
            }
            
            # Calculate overall success rates
            if self.broker_stats:
                total_calls = sum(stat['total_calls'] for stat in self.broker_stats.values())
                total_successful = sum(stat['successful_calls'] for stat in self.broker_stats.values())
                
                if total_calls > 0:
                    stats['overall_success_rate'] = (total_successful / total_calls) * 100
                else:
                    stats['overall_success_rate'] = 0
            
            return stats
            
        except Exception as e:
            self.logger.log_error("Failed to get broker stats", str(e), "BrokerBreaker")
            return {'error': str(e)}
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
            return False
        except:
            return False