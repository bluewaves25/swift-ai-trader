#!/usr/bin/env python3
"""
Portfolio Performance Tracker
Implements 2% daily portfolio loss limit and 20% weekly reward target
Manages portfolio-level risk with circuit breaker functionality
"""

import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from .connection_manager import ConnectionManager
from .circuit_breaker import CircuitBreaker

class PortfolioPerformanceTracker:
    """Tracks portfolio performance and enforces daily loss limits and weekly reward targets."""
    
    def __init__(self, connection_manager: ConnectionManager, config: Dict[str, Any]):
        self.connection_manager = connection_manager
        self.config = config
        
        # Get portfolio performance configuration
        self.portfolio_config = config.get('portfolio_performance', {})
        self.daily_loss_limit = self.portfolio_config.get('daily_loss_limit', 0.02)  # 2%
        self.weekly_reward_target = self.portfolio_config.get('weekly_reward_target', 0.20)  # 20%
        self.performance_tracking_window = self.portfolio_config.get('performance_tracking_window', 7)
        self.daily_loss_circuit_breaker = self.portfolio_config.get('daily_loss_circuit_breaker', True)
        self.reward_optimization_enabled = self.portfolio_config.get('reward_optimization_enabled', True)
        self.performance_alert_threshold = self.portfolio_config.get('performance_alert_threshold', 0.015)
        
        # Initialize circuit breaker for daily loss limit
        self.daily_loss_circuit_breaker = CircuitBreaker(
            failure_threshold=1,  # Trigger immediately when daily loss exceeds limit
            recovery_timeout=3600,  # 1 hour recovery timeout
            name="daily_loss_limit"
        )
        
        # Portfolio performance history
        self.performance_history = []
        self.max_history_length = 1000
        
        # Current performance metrics
        self.current_metrics = {
            'total_portfolio_value': 100000.0,
            'daily_pnl': 0.0,
            'daily_pnl_percent': 0.0,
            'weekly_pnl': 0.0,
            'weekly_pnl_percent': 0.0,
            'monthly_pnl': 0.0,
            'monthly_pnl_percent': 0.0,
            'current_drawdown': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'sharpe_ratio': 0.0,
            'last_update': time.time()
        }
        
        # Daily and weekly tracking
        self.daily_tracker = {
            'start_value': 100000.0,
            'current_value': 100000.0,
            'high_water_mark': 100000.0,
            'low_water_mark': 100000.0,
            'start_time': time.time(),
            'last_reset': time.time()
        }
        
        self.weekly_tracker = {
            'start_value': 100000.0,
            'current_value': 100000.0,
            'high_water_mark': 100000.0,
            'low_water_mark': 100000.0,
            'start_time': time.time(),
            'last_reset': time.time()
        }
        
        # Circuit breaker state
        self.daily_loss_breached = False
        self.weekly_target_achieved = False
        
    async def update_portfolio_performance(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update portfolio performance metrics and check limits."""
        try:
            # Update current portfolio value
            current_value = portfolio_data.get('total_value', self.current_metrics['total_portfolio_value'])
            self.current_metrics['total_portfolio_value'] = current_value
            
            # Update daily tracking
            await self._update_daily_tracking(current_value)
            
            # Update weekly tracking
            await self._update_weekly_tracking(current_value)
            
            # Calculate performance metrics
            await self._calculate_performance_metrics()
            
            # Check daily loss limit
            daily_loss_check = await self._check_daily_loss_limit()
            
            # Check weekly reward target
            weekly_reward_check = await self._check_weekly_reward_target()
            
            # Update performance history
            await self._update_performance_history()
            
            # Return performance summary
            return {
                'current_metrics': self.current_metrics.copy(),
                'daily_tracker': self.daily_tracker.copy(),
                'weekly_tracker': self.weekly_tracker.copy(),
                'daily_loss_check': daily_loss_check,
                'weekly_reward_check': weekly_reward_check,
                'circuit_breaker_state': {
                    'daily_loss_breached': self.daily_loss_breached,
                    'weekly_target_achieved': self.weekly_target_achieved
                }
            }
            
        except Exception as e:
            print(f"❌ Error updating portfolio performance: {e}")
            return {}
    
    async def _update_daily_tracking(self, current_value: float):
        """Update daily performance tracking."""
        try:
            current_time = time.time()
            
            # Check if we need to reset daily tracking (new day)
            if self._is_new_day():
                self.daily_tracker = {
                    'start_value': current_value,
                    'current_value': current_value,
                    'high_water_mark': current_value,
                    'low_water_mark': current_value,
                    'start_time': current_time,
                    'last_reset': current_time
                }
            else:
                # Update current value and water marks
                self.daily_tracker['current_value'] = current_value
                self.daily_tracker['high_water_mark'] = max(
                    self.daily_tracker['high_water_mark'], current_value
                )
                self.daily_tracker['low_water_mark'] = min(
                    self.daily_tracker['low_water_mark'], current_value
                )
                
        except Exception as e:
            print(f"❌ Error updating daily tracking: {e}")
    
    async def _update_weekly_tracking(self, current_value: float):
        """Update weekly performance tracking."""
        try:
            current_time = time.time()
            
            # Check if we need to reset weekly tracking (new week)
            if self._is_new_week():
                self.weekly_tracker = {
                    'start_value': current_value,
                    'current_value': current_value,
                    'high_water_mark': current_value,
                    'low_water_mark': current_value,
                    'start_time': current_time,
                    'last_reset': current_time
                }
            else:
                # Update current value and water marks
                self.weekly_tracker['current_value'] = current_value
                self.weekly_tracker['high_water_mark'] = max(
                    self.weekly_tracker['high_water_mark'], current_value
                )
                self.weekly_tracker['low_water_mark'] = min(
                    self.weekly_tracker['low_water_mark'], current_value
                )
                
        except Exception as e:
            print(f"❌ Error updating weekly tracking: {e}")
    
    async def _calculate_performance_metrics(self):
        """Calculate current performance metrics."""
        try:
            # Daily P&L
            daily_pnl = self.daily_tracker['current_value'] - self.daily_tracker['start_value']
            daily_pnl_percent = (daily_pnl / self.daily_tracker['start_value']) * 100
            
            # Weekly P&L
            weekly_pnl = self.weekly_tracker['current_value'] - self.weekly_tracker['start_value']
            weekly_pnl_percent = (weekly_pnl / self.weekly_tracker['start_value']) * 100
            
            # Update current metrics
            self.current_metrics.update({
                'daily_pnl': daily_pnl,
                'daily_pnl_percent': daily_pnl_percent,
                'weekly_pnl': weekly_pnl,
                'weekly_pnl_percent': weekly_pnl_percent,
                'last_update': time.time()
            })
            
        except Exception as e:
            print(f"❌ Error calculating performance metrics: {e}")
    
    async def _check_daily_loss_limit(self) -> Dict[str, Any]:
        """Check if daily loss limit is breached."""
        try:
            daily_loss_percent = abs(self.current_metrics['daily_pnl_percent'])
            is_breached = daily_loss_percent > (self.daily_loss_limit * 100)
            
            # Check circuit breaker
            if is_breached and not self.daily_loss_breached:
                self.daily_loss_breached = True
                print(f"🚨 DAILY LOSS LIMIT BREACHED: {daily_loss_percent:.2f}% (Limit: {self.daily_loss_limit * 100:.1f}%)")
                
                # Trigger circuit breaker
                if self.daily_loss_circuit_breaker:
                    await self._trigger_daily_loss_circuit_breaker()
            
            # Check if we can reset circuit breaker (new day)
            if self._is_new_day() and self.daily_loss_breached:
                self.daily_loss_breached = False
                print("✅ Daily loss circuit breaker reset (new day)")
            
            return {
                'limit': self.daily_loss_limit * 100,
                'current': daily_loss_percent,
                'breached': is_breached,
                'circuit_breaker_active': self.daily_loss_breached
            }
            
        except Exception as e:
            print(f"❌ Error checking daily loss limit: {e}")
            return {}
    
    async def _check_weekly_reward_target(self) -> Dict[str, Any]:
        """Check if weekly reward target is achieved."""
        try:
            weekly_reward_percent = self.current_metrics['weekly_pnl_percent']
            is_achieved = weekly_reward_percent >= (self.weekly_reward_target * 100)
            
            if is_achieved and not self.weekly_target_achieved:
                self.weekly_target_achieved = True
                print(f"🎯 WEEKLY REWARD TARGET ACHIEVED: {weekly_reward_percent:.2f}% (Target: {self.weekly_reward_target * 100:.1f}%)")
            
            # Check if we can reset weekly target (new week)
            if self._is_new_week() and self.weekly_target_achieved:
                self.weekly_target_achieved = False
                print("🔄 Weekly reward target reset (new week)")
            
            return {
                'target': self.weekly_reward_target * 100,
                'current': weekly_reward_percent,
                'achieved': is_achieved,
                'remaining': max(0, (self.weekly_reward_target * 100) - weekly_reward_percent)
            }
            
        except Exception as e:
            print(f"❌ Error checking weekly reward target: {e}")
            return {}
    
    async def _trigger_daily_loss_circuit_breaker(self):
        """Trigger circuit breaker when daily loss limit is breached."""
        try:
            print("🚨 TRIGGERING DAILY LOSS CIRCUIT BREAKER")
            
            # Notify execution agent to close all positions
            redis_client = await self.connection_manager.get_redis_client()
            if redis_client:
                circuit_breaker_action = {
                    'action': 'circuit_breaker_triggered',
                    'type': 'daily_loss_limit',
                    'reason': f"Daily loss limit {self.daily_loss_limit * 100:.1f}% exceeded",
                    'current_loss': f"{self.current_metrics['daily_pnl_percent']:.2f}%",
                    'timestamp': time.time(),
                    'instructions': 'Close all positions immediately'
                }
                
                redis_client.publish("execution_agent", str(circuit_breaker_action))
                redis_client.set("risk_management:daily_loss_circuit_breaker", str(circuit_breaker_action), ex=3600)
                
                print("✅ Circuit breaker action sent to execution agent")
            
        except Exception as e:
            print(f"❌ Error triggering circuit breaker: {e}")
    
    async def _update_performance_history(self):
        """Update performance history."""
        try:
            history_entry = {
                'timestamp': time.time(),
                'metrics': self.current_metrics.copy(),
                'daily_tracker': self.daily_tracker.copy(),
                'weekly_tracker': self.weekly_tracker.copy()
            }
            
            self.performance_history.append(history_entry)
            
            # Maintain history length
            if len(self.performance_history) > self.max_history_length:
                self.performance_history.pop(0)
                
        except Exception as e:
            print(f"❌ Error updating performance history: {e}")
    
    def _is_new_day(self) -> bool:
        """Check if it's a new day since last reset."""
        current_time = time.time()
        last_reset = self.daily_tracker['last_reset']
        
        # Check if 24 hours have passed
        return (current_time - last_reset) >= 86400  # 24 hours in seconds
    
    def _is_new_week(self) -> bool:
        """Check if it's a new week since last reset."""
        current_time = time.time()
        last_reset = self.weekly_tracker['last_reset']
        
        # Check if 7 days have passed
        return (current_time - last_reset) >= 604800  # 7 days in seconds
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        try:
            return {
                'current_metrics': self.current_metrics.copy(),
                'daily_tracker': self.daily_tracker.copy(),
                'weekly_tracker': self.weekly_tracker.copy(),
                'limits': {
                    'daily_loss_limit': self.daily_loss_limit * 100,
                    'weekly_reward_target': self.weekly_reward_target * 100
                },
                'circuit_breaker_state': {
                    'daily_loss_breached': self.daily_loss_breached,
                    'weekly_target_achieved': self.weekly_target_achieved
                },
                'performance_history_count': len(self.performance_history),
                'last_update': time.time()
            }
        except Exception as e:
            print(f"❌ Error getting performance summary: {e}")
            return {}
    
    async def reset_tracking(self, tracking_type: str = 'all'):
        """Reset tracking data."""
        try:
            current_value = self.current_metrics['total_portfolio_value']
            current_time = time.time()
            
            if tracking_type in ['daily', 'all']:
                self.daily_tracker = {
                    'start_value': current_value,
                    'current_value': current_value,
                    'high_water_mark': current_value,
                    'low_water_mark': current_value,
                    'start_time': current_time,
                    'last_reset': current_time
                }
                print("✅ Daily tracking reset")
            
            if tracking_type in ['weekly', 'all']:
                self.weekly_tracker = {
                    'start_value': current_value,
                    'current_value': current_value,
                    'high_water_mark': current_value,
                    'low_water_mark': current_value,
                    'start_time': current_time,
                    'last_reset': current_time
                }
                print("✅ Weekly tracking reset")
            
            if tracking_type == 'all':
                self.daily_loss_breached = False
                self.weekly_target_achieved = False
                print("✅ All tracking and circuit breakers reset")
                
        except Exception as e:
            print(f"❌ Error resetting tracking: {e}")
