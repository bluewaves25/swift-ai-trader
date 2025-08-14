#!/usr/bin/env python3
"""
Cost Calculator - SIMPLIFIED CORE MODULE
Handles real-time cost calculation and tracking
SIMPLE: ~150 lines focused on cost calculation only
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from ...shared_utils import get_shared_logger

class CostCalculator:
    """
    Simplified cost calculation engine.
    Focuses on essential cost tracking and calculation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("fees_monitor", "cost_calculator")
        
        # Cost tracking state
        self.cost_state = {
            "total_fees": 0.0,
            "total_slippage": 0.0,
            "total_trades": 0,
            "average_cost_per_trade": 0.0
        }
        
        # Cost thresholds
        self.thresholds = {
            "high_fee_ratio": 0.002,      # 0.2%
            "high_slippage": 0.001,       # 0.1%
            "cost_alert_threshold": 0.005  # 0.5%
        }
    
    async def calculate_realtime_costs(self) -> Dict[str, Any]:
        """Calculate real-time trading costs."""
        try:
            # Simulate real-time cost calculation
            await asyncio.sleep(0.001)  # 1ms calculation time
            
            current_time = time.time()
            
            # Basic cost metrics
            result = {
                "timestamp": current_time,
                "fees": self._calculate_current_fees(),
                "slippage": self._calculate_current_slippage(),
                "total_cost": 0.0,
                "cost_ratio": 0.0,
                "efficiency_score": 1.0,
                "high_cost_strategies": []
            }
            
            # Calculate total cost and ratios
            result["total_cost"] = result["fees"] + result["slippage"]
            
            # Cost efficiency score (1.0 = perfect, 0.0 = terrible)
            if result["total_cost"] > 0:
                result["cost_ratio"] = result["total_cost"] / max(self._get_trade_value(), 1.0)
                result["efficiency_score"] = max(0.0, 1.0 - (result["cost_ratio"] * 100))
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Error calculating realtime costs: {e}")
            return {
                "timestamp": time.time(),
                "error": str(e),
                "fees": 0.0,
                "slippage": 0.0,
                "total_cost": 0.0
            }
    
    async def calculate_trade_costs(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate costs for a specific trade."""
        try:
            trade_value = trade_data.get("value", trade_data.get("quantity", 0) * trade_data.get("price", 0))
            
            # Calculate different cost components
            trading_fees = self._calculate_trading_fees(trade_data)
            slippage_cost = self._calculate_slippage_cost(trade_data)
            opportunity_cost = self._calculate_opportunity_cost(trade_data)
            
            total_cost = trading_fees + slippage_cost + opportunity_cost
            cost_ratio = total_cost / max(trade_value, 1.0)
            
            # Determine if costs are high
            is_high_cost = cost_ratio > self.thresholds["high_fee_ratio"]
            
            # Calculate potential savings (simplified)
            potential_savings = self._calculate_potential_savings(trade_data, total_cost)
            
            result = {
                "trade_id": trade_data.get("order_id", "unknown"),
                "trading_fees": trading_fees,
                "slippage_cost": slippage_cost,
                "opportunity_cost": opportunity_cost,
                "total_cost": total_cost,
                "cost_ratio": cost_ratio,
                "trade_value": trade_value,
                "is_high_cost": is_high_cost,
                "savings": potential_savings,
                "timestamp": time.time()
            }
            
            # Update internal state
            self._update_cost_state(result)
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Error calculating trade costs: {e}")
            return {
                "error": str(e),
                "total_cost": 0.0,
                "timestamp": time.time()
            }
    
    async def track_order_costs(self, order_data: Dict[str, Any]):
        """Track costs for an order (real-time)."""
        try:
            # Simple order cost tracking
            order_fees = order_data.get("fees", 0.0)
            order_slippage = order_data.get("slippage", 0.0)
            
            # Update running totals
            self.cost_state["total_fees"] += order_fees
            self.cost_state["total_slippage"] += order_slippage
            
        except Exception as e:
            self.logger.warning(f"Error tracking order costs: {e}")
    
    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cost metrics."""
        try:
            total_trades = max(self.cost_state["total_trades"], 1)
            total_cost = self.cost_state["total_fees"] + self.cost_state["total_slippage"]
            
            return {
                "total_fees": self.cost_state["total_fees"],
                "total_slippage": self.cost_state["total_slippage"],
                "total_cost": total_cost,
                "total_trades": self.cost_state["total_trades"],
                "average_cost_per_trade": total_cost / total_trades,
                "average_fee_per_trade": self.cost_state["total_fees"] / total_trades,
                "average_slippage_per_trade": self.cost_state["total_slippage"] / total_trades,
                "cost_efficiency": self._calculate_cost_efficiency(),
                "optimization_savings": self._calculate_optimization_savings(),
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting comprehensive metrics: {e}")
            return {"error": str(e), "timestamp": time.time()}
    
    # ============= PRIVATE CALCULATION METHODS =============
    
    def _calculate_current_fees(self) -> float:
        """Calculate current fees (simplified)."""
        # Simulate current trading fees
        base_fee_rate = 0.001  # 0.1%
        return base_fee_rate * 10000  # Assume $10k trading volume
    
    def _calculate_current_slippage(self) -> float:
        """Calculate current slippage (simplified)."""
        # Simulate current slippage
        base_slippage_rate = 0.0005  # 0.05%
        return base_slippage_rate * 10000  # Assume $10k trading volume
    
    def _get_trade_value(self) -> float:
        """Get current trade value (simplified)."""
        return 10000.0  # Assume $10k average trade value
    
    def _calculate_trading_fees(self, trade_data: Dict[str, Any]) -> float:
        """Calculate trading fees for a trade."""
        trade_value = trade_data.get("value", 1000.0)
        fee_rate = trade_data.get("fee_rate", 0.001)  # 0.1% default
        return trade_value * fee_rate
    
    def _calculate_slippage_cost(self, trade_data: Dict[str, Any]) -> float:
        """Calculate slippage cost for a trade."""
        expected_price = trade_data.get("expected_price", trade_data.get("price", 0.0))
        actual_price = trade_data.get("price", expected_price)
        quantity = trade_data.get("quantity", 0.0)
        
        slippage = abs(actual_price - expected_price)
        return slippage * quantity
    
    def _calculate_opportunity_cost(self, trade_data: Dict[str, Any]) -> float:
        """Calculate opportunity cost for a trade."""
        # Simplified opportunity cost calculation
        trade_value = trade_data.get("value", 1000.0)
        delay_seconds = trade_data.get("execution_delay", 0.0)
        
        # Assume 0.01% opportunity cost per second of delay
        return trade_value * 0.0001 * delay_seconds
    
    def _calculate_potential_savings(self, trade_data: Dict[str, Any], total_cost: float) -> float:
        """Calculate potential savings for a trade."""
        # Simplified savings calculation
        # Assume 10% of costs could be saved with optimization
        return total_cost * 0.1
    
    def _update_cost_state(self, trade_result: Dict[str, Any]):
        """Update internal cost state."""
        try:
            self.cost_state["total_fees"] += trade_result.get("trading_fees", 0.0)
            self.cost_state["total_slippage"] += trade_result.get("slippage_cost", 0.0)
            self.cost_state["total_trades"] += 1
            
            # Update average cost per trade
            total_cost = self.cost_state["total_fees"] + self.cost_state["total_slippage"]
            self.cost_state["average_cost_per_trade"] = total_cost / max(self.cost_state["total_trades"], 1)
            
        except Exception as e:
            self.logger.warning(f"Error updating cost state: {e}")
    
    def _calculate_cost_efficiency(self) -> float:
        """Calculate overall cost efficiency."""
        try:
            total_cost = self.cost_state["total_fees"] + self.cost_state["total_slippage"]
            total_trades = max(self.cost_state["total_trades"], 1)
            
            # Efficiency score based on average cost per trade
            average_cost = total_cost / total_trades
            
            # Normalize to 0-1 scale (assuming $10 average cost is "normal")
            efficiency = max(0.0, 1.0 - (average_cost / 10.0))
            return min(1.0, efficiency)
            
        except Exception as e:
            self.logger.warning(f"Error calculating cost efficiency: {e}")
            return 0.5  # Default to neutral efficiency
    
    def _calculate_optimization_savings(self) -> float:
        """Calculate total optimization savings."""
        # This would track actual savings from optimizations
        # For now, return a simple estimate
        return self.cost_state["total_fees"] * 0.05  # Assume 5% savings
    
    # ============= UTILITY METHODS =============
    
    def reset_cost_state(self):
        """Reset cost tracking state."""
        self.cost_state = {
            "total_fees": 0.0,
            "total_slippage": 0.0,
            "total_trades": 0,
            "average_cost_per_trade": 0.0
        }
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get simple cost summary."""
        return {
            **self.cost_state,
            "efficiency_score": self._calculate_cost_efficiency(),
            "optimization_savings": self._calculate_optimization_savings()
        }
