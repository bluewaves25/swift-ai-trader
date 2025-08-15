#!/usr/bin/env python3
"""
Broker Router - SIMPLIFIED CORE MODULE
Handles strategy-specific broker routing and optimization
SIMPLE: ~150 lines focused on routing logic only
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from ...shared_utils import get_shared_logger

class BrokerRouter:
    """
    Simplified broker routing engine.
    Focuses on strategy-specific routing and optimization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("adapters", "broker_router")
        
        # Strategy-specific routing rules
        self.routing_rules = {
            "arbitrage": {
                "preferred_brokers": ["binance", "exness_mt5"],
                "latency_requirement": 1,          # 1ms max
                "redundancy": "high",
                "failover_mode": "immediate"
            },
            "market_making": {
                "preferred_brokers": ["exness_mt5", "binance"],
                "latency_requirement": 100,        # 100ms max
                "redundancy": "medium",
                "failover_mode": "quick"
            },
            "statistical": {
                "preferred_brokers": ["exness_mt5"],
                "latency_requirement": 1000,       # 1s max
                "redundancy": "low",
                "failover_mode": "standard"
            },
            "trend_following": {
                "preferred_brokers": ["exness_mt5"],
                "latency_requirement": 1000,       # 1s max
                "redundancy": "low", 
                "failover_mode": "standard"
            },
            "news_driven": {
                "preferred_brokers": ["binance", "exness_mt5"],
                "latency_requirement": 500,        # 500ms max
                "redundancy": "medium",
                "failover_mode": "quick"
            },
            "htf": {
                "preferred_brokers": ["exness_mt5"],
                "latency_requirement": 5000,       # 5s max
                "redundancy": "low",
                "failover_mode": "standard"
            }
        }
        
        # Routing state
        self.routing_state = {
            "pending_orders": [],
            "active_routes": {},
            "failed_routes": {},
            "optimization_metrics": {}
        }
        
        # Performance tracking
        self.performance_metrics = {
            "total_routes": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "average_routing_time_ms": 0.0
        }
    
    async def initialize_routing(self):
        """Initialize routing strategies and configurations."""
        try:
            self.logger.info("✅ Broker routing initialized")
            self.logger.info(f"✅ Routing rules configured for {len(self.routing_rules)} strategies")
            
            # Initialize routing state
            self.routing_state["initialization_time"] = time.time()
            self.routing_state["ready"] = True
            
            # Log routing capabilities
            for strategy, rules in self.routing_rules.items():
                preferred_brokers = ", ".join(rules["preferred_brokers"])
                self.logger.info(f"✅ {strategy} strategy: {preferred_brokers} (latency: {rules['latency_requirement']}ms)")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing broker routing: {e}")
            raise
    
    async def route_order(self, order_data: Dict[str, Any], strategy_type: str) -> Dict[str, Any]:
        """Route order to appropriate broker based on strategy."""
        try:
            start_time = time.time()
            
            # Get routing rules for strategy
            routing_rules = self.routing_rules.get(strategy_type, self.routing_rules["statistical"])
            
            # Select best broker
            selected_broker = await self._select_broker(order_data, routing_rules)
            
            # Execute routing
            routing_result = await self._execute_routing(order_data, selected_broker, routing_rules)
            
            # Update performance metrics
            routing_time_ms = (time.time() - start_time) * 1000
            self._update_routing_metrics(routing_result, routing_time_ms)
            
            return routing_result
            
        except Exception as e:
            self.logger.warning(f"Error routing order: {e}")
            self.performance_metrics["failed_routes"] += 1
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def route_pending_orders(self):
        """Route any pending orders in the queue."""
        try:
            if not self.routing_state["pending_orders"]:
                return
            
            # Process pending orders
            orders_to_process = self.routing_state["pending_orders"].copy()
            self.routing_state["pending_orders"].clear()
            
            for order_info in orders_to_process:
                order_data = order_info["order_data"]
                strategy_type = order_info["strategy_type"]
                
                await self.route_order(order_data, strategy_type)
            
        except Exception as e:
            self.logger.warning(f"Error routing pending orders: {e}")
    
    async def optimize_for_strategy(self, strategy_type: str):
        """Optimize routing for a specific strategy."""
        try:
            # Get current routing performance for strategy
            strategy_performance = self._get_strategy_performance(strategy_type)
            
            # Update routing rules if needed
            if strategy_performance.get("success_rate", 1.0) < 0.9:
                await self._update_routing_rules_for_strategy(strategy_type, strategy_performance)
            
        except Exception as e:
            self.logger.warning(f"Error optimizing for strategy {strategy_type}: {e}")
    
    async def optimize_connections(self) -> Dict[str, Any]:
        """Optimize overall connection routing."""
        try:
            optimization_results = {
                "timestamp": time.time(),
                "optimizations_applied": [],
                "performance_improvements": {},
                "routing_efficiency": self._calculate_routing_efficiency()
            }
            
            # Optimize each strategy
            for strategy_type in self.routing_rules.keys():
                strategy_optimization = await self._optimize_strategy_routing(strategy_type)
                optimization_results["optimizations_applied"].append(strategy_optimization)
            
            # Update routing state
            self.routing_state["optimization_metrics"] = optimization_results
            
            return optimization_results
            
        except Exception as e:
            self.logger.warning(f"Error optimizing connections: {e}")
            return {"error": str(e), "timestamp": time.time()}
    
    async def update_routing_strategies(self, optimization_results: Dict[str, Any]):
        """Update routing strategies based on optimization results."""
        try:
            optimizations = optimization_results.get("optimizations_applied", [])
            
            for optimization in optimizations:
                strategy_type = optimization.get("strategy_type")
                improvements = optimization.get("improvements", {})
                
                if strategy_type and improvements:
                    # Update routing rules for strategy
                    await self._apply_routing_improvements(strategy_type, improvements)
            
            self.logger.info(f"Updated routing strategies for {len(optimizations)} strategies")
            
        except Exception as e:
            self.logger.warning(f"Error updating routing strategies: {e}")
    
    # ============= PRIVATE ROUTING METHODS =============
    
    async def _select_broker(self, order_data: Dict[str, Any], routing_rules: Dict[str, Any]) -> str:
        """Select the best broker for an order."""
        try:
            preferred_brokers = routing_rules.get("preferred_brokers", ["exness_mt5"])
            
            # Simple broker selection (first available preferred broker)
            for broker in preferred_brokers:
                if await self._is_broker_available(broker):
                    return broker
            
            # Fallback to any available broker
            return await self._get_fallback_broker()
            
        except Exception as e:
            self.logger.warning(f"Error selecting broker: {e}")
            return "exness_mt5"  # Default fallback
    
    async def _execute_routing(self, order_data: Dict[str, Any], broker: str, routing_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the order routing."""
        try:
            # Simulate routing execution
            await asyncio.sleep(0.01)  # 10ms routing time
            
            # Simulate routing success (95% success rate)
            import random
            success = random.random() > 0.05
            
            latency_ms = self._simulate_routing_latency(routing_rules)
            
            result = {
                "success": success,
                "broker": broker,
                "order_id": order_data.get("order_id", f"route_{int(time.time() * 1000)}"),
                "latency_ms": latency_ms,
                "routing_time_ms": 10,  # Simulated routing time
                "timestamp": time.time()
            }
            
            if success:
                self.routing_state["active_routes"][result["order_id"]] = result
            else:
                result["error"] = "Routing failed"
                self.routing_state["failed_routes"][result["order_id"]] = result
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Error executing routing: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _is_broker_available(self, broker: str) -> bool:
        """Check if a broker is available for routing."""
        # Simulate broker availability (90% availability)
        import random
        return random.random() > 0.1
    
    async def _get_fallback_broker(self) -> str:
        """Get a fallback broker when preferred brokers are unavailable."""
        # Simple fallback logic
        fallback_brokers = ["exness_mt5", "binance"]
        
        for broker in fallback_brokers:
            if await self._is_broker_available(broker):
                return broker
        
        return "exness_mt5"  # Ultimate fallback
    
    def _simulate_routing_latency(self, routing_rules: Dict[str, Any]) -> float:
        """Simulate routing latency based on requirements."""
        latency_requirement = routing_rules.get("latency_requirement", 1000)
        
        # Simulate actual latency (typically 10-50% of requirement)
        import random
        return random.uniform(latency_requirement * 0.1, latency_requirement * 0.5)
    
    def _update_routing_metrics(self, routing_result: Dict[str, Any], routing_time_ms: float):
        """Update routing performance metrics."""
        try:
            self.performance_metrics["total_routes"] += 1
            
            if routing_result.get("success", False):
                self.performance_metrics["successful_routes"] += 1
            else:
                self.performance_metrics["failed_routes"] += 1
            
            # Update average routing time
            total_routes = self.performance_metrics["total_routes"]
            current_avg = self.performance_metrics["average_routing_time_ms"]
            
            self.performance_metrics["average_routing_time_ms"] = (
                (current_avg * (total_routes - 1) + routing_time_ms) / total_routes
            )
            
        except Exception as e:
            self.logger.warning(f"Error updating routing metrics: {e}")
    
    def _get_strategy_performance(self, strategy_type: str) -> Dict[str, Any]:
        """Get performance metrics for a specific strategy."""
        # Simulate strategy performance metrics
        import random
        return {
            "strategy_type": strategy_type,
            "success_rate": random.uniform(0.85, 0.98),
            "average_latency_ms": random.uniform(10, 100),
            "total_routes": random.randint(10, 100)
        }
    
    async def _update_routing_rules_for_strategy(self, strategy_type: str, performance: Dict[str, Any]):
        """Update routing rules for a strategy based on performance."""
        try:
            success_rate = performance.get("success_rate", 1.0)
            
            if success_rate < 0.8:
                # Poor performance - switch to more reliable brokers
                self.routing_rules[strategy_type]["preferred_brokers"] = ["exness_mt5"]
                self.routing_rules[strategy_type]["redundancy"] = "high"
                
                self.logger.info(f"Updated routing rules for {strategy_type} due to poor performance")
            
        except Exception as e:
            self.logger.warning(f"Error updating routing rules for {strategy_type}: {e}")
    
    async def _optimize_strategy_routing(self, strategy_type: str) -> Dict[str, Any]:
        """Optimize routing for a specific strategy."""
        try:
            performance = self._get_strategy_performance(strategy_type)
            
            optimization = {
                "strategy_type": strategy_type,
                "current_performance": performance,
                "improvements": {},
                "optimization_applied": False
            }
            
            # Apply optimizations if needed
            if performance.get("success_rate", 1.0) < 0.9:
                optimization["improvements"]["redundancy"] = "increased"
                optimization["improvements"]["failover_mode"] = "quicker"
                optimization["optimization_applied"] = True
            
            return optimization
            
        except Exception as e:
            self.logger.warning(f"Error optimizing strategy routing for {strategy_type}: {e}")
            return {"strategy_type": strategy_type, "error": str(e)}
    
    async def _apply_routing_improvements(self, strategy_type: str, improvements: Dict[str, Any]):
        """Apply routing improvements for a strategy."""
        try:
            if strategy_type in self.routing_rules:
                for improvement_type, improvement_value in improvements.items():
                    if improvement_type in self.routing_rules[strategy_type]:
                        self.routing_rules[strategy_type][improvement_type] = improvement_value
                
                self.logger.info(f"Applied routing improvements for {strategy_type}")
            
        except Exception as e:
            self.logger.warning(f"Error applying routing improvements for {strategy_type}: {e}")
    
    def _calculate_routing_efficiency(self) -> float:
        """Calculate overall routing efficiency."""
        try:
            total_routes = self.performance_metrics["total_routes"]
            successful_routes = self.performance_metrics["successful_routes"]
            
            if total_routes > 0:
                return successful_routes / total_routes
            else:
                return 1.0
                
        except Exception as e:
            self.logger.warning(f"Error calculating routing efficiency: {e}")
            return 0.5  # Default to neutral efficiency
    
    # ============= UTILITY METHODS =============
    
    def get_routing_status(self) -> Dict[str, Any]:
        """Get current routing status."""
        return {
            "performance_metrics": self.performance_metrics,
            "routing_state": self.routing_state,
            "active_routes_count": len(self.routing_state["active_routes"]),
            "failed_routes_count": len(self.routing_state["failed_routes"]),
            "routing_efficiency": self._calculate_routing_efficiency()
        }
