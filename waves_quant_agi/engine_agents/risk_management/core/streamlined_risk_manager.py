#!/usr/bin/env python3
"""
Streamlined Risk Manager - Improved 2-tier architecture
Replaces over-engineered 4-tier system with efficient 2-tier approach
Provides adaptive timing and intelligent request processing
"""

import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from .connection_manager import ConnectionManager
from .dynamic_risk_limits import DynamicRiskLimits
from .circuit_breaker import CircuitBreakerManager
from .load_balancer import LoadBalancer, RiskRequest, RequestPriority
from .performance_monitor import PerformanceMonitor

class AdaptiveTimer:
    """Adaptive timing system for risk validation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timing_stats = {
            'fast': {'target': 50, 'current': 50, 'adjustments': []},
            'comprehensive': {'target': 500, 'current': 500, 'adjustments': []}
        }
        self.max_adjustments = 100
        self.adjustment_factor = 0.1
    
    def update_timing(self, tier: str, actual_duration_ms: float):
        """Update timing based on actual performance."""
        if tier not in self.timing_stats:
            return
        
        stats = self.timing_stats[tier]
        target = stats['target']
        
        # Calculate adjustment
        if actual_duration_ms > target * 1.2:  # 20% over target
            # Performance degraded, increase target
            adjustment = min(actual_duration_ms * self.adjustment_factor, target * 0.2)
            stats['current'] = min(stats['current'] + adjustment, target * 2)
        elif actual_duration_ms < target * 0.8:  # 20% under target
            # Performance improved, decrease target
            adjustment = min(target * self.adjustment_factor, target * 0.1)
            stats['current'] = max(stats['current'] - adjustment, target * 0.5)
        
        # Record adjustment
        stats['adjustments'].append({
            'timestamp': time.time(),
            'actual': actual_duration_ms,
            'target': target,
            'new_current': stats['current']
        })
        
        # Keep only recent adjustments
        if len(stats['adjustments']) > self.max_adjustments:
            stats['adjustments'] = stats['adjustments'][-self.max_adjustments:]
    
    def get_timing(self, tier: str) -> float:
        """Get current timing for a tier."""
        return self.timing_stats.get(tier, {}).get('current', 500)
    
    def get_timing_stats(self) -> Dict[str, Any]:
        """Get timing statistics."""
        return {
            tier: {
                'target_ms': stats['target'],
                'current_ms': stats['current'],
                'adjustment_count': len(stats['adjustments'])
            }
            for tier, stats in self.timing_stats.items()
        }

class StreamlinedRiskManager:
    """Streamlined risk management with 2-tier architecture."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize core components
        self.connection_manager = ConnectionManager(config)
        self.dynamic_risk_limits = DynamicRiskLimits(self.connection_manager, config)
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.load_balancer = LoadBalancer(
            num_workers=config.get('num_workers', 4),
            max_queue_size=config.get('max_queue_size', 1000)
        )
        self.performance_monitor = PerformanceMonitor(config)
        self.adaptive_timer = AdaptiveTimer(config)
        
        # Initialize circuit breakers
        self._setup_circuit_breakers()
        
        # Risk validation state
        self.risk_state = {}
        self.validation_stats = {
            'fast_validations': 0,
            'comprehensive_validations': 0,
            'total_requests': 0,
            'successful_validations': 0,
            'failed_validations': 0
        }
        
        # Request processing
        self.is_running = False
        self.request_queue = asyncio.Queue(maxsize=10000)
        
        # Performance tracking
        self.start_time = time.time()
    
    def _setup_circuit_breakers(self):
        """Setup circuit breakers for different components."""
        # Risk validation circuit breaker
        self.circuit_breaker_manager.create_circuit_breaker(
            name='risk_validation',
            failure_threshold=5,
            recovery_timeout=30
        )
        
        # Portfolio monitoring circuit breaker
        self.circuit_breaker_manager.create_circuit_breaker(
            name='portfolio_monitoring',
            failure_threshold=3,
            recovery_timeout=60
        )
        
        # Data fetching circuit breaker
        self.circuit_breaker_manager.create_circuit_breaker(
            name='data_fetching',
            failure_threshold=10,
            recovery_timeout=120
        )
    
    async def start(self):
        """Start the streamlined risk manager."""
        try:
            self.is_running = True
            
            # Start load balancer
            await self.load_balancer.start(self._process_risk_request)
            
            # Start request processing loop
            asyncio.create_task(self._request_processing_loop())
            
            print("Streamlined Risk Manager started successfully")
            
        except Exception as e:
            print(f"Failed to start Streamlined Risk Manager: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """Stop the streamlined risk manager."""
        self.is_running = False
        self.load_balancer.stop()
        print("Streamlined Risk Manager stopped")
    
    async def submit_risk_request(self, strategy_type: str, symbol: str, 
                                 request_data: Dict[str, Any]) -> str:
        """Submit a risk validation request."""
        try:
            # Determine request priority
            priority = self._determine_request_priority(strategy_type)
            
            # Create risk request
            request = RiskRequest(
                request_id=str(uuid.uuid4()),
                strategy_type=strategy_type,
                symbol=symbol,
                priority=priority,
                timestamp=time.time(),
                data=request_data
            )
            
            # Add to request queue
            await self.request_queue.put(request)
            self.validation_stats['total_requests'] += 1
            
            return request.request_id
            
        except Exception as e:
            print(f"Error submitting risk request: {e}")
            raise
    
    def _determine_request_priority(self, strategy_type: str) -> RequestPriority:
        """Determine request priority based on strategy type."""
        if strategy_type in ['arbitrage', 'market_making']:
            return RequestPriority.ULTRA_HIGH  # HFT strategies
        elif strategy_type in ['trend_following', 'statistical_arbitrage']:
            return RequestPriority.HIGH  # Standard strategies
        elif strategy_type in ['news_driven', 'htf']:
            return RequestPriority.MEDIUM  # Strategic strategies
        else:
            return RequestPriority.LOW  # Background tasks
    
    async def _request_processing_loop(self):
        """Main request processing loop."""
        while self.is_running:
            try:
                # Get request from queue
                try:
                    request = await asyncio.wait_for(self.request_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Route request to load balancer
                success = await self.load_balancer.route_request(request)
                
                if not success:
                    print(f"Failed to route request {request.request_id}")
                    self.validation_stats['failed_validations'] += 1
                
            except Exception as e:
                print(f"Error in request processing loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_risk_request(self, request: RiskRequest) -> Dict[str, Any]:
        """Process a risk validation request."""
        start_time = time.time()
        
        try:
            # Determine validation tier
            if request.priority == RequestPriority.ULTRA_HIGH:
                # Tier 1: Fast validation (10-50ms)
                result = await self._fast_validation(request)
                self.validation_stats['fast_validations'] += 1
            else:
                # Tier 2: Comprehensive validation (100-500ms)
                result = await self._comprehensive_validation(request)
                self.validation_stats['comprehensive_validations'] += 1
            
            # Record performance metrics
            duration_ms = (time.time() - start_time) * 1000
            await self.performance_monitor.record_operation(
                operation_type='risk_validation',
                duration_ms=duration_ms,
                success=True,
                component=f'risk_manager_{request.strategy_type}',
                metadata={'request_id': request.request_id, 'tier': 'fast' if request.priority == RequestPriority.ULTRA_HIGH else 'comprehensive'}
            )
            
            # Update adaptive timing
            tier = 'fast' if request.priority == RequestPriority.ULTRA_HIGH else 'comprehensive'
            self.adaptive_timer.update_timing(tier, duration_ms)
            
            self.validation_stats['successful_validations'] += 1
            
            return result
            
        except Exception as e:
            # Record failure
            duration_ms = (time.time() - start_time) * 1000
            await self.performance_monitor.record_operation(
                operation_type='risk_validation',
                duration_ms=duration_ms,
                success=False,
                component=f'risk_manager_{request.strategy_type}',
                metadata={'request_id': request.request_id, 'error': str(e)}
            )
            
            self.validation_stats['failed_validations'] += 1
            raise
    
    async def _fast_validation(self, request: RiskRequest) -> Dict[str, Any]:
        """Fast validation for HFT strategies."""
        try:
            # Get dynamic risk limits
            risk_limits = await self.dynamic_risk_limits.get_strategy_risk_limits(
                request.strategy_type, request.symbol
            )
            
            # Essential checks only
            validation_result = {
                'request_id': request.request_id,
                'strategy_type': request.strategy_type,
                'symbol': request.symbol,
                'validation_tier': 'fast',
                'risk_limits': risk_limits,
                'basic_checks': await self._perform_basic_checks(request, risk_limits),
                'timestamp': time.time(),
                'processing_time_ms': 0  # Will be set by caller
            }
            
            return validation_result
            
        except Exception as e:
            print(f"Fast validation failed: {e}")
            raise
    
    async def _comprehensive_validation(self, request: RiskRequest) -> Dict[str, Any]:
        """Comprehensive validation for standard strategies."""
        try:
            # Get dynamic risk limits
            risk_limits = await self.dynamic_risk_limits.get_strategy_risk_limits(
                request.strategy_type, request.symbol
            )
            
            # Perform comprehensive validation
            validation_result = {
                'request_id': request.request_id,
                'strategy_type': request.strategy_type,
                'symbol': request.symbol,
                'validation_tier': 'comprehensive',
                'risk_limits': risk_limits,
                'basic_checks': await self._perform_basic_checks(request, risk_limits),
                'portfolio_checks': await self._perform_portfolio_checks(request),
                'market_checks': await self._perform_market_checks(request),
                'correlation_checks': await self._perform_correlation_checks(request),
                'timestamp': time.time(),
                'processing_time_ms': 0  # Will be set by caller
            }
            
            return validation_result
            
        except Exception as e:
            print(f"Comprehensive validation failed: {e}")
            raise
    
    async def _perform_basic_checks(self, request: RiskRequest, 
                                   risk_limits: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic risk validation checks."""
        try:
            # Position size check
            position_size = request.data.get('position_size', 0)
            max_position = risk_limits.get('max_position_size', 0.1)
            position_check = position_size <= max_position
            
            # Leverage check
            leverage = request.data.get('leverage', 1.0)
            max_leverage = risk_limits.get('max_leverage', 1.0)
            leverage_check = leverage <= max_leverage
            
            # Stop loss check
            stop_loss = request.data.get('stop_loss', 0)
            max_stop_loss = risk_limits.get('stop_loss', 0.02)
            stop_loss_check = stop_loss <= max_stop_loss
            
            return {
                'position_size_check': position_check,
                'leverage_check': leverage_check,
                'stop_loss_check': stop_loss_check,
                'all_checks_passed': position_check and leverage_check and stop_loss_check
            }
            
        except Exception as e:
            print(f"Basic checks failed: {e}")
            return {'all_checks_passed': False, 'error': str(e)}
    
    async def _perform_portfolio_checks(self, request: RiskRequest) -> Dict[str, Any]:
        """Perform portfolio-level risk checks."""
        try:
            # Mock portfolio checks - replace with actual implementation
            return {
                'portfolio_exposure_check': True,
                'diversification_check': True,
                'correlation_check': True,
                'all_checks_passed': True
            }
        except Exception as e:
            print(f"Portfolio checks failed: {e}")
            return {'all_checks_passed': False, 'error': str(e)}
    
    async def _perform_market_checks(self, request: RiskRequest) -> Dict[str, Any]:
        """Perform market condition checks."""
        try:
            # Mock market checks - replace with actual implementation
            return {
                'volatility_check': True,
                'liquidity_check': True,
                'market_regime_check': True,
                'all_checks_passed': True
            }
        except Exception as e:
            print(f"Market checks failed: {e}")
            return {'all_checks_passed': False, 'error': str(e)}
    
    async def _perform_correlation_checks(self, request: RiskRequest) -> Dict[str, Any]:
        """Perform correlation risk checks."""
        try:
            # Mock correlation checks - replace with actual implementation
            return {
                'portfolio_correlation_check': True,
                'sector_correlation_check': True,
                'all_checks_passed': True
            }
        except Exception as e:
            print(f"Correlation checks failed: {e}")
            return {'all_checks_passed': False, 'error': str(e)}
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        uptime = time.time() - self.start_time
        
        return {
            **self.validation_stats,
            'uptime_seconds': uptime,
            'requests_per_second': self.validation_stats['total_requests'] / max(uptime, 1),
            'success_rate': self.validation_stats['successful_validations'] / max(self.validation_stats['total_requests'], 1),
            'fast_validation_rate': self.validation_stats['fast_validations'] / max(self.validation_stats['total_requests'], 1),
            'comprehensive_validation_rate': self.validation_stats['comprehensive_validations'] / max(self.validation_stats['total_requests'], 1)
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        return {
            'risk_manager': {
                'status': 'running' if self.is_running else 'stopped',
                'stats': self.get_validation_stats()
            },
            'load_balancer': self.load_balancer.health_check(),
            'circuit_breakers': self.circuit_breaker_manager.health_check(),
            'performance': self.performance_monitor.get_monitor_stats(),
            'timing': self.adaptive_timer.get_timing_stats(),
            'timestamp': time.time()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            # Check connection health
            connection_health = await self.connection_manager.health_check()
            
            # Get system health
            system_health = self.get_system_health()
            
            # Overall health assessment
            overall_health = 'healthy'
            if connection_health['status'] != 'healthy':
                overall_health = 'unhealthy'
            elif system_health['load_balancer']['overall_health'] < 0.8:
                overall_health = 'degraded'
            
            return {
                'overall_health': overall_health,
                'connection_health': connection_health,
                'system_health': system_health,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'overall_health': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
