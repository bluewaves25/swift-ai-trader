#!/usr/bin/env python3
"""
Enhanced Strategy Engine Agent - CENTRAL COORDINATOR & STRATEGY MANAGER
Consolidates all strategy-related functionality from other agents.
Becomes the single source of truth for strategy execution, strategy optimization (NOT cost optimization), and learning.
Cost optimization is handled by Fees Monitor Agent.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from ..shared_utils import BaseAgent, register_agent

class EnhancedStrategyEngineAgent(BaseAgent):
    """Enhanced strategy engine agent - central coordinator for all agents."""
    
    def _initialize_agent_components(self):
        """Initialize strategy engine specific components."""
        # Initialize strategy engine components
        self.strategy_manager = None
        self.optimization_engine = None
        self.learning_coordinator = None
        self.order_manager = None
        
        # Strategy engine state
        self.strategy_state = {
            "active_strategies": {},
            "strategy_performance": {},
            "strategy_optimization_queue": [],  # Only strategy optimization, not cost optimization
            "learning_events": [],
            "order_queue": [],
            "last_strategy_update": time.time()
        }
        
        # Strategy engine statistics
        self.stats = {
            "total_strategies_executed": 0,
            "optimizations_applied": 0,
            "learning_events_processed": 0,

            "orders_managed": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Strategy engine specific startup logic."""
        try:
            # Initialize strategy management components
            await self._initialize_strategy_management()
            
            # Initialize optimization engine
            await self._initialize_optimization_engine()
            
            # Initialize learning coordination
            await self._initialize_learning_coordination()
            

            
            # Initialize order management
            await self._initialize_order_management()
            
            # Initialize strategy composer
            await self._initialize_strategy_composer()
            
            # Initialize strategy applicator
            await self._initialize_strategy_applicator()
            
            self.logger.info("✅ Strategy Engine Agent: Central coordination systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in strategy engine startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Strategy engine specific shutdown logic."""
        try:
            # Cleanup strategy engine resources
            await self._cleanup_strategy_components()
            
            self.logger.info("✅ Strategy Engine Agent: Central coordination systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in strategy engine shutdown: {e}")
    
    # ============= BACKGROUND TASKS =============
    
    async def _strategy_optimization_loop(self):
        """Strategy optimization loop."""
        while self.is_running:
            try:
                # Optimize strategies
                await self._optimize_strategies()
                
                await asyncio.sleep(10.0)  # 10 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in strategy optimization loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _strategy_performance_monitoring_loop(self):
        """Strategy performance monitoring loop."""
        while self.is_running:
            try:
                # Monitor strategy performance
                await self._monitor_strategy_performance()
                
                await asyncio.sleep(5.0)  # 5 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in strategy performance monitoring loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _strategy_reporting_loop(self):
        """Strategy reporting loop."""
        while self.is_running:
            try:
                # Report strategy status
                await self._report_strategy_status()
                
                await asyncio.sleep(30.0)  # 30 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in strategy reporting loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _optimize_strategies(self):
        """Optimize strategies."""
        try:
            # Placeholder for strategy optimization
            pass
        except Exception as e:
            self.logger.error(f"Error optimizing strategies: {e}")
    
    async def _monitor_strategy_performance(self):
        """Monitor strategy performance."""
        try:
            # Placeholder for strategy performance monitoring
            pass
        except Exception as e:
            self.logger.error(f"Error monitoring strategy performance: {e}")
    
    async def _report_strategy_status(self):
        """Report strategy status."""
        try:
            # Placeholder for strategy status reporting
            pass
        except Exception as e:
            self.logger.error(f"Error reporting strategy status: {e}")

    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._strategy_management_loop, "Strategy Management", "fast"),
            (self._strategy_optimization_loop, "Strategy Optimization", "tactical"),
            (self._strategy_performance_monitoring_loop, "Strategy Performance Monitoring", "tactical"),
            (self._strategy_reporting_loop, "Strategy Reporting", "strategic")
        ]
    
    # ============= STRATEGY MANAGEMENT INITIALIZATION =============
    
    async def _initialize_strategy_management(self):
        """Initialize strategy management components."""
        try:
            # Initialize strategy manager
            from .core.strategy_manager import StrategyManager
            self.strategy_manager = StrategyManager(self.config)
            await self.strategy_manager.initialize()
            
            self.logger.info("✅ Strategy management initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing strategy management: {e}")
            raise
    
    async def _initialize_optimization_engine(self):
        """Initialize optimization engine."""
        try:
            # Initialize optimization engine
            from .core.optimization_engine import OptimizationEngine
            self.optimization_engine = OptimizationEngine(self.config)
            await self.optimization_engine.initialize()
            
            self.logger.info("✅ Optimization engine initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing optimization engine: {e}")
            raise
    
    async def _initialize_learning_coordination(self):
        """Initialize learning coordination."""
        try:
            # Initialize learning coordinator
            from .core.learning_coordinator import LearningCoordinator
            self.learning_coordinator = LearningCoordinator(self.config)
            await self.learning_coordinator.initialize()
            
            self.logger.info("✅ Learning coordination initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing learning coordination: {e}")
            raise
    

    
    async def _initialize_order_management(self):
        """Initialize order management."""
        try:
            # Initialize order manager
            from .core.order_manager import OrderManager
            self.order_manager = OrderManager(self.config)
            await self.order_manager.initialize()
            
            self.logger.info("✅ Order management initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing order management: {e}")
            raise
    
    async def _initialize_strategy_composer(self):
        """Initialize strategy composer."""
        try:
            # Initialize strategy composer
            from .core.strategy_composer import StrategyComposer
            self.strategy_composer = StrategyComposer(self.config)
            await self.strategy_composer.initialize()
            
            self.logger.info("✅ Strategy composer initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing strategy composer: {e}")
            raise
    
    async def _initialize_strategy_applicator(self):
        """Initialize strategy applicator."""
        try:
            # Initialize strategy applicator
            from .core.strategy_applicator import StrategyApplicator
            self.strategy_applicator = StrategyApplicator(self.config)
            await self.strategy_applicator.initialize()
            
            self.logger.info("✅ Strategy applicator initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing strategy applicator: {e}")
            raise
    
    # ============= STRATEGY MANAGEMENT LOOP =============
    
    async def _strategy_management_loop(self):
        """Strategy management loop (30s intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Manage active strategies
                strategies_updated = await self._manage_active_strategies()
                
                # Update strategy state
                if strategies_updated > 0:
                    self._update_strategy_state()
                
                # Record operation
                duration_ms = (time.time() - start_time) * 1000
                if hasattr(self, 'status_monitor') and self.status_monitor:
                    self.status_monitor.record_operation(duration_ms, strategies_updated > 0)
                
                await asyncio.sleep(30)  # 30s for strategy management
                
            except Exception as e:
                self.logger.error(f"Error in strategy management loop: {e}")
                await asyncio.sleep(30)
    
    async def _manage_active_strategies(self) -> int:
        """Manage active strategies and return number of strategies updated."""
        try:
            strategies_updated = 0
            
            if not self.strategy_manager:
                return 0
            
            # Get active strategies from Redis
            active_strategies = await self._get_active_strategies()
            
            for strategy in active_strategies:
                if await self._update_strategy_performance(strategy):
                    strategies_updated += 1
                
                # Check if strategy needs optimization (strategy parameters only, not costs)
                if await self._check_strategy_optimization_needed(strategy):
                    await self._queue_strategy_optimization(strategy)
            
            return strategies_updated
            
        except Exception as e:
            self.logger.error(f"Error managing active strategies: {e}")
            return 0
    
    async def _get_active_strategies(self) -> List[Dict[str, Any]]:
        """Get active strategies from Redis."""
        try:
            # Get active strategies from Redis
            active_strategies = await self.redis_conn.lrange("strategies:active", 0, 19)
            
            strategies = []
            for strategy in active_strategies:
                try:
                    strategies.append(json.loads(strategy))
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid strategy format: {strategy}")
            
            return strategies
            
        except Exception as e:
            self.logger.error(f"Error getting active strategies: {e}")
            return []
    
    async def _update_strategy_performance(self, strategy: Dict[str, Any]) -> bool:
        """Update strategy performance metrics."""
        try:
            strategy_id = strategy.get("strategy_id", "unknown")
            
            # Get performance data from other agents
            performance_data = await self._get_strategy_performance_data(strategy_id)
            
            if performance_data:
                # Update strategy performance
                self.strategy_state["strategy_performance"][strategy_id] = performance_data
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating strategy performance: {e}")
            return False
    
    async def _get_strategy_performance_data(self, strategy_id: str) -> Dict[str, Any]:
        """Get strategy performance data from other agents."""
        try:
            # Get performance data from Redis (published by other agents)
            performance_data = await self.redis_conn.get(f"strategy:performance:{strategy_id}")
            
            if performance_data:
                return json.loads(performance_data)
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting strategy performance data: {e}")
            return {}
    
    async def _check_strategy_optimization_needed(self, strategy: Dict[str, Any]) -> bool:
        """Check if strategy needs optimization."""
        try:
            strategy_id = strategy.get("strategy_id", "unknown")
            performance = self.strategy_state["strategy_performance"].get(strategy_id, {})
            
            # Check performance thresholds
            if performance:
                performance_score = performance.get("performance_score", 1.0)
                return performance_score < 0.7  # Below 70% performance
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking strategy optimization: {e}")
            return False
    
    async def _queue_strategy_optimization(self, strategy: Dict[str, Any]):
        """Queue strategy for optimization."""
        try:
            optimization_request = {
                "strategy": strategy,
                "timestamp": time.time(),
                "priority": "medium"
            }
            
            # Add to strategy optimization queue (strategy parameters only, not costs)
            self.strategy_state["strategy_optimization_queue"].append(optimization_request)
            
            # Publish strategy optimization request
            await self.redis_conn.publish_async("strategy_engine:strategy_optimization_requests", 
                                        json.dumps(optimization_request))
            
        except Exception as e:
            self.logger.error(f"Error queuing strategy optimization: {e}")
    
    # ============= OPTIMIZATION ENGINE LOOP =============
    
    async def _optimization_engine_loop(self):
        """Optimization engine loop (60s intervals)."""
        while self.is_running:
            try:
                # Process optimization queue
                optimizations_processed = await self._process_optimization_queue()
                
                # Update optimization statistics
                if optimizations_processed > 0:
                    self.stats["optimizations_applied"] += optimizations_processed
                
                await asyncio.sleep(60)  # 60s for optimization engine
                
            except Exception as e:
                self.logger.error(f"Error in optimization engine loop: {e}")
                await asyncio.sleep(60)
    
    async def _process_optimization_queue(self) -> int:
        """Process optimization queue and return number of optimizations processed."""
        try:
            optimizations_processed = 0
            
            if not self.optimization_engine:
                return 0
            
            # Process strategy optimization requests (strategy parameters only, not costs)
            for optimization_request in self.strategy_state["strategy_optimization_queue"][:5]:  # Process up to 5 at a time
                if await self._process_optimization_request(optimization_request):
                    optimizations_processed += 1
                    
                    # Remove processed request
                    self.strategy_state["strategy_optimization_queue"].remove(optimization_request)
            
            return optimizations_processed
            
        except Exception as e:
            self.logger.error(f"Error processing optimization queue: {e}")
            return 0
    
    async def _process_optimization_request(self, optimization_request: Dict[str, Any]) -> bool:
        """Process a single optimization request."""
        try:
            strategy = optimization_request.get("strategy", {})
            
            # Perform strategy optimization
            optimization_result = await self.optimization_engine.optimize_strategy(strategy)
            
            if optimization_result:
                # Apply optimization
                await self._apply_strategy_optimization(strategy, optimization_result)
                
                # Publish optimization result
                await self._publish_optimization_result(strategy, optimization_result)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error processing optimization request: {e}")
            return False
    
    async def _apply_strategy_optimization(self, strategy: Dict[str, Any], optimization_result: Dict[str, Any]):
        """Apply strategy optimization."""
        try:
            strategy_id = strategy.get("strategy_id", "unknown")
            
            # Update strategy with optimization
            if strategy_id in self.strategy_state["active_strategies"]:
                self.strategy_state["active_strategies"][strategy_id].update(optimization_result)
            
            # Publish strategy update
            await self.redis_conn.publish_async("strategy_engine:strategy_updates", 
                                        json.dumps({
                                            "strategy_id": strategy_id,
                                            "optimization": optimization_result,
                                            "timestamp": time.time()
                                        }))
            
        except Exception as e:
            self.logger.error(f"Error applying strategy optimization: {e}")
    
    # ============= LEARNING COORDINATION LOOP =============
    
    async def _learning_coordination_loop(self):
        """Learning coordination loop (30s intervals)."""
        while self.is_running:
            try:
                # Coordinate learning events
                learning_events_processed = await self._coordinate_learning_events()
                
                # Update learning statistics
                if learning_events_processed > 0:
                    self.stats["learning_events_processed"] += learning_events_processed
                
                await asyncio.sleep(30)  # 30s for learning coordination
                
            except Exception as e:
                self.logger.error(f"Error in learning coordination loop: {e}")
                await asyncio.sleep(30)
    
    async def _coordinate_learning_events(self) -> int:
        """Coordinate learning events and return number of events processed."""
        try:
            learning_events_processed = 0
            
            if not self.learning_coordinator:
                return 0
            
            # Get learning events from Redis
            learning_events = await self._get_learning_events()
            
            for event in learning_events:
                if await self._process_learning_event(event):
                    learning_events_processed += 1
                    
                    # Add to learning events history
                    self.strategy_state["learning_events"].append({
                        **event,
                        "processed_time": time.time()
                    })
            
            return learning_events_processed
            
        except Exception as e:
            self.logger.error(f"Error coordinating learning events: {e}")
            return 0
    
    async def _get_learning_events(self) -> List[Dict[str, Any]]:
        """Get learning events from Redis."""
        try:
            # Get learning events from Redis
            learning_events = await self.redis_conn.lrange("learning:events", 0, 9)
            
            events = []
            for event in learning_events:
                try:
                    events.append(json.loads(event))
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid learning event format: {event}")
            
            return events
            
        except Exception as e:
            self.logger.error(f"Error getting learning events: {e}")
            return []
    
    async def _process_learning_event(self, event: Dict[str, Any]) -> bool:
        """Process a single learning event."""
        try:
            event_type = event.get("type", "unknown")
            
            # Process learning event based on type
            if event_type == "performance_improvement":
                await self._process_performance_improvement(event)
            elif event_type == "strategy_failure":
                await self._process_strategy_failure(event)
            elif event_type == "market_regime_change":
                await self._process_market_regime_change(event)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing learning event: {e}")
            return False
    
    async def _process_performance_improvement(self, event: Dict[str, Any]):
        """Process performance improvement learning event."""
        try:
            # Extract learning data
            strategy_id = event.get("strategy_id", "unknown")
            improvement_data = event.get("improvement_data", {})
            
            # Apply learning to strategy
            if self.learning_coordinator:
                await self.learning_coordinator.apply_learning(strategy_id, improvement_data)
            
        except Exception as e:
            self.logger.error(f"Error processing performance improvement: {e}")
    
    async def _process_strategy_failure(self, event: Dict[str, Any]):
        """Process strategy failure learning event."""
        try:
            # Extract failure data
            strategy_id = event.get("strategy_id", "unknown")
            failure_data = event.get("failure_data", {})
            
            # Apply failure learning to strategy
            if self.learning_coordinator:
                await self.learning_coordinator.apply_failure_learning(strategy_id, failure_data)
            
        except Exception as e:
            self.logger.error(f"Error processing strategy failure: {e}")
    
    async def _process_market_regime_change(self, event: Dict[str, Any]):
        """Process market regime change learning event."""
        try:
            # Extract regime change data
            old_regime = event.get("old_regime", "unknown")
            new_regime = event.get("new_regime", "unknown")
            
            # Apply regime change learning to all strategies
            if self.learning_coordinator:
                await self.learning_coordinator.apply_regime_change_learning(old_regime, new_regime)
            
        except Exception as e:
            self.logger.error(f"Error processing market regime change: {e}")
    

    

    

    

    

    
    # ============= ORDER MANAGEMENT LOOP =============
    
    async def _order_management_loop(self):
        """Order management loop (100ms intervals)."""
        while self.is_running:
            try:
                # Process order management requests
                orders_managed = await self._process_order_management_requests()
                
                # Update order management statistics
                if orders_managed > 0:
                    self.stats["orders_managed"] += orders_managed
                
                await asyncio.sleep(0.1)  # 100ms for order management
                
            except Exception as e:
                self.logger.error(f"Error in order management loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_order_management_requests(self) -> int:
        """Process order management requests and return number of orders managed."""
        try:
            orders_managed = 0
            
            if not self.order_manager:
                return 0
            
            # Get order management requests from Redis
            order_requests = await self._get_order_management_requests()
            
            for request in order_requests:
                if await self._process_order_management_request(request):
                    orders_managed += 1
                    
                    # Add to order queue
                    self.strategy_state["order_queue"].append({
                        **request,
                        "management_time": time.time()
                    })
            
            return orders_managed
            
        except Exception as e:
            self.logger.error(f"Error processing order management requests: {e}")
            return 0
    
    async def _get_order_management_requests(self) -> List[Dict[str, Any]]:
        """Get order management requests from Redis."""
        try:
            # Get order management requests from Redis
            order_requests = await self.redis_conn.lrange("orders:management_requests", 0, 9)
            
            requests = []
            for request in order_requests:
                try:
                    requests.append(json.loads(request))
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid order management request format: {request}")
            
            return requests
            
        except Exception as e:
            self.logger.error(f"Error getting order management requests: {e}")
            return []
    
    async def _process_order_management_request(self, request: Dict[str, Any]) -> bool:
        """Process a single order management request."""
        try:
            request_type = request.get("type", "unknown")
            
            # Process order management based on type
            if request_type == "order_creation":
                return await self._create_order(request)
            elif request_type == "order_modification":
                return await self._modify_order(request)
            elif request_type == "order_cancellation":
                return await self._cancel_order(request)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error processing order management request: {e}")
            return False
    
    async def _create_order(self, request: Dict[str, Any]) -> bool:
        """Create an order."""
        try:
            order_data = request.get("order_data", {})
            
            # Create order using order manager
            order_result = await self.order_manager.create_order(order_data)
            
            if order_result:
                # Publish order creation result
                await self._publish_order_result("creation", order_data, order_result)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error creating order: {e}")
            return False
    
    async def _modify_order(self, request: Dict[str, Any]) -> bool:
        """Modify an order."""
        try:
            order_id = request.get("order_id", "unknown")
            modification_data = request.get("modification_data", {})
            
            # Modify order using order manager
            modification_result = await self.order_manager.modify_order(order_id, modification_data)
            
            if modification_result:
                # Publish order modification result
                await self._publish_order_result("modification", request, modification_result)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error modifying order: {e}")
            return False
    
    async def _cancel_order(self, request: Dict[str, Any]) -> bool:
        """Cancel an order."""
        try:
            order_id = request.get("order_id", "unknown")
            
            # Cancel order using order manager
            cancellation_result = await self.order_manager.cancel_order(order_id)
            
            if cancellation_result:
                # Publish order cancellation result
                await self._publish_order_result("cancellation", request, cancellation_result)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return False
    
    # ============= UTILITY METHODS =============
    
    def _update_strategy_state(self):
        """Update strategy state with current information."""
        try:
            # Update last strategy update timestamp
            self.strategy_state["last_strategy_update"] = time.time()
            
            # Clean up old learning events (older than 1 hour)
            current_time = time.time()
            self.strategy_state["learning_events"] = [
                event for event in self.strategy_state["learning_events"]
                if current_time - event.get("processed_time", 0) < 3600
            ]
            
        except Exception as e:
            self.logger.error(f"Error updating strategy state: {e}")
    
    async def _cleanup_strategy_components(self):
        """Cleanup strategy engine components."""
        try:
            # Cleanup strategy manager
            if self.strategy_manager:
                await self.strategy_manager.cleanup()
            
            # Cleanup optimization engine
            if self.optimization_engine:
                await self.optimization_engine.cleanup()
            
            # Cleanup learning coordinator
            if self.learning_coordinator:
                await self.learning_coordinator.cleanup()
            

            
            # Cleanup order manager
            if self.order_manager:
                await self.order_manager.cleanup()
            
            self.logger.info("✅ Strategy engine components cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up strategy components: {e}")
    
    # ============= PUBLISHING METHODS =============
    
    async def _publish_optimization_result(self, strategy: Dict[str, Any], result: Dict[str, Any]):
        """Publish optimization result."""
        try:
            optimization_update = {
                "strategy_id": strategy.get("strategy_id", "unknown"),
                "optimization_result": result,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("strategy_engine:optimization_results", 
                                        json.dumps(optimization_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing optimization result: {e}")
    

    
    async def _publish_order_result(self, operation: str, request: Dict[str, Any], result: Dict[str, Any]):
        """Publish order result."""
        try:
            order_update = {
                "operation": operation,
                "request": request,
                "result": result,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("strategy_engine:order_results", 
                                        json.dumps(order_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing order result: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_strategy_engine_status(self) -> Dict[str, Any]:
        """Get current strategy engine status."""
        return {
            "strategy_state": self.strategy_state,
            "stats": self.stats,
            "last_update": time.time()
        }
    
    async def get_active_strategies(self) -> Dict[str, Any]:
        """Get active strategies."""
        return self.strategy_state.get("active_strategies", {})
    
    async def get_strategy_performance(self) -> Dict[str, Any]:
        """Get strategy performance metrics."""
        return self.strategy_state.get("strategy_performance", {})
    
    async def get_optimization_queue(self) -> List[Dict[str, Any]]:
        """Get optimization queue."""
        return self.strategy_state.get("strategy_optimization_queue", [])
    
    async def submit_strategy_optimization_request(self, strategy: Dict[str, Any], priority: str = "medium") -> bool:
        """Submit a strategy optimization request."""
        try:
            optimization_request = {
                "strategy": strategy,
                "timestamp": time.time(),
                "priority": priority
            }
            
            # Add to strategy optimization queue (strategy parameters only, not costs)
            self.strategy_state["strategy_optimization_queue"].append(optimization_request)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting strategy optimization request: {e}")
            return False
    

    
    async def submit_order_management_request(self, request_type: str, data: Dict[str, Any]) -> bool:
        """Submit an order management request."""
        try:
            order_request = {
                "type": request_type,
                "data": data,
                "timestamp": time.time()
            }
            
            # Add to order management queue
            await self.redis_conn.lpush("orders:management_requests", json.dumps(order_request))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting order management request: {e}")
            return False
