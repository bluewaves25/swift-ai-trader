#!/usr/bin/env python3
"""
Execution Optimizer - Trade Execution Optimization
Provides intelligent trade execution optimization and cost management.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from ...shared_utils import get_shared_logger

class ExecutionOptimizer:
    """Optimizes trade execution for best price and minimal market impact."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("execution", "execution_optimizer")
        
        # Optimization configuration
        self.optimization_enabled = config.get("execution_optimization_enabled", True)
        self.max_slippage = config.get("max_slippage", 0.001)  # 0.1%
        self.min_spread = config.get("min_spread", 0.0001)     # 0.01%
        self.execution_timeout = config.get("execution_timeout", 30)  # seconds
        
        # Optimization state
        self.optimization_history: List[Dict[str, Any]] = []
        self.current_optimizations: Dict[str, Any] = {}
        
        self.logger.info("Execution Optimizer initialized")
    
    async def optimize_execution(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize execution parameters for a trade order."""
        try:
            if not self.optimization_enabled:
                return order_data
            
            symbol = order_data.get("symbol", "unknown")
            order_type = order_data.get("order_type", "market")
            quantity = order_data.get("quantity", 0.0)
            
            # Get market conditions
            market_conditions = await self._get_market_conditions(symbol)
            
            # Calculate optimal execution parameters
            optimal_params = await self._calculate_optimal_params(
                order_data, market_conditions
            )
            
            # Store optimization result
            optimization_result = {
                "order_id": order_data.get("order_id", "unknown"),
                "symbol": symbol,
                "original_params": order_data,
                "optimized_params": optimal_params,
                "market_conditions": market_conditions,
                "optimization_timestamp": time.time()
            }
            
            self.optimization_history.append(optimization_result)
            self.current_optimizations[order_data.get("order_id", "unknown")] = optimization_result
            
            # Keep only last 1000 optimizations
            if len(self.optimization_history) > 1000:
                self.optimization_history.pop(0)
            
            self.logger.info(f"Execution optimized for {symbol} order")
            return optimal_params
            
        except Exception as e:
            self.logger.error(f"Error optimizing execution: {e}")
            return order_data
    
    async def _get_market_conditions(self, symbol: str) -> Dict[str, Any]:
        """Get current market conditions for optimization."""
        try:
            # This would typically fetch real-time market data
            # For now, return default conditions
            return {
                "spread": 0.0002,  # 0.02%
                "volatility": 0.15,  # 15%
                "liquidity": "high",
                "market_impact": "low",
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.error(f"Error getting market conditions: {e}")
            return {}
    
    async def _calculate_optimal_params(self, order_data: Dict[str, Any], 
                                      market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal execution parameters."""
        try:
            optimized_order = order_data.copy()
            
            # Adjust order type based on market conditions
            if market_conditions.get("volatility", 0) > 0.2:  # High volatility
                if order_data.get("order_type") == "market":
                    optimized_order["order_type"] = "limit"
                    optimized_order["limit_price"] = self._calculate_limit_price(
                        order_data, market_conditions
                    )
            
            # Adjust quantity for large orders to minimize market impact
            quantity = order_data.get("quantity", 0.0)
            if quantity > 1000000:  # Large order
                optimized_order["quantity"] = self._split_large_order(quantity, market_conditions)
                optimized_order["execution_strategy"] = "iceberg"
            
            # Set optimal time in force
            if market_conditions.get("liquidity") == "low":
                optimized_order["time_in_force"] = "day"
            else:
                optimized_order["time_in_force"] = "ioc"  # Immediate or cancel
            
            # Add execution constraints
            optimized_order["max_slippage"] = self.max_slippage
            optimized_order["execution_timeout"] = self.execution_timeout
            
            return optimized_order
            
        except Exception as e:
            self.logger.error(f"Error calculating optimal params: {e}")
            return order_data
    
    def _calculate_limit_price(self, order_data: Dict[str, Any], 
                              market_conditions: Dict[str, Any]) -> float:
        """Calculate optimal limit price."""
        try:
            current_price = order_data.get("current_price", 0.0)
            spread = market_conditions.get("spread", 0.0002)
            
            if order_data.get("side") == "buy":
                # For buy orders, set limit slightly above current price
                return current_price * (1 + spread * 0.5)
            else:
                # For sell orders, set limit slightly below current price
                return current_price * (1 - spread * 0.5)
                
        except Exception as e:
            self.logger.error(f"Error calculating limit price: {e}")
            return order_data.get("current_price", 0.0)
    
    def _split_large_order(self, quantity: float, market_conditions: Dict[str, Any]) -> List[float]:
        """Split large orders to minimize market impact."""
        try:
            if quantity <= 1000000:
                return [quantity]
            
            # Split into smaller chunks based on liquidity
            liquidity_factor = 1.0 if market_conditions.get("liquidity") == "high" else 0.5
            chunk_size = int(quantity * 0.1 * liquidity_factor)
            
            chunks = []
            remaining = quantity
            
            while remaining > 0:
                chunk = min(chunk_size, remaining)
                chunks.append(chunk)
                remaining -= chunk
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error splitting large order: {e}")
            return [quantity]
    
    async def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization performance."""
        try:
            if not self.optimization_history:
                return {"total_optimizations": 0}
            
            total_optimizations = len(self.optimization_history)
            recent_optimizations = self.optimization_history[-100:] if total_optimizations > 100 else self.optimization_history
            
            # Calculate optimization metrics
            market_impact_reduced = sum(
                1 for opt in recent_optimizations 
                if opt.get("market_conditions", {}).get("market_impact") == "low"
            )
            
            return {
                "total_optimizations": total_optimizations,
                "recent_optimizations": len(recent_optimizations),
                "market_impact_reduced": market_impact_reduced,
                "optimization_rate": market_impact_reduced / len(recent_optimizations) if recent_optimizations else 0.0,
                "last_optimization": self.optimization_history[-1].get("optimization_timestamp") if self.optimization_history else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting optimization summary: {e}")
            return {}
    
    async def get_optimization_history(self, symbol: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get optimization history."""
        try:
            if symbol:
                filtered_history = [
                    opt for opt in self.optimization_history 
                    if opt.get("symbol") == symbol
                ]
            else:
                filtered_history = self.optimization_history
            
            return filtered_history[-limit:] if limit > 0 else filtered_history
            
        except Exception as e:
            self.logger.error(f"Error getting optimization history: {e}")
            return []
    
    def enable_optimization(self, enabled: bool = True):
        """Enable or disable execution optimization."""
        try:
            self.optimization_enabled = enabled
            self.logger.info(f"Execution optimization {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            self.logger.error(f"Error setting optimization state: {e}")
    
    def set_max_slippage(self, max_slippage: float):
        """Set maximum allowed slippage."""
        try:
            self.max_slippage = max_slippage
            self.logger.info(f"Maximum slippage set to: {max_slippage:.6f}")
        except Exception as e:
            self.logger.error(f"Error setting max slippage: {e}")
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            self.optimization_history.clear()
            self.current_optimizations.clear()
            self.logger.info("Execution Optimizer cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
