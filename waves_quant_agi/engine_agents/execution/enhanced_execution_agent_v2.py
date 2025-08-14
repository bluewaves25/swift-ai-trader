#!/usr/bin/env python3
"""
Enhanced Execution Agent V2 - ROLE CONSOLIDATED: ORDER EXECUTION ONLY
Removed order management functionality - now handled by Strategy Engine Agent.
Focuses exclusively on order execution, slippage management, and execution optimization.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from engine_agents.shared_utils.base_agent import BaseAgent
from .python_bridge import ExecutionBridge

class EnhancedExecutionAgentV2(BaseAgent):
    """
    Enhanced execution agent - focused solely on order execution.
    Inherits from BaseAgent to eliminate infrastructure duplication.
    """
    
    def _initialize_agent_components(self):
        """Initialize execution-specific components."""
        # Initialize execution components
        self.execution_bridge = None
        self.slippage_manager = None
        self.execution_optimizer = None
        
        # Execution state
        self.execution_state = {
            "active_executions": {},
            "execution_history": [],
            "last_execution_time": None
        }
        
        # Execution statistics
        self.execution_stats = {
            "total_signals_processed": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "execution_timeouts": 0,
            "slippage_events": 0,
            "start_time": time.time()
        }
        
        # Execution configuration
        self.execution_config = {
            "max_slippage": self.config.get("max_slippage", 0.001),
            "execution_timeout": self.config.get("execution_timeout", 30),
            "retry_attempts": self.config.get("retry_attempts", 3),
            "batch_size": self.config.get("batch_size", 10)
        }
        
        # Register this agent
        from engine_agents.shared_utils import register_agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Initialize execution-specific components."""
        try:
            # Initialize execution bridge
            await self._initialize_execution_bridge()
            
            # Initialize slippage management
            await self._initialize_slippage_management()
            
            # Initialize execution optimization
            await self._initialize_execution_optimization()
            
            self.logger.info("✅ Execution agent initialization completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in execution startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Shutdown execution-specific components."""
        try:
            # Cleanup execution components
            await self._cleanup_execution_components()
            
            self.logger.info("✅ Execution agent shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in execution shutdown: {e}")
    
    # ============= BACKGROUND TASKS =============
    
    async def _order_execution_loop(self):
        """Order execution loop."""
        while self.is_running:
            try:
                # Execute orders
                await self._execute_orders()
                
                await asyncio.sleep(0.1)  # 100ms cycle
                
            except Exception as e:
                self.logger.error(f"Error in order execution loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _execution_health_monitoring_loop(self):
        """Execution health monitoring loop."""
        while self.is_running:
            try:
                # Monitor execution health
                await self._monitor_execution_health()
                
                await asyncio.sleep(2.0)  # 2 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in execution health monitoring loop: {e}")
                await asyncio.sleep(2.0)
    
    async def _execution_reporting_loop(self):
        """Execution reporting loop."""
        while self.is_running:
            try:
                # Report execution status
                await self._report_execution_status()
                
                await asyncio.sleep(30.0)  # 30 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in execution reporting loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _execute_orders(self):
        """Execute orders."""
        try:
            # Placeholder for order execution
            pass
        except Exception as e:
            self.logger.error(f"Error executing orders: {e}")
    
    async def _monitor_execution_health(self):
        """Monitor execution health."""
        try:
            # Placeholder for execution health monitoring
            pass
        except Exception as e:
            self.logger.error(f"Error monitoring execution health: {e}")
    
    async def _report_execution_status(self):
        """Report execution status."""
        try:
            # Placeholder for execution status reporting
            pass
        except Exception as e:
            self.logger.error(f"Error reporting execution status: {e}")

    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._order_execution_loop, "Order Execution", "fast"),
            (self._slippage_monitoring_loop, "Slippage Monitoring", "fast"),
            (self._execution_health_monitoring_loop, "Execution Health Monitoring", "tactical"),
            (self._execution_reporting_loop, "Execution Reporting", "strategic")
        ]
    
    # ============= EXECUTION INITIALIZATION =============
    
    async def _initialize_execution_bridge(self):
        """Initialize execution bridge."""
        try:
            # Initialize execution bridge
            self.execution_bridge = ExecutionBridge(self.config)
            
            self.logger.info("✅ Execution bridge initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing execution bridge: {e}")
            raise
    
    async def _initialize_slippage_management(self):
        """Initialize slippage management."""
        try:
            # Initialize slippage manager
            from .core.slippage_manager import SlippageManager
            self.slippage_manager = SlippageManager(self.config)
            
            self.logger.info("✅ Slippage management initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing slippage management: {e}")
            raise
    
    async def _initialize_execution_optimization(self):
        """Initialize execution optimization."""
        try:
            # Initialize execution optimizer
            from .core.execution_optimizer import ExecutionOptimizer
            self.execution_optimizer = ExecutionOptimizer(self.config)
            
            self.logger.info("✅ Execution optimization initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing execution optimization: {e}")
            raise
    
    # ============= EXECUTION PROCESSING LOOP =============
    
    async def _execution_processing_loop(self):
        """Execution monitoring loop (100ms intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Monitor execution status and health
                await self._monitor_execution_status()
                
                # Record operation
                duration_ms = (time.time() - start_time) * 1000
                if hasattr(self, 'status_monitor') and self.status_monitor:
                    self.status_monitor.record_operation(duration_ms, True)
                
                await asyncio.sleep(0.1)  # 100ms for execution monitoring
                
            except Exception as e:
                self.logger.error(f"Error in execution monitoring loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _monitor_execution_status(self):
        """Monitor execution status and health."""
        try:
            # Update last execution time
            if self.execution_state["execution_history"]:
                self.execution_state["last_execution_time"] = self.execution_state["execution_history"][-1]["timestamp"]
            
            # Check execution bridge health
            if self.execution_bridge:
                bridge_status = await self.execution_bridge.get_status()
                if not bridge_status.get("healthy", False):
                    self.logger.warning("Execution bridge health check failed")
            
            # Clean up old active executions
            current_time = time.time()
            expired_executions = []
            for exec_id, exec_data in self.execution_state["active_executions"].items():
                if current_time - exec_data.get("start_time", 0) > 300:  # 5 minutes
                    expired_executions.append(exec_id)
            
            for exec_id in expired_executions:
                del self.execution_state["active_executions"][exec_id]
                
        except Exception as e:
            self.logger.error(f"Error monitoring execution status: {e}")
    
    async def _execute_order(self, order_data: Dict[str, Any], strategy_type: str) -> Dict[str, Any]:
        """Execute an order using the execution bridge."""
        try:
            if not self.execution_bridge:
                return {"success": False, "error": "Execution bridge not available"}
            
            # Execute order
            execution_result = await self.execution_bridge.execute_order(order_data, strategy_type)
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Error executing order: {e}")
            return {"success": False, "error": str(e)}
    
    # ============= SLIPPAGE MONITORING LOOP =============
    
    async def _slippage_monitoring_loop(self):
        """Slippage monitoring loop (100ms intervals)."""
        while self.is_running:
            try:
                # Monitor for slippage events
                slippage_events = await self._monitor_slippage_events()
                
                # Update slippage statistics
                if slippage_events > 0:
                    self.execution_stats["slippage_events"] += slippage_events
                
                await asyncio.sleep(0.1)  # 100ms for slippage monitoring
                
            except Exception as e:
                self.logger.error(f"Error in slippage monitoring loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _monitor_slippage_events(self) -> int:
        """Monitor for slippage events and return count."""
        try:
            slippage_events = 0
            
            if not self.slippage_manager:
                return 0
            
            # Check for new slippage events
            events = await self.slippage_manager.check_slippage_events()
            
            # Process slippage events
            for event in events:
                await self._process_slippage_event(event)
                slippage_events += 1
            
            return slippage_events
            
        except Exception as e:
            self.logger.error(f"Error monitoring slippage events: {e}")
            return 0
    
    async def _process_slippage_event(self, slippage_event: Dict[str, Any]):
        """Process a slippage event."""
        try:
            # Log slippage event
            self.logger.warning(f"Slippage event detected: {slippage_event.get('type', 'unknown')}")
            
            # Check if slippage exceeds threshold
            slippage_amount = slippage_event.get("amount", 0.0)
            threshold = self.execution_config.get("max_slippage", 0.001)
            
            if slippage_amount > threshold:
                # Trigger slippage alert
                await self._trigger_slippage_alert(slippage_event)
            
            # Publish slippage update
            await self._publish_slippage_update(slippage_event)
            
        except Exception as e:
            self.logger.error(f"Error processing slippage event: {e}")
    
    # ============= EXECUTION OPTIMIZATION LOOP =============
    
    async def _execution_optimization_loop(self):
        """Execution optimization loop (30s intervals)."""
        while self.is_running:
            try:
                # Perform execution optimization
                optimization_results = await self._perform_execution_optimization()
                
                # Apply optimization recommendations
                if optimization_results:
                    await self._apply_optimization_recommendations(optimization_results)
                
                await asyncio.sleep(30)  # 30s for execution optimization
                
            except Exception as e:
                self.logger.error(f"Error in execution optimization loop: {e}")
                await asyncio.sleep(30)
    
    async def _perform_execution_optimization(self) -> Dict[str, Any]:
        """Perform execution optimization."""
        try:
            if not self.execution_optimizer:
                return {}
            
            # Get execution performance data
            performance_data = {
                "execution_history": self.execution_state["execution_history"],
                "execution_stats": self.execution_stats,
                "execution_config": self.execution_config
            }
            
            # Perform optimization analysis
            optimization_results = await self.execution_optimizer.optimize_execution(performance_data)
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Error performing execution optimization: {e}")
            return {}
    
    async def _apply_optimization_recommendations(self, optimization_results: Dict[str, Any]):
        """Apply optimization recommendations."""
        try:
            recommendations = optimization_results.get("recommendations", [])
            
            for recommendation in recommendations:
                recommendation_type = recommendation.get("type", "unknown")
                
                if recommendation_type == "slippage_threshold":
                    await self._apply_slippage_threshold_optimization(recommendation)
                elif recommendation_type == "execution_timeout":
                    await self._apply_execution_timeout_optimization(recommendation)
                elif recommendation_type == "batch_size":
                    await self._apply_batch_size_optimization(recommendation)
            
        except Exception as e:
            self.logger.error(f"Error applying optimization recommendations: {e}")
    
    async def _apply_slippage_threshold_optimization(self, recommendation: Dict[str, Any]):
        """Apply slippage threshold optimization."""
        try:
            new_threshold = recommendation.get("value", 0.001)
            self.execution_config["max_slippage"] = new_threshold
            
            self.logger.info(f"Slippage threshold optimized to: {new_threshold}")
            
        except Exception as e:
            self.logger.error(f"Error applying slippage threshold optimization: {e}")
    
    async def _apply_execution_timeout_optimization(self, recommendation: Dict[str, Any]):
        """Apply execution timeout optimization."""
        try:
            new_timeout = recommendation.get("value", 30)
            self.execution_config["execution_timeout"] = new_timeout
            
            self.logger.info(f"Execution timeout optimized to: {new_timeout}")
            
        except Exception as e:
            self.logger.error(f"Error applying execution timeout optimization: {e}")
    
    async def _apply_batch_size_optimization(self, recommendation: Dict[str, Any]):
        """Apply batch size optimization."""
        try:
            new_batch_size = recommendation.get("value", 10)
            self.execution_config["batch_size"] = new_batch_size
            
            self.logger.info(f"Batch size optimized to: {new_batch_size}")
            
        except Exception as e:
            self.logger.error(f"Error applying batch size optimization: {e}")
    
    # ============= UTILITY METHODS =============
    
    async def _cleanup_execution_components(self):
        """Cleanup execution components."""
        try:
            # Cleanup execution bridge
            if self.execution_bridge:
                await self.execution_bridge.stop()
            
            # Cleanup slippage manager
            if self.slippage_manager:
                await self.slippage_manager.cleanup()
            
            # Cleanup execution optimizer
            if self.execution_optimizer:
                await self.execution_optimizer.cleanup()
            
            self.logger.info("✅ Execution components cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up execution components: {e}")
    
    # ============= PUBLISHING METHODS =============
    
    async def _publish_execution_result(self, execution_id: str, result: Dict[str, Any]):
        """Publish execution result."""
        try:
            execution_update = {
                "execution_id": execution_id,
                "result": result,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("execution:results", json.dumps(execution_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing execution result: {e}")
    
    async def _trigger_slippage_alert(self, slippage_event: Dict[str, Any]):
        """Trigger slippage alert."""
        try:
            alert_data = {
                "alert_type": "slippage_alert",
                "slippage_data": slippage_event,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("execution:slippage_alerts", json.dumps(alert_data))
            
        except Exception as e:
            self.logger.error(f"Error triggering slippage alert: {e}")
    
    async def _publish_slippage_update(self, slippage_event: Dict[str, Any]):
        """Publish slippage update."""
        try:
            slippage_update = {
                "slippage_event": slippage_event,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("execution:slippage_updates", json.dumps(slippage_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing slippage update: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        return {
            "execution_state": self.execution_state,
            "execution_stats": self.execution_stats,
            "execution_config": self.execution_config,
            "last_update": time.time()
        }
    
    async def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return self.execution_state.get("execution_history", [])
    
    async def get_active_executions(self) -> Dict[str, Any]:
        """Get active executions."""
        return self.execution_state.get("active_executions", {})
    
    async def execute_order_request(self, order_data: Dict[str, Any], strategy_type: str = "general") -> Dict[str, Any]:
        """Execute an order request (called by Strategy Engine)."""
        try:
            execution_id = f"exec_{int(time.time() * 1000)}_{len(self.execution_state['execution_history'])}"
            
            # Execute the order directly
            execution_result = await self._execute_order(order_data, strategy_type)
            
            # Store execution result
            self.execution_state["execution_history"].append({
                "execution_id": execution_id,
                "order_data": order_data,
                "result": execution_result,
                "timestamp": time.time()
            })
            
            # Update statistics
            self.execution_stats["total_signals_processed"] += 1
            if execution_result.get("success", False):
                self.execution_stats["successful_executions"] += 1
            else:
                self.execution_stats["failed_executions"] += 1
            
            # Publish execution result
            await self._publish_execution_result(execution_id, execution_result)
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Error executing order request: {e}")
            return {"success": False, "error": str(e)}
