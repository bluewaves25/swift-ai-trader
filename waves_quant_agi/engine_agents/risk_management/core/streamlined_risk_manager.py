#!/usr/bin/env python3
"""
Streamlined Risk Manager - 2-Tier Architecture
Core risk management logic with integrated trailing stops and performance tracking
"""

import time
import asyncio
import uuid
from typing import Dict, Any, List, Optional, Callable
from .connection_manager import ConnectionManager
from .dynamic_risk_limits import DynamicRiskLimits
from .circuit_breaker import CircuitBreakerManager
from .load_balancer import LoadBalancer, RiskRequest, RequestPriority
from .performance_monitor import PerformanceMonitor
from .trailing_stop_manager import TrailingStopManager
from .portfolio_performance_tracker import PortfolioPerformanceTracker

class AdaptiveTimer:
    """Adaptive timing system for risk validation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.fast_target_ms = config.get('fast_target_ms', 50)
        self.comprehensive_target_ms = config.get('comprehensive_target_ms', 500)
        self.adjustment_factor = config.get('adjustment_factor', 0.1)
        self.max_adjustments = config.get('max_adjustments', 100)
        
        self.timing_history = []
        self.current_adjustment = 0.0
        
    def record_operation(self, duration_ms: float, operation_type: str):
        """Record operation timing for adaptive adjustment."""
        self.timing_history.append({
            'duration_ms': duration_ms,
            'operation_type': operation_type,
            'timestamp': time.time()
        })
        
        # Maintain history length
        if len(self.timing_history) > self.max_adjustments:
            self.timing_history.pop(0)
            
        # Calculate adjustment
        target_ms = self.fast_target_ms if operation_type == 'fast' else self.comprehensive_target_ms
        if duration_ms > target_ms:
            self.current_adjustment += self.adjustment_factor
        elif duration_ms < target_ms * 0.8:
            self.current_adjustment -= self.adjustment_factor
            
        # Clamp adjustment
        self.current_adjustment = max(-1.0, min(1.0, self.current_adjustment))
        
    def get_adjusted_timeout(self, base_timeout_ms: float) -> float:
        """Get adjusted timeout based on performance history."""
        return base_timeout_ms * (1 + self.current_adjustment)

class StreamlinedRiskManager:
    """Streamlined 2-tier risk management system."""
    
    def __init__(self, connection_manager: ConnectionManager, config: Dict[str, Any]):
        self.connection_manager = connection_manager
        self.config = config
        
        # Initialize core components
        self.dynamic_risk_limits = DynamicRiskLimits(connection_manager, config)
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.load_balancer = LoadBalancer(config)
        self.performance_monitor = PerformanceMonitor(config)
        
        # Initialize new components for USER REQUIREMENTS
        self.trailing_stop_manager = TrailingStopManager(connection_manager, config)
        self.portfolio_performance_tracker = PortfolioPerformanceTracker(connection_manager, config)
        
        # Adaptive timing system
        self.adaptive_timer = AdaptiveTimer(config.get('adaptive_timer', {}))
        
        # Risk management state
        self.active_positions = {}
        self.risk_alerts = []
        self.last_health_check = time.time()
        
        print("✅ Streamlined Risk Manager initialized with trailing stops and performance tracking")
    
    async def validate_trade_request(self, trade_request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade request against risk limits."""
        start_time = time.time()
        
        try:
            # Create risk request
            risk_request = RiskRequest(
                id=str(uuid.uuid4()),
                trade_request=trade_request,
                priority=RequestPriority.HIGH if trade_request.get('urgent', False) else RequestPriority.NORMAL,
                timestamp=time.time()
            )
            
            # Process through load balancer
            result = await self.load_balancer.process_request(risk_request)
            
            # Record performance
            duration_ms = (time.time() - start_time) * 1000
            self.adaptive_timer.record_operation(duration_ms, 'comprehensive')
            
            return result
            
        except Exception as e:
            print(f"❌ Error validating trade request: {e}")
            return {'approved': False, 'reason': f'Validation error: {e}'}
    
    async def manage_position_risk(self, position_id: str, position_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage risk for an active position."""
        try:
            strategy_type = position_data.get('strategy_type', 'unknown')
            
            # Initialize trailing stop if strategy supports it
            if strategy_type in ['trend_following', 'htf']:
                await self.trailing_stop_manager.initialize_trailing_stop(
                    position_id=position_id,
                    strategy_type=strategy_type,
                    entry_price=position_data.get('entry_price', 0.0),
                    position_size=position_data.get('position_size', 0.0),
                    side=position_data.get('side', 'buy')
                )
            
            # Update active positions
            self.active_positions[position_id] = position_data
            
            return {'status': 'position_risk_managed', 'trailing_stop_active': strategy_type in ['trend_following', 'htf']}
            
        except Exception as e:
            print(f"❌ Error managing position risk: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def update_position_prices(self, position_updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update position prices and check trailing stops."""
        try:
            actions = []
            
            for update in position_updates:
                position_id = update.get('position_id')
                current_price = update.get('current_price')
                
                if position_id and current_price:
                    # Update trailing stop
                    stop_action = await self.trailing_stop_manager.update_trailing_stop(
                        position_id, current_price
                    )
                    
                    if stop_action:
                        actions.append(stop_action)
                        print(f"🚨 Trailing stop triggered for {position_id}: {stop_action['reason']}")
            
            return actions
            
        except Exception as e:
            print(f"❌ Error updating position prices: {e}")
            return []
    
    async def update_portfolio_performance(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update portfolio performance and check daily loss limits."""
        try:
            # Update portfolio performance tracker
            performance_result = await self.portfolio_performance_tracker.update_portfolio_performance(portfolio_data)
            
            # Check if daily loss circuit breaker is active
            if performance_result.get('daily_loss_check', {}).get('circuit_breaker_active', False):
                print("🚨 Daily loss circuit breaker is ACTIVE - all trading suspended")
                
                # Notify all components
                await self._notify_daily_loss_breach(performance_result['daily_loss_check'])
            
            # Check weekly reward target
            weekly_check = performance_result.get('weekly_reward_check', {})
            if weekly_check.get('achieved', False):
                print(f"🎯 Weekly reward target achieved: {weekly_check.get('current', 0):.2f}%")
            
            return performance_result
            
        except Exception as e:
            print(f"❌ Error updating portfolio performance: {e}")
            return {}
    
    async def _notify_daily_loss_breach(self, daily_loss_check: Dict[str, Any]):
        """Notify all components of daily loss breach."""
        try:
            notification = {
                'type': 'daily_loss_breach',
                'timestamp': time.time(),
                'details': daily_loss_check,
                'action_required': 'suspend_all_trading'
            }
            
            # Notify execution agent
            redis_client = await self.connection_manager.get_redis_client()
            if redis_client:
                redis_client.publish("execution_agent", str(notification))
                redis_client.publish("risk_management_alerts", str(notification))
                
            print("✅ Daily loss breach notification sent to all components")
            
        except Exception as e:
            print(f"❌ Error notifying daily loss breach: {e}")
    
    async def get_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive risk summary."""
        try:
            # Get trailing stop summary
            trailing_stop_summary = await self.trailing_stop_manager.get_trailing_stop_summary()
            
            # Get portfolio performance summary
            performance_summary = await self.portfolio_performance_tracker.get_performance_summary()
            
            # Get circuit breaker status
            circuit_breaker_status = self.circuit_breaker_manager.get_status()
            
            return {
                'trailing_stops': trailing_stop_summary,
                'portfolio_performance': performance_summary,
                'circuit_breakers': circuit_breaker_status,
                'active_positions': len(self.active_positions),
                'risk_alerts': len(self.risk_alerts),
                'last_health_check': self.last_health_check,
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"❌ Error getting risk summary: {e}")
            return {}
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            start_time = time.time()
            
            # Check all components
            health_status = {
                'connection_manager': await self._check_connection_manager(),
                'dynamic_risk_limits': await self._check_dynamic_risk_limits(),
                'circuit_breaker_manager': await self._check_circuit_breaker_manager(),
                'load_balancer': await self._check_load_balancer(),
                'performance_monitor': await self._check_performance_monitor(),
                'trailing_stop_manager': await self._check_trailing_stop_manager(),
                'portfolio_performance_tracker': await self._check_portfolio_performance_tracker()
            }
            
            # Update last health check
            self.last_health_check = time.time()
            
            # Record performance
            duration_ms = (time.time() - start_time) * 1000
            self.adaptive_timer.record_operation(duration_ms, 'comprehensive')
            
            return health_status
            
        except Exception as e:
            print(f"❌ Error performing health check: {e}")
            return {'error': str(e)}
    
    async def _check_connection_manager(self) -> Dict[str, Any]:
        """Check connection manager health."""
        try:
            redis_client = await self.connection_manager.get_redis_client()
            return {'status': 'healthy', 'redis_connected': redis_client is not None}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def _check_dynamic_risk_limits(self) -> Dict[str, Any]:
        """Check dynamic risk limits health."""
        try:
            # Test with a sample strategy
            test_limits = await self.dynamic_risk_limits.get_strategy_risk_limits('trend_following', 'BTC/USD')
            return {'status': 'healthy', 'test_limits_retrieved': bool(test_limits)}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def _check_circuit_breaker_manager(self) -> Dict[str, Any]:
        """Check circuit breaker manager health."""
        try:
            status = self.circuit_breaker_manager.get_status()
            return {'status': 'healthy', 'circuit_breakers': len(status)}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def _check_load_balancer(self) -> Dict[str, Any]:
        """Check load balancer health."""
        try:
            workers = self.load_balancer.get_worker_status()
            return {'status': 'healthy', 'active_workers': len([w for w in workers if w['status'] == 'active'])}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def _check_performance_monitor(self) -> Dict[str, Any]:
        """Check performance monitor health."""
        try:
            metrics = await self.performance_monitor.get_metrics()
            return {'status': 'healthy', 'metrics_count': len(metrics)}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def _check_trailing_stop_manager(self) -> Dict[str, Any]:
        """Check trailing stop manager health."""
        try:
            summary = await self.trailing_stop_manager.get_trailing_stop_summary()
            return {'status': 'healthy', 'active_trailing_stops': summary.get('total_active', 0)}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def _check_portfolio_performance_tracker(self) -> Dict[str, Any]:
        """Check portfolio performance tracker health."""
        try:
            summary = await self.portfolio_performance_tracker.get_performance_summary()
            return {'status': 'healthy', 'performance_history_count': summary.get('performance_history_count', 0)}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            # Cleanup trailing stops
            await self.trailing_stop_manager.cleanup_expired_stops()
            
            # Clear old risk alerts
            if len(self.risk_alerts) > 1000:
                self.risk_alerts = self.risk_alerts[-1000:]
                
            print("✅ Streamlined Risk Manager cleanup completed")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
