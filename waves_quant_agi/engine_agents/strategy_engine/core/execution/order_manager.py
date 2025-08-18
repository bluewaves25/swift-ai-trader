#!/usr/bin/env python3
"""
Order Manager - Core Strategy Order Management Component
Manages trading orders and their execution, integrating with consolidated trading functionality.
Focuses purely on strategy-specific order management, delegating risk management to the risk management agent.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque

# Import consolidated trading functionality
from ..pipeline.execution_pipeline import TradingExecutionPipeline
from ..memory.trading_context import TradingContext

@dataclass
class OrderRequest:
    """A trading order request."""
    order_id: str
    strategy_id: str
    symbol: str
    action: str  # buy, sell, buy_limit, sell_limit, stop_loss, take_profit
    amount: float
    price: float
    order_type: str  # market, limit, stop, stop_limit
    status: str = "pending"
    created_at: float = None
    priority: int = 5
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class OrderResult:
    """Result of order execution."""
    result_id: str
    order_id: str
    strategy_id: str
    symbol: str
    action: str
    amount: float
    executed_price: float
    execution_time: float
    execution_duration: float
    timestamp: float
    success: bool
    execution_notes: str = ""

class OrderManager:
    """Manages trading orders and their execution.
    
    Focuses purely on strategy-specific order management:
    - Order creation and validation
    - Order execution coordination
    - Order status tracking
    - Order performance monitoring
    
    Risk management is delegated to the risk management agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize consolidated trading components
        self.trading_execution_pipeline = TradingExecutionPipeline(config)
        self.trading_context = TradingContext(max_history=1000)  # Fixed: pass integer instead of config
        
        # Order management state
        self.order_queue: deque = deque(maxlen=1000)
        self.active_orders: Dict[str, OrderRequest] = {}
        self.order_results: Dict[str, List[OrderResult]] = {}
        self.order_history: deque = deque(maxlen=10000)
        
        # Order management settings (strategy-specific only)
        self.order_settings = {
            "max_concurrent_orders": 50,
            "order_timeout": 300,  # 5 minutes
            "max_order_size": 1000000,  # $1M max order size
            "order_priority_levels": ["high", "medium", "low"],
            "strategy_parameters": {
                "default_slippage_tolerance": 0.001,  # 0.1%
                "execution_timeout": 60,
                "retry_attempts": 3
            }
        }
        
        # Order management statistics
        self.order_stats = {
            "total_orders": 0,
            "successful_orders": 0,
            "failed_orders": 0,
            "pending_orders": 0,
            "total_volume": 0.0,
            "average_execution_time": 0.0
        }
        
    async def initialize(self):
        """Initialize the order manager."""
        try:
            # Initialize trading components
            await self.trading_execution_pipeline.initialize()
            await self.trading_context.initialize()
            
            # Load order settings
            await self._load_order_settings()
            
            print("✅ Order Manager initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Order Manager: {e}")
            raise
    
    async def _load_order_settings(self):
        """Load order management settings from configuration."""
        try:
            order_config = self.config.get("strategy_engine", {}).get("order_management", {})
            self.order_settings.update(order_config)
        except Exception as e:
            print(f"❌ Error loading order settings: {e}")

    async def submit_order(self, strategy_id: str, symbol: str, action: str, 
                          amount: float, price: float, order_type: str = "market") -> str:
        """Submit a new trading order.
        
        This focuses purely on order creation and validation, not risk management.
        """
        try:
            # Generate order ID
            order_id = f"order_{strategy_id}_{symbol}_{int(time.time())}"
            
            # Create order request
            order = OrderRequest(
                order_id=order_id,
                strategy_id=strategy_id,
                symbol=symbol,
                action=action,
                amount=amount,
                price=price,
                order_type=order_type
            )
            
            # Validate order (strategy-specific validation only)
            if not await self._validate_order(order):
                raise ValueError("Order validation failed")
            
            # Add to order queue
            self.order_queue.append(order)
            
            # Store order in trading context
            await self.trading_context.store_signal({
                "type": "order_submission",
                "order_id": order_id,
                "strategy_id": strategy_id,
                "order_data": {
                    "symbol": symbol,
                    "action": action,
                    "amount": amount,
                    "price": price,
                    "order_type": order_type
                },
                "timestamp": int(time.time())
            })
            
            # Update statistics
            self.order_stats["total_orders"] += 1
            self.order_stats["pending_orders"] += 1
            self.order_stats["total_volume"] += amount * price
            
            print(f"✅ Order submitted: {order_id}")
            return order_id
            
        except Exception as e:
            print(f"❌ Error submitting order: {e}")
            raise

    async def _validate_order(self, order: OrderRequest) -> bool:
        """Validate order parameters (strategy-specific validation only).
        
        This does NOT include risk management validation.
        """
        try:
            # Basic parameter validation
            if not order.symbol or not order.action or order.amount <= 0:
                return False
            
            # Action validation
            valid_actions = ["buy", "sell", "buy_limit", "sell_limit", "stop_loss", "take_profit"]
            if order.action not in valid_actions:
                return False
            
            # Order type validation
            valid_types = ["market", "limit", "stop", "stop_limit"]
            if order.order_type not in valid_types:
                return False
            
            # Price validation for limit orders
            if order.order_type in ["limit", "stop_limit"] and order.price <= 0:
                return False
            
            # Amount validation
            if order.amount > self.order_settings["max_order_size"]:
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating order: {e}")
            return False

    async def process_order_queue(self) -> List[OrderResult]:
        """Process the order queue."""
        try:
            results = []
            
            while self.order_queue and len(self.active_orders) < self.order_settings["max_concurrent_orders"]:
                order = self.order_queue.popleft()
                result = await self._execute_order(order)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing order queue: {e}")
            return []

    async def _execute_order(self, order: OrderRequest) -> Optional[OrderResult]:
        """Execute a single order."""
        start_time = time.time()
        
        try:
            # Mark as active
            self.active_orders[order.order_id] = order
            order.status = "executing"
            
            # Calculate execution priority
            priority = self._calculate_execution_priority(order)
            
            # Execute order through trading execution pipeline
            execution_result = await self.trading_execution_pipeline.send_to_execution({
                "order_id": order.order_id,
                "strategy_id": order.strategy_id,
                "symbol": order.symbol,
                "action": order.action,
                "amount": order.amount,
                "price": order.price,
                "order_type": order.order_type,
                "priority": priority
            })
            
            # Process execution result
            if execution_result.get("success", False):
                # Order executed successfully
                result = OrderResult(
                    result_id=f"result_{order.order_id}",
                    order_id=order.order_id,
                    strategy_id=order.strategy_id,
                    symbol=order.symbol,
                    action=order.action,
                    amount=order.amount,
                    executed_price=execution_result.get("executed_price", order.price),
                    execution_time=execution_result.get("execution_time", time.time()),
                    execution_duration=time.time() - start_time,
                    timestamp=time.time(),
                    success=True,
                    execution_notes=execution_result.get("notes", "Order executed successfully")
                )
                
                # Update statistics
                self.order_stats["successful_orders"] += 1
                self.order_stats["pending_orders"] -= 1
                
                print(f"✅ Order executed: {order.order_id}")
                
            else:
                # Order execution failed
                result = OrderResult(
                    result_id=f"failed_{order.order_id}",
                    order_id=order.order_id,
                    strategy_id=order.strategy_id,
                    symbol=order.symbol,
                    action=order.action,
                    amount=order.amount,
                    executed_price=0.0,
                    execution_time=time.time(),
                    execution_duration=time.time() - start_time,
                    timestamp=time.time(),
                    success=False,
                    execution_notes=execution_result.get("error", "Order execution failed")
                )
                
                # Update statistics
                self.order_stats["failed_orders"] += 1
                self.order_stats["pending_orders"] -= 1
                
                print(f"❌ Order execution failed: {order.order_id}")
            
            # Store result
            if order.strategy_id not in self.order_results:
                self.order_results[order.strategy_id] = []
            self.order_results[order.strategy_id].append(result)
            
            # Store result in trading context
            await self.trading_context.store_signal({
                "type": "order_execution_result",
                "order_id": order.order_id,
                "strategy_id": order.strategy_id,
                "result_data": {
                    "success": result.success,
                    "executed_price": result.executed_price,
                    "execution_duration": result.execution_duration,
                    "notes": result.execution_notes
                },
                "timestamp": int(time.time())
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Error executing order: {e}")
            
            # Return failed result
            result = OrderResult(
                result_id=f"error_{order.order_id}",
                order_id=order.order_id,
                strategy_id=order.strategy_id,
                symbol=order.symbol,
                action=order.action,
                amount=order.amount,
                executed_price=0.0,
                execution_time=time.time(),
                execution_duration=time.time() - start_time,
                timestamp=time.time(),
                success=False,
                execution_notes=f"Execution error: {str(e)}"
            )
            
            # Update statistics
            self.order_stats["failed_orders"] += 1
            self.order_stats["pending_orders"] -= 1
            
            return result
            
        finally:
            # Remove from active orders
            self.active_orders.pop(order.order_id, None)

    def _calculate_execution_priority(self, order: OrderRequest) -> int:
        """Calculate execution priority for an order."""
        try:
            # Base priority
            priority = 5
            
            # Order type priority
            if order.order_type == "market":
                priority += 3  # Market orders get highest priority
            elif order.order_type == "stop":
                priority += 2  # Stop orders get high priority
            elif order.order_type == "limit":
                priority += 1  # Limit orders get medium priority
            
            # Action priority
            if order.action in ["stop_loss", "take_profit"]:
                priority += 2  # Risk management orders get high priority
            
            # Amount priority (larger orders get higher priority)
            if order.amount > 100000:  # $100K+
                priority += 1
            elif order.amount > 1000000:  # $1M+
                priority += 2
            
            return max(1, min(10, priority))  # Clamp between 1 and 10
            
        except Exception as e:
            print(f"❌ Error calculating execution priority: {e}")
            return 5

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""
        try:
            # Find order in queue
            for i, order in enumerate(self.order_queue):
                if order.order_id == order_id:
                    # Remove from queue
                    self.order_queue.pop(i)
                    
                    # Update statistics
                    self.order_stats["pending_orders"] -= 1
                    
                    # Store cancellation in trading context
                    await self.trading_context.store_signal({
                        "type": "order_cancellation",
                        "order_id": order_id,
                        "strategy_id": order.strategy_id,
                        "cancellation_data": {
                            "reason": "user_requested",
                            "timestamp": int(time.time())
                        },
                        "timestamp": int(time.time())
                    })
                    
                    print(f"✅ Order cancelled: {order_id}")
                    return True
            
            # Check if order is active
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
                order.status = "cancelled"
                
                # Update statistics
                self.order_stats["pending_orders"] -= 1
                
                print(f"✅ Active order cancelled: {order_id}")
                return True
            
            print(f"⚠️ Order not found: {order_id}")
            return False
            
        except Exception as e:
            print(f"❌ Error cancelling order: {e}")
            return False

    async def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific order."""
        try:
            # Check active orders
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
                return {
                    "order_id": order_id,
                    "status": order.status,
                    "strategy_id": order.strategy_id,
                    "symbol": order.symbol,
                    "action": order.action,
                    "amount": order.amount,
                    "price": order.price,
                    "order_type": order.order_type,
                    "created_at": order.created_at
                }
            
            # Check queue
            for order in self.order_queue:
                if order.order_id == order_id:
                    return {
                        "order_id": order_id,
                        "status": "queued",
                        "strategy_id": order.strategy_id,
                        "symbol": order.symbol,
                        "action": order.action,
                        "amount": order.amount,
                        "price": order.price,
                        "order_type": order.order_type,
                        "created_at": order.created_at
                    }
            
            # Check results
            for strategy_id, results in self.order_results.items():
                for result in results:
                    if result.order_id == order_id:
                        return {
                            "order_id": order_id,
                            "status": "completed" if result.success else "failed",
                            "strategy_id": result.strategy_id,
                            "symbol": result.symbol,
                            "action": result.action,
                            "amount": result.amount,
                            "executed_price": result.executed_price,
                            "execution_time": result.execution_time,
                            "success": result.success,
                            "notes": result.execution_notes
                        }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting order status: {e}")
            return None

    async def get_orders_by_strategy(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a specific strategy."""
        try:
            orders = []
            
            # Get orders from queue
            for order in self.order_queue:
                if order.strategy_id == strategy_id:
                    orders.append({
                        "order_id": order.order_id,
                        "status": "queued",
                        "symbol": order.symbol,
                        "action": order.action,
                        "amount": order.amount,
                        "price": order.price,
                        "order_type": order.order_type,
                        "created_at": order.created_at
                    })
            
            # Get active orders
            for order_id, order in self.active_orders.items():
                if order.strategy_id == strategy_id:
                    orders.append({
                        "order_id": order_id,
                        "status": order.status,
                        "symbol": order.symbol,
                        "action": order.action,
                        "amount": order.amount,
                        "price": order.price,
                        "order_type": order.order_type,
                        "created_at": order.created_at
                    })
            
            # Get completed orders
            if strategy_id in self.order_results:
                for result in self.order_results[strategy_id]:
                    orders.append({
                        "order_id": result.order_id,
                        "status": "completed" if result.success else "failed",
                        "symbol": result.symbol,
                        "action": result.action,
                        "amount": result.amount,
                        "executed_price": result.executed_price,
                        "execution_time": result.execution_time,
                        "success": result.success,
                        "notes": result.execution_notes
                    })
            
            return orders
            
        except Exception as e:
            print(f"❌ Error getting orders by strategy: {e}")
            return []

    async def get_order_summary(self) -> Dict[str, Any]:
        """Get summary of order management statistics."""
        try:
            # Calculate average execution time
            if self.order_stats["successful_orders"] > 0:
                avg_execution_time = self.order_stats["total_volume"] / self.order_stats["successful_orders"]
            else:
                avg_execution_time = 0.0
            
            return {
                "stats": {**self.order_stats, "average_execution_time": avg_execution_time},
                "queue_size": len(self.order_queue),
                "active_orders": len(self.active_orders),
                "order_history_size": len(self.order_history),
                "order_settings": self.order_settings
            }
            
        except Exception as e:
            print(f"❌ Error getting order summary: {e}")
            return {}

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_execution_pipeline.cleanup()
            await self.trading_context.cleanup()
            print("✅ Order Manager cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up Order Manager: {e}")
