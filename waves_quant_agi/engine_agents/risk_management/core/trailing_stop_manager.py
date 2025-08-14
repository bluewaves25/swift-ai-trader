#!/usr/bin/env python3
"""
Trailing Stop Loss Manager
Implements trailing stop loss for trend_following and htf strategies
Manages dynamic stop loss adjustment based on price movement
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from .connection_manager import ConnectionManager

class TrailingStopManager:
    """Manages trailing stop losses for eligible strategies."""
    
    def __init__(self, connection_manager: ConnectionManager, config: Dict[str, Any]):
        self.connection_manager = connection_manager
        self.config = config
        self.active_trailing_stops = {}
        self.trailing_stop_config = config.get('portfolio_performance', {}).get('trailing_stop_management', True)
        
    async def initialize_trailing_stop(self, position_id: str, strategy_type: str, 
                                     entry_price: float, position_size: float, 
                                     side: str) -> bool:
        """Initialize trailing stop for a new position."""
        try:
            # Check if strategy supports trailing stop
            strategy_config = self.config.get('strategy_risk_limits', {}).get(strategy_type, {})
            if not strategy_config.get('trailing_stop_enabled', False):
                return False
                
            # Get trailing stop parameters
            trailing_distance = strategy_config.get('trailing_stop_distance', 0.01)
            activation_threshold = strategy_config.get('trailing_stop_activation', 0.01)
            tightening_increment = strategy_config.get('trailing_stop_tightening', 0.002)
            
            # Initialize trailing stop state
            self.active_trailing_stops[position_id] = {
                'strategy_type': strategy_type,
                'entry_price': entry_price,
                'position_size': position_size,
                'side': side,  # 'buy' or 'sell'
                'trailing_distance': trailing_distance,
                'activation_threshold': activation_threshold,
                'tightening_increment': tightening_increment,
                'current_stop_price': None,
                'highest_profit_price': entry_price,
                'lowest_loss_price': entry_price,
                'is_activated': False,
                'last_update': time.time(),
                'stop_loss_triggered': False
            }
            
            print(f"✅ Trailing stop initialized for {position_id} ({strategy_type})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize trailing stop for {position_id}: {e}")
            return False
    
    async def update_trailing_stop(self, position_id: str, current_price: float) -> Optional[Dict[str, Any]]:
        """Update trailing stop based on current price and return action if needed."""
        try:
            if position_id not in self.active_trailing_stops:
                return None
                
            trailing_stop = self.active_trailing_stops[position_id]
            entry_price = trailing_stop['entry_price']
            side = trailing_stop['side']
            
            # Calculate current P&L
            if side == 'buy':
                current_pnl = (current_price - entry_price) / entry_price
                profit_price = max(trailing_stop['highest_profit_price'], current_price)
                trailing_stop['highest_profit_price'] = profit_price
            else:  # sell (short)
                current_pnl = (entry_price - current_price) / entry_price
                profit_price = min(trailing_stop['lowest_loss_price'], current_price)
                trailing_stop['lowest_loss_price'] = profit_price
            
            # Check if trailing stop should be activated
            if not trailing_stop['is_activated'] and current_pnl >= trailing_stop['activation_threshold']:
                trailing_stop['is_activated'] = True
                print(f"🎯 Trailing stop activated for {position_id} at {current_pnl:.2%} profit")
            
            # Update trailing stop if activated
            if trailing_stop['is_activated']:
                await self._adjust_trailing_stop(trailing_stop, current_price, side)
            
            # Check if stop loss is triggered
            stop_action = await self._check_stop_loss_trigger(trailing_stop, current_price, side)
            if stop_action:
                trailing_stop['stop_loss_triggered'] = True
                return stop_action
            
            # Update last update time
            trailing_stop['last_update'] = time.time()
            return None
            
        except Exception as e:
            print(f"❌ Error updating trailing stop for {position_id}: {e}")
            return None
    
    async def _adjust_trailing_stop(self, trailing_stop: Dict[str, Any], 
                                   current_price: float, side: str):
        """Adjust trailing stop price based on profit movement."""
        try:
            if side == 'buy':
                profit_price = trailing_stop['highest_profit_price']
                new_stop_price = profit_price * (1 - trailing_stop['trailing_distance'])
                
                # Tighten stop if profit increases
                if (trailing_stop['current_stop_price'] is None or 
                    new_stop_price > trailing_stop['current_stop_price']):
                    trailing_stop['current_stop_price'] = new_stop_price
                    print(f"📈 Trailing stop tightened for buy position: {new_stop_price:.4f}")
                    
            else:  # sell (short)
                profit_price = trailing_stop['lowest_loss_price']
                new_stop_price = profit_price * (1 + trailing_stop['trailing_distance'])
                
                # Tighten stop if profit increases
                if (trailing_stop['current_stop_price'] is None or 
                    new_stop_price < trailing_stop['current_stop_price']):
                    trailing_stop['current_stop_price'] = new_stop_price
                    print(f"📉 Trailing stop tightened for sell position: {new_stop_price:.4f}")
                    
        except Exception as e:
            print(f"❌ Error adjusting trailing stop: {e}")
    
    async def _check_stop_loss_trigger(self, trailing_stop: Dict[str, Any], 
                                      current_price: float, side: str) -> Optional[Dict[str, Any]]:
        """Check if trailing stop loss is triggered."""
        try:
            if trailing_stop['current_stop_price'] is None:
                return None
            
            stop_triggered = False
            
            if side == 'buy' and current_price <= trailing_stop['current_stop_price']:
                stop_triggered = True
            elif side == 'sell' and current_price >= trailing_stop['current_stop_price']:
                stop_triggered = True
            
            if stop_triggered:
                return {
                    'action': 'close_position',
                    'position_id': list(self.active_trailing_stops.keys())[
                        list(self.active_trailing_stops.values()).index(trailing_stop)
                    ],
                    'reason': 'trailing_stop_loss',
                    'stop_price': trailing_stop['current_stop_price'],
                    'current_price': current_price,
                    'timestamp': time.time()
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error checking stop loss trigger: {e}")
            return None
    
    async def close_trailing_stop(self, position_id: str) -> bool:
        """Close trailing stop for a position."""
        try:
            if position_id in self.active_trailing_stops:
                del self.active_trailing_stops[position_id]
                print(f"✅ Trailing stop closed for {position_id}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error closing trailing stop for {position_id}: {e}")
            return False
    
    async def get_active_trailing_stops(self) -> Dict[str, Any]:
        """Get all active trailing stops."""
        return self.active_trailing_stops.copy()
    
    async def cleanup_expired_stops(self, max_age_hours: int = 24):
        """Clean up expired trailing stops."""
        try:
            current_time = time.time()
            expired_positions = []
            
            for position_id, trailing_stop in self.active_trailing_stops.items():
                age_hours = (current_time - trailing_stop['last_update']) / 3600
                if age_hours > max_age_hours:
                    expired_positions.append(position_id)
            
            for position_id in expired_positions:
                await self.close_trailing_stop(position_id)
                
            if expired_positions:
                print(f"🧹 Cleaned up {len(expired_positions)} expired trailing stops")
                
        except Exception as e:
            print(f"❌ Error cleaning up expired stops: {e}")
    
    async def get_trailing_stop_summary(self) -> Dict[str, Any]:
        """Get summary of all trailing stops."""
        try:
            active_count = len(self.active_trailing_stops)
            activated_count = sum(1 for ts in self.active_trailing_stops.values() if ts['is_activated'])
            
            return {
                'total_active': active_count,
                'activated': activated_count,
                'pending_activation': active_count - activated_count,
                'timestamp': time.time()
            }
        except Exception as e:
            print(f"❌ Error getting trailing stop summary: {e}")
            return {}
