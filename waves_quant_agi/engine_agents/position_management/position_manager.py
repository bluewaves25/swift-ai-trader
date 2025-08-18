#!/usr/bin/env python3
"""
Position Manager - Advanced Position Management and Portfolio Optimization
"""

import asyncio
import time
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class PositionStatus(Enum):
    """Position status enumeration."""
    OPEN = "open"
    PARTIALLY_CLOSED = "partially_closed"
    CLOSED = "closed"
    PENDING = "pending"
    CANCELLED = "cancelled"

class PositionType(Enum):
    """Position type enumeration."""
    LONG = "long"
    SHORT = "short"
    HEDGE = "hedge"

@dataclass
class PositionMetrics:
    """Position performance metrics."""
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    max_profit: float = 0.0
    max_loss: float = 0.0
    drawdown: float = 0.0
    time_open: float = 0.0
    risk_adjusted_return: float = 0.0

@dataclass
class PortfolioAllocation:
    """Portfolio allocation configuration."""
    strategy_type: str
    target_allocation: float  # Target percentage of portfolio
    max_allocation: float     # Maximum percentage of portfolio
    min_allocation: float     # Minimum percentage of portfolio
    rebalance_threshold: float  # Threshold to trigger rebalancing

class PositionManager:
    """Advanced position management and portfolio optimization system."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        self.positions = {}
        self.portfolio_metrics = {
            "total_value": 0.0,
            "total_pnl": 0.0,
            "unrealized_pnl": 0.0,
            "realized_pnl": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "volatility": 0.0,
            "last_update": time.time()
        }
        self.portfolio_allocation = self._initialize_portfolio_allocation()
        self.position_history = []
        self.rebalancing_queue = []
        
    def _initialize_portfolio_allocation(self) -> Dict[str, PortfolioAllocation]:
        """Initialize portfolio allocation configuration."""
        allocations = {
            "arbitrage": PortfolioAllocation(
                strategy_type="arbitrage",
                target_allocation=0.25,  # 25% target
                max_allocation=0.35,     # 35% maximum
                min_allocation=0.15,     # 15% minimum
                rebalance_threshold=0.05  # 5% threshold
            ),
            "trend_following": PortfolioAllocation(
                strategy_type="trend_following",
                target_allocation=0.20,  # 20% target
                max_allocation=0.30,     # 30% maximum
                min_allocation=0.10,     # 10% minimum
                rebalance_threshold=0.05  # 5% threshold
            ),
            "market_making": PortfolioAllocation(
                strategy_type="market_making",
                target_allocation=0.15,  # 15% target
                max_allocation=0.25,     # 25% maximum
                min_allocation=0.05,     # 5% minimum
                rebalance_threshold=0.05  # 5% threshold
            ),
            "htf": PortfolioAllocation(
                strategy_type="htf",
                target_allocation=0.15,  # 15% target
                max_allocation=0.25,     # 25% maximum
                min_allocation=0.05,     # 5% minimum
                rebalance_threshold=0.05  # 5% threshold
            ),
            "news_driven": PortfolioAllocation(
                strategy_type="news_driven",
                target_allocation=0.15,  # 15% target
                max_allocation=0.25,     # 25% maximum
                min_allocation=0.05,     # 5% minimum
                rebalance_threshold=0.05  # 5% threshold
            ),
            "statistical_arbitrage": PortfolioAllocation(
                strategy_type="statistical_arbitrage",
                target_allocation=0.10,  # 10% target
                max_allocation=0.20,     # 20% maximum
                min_allocation=0.05,     # 5% minimum
                rebalance_threshold=0.05  # 5% threshold
            )
        }
        return allocations
        
    async def add_position(self, position_data: Dict[str, Any]) -> str:
        """Add a new position to the position manager."""
        try:
            position_id = position_data.get("position_id", str(uuid.uuid4()))
            
            # Create position object
            position = {
                "position_id": position_id,
                "symbol": position_data.get("symbol", ""),
                "strategy_type": position_data.get("strategy_type", "unknown"),
                "strategy_name": position_data.get("strategy_name", "unknown"),
                "action": position_data.get("action", ""),
                "position_type": PositionType.LONG if position_data.get("action") == "BUY" else PositionType.SHORT,
                "volume": position_data.get("volume", 0),
                "entry_price": position_data.get("entry_price", 0),
                "stop_loss": position_data.get("stop_loss", 0),
                "take_profit": position_data.get("take_profit", 0),
                "status": PositionStatus.OPEN,
                "created_at": time.time(),
                "last_update": time.time(),
                "metrics": PositionMetrics(),
                "partial_exits": [],
                "risk_management": {
                    "trailing_stop_active": False,
                    "partial_profit_active": False,
                    "dynamic_sltp_active": False
                }
            }
            
            self.positions[position_id] = position
            
            # Add to position history
            self.position_history.append({
                "action": "opened",
                "position_id": position_id,
                "timestamp": time.time(),
                "data": position.copy()
            })
            
            if self.logger:
                self.logger.info(f"🎯 Position {position_id} added: {position['symbol']} {position['action']} "
                               f"({position['strategy_name']}) - {position['volume']} lots @ {position['entry_price']}")
            
            return position_id
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error adding position: {e}")
            return ""
    
    async def update_position(self, position_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing position."""
        try:
            if position_id not in self.positions:
                if self.logger:
                    self.logger.warning(f"⚠️ Position {position_id} not found for update")
                return False
            
            position = self.positions[position_id]
            
            # Update position data
            for key, value in update_data.items():
                if key in position and key not in ["position_id", "created_at"]:
                    position[key] = value
            
            position["last_update"] = time.time()
            
            # Update metrics
            await self._update_position_metrics(position_id)
            
            if self.logger:
                self.logger.info(f"🎯 Position {position_id} updated: {update_data}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error updating position {position_id}: {e}")
            return False
    
    async def close_position(self, position_id: str, close_data: Dict[str, Any]) -> bool:
        """Close a position."""
        try:
            if position_id not in self.positions:
                if self.logger:
                    self.logger.warning(f"⚠️ Position {position_id} not found for closing")
                return False
            
            position = self.positions[position_id]
            
            # Update position with close data
            close_price = close_data.get("close_price", 0)
            close_volume = close_data.get("close_volume", position["volume"])
            close_reason = close_data.get("close_reason", "manual")
            
            # Calculate realized PnL
            if position["action"] == "BUY":
                realized_pnl = (close_price - position["entry_price"]) * close_volume
            else:
                realized_pnl = (position["entry_price"] - close_price) * close_volume
            
            # Update position
            position.update({
                "status": PositionStatus.CLOSED,
                "close_price": close_price,
                "close_volume": close_volume,
                "close_reason": close_reason,
                "close_time": time.time(),
                "last_update": time.time()
            })
            
            # Update metrics
            position["metrics"].realized_pnl += realized_pnl
            
            # Add to position history
            self.position_history.append({
                "action": "closed",
                "position_id": position_id,
                "timestamp": time.time(),
                "data": {
                    "close_price": close_price,
                    "close_volume": close_volume,
                    "close_reason": close_reason,
                    "realized_pnl": realized_pnl
                }
            })
            
            if self.logger:
                self.logger.info(f"🎯 Position {position_id} closed: {position['symbol']} @ {close_price} "
                               f"({close_reason}) - PnL: {realized_pnl:.2f}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error closing position {position_id}: {e}")
            return False
    
    async def partial_exit(self, position_id: str, exit_data: Dict[str, Any]) -> bool:
        """Execute a partial exit from a position."""
        try:
            if position_id not in self.positions:
                if self.logger:
                    self.logger.warning(f"⚠️ Position {position_id} not found for partial exit")
                return False
            
            position = self.positions[position_id]
            
            # Validate partial exit
            exit_volume = exit_data.get("exit_volume", 0)
            if exit_volume >= position["volume"]:
                if self.logger:
                    self.logger.warning(f"⚠️ Partial exit volume {exit_volume} >= total volume {position['volume']}")
                return False
            
            # Execute partial exit
            exit_price = exit_data.get("exit_price", 0)
            exit_reason = exit_data.get("exit_reason", "partial_profit")
            
            # Calculate realized PnL
            if position["action"] == "BUY":
                realized_pnl = (exit_price - position["entry_price"]) * exit_volume
            else:
                realized_pnl = (position["entry_price"] - exit_price) * exit_volume
            
            # Update position
            position["volume"] -= exit_volume
            position["status"] = PositionStatus.PARTIALLY_CLOSED
            position["last_update"] = time.time()
            
            # Add partial exit record
            partial_exit = {
                "exit_time": time.time(),
                "exit_price": exit_price,
                "exit_volume": exit_volume,
                "exit_reason": exit_reason,
                "realized_pnl": realized_pnl
            }
            position["partial_exits"].append(partial_exit)
            
            # Update metrics
            position["metrics"].realized_pnl += realized_pnl
            
            # Add to position history
            self.position_history.append({
                "action": "partial_exit",
                "position_id": position_id,
                "timestamp": time.time(),
                "data": partial_exit
            })
            
            if self.logger:
                self.logger.info(f"🎯 Partial exit for {position_id}: {exit_volume} lots @ {exit_price} "
                               f"({exit_reason}) - PnL: {realized_pnl:.2f}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error executing partial exit for {position_id}: {e}")
            return False
    
    async def _update_position_metrics(self, position_id: str):
        """Update metrics for a specific position."""
        try:
            if position_id not in self.positions:
                return
            
            position = self.positions[position_id]
            current_price = position.get("current_price", position["entry_price"])
            
            # Calculate unrealized PnL
            if position["action"] == "BUY":
                unrealized_pnl = (current_price - position["entry_price"]) * position["volume"]
            else:
                unrealized_pnl = (position["entry_price"] - current_price) * position["volume"]
            
            # Update metrics
            metrics = position["metrics"]
            metrics.unrealized_pnl = unrealized_pnl
            metrics.max_profit = max(metrics.max_profit, unrealized_pnl)
            metrics.max_loss = min(metrics.max_loss, unrealized_pnl)
            metrics.drawdown = min(metrics.drawdown, unrealized_pnl)
            metrics.time_open = time.time() - position["created_at"]
            
            # Calculate risk-adjusted return (simplified)
            if position["stop_loss"] and position["take_profit"]:
                risk = abs(position["entry_price"] - position["stop_loss"])
                if risk > 0:
                    metrics.risk_adjusted_return = unrealized_pnl / risk
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error updating position metrics for {position_id}: {e}")
    
    async def update_portfolio_metrics(self, current_prices: Dict[str, float]):
        """Update portfolio-wide metrics."""
        try:
            total_value = 0.0
            total_unrealized_pnl = 0.0
            total_realized_pnl = 0.0
            
            # Update all positions with current prices
            for position_id, position in self.positions.items():
                if position["status"] == PositionStatus.OPEN:
                    symbol = position["symbol"]
                    current_price = current_prices.get(symbol, position["entry_price"])
                    
                    # Update position with current price
                    position["current_price"] = current_price
                    await self._update_position_metrics(position_id)
                    
                    # Calculate position value
                    position_value = position["volume"] * current_price
                    total_value += position_value
                    total_unrealized_pnl += position["metrics"].unrealized_pnl
                    total_realized_pnl += position["metrics"].realized_pnl
            
            # Update portfolio metrics
            self.portfolio_metrics.update({
                "total_value": total_value,
                "unrealized_pnl": total_unrealized_pnl,
                "realized_pnl": total_realized_pnl,
                "total_pnl": total_unrealized_pnl + total_realized_pnl,
                "last_update": time.time()
            })
            
            # Update max drawdown
            total_pnl = self.portfolio_metrics["total_pnl"]
            if total_pnl < self.portfolio_metrics["max_drawdown"]:
                self.portfolio_metrics["max_drawdown"] = total_pnl
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error updating portfolio metrics: {e}")
    
    async def check_portfolio_rebalancing(self) -> List[Dict[str, Any]]:
        """Check if portfolio rebalancing is needed."""
        try:
            rebalancing_needed = []
            
            # Calculate current allocations
            current_allocations = {}
            total_value = self.portfolio_metrics["total_value"]
            
            if total_value > 0:
                for position in self.positions.values():
                    if position["status"] == PositionStatus.OPEN:
                        strategy_type = position["strategy_type"]
                        position_value = position["volume"] * position.get("current_price", position["entry_price"])
                        current_allocations[strategy_type] = current_allocations.get(strategy_type, 0.0) + position_value
                
                # Check each strategy allocation
                for strategy_type, current_allocation in current_allocations.items():
                    current_percentage = current_allocation / total_value
                    target_allocation = self.portfolio_allocation.get(strategy_type)
                    
                    if target_allocation:
                        # Check if rebalancing is needed
                        deviation = abs(current_percentage - target_allocation.target_allocation)
                        if deviation > target_allocation.rebalance_threshold:
                            rebalancing_needed.append({
                                "strategy_type": strategy_type,
                                "current_allocation": current_percentage,
                                "target_allocation": target_allocation.target_allocation,
                                "deviation": deviation,
                                "action": "reduce" if current_percentage > target_allocation.target_allocation else "increase",
                                "priority": "high" if deviation > target_allocation.rebalance_threshold * 2 else "medium"
                            })
            
            return rebalancing_needed
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error checking portfolio rebalancing: {e}")
            return []
    
    async def get_position_summary(self, position_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed summary of a specific position."""
        try:
            if position_id not in self.positions:
                return None
            
            position = self.positions[position_id]
            return {
                "position_id": position_id,
                "symbol": position["symbol"],
                "strategy_type": position["strategy_type"],
                "strategy_name": position["strategy_name"],
                "status": position["status"].value,
                "action": position["action"],
                "volume": position["volume"],
                "entry_price": position["entry_price"],
                "current_price": position.get("current_price", position["entry_price"]),
                "stop_loss": position["stop_loss"],
                "take_profit": position["take_profit"],
                "metrics": {
                    "unrealized_pnl": position["metrics"].unrealized_pnl,
                    "realized_pnl": position["metrics"].realized_pnl,
                    "max_profit": position["metrics"].max_profit,
                    "max_loss": position["metrics"].max_loss,
                    "drawdown": position["metrics"].drawdown,
                    "time_open": position["metrics"].time_open,
                    "risk_adjusted_return": position["metrics"].risk_adjusted_return
                },
                "partial_exits": position["partial_exits"],
                "risk_management": position["risk_management"],
                "created_at": position["created_at"],
                "last_update": position["last_update"]
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting position summary for {position_id}: {e}")
            return None
    
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary."""
        try:
            # Calculate strategy performance
            strategy_performance = {}
            for position in self.positions.values():
                if position["status"] == PositionStatus.OPEN:
                    strategy_type = position["strategy_type"]
                    if strategy_type not in strategy_performance:
                        strategy_performance[strategy_type] = {
                            "positions": 0,
                            "total_value": 0.0,
                            "total_pnl": 0.0,
                            "avg_risk_adjusted_return": 0.0
                        }
                    
                    strategy_performance[strategy_type]["positions"] += 1
                    position_value = position["volume"] * position.get("current_price", position["entry_price"])
                    strategy_performance[strategy_type]["total_value"] += position_value
                    strategy_performance[strategy_type]["total_pnl"] += position["metrics"].unrealized_pnl
                    strategy_performance[strategy_type]["avg_risk_adjusted_return"] += position["metrics"].risk_adjusted_return
            
            # Calculate averages
            for strategy_data in strategy_performance.values():
                if strategy_data["positions"] > 0:
                    strategy_data["avg_risk_adjusted_return"] /= strategy_data["positions"]
            
            return {
                "portfolio_metrics": self.portfolio_metrics,
                "strategy_performance": strategy_performance,
                "active_positions": len([p for p in self.positions.values() if p["status"] == PositionStatus.OPEN]),
                "total_positions": len(self.positions),
                "rebalancing_needed": await self.check_portfolio_rebalancing(),
                "timestamp": time.time()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting portfolio summary: {e}")
            return {"error": str(e), "timestamp": time.time()}
    
    async def cleanup(self):
        """Cleanup position manager resources."""
        try:
            self.positions.clear()
            self.position_history.clear()
            self.rebalancing_queue.clear()
            
            if self.logger:
                self.logger.info("✅ Position manager cleaned up")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error cleaning up position manager: {e}")
