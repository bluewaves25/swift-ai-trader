#!/usr/bin/env python3
"""
Trailing Stop Manager - Advanced Risk Management for AI Trading Engine
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class TrailingStopConfig:
    """Configuration for trailing stop behavior."""
    strategy_type: str
    trailing_enabled: bool
    trailing_distance: float  # Distance from current price
    trailing_step: float      # Minimum step size for adjustments
    activation_threshold: float  # Profit level to activate trailing
    max_trailing_distance: float  # Maximum trailing distance

class TrailingStopManager:
    """Manages trailing stops for active positions."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        self.active_trailing_stops = {}
        self.trailing_configs = self._initialize_trailing_configs()
        
    def _initialize_trailing_configs(self) -> Dict[str, TrailingStopConfig]:
        """Initialize trailing stop configurations for different strategy types."""
        configs = {
            "arbitrage": TrailingStopConfig(
                strategy_type="arbitrage",
                trailing_enabled=True,
                trailing_distance=0.002,  # 0.2% for HFT
                trailing_step=0.0005,     # 0.05% minimum step
                activation_threshold=0.005,  # Activate at 0.5% profit
                max_trailing_distance=0.01   # Max 1% trailing
            ),
            "trend_following": TrailingStopConfig(
                strategy_type="trend_following",
                trailing_enabled=True,
                trailing_distance=0.015,  # 1.5% for trend strategies
                trailing_step=0.005,      # 0.5% minimum step
                activation_threshold=0.02,  # Activate at 2% profit
                max_trailing_distance=0.05   # Max 5% trailing
            ),
            "market_making": TrailingStopConfig(
                strategy_type="market_making",
                trailing_enabled=True,
                trailing_distance=0.008,  # 0.8% for market making
                trailing_step=0.002,      # 0.2% minimum step
                activation_threshold=0.01,  # Activate at 1% profit
                max_trailing_distance=0.025  # Max 2.5% trailing
            ),
            "htf": TrailingStopConfig(
                strategy_type="htf",
                trailing_enabled=True,
                trailing_distance=0.025,  # 2.5% for HTF strategies
                trailing_step=0.01,       # 1% minimum step
                activation_threshold=0.03,  # Activate at 3% profit
                max_trailing_distance=0.08   # Max 8% trailing
            ),
            "news_driven": TrailingStopConfig(
                strategy_type="news_driven",
                trailing_enabled=True,
                trailing_distance=0.012,  # 1.2% for news strategies
                trailing_step=0.005,      # 0.5% minimum step
                activation_threshold=0.015,  # Activate at 1.5% profit
                max_trailing_distance=0.04   # Max 4% trailing
            ),
            "statistical_arbitrage": TrailingStopConfig(
                strategy_type="statistical_arbitrage",
                trailing_enabled=True,
                trailing_distance=0.01,   # 1% for stat arb
                trailing_step=0.003,      # 0.3% minimum step
                activation_threshold=0.018,  # Activate at 1.8% profit
                max_trailing_distance=0.035  # Max 3.5% trailing
            )
        }
        return configs
    
    async def add_trailing_stop(self, position_data: Dict[str, Any]) -> bool:
        """Add a new position to trailing stop management."""
        try:
            position_id = position_data.get("position_id")
            symbol = position_data.get("symbol")
            strategy_type = position_data.get("strategy_type", "unknown")
            entry_price = position_data.get("entry_price", 0)
            stop_loss = position_data.get("stop_loss", 0)
            take_profit = position_data.get("take_profit", 0)
            action = position_data.get("action", "BUY")
            
            if not all([position_id, symbol, entry_price, stop_loss, take_profit]):
                if self.logger:
                    self.logger.warning(f"⚠️ Incomplete position data for trailing stop: {position_data}")
                return False
            
            # Get trailing configuration for strategy type
            trailing_config = self.trailing_configs.get(strategy_type)
            if not trailing_config or not trailing_config.trailing_enabled:
                if self.logger:
                    self.logger.info(f"ℹ️ Trailing stop disabled for {strategy_type} strategy")
                return False
            
            # Calculate activation price
            if action.upper() == "BUY":
                activation_price = entry_price * (1 + trailing_config.activation_threshold)
            else:  # SELL
                activation_price = entry_price * (1 - trailing_config.activation_threshold)
            
            trailing_stop_data = {
                "position_id": position_id,
                "symbol": symbol,
                "strategy_type": strategy_type,
                "entry_price": entry_price,
                "current_stop_loss": stop_loss,
                "original_stop_loss": stop_loss,
                "take_profit": take_profit,
                "action": action,
                "trailing_config": trailing_config,
                "activation_price": activation_price,
                "is_active": False,  # Will activate when price reaches threshold
                "last_adjustment": time.time(),
                "adjustments_count": 0,
                "max_profit_reached": entry_price,
                "created_at": time.time()
            }
            
            self.active_trailing_stops[position_id] = trailing_stop_data
            
            if self.logger:
                self.logger.info(f"🎯 Trailing stop added for {symbol} ({strategy_type}): "
                               f"Activation at {activation_price:.5f}, "
                               f"Trailing distance: {trailing_config.trailing_distance:.3f}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error adding trailing stop: {e}")
            return False
    
    async def update_trailing_stops(self, current_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """Update all active trailing stops with current market prices."""
        try:
            adjustments_made = []
            
            for position_id, trailing_data in self.active_trailing_stops.items():
                symbol = trailing_data["symbol"]
                current_price = current_prices.get(symbol)
                
                if not current_price:
                    continue
                
                # Check if trailing stop should activate
                if not trailing_data["is_active"]:
                    if await self._should_activate_trailing(trailing_data, current_price):
                        trailing_data["is_active"] = True
                        if self.logger:
                            self.logger.info(f"🎯 Trailing stop ACTIVATED for {symbol} at {current_price:.5f}")
                
                # Update trailing stop if active
                if trailing_data["is_active"]:
                    adjustment = await self._adjust_trailing_stop(trailing_data, current_price)
                    if adjustment:
                        adjustments_made.append(adjustment)
            
            return adjustments_made
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error updating trailing stops: {e}")
            return []
    
    async def _should_activate_trailing(self, trailing_data: Dict[str, Any], current_price: float) -> bool:
        """Check if trailing stop should activate based on profit threshold."""
        try:
            action = trailing_data["action"]
            activation_price = trailing_data["activation_price"]
            
            if action.upper() == "BUY":
                return current_price >= activation_price
            else:  # SELL
                return current_price <= activation_price
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error checking trailing activation: {e}")
            return False
    
    async def _adjust_trailing_stop(self, trailing_data: Dict[str, Any], current_price: float) -> Optional[Dict[str, Any]]:
        """Adjust trailing stop based on current price and strategy configuration."""
        try:
            action = trailing_data["action"]
            config = trailing_data["trailing_config"]
            current_stop = trailing_data["current_stop_loss"]
            
            # Calculate new stop loss
            new_stop_loss = None
            
            if action.upper() == "BUY":
                # For BUY positions, trail below current price
                potential_stop = current_price * (1 - config.trailing_distance)
                
                # Only move stop up (more profitable)
                if potential_stop > current_stop + (current_price * config.trailing_step):
                    new_stop_loss = potential_stop
                    
            else:  # SELL
                # For SELL positions, trail above current price
                potential_stop = current_price * (1 + config.trailing_distance)
                
                # Only move stop down (more profitable)
                if potential_stop < current_stop - (current_price * config.trailing_step):
                    new_stop_loss = potential_stop
            
            # Apply adjustment if beneficial
            if new_stop_loss:
                # Ensure we don't trail too far
                if action.upper() == "BUY":
                    max_stop = trailing_data["entry_price"] * (1 - config.max_trailing_distance)
                    new_stop_loss = max(new_stop_loss, max_stop)
                else:
                    min_stop = trailing_data["entry_price"] * (1 + config.max_trailing_distance)
                    new_stop_loss = min(new_stop_loss, min_stop)
                
                # Update trailing data
                old_stop = trailing_data["current_stop_loss"]
                trailing_data["current_stop_loss"] = new_stop_loss
                trailing_data["last_adjustment"] = time.time()
                trailing_data["adjustments_count"] += 1
                
                # Update max profit reached
                if action.upper() == "BUY":
                    trailing_data["max_profit_reached"] = max(trailing_data["max_profit_reached"], current_price)
                else:
                    trailing_data["max_profit_reached"] = min(trailing_data["max_profit_reached"], current_price)
                
                adjustment = {
                    "position_id": trailing_data["position_id"],
                    "symbol": trailing_data["symbol"],
                    "strategy_type": trailing_data["strategy_type"],
                    "old_stop_loss": old_stop,
                    "new_stop_loss": new_stop_loss,
                    "current_price": current_price,
                    "adjustment_time": time.time(),
                    "adjustments_count": trailing_data["adjustments_count"]
                }
                
                if self.logger:
                    self.logger.info(f"🎯 Trailing stop adjusted for {trailing_data['symbol']}: "
                                   f"{old_stop:.5f} → {new_stop_loss:.5f} "
                                   f"({action} @ {current_price:.5f})")
                
                return adjustment
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error adjusting trailing stop: {e}")
            return None
    
    async def remove_trailing_stop(self, position_id: str) -> bool:
        """Remove a position from trailing stop management."""
        try:
            if position_id in self.active_trailing_stops:
                trailing_data = self.active_trailing_stops[position_id]
                symbol = trailing_data["symbol"]
                strategy_type = trailing_data["strategy_type"]
                adjustments = trailing_data["adjustments_count"]
                
                del self.active_trailing_stops[position_id]
                
                if self.logger:
                    self.logger.info(f"🎯 Trailing stop removed for {symbol} ({strategy_type}): "
                                   f"{adjustments} adjustments made")
                
                return True
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error removing trailing stop: {e}")
            return False
    
    async def get_trailing_stop_status(self, position_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a trailing stop."""
        try:
            return self.active_trailing_stops.get(position_id)
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting trailing stop status: {e}")
            return None
    
    async def get_all_trailing_stops(self) -> Dict[str, Any]:
        """Get all active trailing stops."""
        try:
            return {
                "active_count": len(self.active_trailing_stops),
                "trailing_stops": self.active_trailing_stops,
                "timestamp": time.time()
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting all trailing stops: {e}")
            return {"active_count": 0, "trailing_stops": {}, "timestamp": time.time()}
    
    async def cleanup(self):
        """Cleanup trailing stop manager resources."""
        try:
            self.active_trailing_stops.clear()
            if self.logger:
                self.logger.info("✅ Trailing stop manager cleaned up")
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error cleaning up trailing stop manager: {e}")
