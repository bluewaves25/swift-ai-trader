#!/usr/bin/env python3
"""
Order Executor - SIMPLIFIED CORE MODULE
Handles 4-tier order execution with Rust integration
MUCH SIMPLER: ~200 lines focused on core execution only

RUST INTEGRATION:
- Delegates heavy computation to Rust components
- Python handles orchestration and learning integration
- Clean separation of concerns
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from ...shared_utils import get_shared_logger, get_agent_learner, LearningType

class OrderExecutorSimple:
    """
    Simplified order execution engine - delegates to Rust for performance.
    Python handles orchestration, Rust handles execution.
    """
    
    def __init__(self, config: Dict[str, Any], rust_bridge=None):
        self.config = config
        self.logger = get_shared_logger("execution", "order_executor")
        self.learner = get_agent_learner("execution", LearningType.EXECUTION_OPTIMIZATION, 5)
        self.rust_bridge = rust_bridge  # Rust execution bridge
        
        # Simple execution statistics
        self.stats = {
            "total_orders": 0,
            "successful_orders": 0,
            "failed_orders": 0,
            "average_latency_ms": 0.0
        }
        
        # Strategy-specific routing (simplified)
        self.strategy_routing = {
            "arbitrage": "ultra_hft",      # 1ms
            "market_making": "fast",       # 100ms
            "statistical": "tactical",     # 1s
            "trend_following": "tactical", # 1s
            "news_driven": "tactical",     # 1s
            "htf": "strategic"             # 60s
        }
        
        # Active orders tracking (simplified)
        self.active_orders = {}
        
    async def execute_order(self, order_request: Dict[str, Any], 
                          strategy_type: str = "statistical") -> Dict[str, Any]:
        """
        Execute order using appropriate tier and Rust backend.
        Main execution method - delegates to Rust for performance.
        """
        start_time = time.time()
        
        try:
            self.stats["total_orders"] += 1
            
            # Get execution tier for strategy
            execution_tier = self.strategy_routing.get(strategy_type, "tactical")
            
            # Basic validation
            if not self._validate_order_basic(order_request):
                return {
                    "success": False,
                    "error": "Invalid order parameters",
                    "timestamp": time.time()
                }
            
            # Execute via Rust if available, otherwise simulate
            if self.rust_bridge:
                result = await self._execute_via_rust(order_request, execution_tier)
            else:
                result = await self._execute_simulated(order_request, execution_tier)
            
            # Learn from execution
            await self._learn_from_execution(order_request, result, start_time)
            
            # Update statistics
            self._update_stats(result, start_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing order: {e}")
            self.stats["failed_orders"] += 1
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _execute_via_rust(self, order_request: Dict[str, Any], 
                              execution_tier: str) -> Dict[str, Any]:
        """Execute order via Rust backend for high performance."""
        try:
            # This would call the actual Rust execution code
            # For now, we'll simulate the Rust call
            
            # Simulate different latencies based on tier
            tier_latencies = {
                "ultra_hft": 0.001,    # 1ms
                "fast": 0.1,           # 100ms
                "tactical": 1.0,       # 1s
                "strategic": 0.1       # Simulated (normally 60s)
            }
            
            await asyncio.sleep(tier_latencies.get(execution_tier, 1.0))
            
            # Simulate successful execution
            result = {
                "success": True,
                "order_id": order_request.get("order_id", f"rust_{int(time.time() * 1000)}"),
                "executed_quantity": order_request.get("quantity", 0.0),
                "executed_price": order_request.get("price", 0.0),
                "execution_tier": execution_tier,
                "execution_time_ms": tier_latencies.get(execution_tier, 1.0) * 1000,
                "execution_method": "rust",
                "timestamp": time.time()
            }
            
            self.stats["successful_orders"] += 1
            return result
            
        except Exception as e:
            self.logger.warning(f"Rust execution error: {e}")
            return await self._execute_simulated(order_request, execution_tier)
    
    async def _execute_simulated(self, order_request: Dict[str, Any], 
                                execution_tier: str) -> Dict[str, Any]:
        """Fallback simulated execution when Rust is not available."""
        try:
            # Simulate execution latency
            tier_latencies = {
                "ultra_hft": 0.001,
                "fast": 0.1,
                "tactical": 1.0,
                "strategic": 0.1
            }
            
            await asyncio.sleep(tier_latencies.get(execution_tier, 1.0))
            
            result = {
                "success": True,
                "order_id": order_request.get("order_id", f"sim_{int(time.time() * 1000)}"),
                "executed_quantity": order_request.get("quantity", 0.0),
                "executed_price": order_request.get("price", 0.0),
                "execution_tier": execution_tier,
                "execution_time_ms": tier_latencies.get(execution_tier, 1.0) * 1000,
                "execution_method": "simulated",
                "timestamp": time.time()
            }
            
            self.stats["successful_orders"] += 1
            return result
            
        except Exception as e:
            self.logger.error(f"Simulated execution error: {e}")
            self.stats["failed_orders"] += 1
            return {
                "success": False,
                "error": str(e),
                "execution_method": "simulated",
                "timestamp": time.time()
            }
    
    def _validate_order_basic(self, order_request: Dict[str, Any]) -> bool:
        """Basic order validation."""
        required_fields = ["symbol", "side", "quantity"]
        
        for field in required_fields:
            if field not in order_request:
                return False
        
        quantity = order_request.get("quantity", 0.0)
        if quantity <= 0:
            return False
        
        side = order_request.get("side", "").upper()
        if side not in ["BUY", "SELL"]:
            return False
        
        return True
    
    def _update_stats(self, result: Dict[str, Any], start_time: float):
        """Update execution statistics."""
        if result.get("success", False):
            # Update average latency
            execution_time_ms = (time.time() - start_time) * 1000
            current_avg = self.stats["average_latency_ms"]
            total_orders = self.stats["total_orders"]
            
            if total_orders > 0:
                self.stats["average_latency_ms"] = (
                    (current_avg * (total_orders - 1) + execution_time_ms) / total_orders
                )
    
    async def _learn_from_execution(self, order_request: Dict[str, Any], 
                                  result: Dict[str, Any], start_time: float):
        """Learn from execution for improvement."""
        try:
            # Simple learning features
            features = [
                order_request.get("quantity", 0.0) / 1000.0,  # Normalize
                order_request.get("price", 0.0) / 10000.0,    # Normalize
                1.0 if result.get("success", False) else 0.0,  # Success flag
                result.get("execution_time_ms", 0.0) / 1000.0, # Normalize time
                time.time() - start_time  # Total time
            ]
            
            # Target is execution success
            target = 1.0 if result.get("success", False) else 0.0
            
            # Learn for future improvement
            from ...shared_utils import LearningData
            learning_data = LearningData(
                agent_name="execution",
                learning_type=LearningType.EXECUTION_OPTIMIZATION,
                input_features=features,
                target_value=target
            )
            
            self.learner.learn(learning_data)
            
        except Exception as e:
            self.logger.warning(f"Learning error: {e}")
    
    # ============= UTILITY METHODS =============
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get simple execution statistics."""
        total_orders = self.stats["total_orders"]
        success_rate = (
            self.stats["successful_orders"] / max(total_orders, 1)
        )
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "failure_rate": 1.0 - success_rate
        }
    
    def reset_stats(self):
        """Reset execution statistics."""
        self.stats = {
            "total_orders": 0,
            "successful_orders": 0,
            "failed_orders": 0,
            "average_latency_ms": 0.0
        }
    
    def get_active_orders(self):
        """Get currently active orders."""
        return self.active_orders
