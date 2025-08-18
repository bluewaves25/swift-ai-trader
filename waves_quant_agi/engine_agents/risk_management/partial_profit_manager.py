#!/usr/bin/env python3
"""
Partial Profit Taking Manager - Advanced Risk Management for AI Trading Engine
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class PartialExitLevel:
    """Configuration for a partial profit taking level."""
    profit_target: float  # Profit percentage to trigger exit
    exit_percentage: float  # Percentage of position to close
    stop_loss_adjustment: float  # New stop loss after partial exit

@dataclass
class PartialProfitConfig:
    """Configuration for partial profit taking behavior."""
    strategy_type: str
    partial_exits_enabled: bool
    exit_levels: List[PartialExitLevel]
    min_position_size: float  # Minimum position size to keep
    trailing_stop_after_exit: bool  # Enable trailing stop after partial exits

class PartialProfitManager:
    """Manages partial profit taking for active positions."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        self.active_partial_exits = {}
        self.partial_configs = self._initialize_partial_configs()
        
    def _initialize_partial_configs(self) -> Dict[str, PartialProfitConfig]:
        """Initialize partial profit taking configurations for different strategy types."""
        configs = {
            "arbitrage": PartialProfitConfig(
                strategy_type="arbitrage",
                partial_exits_enabled=True,
                exit_levels=[
                    PartialExitLevel(0.005, 0.25, 0.002),   # 25% at 0.5% profit, SL at 0.2%
                    PartialExitLevel(0.008, 0.25, 0.003),   # 25% at 0.8% profit, SL at 0.3%
                    PartialExitLevel(0.012, 0.25, 0.005),   # 25% at 1.2% profit, SL at 0.5%
                    PartialExitLevel(0.015, 0.25, 0.008),   # 25% at 1.5% profit, SL at 0.8%
                ],
                min_position_size=0.01,
                trailing_stop_after_exit=True
            ),
            "trend_following": PartialProfitConfig(
                strategy_type="trend_following",
                partial_exits_enabled=True,
                exit_levels=[
                    PartialExitLevel(0.03, 0.20, 0.015),   # 20% at 3% profit, SL at 1.5%
                    PartialExitLevel(0.05, 0.20, 0.025),   # 20% at 5% profit, SL at 2.5%
                    PartialExitLevel(0.08, 0.20, 0.04),    # 20% at 8% profit, SL at 4%
                    PartialExitLevel(0.12, 0.20, 0.06),    # 20% at 12% profit, SL at 6%
                    PartialExitLevel(0.18, 0.20, 0.10),    # 20% at 18% profit, SL at 10%
                ],
                min_position_size=0.02,
                trailing_stop_after_exit=True
            ),
            "market_making": PartialProfitConfig(
                strategy_type="market_making",
                partial_exits_enabled=True,
                exit_levels=[
                    PartialExitLevel(0.015, 0.25, 0.008),  # 25% at 1.5% profit, SL at 0.8%
                    PartialExitLevel(0.025, 0.25, 0.015),  # 25% at 2.5% profit, SL at 1.5%
                    PartialExitLevel(0.035, 0.25, 0.025),  # 25% at 3.5% profit, SL at 2.5%
                    PartialExitLevel(0.045, 0.25, 0.035),  # 25% at 4.5% profit, SL at 3.5%
                ],
                min_position_size=0.015,
                trailing_stop_after_exit=True
            ),
            "htf": PartialProfitConfig(
                strategy_type="htf",
                partial_exits_enabled=True,
                exit_levels=[
                    PartialExitLevel(0.04, 0.15, 0.02),    # 15% at 4% profit, SL at 2%
                    PartialExitLevel(0.07, 0.15, 0.035),   # 15% at 7% profit, SL at 3.5%
                    PartialExitLevel(0.12, 0.15, 0.06),    # 15% at 12% profit, SL at 6%
                    PartialExitLevel(0.18, 0.15, 0.10),    # 15% at 18% profit, SL at 10%
                    PartialExitLevel(0.25, 0.15, 0.15),    # 15% at 25% profit, SL at 15%
                    PartialExitLevel(0.35, 0.15, 0.25),    # 15% at 35% profit, SL at 25%
                    PartialExitLevel(0.50, 0.10, 0.35),    # 10% at 50% profit, SL at 35%
                ],
                min_position_size=0.03,
                trailing_stop_after_exit=True
            ),
            "news_driven": PartialProfitConfig(
                strategy_type="news_driven",
                partial_exits_enabled=True,
                exit_levels=[
                    PartialExitLevel(0.02, 0.20, 0.012),   # 20% at 2% profit, SL at 1.2%
                    PartialExitLevel(0.035, 0.20, 0.02),   # 20% at 3.5% profit, SL at 2%
                    PartialExitLevel(0.05, 0.20, 0.03),    # 20% at 5% profit, SL at 3%
                    PartialExitLevel(0.08, 0.20, 0.05),    # 20% at 8% profit, SL at 5%
                    PartialExitLevel(0.12, 0.20, 0.08),    # 20% at 12% profit, SL at 8%
                ],
                min_position_size=0.02,
                trailing_stop_after_exit=True
            ),
            "statistical_arbitrage": PartialProfitConfig(
                strategy_type="statistical_arbitrage",
                partial_exits_enabled=True,
                exit_levels=[
                    PartialExitLevel(0.025, 0.20, 0.015),  # 20% at 2.5% profit, SL at 1.5%
                    PartialExitLevel(0.04, 0.20, 0.025),   # 20% at 4% profit, SL at 2.5%
                    PartialExitLevel(0.06, 0.20, 0.04),    # 20% at 6% profit, SL at 4%
                    PartialExitLevel(0.09, 0.20, 0.06),    # 20% at 9% profit, SL at 6%
                    PartialExitLevel(0.15, 0.20, 0.10),    # 20% at 15% profit, SL at 10%
                ],
                min_position_size=0.02,
                trailing_stop_after_exit=True
            )
        }
        return configs
    
    async def add_partial_exit_tracking(self, position_data: Dict[str, Any]) -> bool:
        """Add a new position to partial profit taking tracking."""
        try:
            position_id = position_data.get("position_id")
            symbol = position_data.get("symbol")
            strategy_type = position_data.get("strategy_type", "unknown")
            entry_price = position_data.get("entry_price", 0)
            current_volume = position_data.get("volume", 0)
            action = position_data.get("action", "BUY")
            
            if not all([position_id, symbol, entry_price, current_volume]):
                if self.logger:
                    self.logger.warning(f"⚠️ Incomplete position data for partial exit: {position_data}")
                return False
            
            # Get partial exit configuration for strategy type
            partial_config = self.partial_configs.get(strategy_type)
            if not partial_config or not partial_config.partial_exits_enabled:
                if self.logger:
                    self.logger.info(f"ℹ️ Partial exits disabled for {strategy_type} strategy")
                return False
            
            # Initialize partial exit tracking
            partial_exit_data = {
                "position_id": position_id,
                "symbol": symbol,
                "strategy_type": strategy_type,
                "entry_price": entry_price,
                "original_volume": current_volume,
                "current_volume": current_volume,
                "action": action,
                "partial_config": partial_config,
                "exits_completed": [],
                "next_exit_level": 0,  # Index of next exit level
                "total_profit_taken": 0.0,
                "created_at": time.time(),
                "last_exit_time": None
            }
            
            self.active_partial_exits[position_id] = partial_exit_data
            
            if self.logger:
                exit_levels = len(partial_config.exit_levels)
                self.logger.info(f"🎯 Partial exit tracking added for {symbol} ({strategy_type}): "
                               f"{exit_levels} exit levels configured, "
                               f"Starting volume: {current_volume}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error adding partial exit tracking: {e}")
            return False
    
    async def check_partial_exits(self, current_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check if any partial exits should be triggered."""
        try:
            exits_triggered = []
            
            for position_id, exit_data in self.active_partial_exits.items():
                symbol = exit_data["symbol"]
                current_price = current_prices.get(symbol)
                
                if not current_price:
                    continue
                
                # Check if we should trigger a partial exit
                exit_trigger = await self._should_trigger_partial_exit(exit_data, current_price)
                if exit_trigger:
                    exits_triggered.append(exit_trigger)
            
            return exits_triggered
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error checking partial exits: {e}")
            return []
    
    async def _should_trigger_partial_exit(self, exit_data: Dict[str, Any], current_price: float) -> Optional[Dict[str, Any]]:
        """Check if a partial exit should be triggered."""
        try:
            action = exit_data["action"]
            entry_price = exit_data["entry_price"]
            current_volume = exit_data["current_volume"]
            partial_config = exit_data["partial_config"]
            next_level_index = exit_data["next_exit_level"]
            
            # Check if we have more exit levels
            if next_level_index >= len(partial_config.exit_levels):
                return None
            
            # Get next exit level
            exit_level = partial_config.exit_levels[next_level_index]
            profit_target = exit_level.profit_target
            
            # Calculate current profit percentage
            if action.upper() == "BUY":
                current_profit_pct = (current_price - entry_price) / entry_price
            else:  # SELL
                current_profit_pct = (entry_price - current_price) / entry_price
            
            # Check if profit target reached
            if current_profit_pct >= profit_target:
                # Calculate exit volume
                exit_volume = current_volume * exit_level.exit_percentage
                
                # Ensure we don't exit below minimum position size
                remaining_volume = current_volume - exit_volume
                if remaining_volume < partial_config.min_position_size:
                    exit_volume = current_volume - partial_config.min_position_size
                
                if exit_volume > 0:
                    # Calculate new stop loss
                    new_stop_loss = None
                    if action.upper() == "BUY":
                        new_stop_loss = entry_price * (1 + exit_level.stop_loss_adjustment)
                    else:
                        new_stop_loss = entry_price * (1 - exit_level.stop_loss_adjustment)
                    
                    # Create exit trigger
                    exit_trigger = {
                        "position_id": exit_data["position_id"],
                        "symbol": exit_data["symbol"],
                        "strategy_type": exit_data["strategy_type"],
                        "exit_level": next_level_index,
                        "profit_target": profit_target,
                        "current_profit": current_profit_pct,
                        "exit_volume": exit_volume,
                        "exit_percentage": exit_level.exit_percentage,
                        "new_stop_loss": new_stop_loss,
                        "current_price": current_price,
                        "action": action,
                        "timestamp": time.time()
                    }
                    
                    # Update exit data
                    exit_data["next_exit_level"] = next_level_index + 1
                    exit_data["current_volume"] = remaining_volume
                    exit_data["exits_completed"].append(exit_trigger)
                    exit_data["last_exit_time"] = time.time()
                    
                    if self.logger:
                        self.logger.info(f"🎯 Partial exit triggered for {symbol}: "
                                       f"Level {next_level_index + 1} at {profit_target:.3f} profit, "
                                       f"Exit {exit_volume:.3f} lots, "
                                       f"New SL: {new_stop_loss:.5f}")
                    
                    return exit_trigger
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error checking partial exit trigger: {e}")
            return None
    
    async def execute_partial_exit(self, exit_trigger: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a partial exit based on the trigger."""
        try:
            # This method would integrate with the execution agent
            # For now, we'll return the execution plan
            
            execution_plan = {
                "type": "partial_exit",
                "position_id": exit_trigger["position_id"],
                "symbol": exit_trigger["symbol"],
                "action": "SELL" if exit_trigger["action"] == "BUY" else "BUY",  # Close opposite
                "volume": exit_trigger["exit_volume"],
                "price": exit_trigger["current_price"],
                "stop_loss_adjustment": exit_trigger["new_stop_loss"],
                "strategy_type": exit_trigger["strategy_type"],
                "exit_level": exit_trigger["exit_level"],
                "timestamp": time.time()
            }
            
            if self.logger:
                self.logger.info(f"📋 Partial exit execution plan created: {execution_plan}")
            
            return execution_plan
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error executing partial exit: {e}")
            return {"error": str(e)}
    
    async def remove_partial_exit_tracking(self, position_id: str) -> bool:
        """Remove a position from partial exit tracking."""
        try:
            if position_id in self.active_partial_exits:
                exit_data = self.active_partial_exits[position_id]
                symbol = exit_data["symbol"]
                strategy_type = exit_data["strategy_type"]
                exits_completed = len(exit_data["exits_completed"])
                
                del self.active_partial_exits[position_id]
                
                if self.logger:
                    self.logger.info(f"🎯 Partial exit tracking removed for {symbol} ({strategy_type}): "
                                   f"{exits_completed} exits completed")
                
                return True
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error removing partial exit tracking: {e}")
            return False
    
    async def get_partial_exit_status(self, position_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of partial exit tracking."""
        try:
            return self.active_partial_exits.get(position_id)
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting partial exit status: {e}")
            return None
    
    async def get_all_partial_exits(self) -> Dict[str, Any]:
        """Get all active partial exit tracking."""
        try:
            return {
                "active_count": len(self.active_partial_exits),
                "partial_exits": self.active_partial_exits,
                "timestamp": time.time()
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting all partial exits: {e}")
            return {"active_count": 0, "partial_exits": {}, "timestamp": time.time()}
    
    async def cleanup(self):
        """Cleanup partial profit manager resources."""
        try:
            self.active_partial_exits.clear()
            if self.logger:
                self.logger.info("✅ Partial profit manager cleaned up")
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error cleaning up partial profit manager: {e}")
