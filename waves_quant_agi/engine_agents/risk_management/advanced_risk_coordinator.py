#!/usr/bin/env python3
"""
Advanced Risk Management Coordinator - Unified Risk Management System
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .trailing_stop_manager import TrailingStopManager
from .partial_profit_manager import PartialProfitManager
from .dynamic_sltp_manager import DynamicSLTPManager

@dataclass
class RiskManagementConfig:
    """Configuration for the advanced risk management system."""
    enabled_features: List[str]  # List of enabled features
    update_frequency: float      # Update frequency in seconds
    max_positions_per_strategy: int  # Maximum positions per strategy type
    risk_allocation_per_strategy: float  # Risk allocation per strategy type

class AdvancedRiskCoordinator:
    """Coordinates all advanced risk management features."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        self.risk_config = self._initialize_risk_config()
        
        # Initialize risk management components
        self.trailing_stop_manager = TrailingStopManager(config, logger)
        self.partial_profit_manager = PartialProfitManager(config, logger)
        self.dynamic_sltp_manager = DynamicSLTPManager(config, logger)
        
        # Risk management state
        self.active_positions = {}
        self.risk_metrics = {
            "total_risk_exposure": 0.0,
            "strategy_risk_allocation": {},
            "daily_pnl": 0.0,
            "weekly_pnl": 0.0,
            "max_drawdown": 0.0,
            "risk_adjustments_made": 0,
            "last_update": time.time()
        }
        
        # Performance tracking
        self.performance_metrics = {
            "trailing_stops_activated": 0,
            "partial_exits_executed": 0,
            "dynamic_adjustments_made": 0,
            "risk_events_processed": 0
        }
        
    def _initialize_risk_config(self) -> RiskManagementConfig:
        """Initialize risk management configuration."""
        return RiskManagementConfig(
            enabled_features=[
                "trailing_stops",
                "partial_profit_taking", 
                "dynamic_sltp_adjustments",
                "position_sizing",
                "correlation_analysis"
            ],
            update_frequency=0.1,  # 100ms updates
            max_positions_per_strategy=5,
            risk_allocation_per_strategy=0.15  # 15% risk per strategy type
        )
    
    async def add_position_to_risk_management(self, position_data: Dict[str, Any]) -> bool:
        """Add a new position to the risk management system."""
        try:
            position_id = position_data.get("position_id")
            symbol = position_data.get("symbol")
            strategy_type = position_data.get("strategy_type", "unknown")
            volume = position_data.get("volume", 0)
            entry_price = position_data.get("entry_price", 0)
            
            if not all([position_id, symbol, strategy_type, volume, entry_price]):
                if self.logger:
                    self.logger.warning(f"⚠️ Incomplete position data for risk management: {position_data}")
                return False
            
            # Check risk allocation limits
            if not await self._check_risk_allocation(strategy_type, volume, entry_price):
                if self.logger:
                    self.logger.warning(f"⚠️ Risk allocation limit exceeded for {strategy_type} strategy")
                return False
            
            # Initialize position tracking
            position_tracking = {
                "position_id": position_id,
                "symbol": symbol,
                "strategy_type": strategy_type,
                "volume": volume,
                "entry_price": entry_price,
                "current_pnl": 0.0,
                "max_pnl": 0.0,
                "risk_management_active": True,
                "created_at": time.time(),
                "last_update": time.time()
            }
            
            self.active_positions[position_id] = position_tracking
            
            # Add to individual risk managers
            if "trailing_stops" in self.risk_config.enabled_features:
                await self.trailing_stop_manager.add_trailing_stop(position_data)
            
            if "partial_profit_taking" in self.risk_config.enabled_features:
                await self.partial_profit_manager.add_partial_exit_tracking(position_data)
            
            if "dynamic_sltp_adjustments" in self.risk_config.enabled_features:
                await self.dynamic_sltp_manager.add_dynamic_adjustment_tracking(position_data)
            
            # Update risk metrics
            await self._update_risk_metrics()
            
            if self.logger:
                self.logger.info(f"🎯 Position {position_id} added to risk management: "
                               f"{symbol} ({strategy_type}) - {volume} lots @ {entry_price}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error adding position to risk management: {e}")
            return False
    
    async def _check_risk_allocation(self, strategy_type: str, volume: float, entry_price: float) -> bool:
        """Check if adding this position would exceed risk allocation limits."""
        try:
            # Calculate current risk for this strategy type
            current_risk = self.risk_metrics["strategy_risk_allocation"].get(strategy_type, 0.0)
            
            # Calculate new position risk
            position_risk = volume * entry_price
            
            # Check if adding this position would exceed limits
            max_risk_allocation = self.risk_config.risk_allocation_per_strategy
            if current_risk + position_risk > max_risk_allocation:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error checking risk allocation: {e}")
            return False
    
    async def update_risk_management(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update all risk management systems with current market data."""
        try:
            update_results = {
                "trailing_stop_adjustments": [],
                "partial_exit_triggers": [],
                "dynamic_sltp_adjustments": [],
                "risk_events": [],
                "timestamp": time.time()
            }
            
            # Update trailing stops
            if "trailing_stops" in self.risk_config.enabled_features:
                trailing_adjustments = await self.trailing_stop_manager.update_trailing_stops(
                    self._extract_prices(market_data)
                )
                update_results["trailing_stop_adjustments"] = trailing_adjustments
                self.performance_metrics["trailing_stops_activated"] += len(trailing_adjustments)
            
            # Check partial exits
            if "partial_profit_taking" in self.risk_config.enabled_features:
                partial_exit_triggers = await self.partial_profit_manager.check_partial_exits(
                    self._extract_prices(market_data)
                )
                update_results["partial_exit_triggers"] = partial_exit_triggers
            
            # Check dynamic SL/TP adjustments
            if "dynamic_sltp_adjustments" in self.risk_config.enabled_features:
                dynamic_adjustments = await self.dynamic_sltp_manager.check_dynamic_adjustments(market_data)
                update_results["dynamic_sltp_adjustments"] = dynamic_adjustments
                self.performance_metrics["dynamic_adjustments_made"] += len(dynamic_adjustments)
            
            # Process risk events
            risk_events = await self._process_risk_events(update_results)
            update_results["risk_events"] = risk_events
            self.performance_metrics["risk_events_processed"] += len(risk_events)
            
            # Update risk metrics
            await self._update_risk_metrics()
            
            if self.logger:
                self.logger.info(f"🎯 Risk management update completed: "
                               f"{len(trailing_adjustments)} trailing adjustments, "
                               f"{len(partial_exit_triggers)} partial exits, "
                               f"{len(dynamic_adjustments)} dynamic adjustments")
            
            return update_results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error updating risk management: {e}")
            return {"error": str(e), "timestamp": time.time()}
    
    def _extract_prices(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract current prices from market data."""
        try:
            prices = {}
            for symbol, data in market_data.items():
                if isinstance(data, dict) and "current_price" in data:
                    prices[symbol] = data["current_price"]
                elif isinstance(data, (int, float)):
                    prices[symbol] = float(data)
            return prices
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error extracting prices: {e}")
            return {}
    
    async def _process_risk_events(self, update_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and categorize risk events."""
        try:
            risk_events = []
            
            # Process trailing stop adjustments
            for adjustment in update_results.get("trailing_stop_adjustments", []):
                risk_events.append({
                    "type": "trailing_stop_adjustment",
                    "severity": "medium",
                    "description": f"Trailing stop adjusted for {adjustment['symbol']}",
                    "data": adjustment,
                    "timestamp": time.time()
                })
            
            # Process partial exit triggers
            for trigger in update_results.get("partial_exit_triggers", []):
                risk_events.append({
                    "type": "partial_exit_trigger",
                    "severity": "low",
                    "description": f"Partial exit triggered for {trigger['symbol']} at {trigger['profit_target']:.3f} profit",
                    "data": trigger,
                    "timestamp": time.time()
                })
            
            # Process dynamic SL/TP adjustments
            for adjustment in update_results.get("dynamic_sltp_adjustments", []):
                risk_events.append({
                    "type": "dynamic_sltp_adjustment",
                    "severity": "medium",
                    "description": f"Dynamic SL/TP adjustment for {adjustment['symbol']}",
                    "data": adjustment,
                    "timestamp": time.time()
                })
            
            return risk_events
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error processing risk events: {e}")
            return []
    
    async def execute_risk_action(self, action_type: str, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific risk management action."""
        try:
            if action_type == "partial_exit":
                return await self.partial_profit_manager.execute_partial_exit(action_data)
            elif action_type == "trailing_stop_adjustment":
                # This would integrate with the execution agent to modify existing orders
                return {"status": "trailing_stop_adjustment_processed", "data": action_data}
            elif action_type == "dynamic_sltp_adjustment":
                # This would integrate with the execution agent to modify existing orders
                return {"status": "dynamic_sltp_adjustment_processed", "data": action_data}
            else:
                return {"error": f"Unknown action type: {action_type}"}
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error executing risk action: {e}")
            return {"error": str(e)}
    
    async def remove_position_from_risk_management(self, position_id: str) -> bool:
        """Remove a position from the risk management system."""
        try:
            if position_id not in self.active_positions:
                return False
            
            position_data = self.active_positions[position_id]
            symbol = position_data["symbol"]
            strategy_type = position_data["strategy_type"]
            
            # Remove from individual risk managers
            await self.trailing_stop_manager.remove_trailing_stop(position_id)
            await self.partial_profit_manager.remove_partial_exit_tracking(position_id)
            await self.dynamic_sltp_manager.remove_dynamic_adjustment_tracking(position_id)
            
            # Remove from active positions
            del self.active_positions[position_id]
            
            # Update risk metrics
            await self._update_risk_metrics()
            
            if self.logger:
                self.logger.info(f"🎯 Position {position_id} removed from risk management: "
                               f"{symbol} ({strategy_type})")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error removing position from risk management: {e}")
            return False
    
    async def _update_risk_metrics(self):
        """Update risk management metrics."""
        try:
            # Calculate total risk exposure
            total_exposure = 0.0
            strategy_allocation = {}
            
            for position_id, position in self.active_positions.items():
                position_risk = position["volume"] * position["entry_price"]
                total_exposure += position_risk
                
                strategy_type = position["strategy_type"]
                strategy_allocation[strategy_type] = strategy_allocation.get(strategy_type, 0.0) + position_risk
            
            self.risk_metrics["total_risk_exposure"] = total_exposure
            self.risk_metrics["strategy_risk_allocation"] = strategy_allocation
            self.risk_metrics["last_update"] = time.time()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error updating risk metrics: {e}")
    
    async def get_risk_management_status(self) -> Dict[str, Any]:
        """Get comprehensive risk management status."""
        try:
            return {
                "risk_metrics": self.risk_metrics,
                "performance_metrics": self.performance_metrics,
                "active_positions": len(self.active_positions),
                "trailing_stops": await self.trailing_stop_manager.get_all_trailing_stops(),
                "partial_exits": await self.partial_profit_manager.get_all_partial_exits(),
                "dynamic_adjustments": await self.dynamic_sltp_manager.get_all_dynamic_adjustments(),
                "timestamp": time.time()
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting risk management status: {e}")
            return {"error": str(e), "timestamp": time.time()}
    
    async def cleanup(self):
        """Cleanup all risk management resources."""
        try:
            await self.trailing_stop_manager.cleanup()
            await self.partial_profit_manager.cleanup()
            await self.dynamic_sltp_manager.cleanup()
            
            self.active_positions.clear()
            
            if self.logger:
                self.logger.info("✅ Advanced risk coordinator cleaned up")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error cleaning up advanced risk coordinator: {e}")
