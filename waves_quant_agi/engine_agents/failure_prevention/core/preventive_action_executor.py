#!/usr/bin/env python3
"""
Preventive Action Executor - Failure Prevention Actions
Executes preventive actions to prevent system failures and maintain stability.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable
from ...shared_utils import get_shared_logger

class PreventiveAction:
    """Represents a preventive action to be executed."""
    
    def __init__(self, action_id: str, action_type: str, description: str, 
                 priority: str = "medium", timeout: float = 30.0):
        self.action_id = action_id
        self.action_type = action_type
        self.description = description
        self.priority = priority
        self.timeout = timeout
        self.created_time = time.time()
        self.execution_time = None
        self.status = "pending"  # pending, executing, completed, failed
        self.result = None
        self.error = None

class PreventiveActionExecutor:
    """Executes preventive actions to prevent system failures."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("failure_prevention", "preventive_action_executor")
        
        # Execution configuration
        self.max_concurrent_actions = config.get("max_concurrent_actions", 5)
        self.action_timeout = config.get("action_timeout", 30.0)  # seconds
        self.retry_attempts = config.get("retry_attempts", 3)
        self.retry_delay = config.get("retry_delay", 5.0)  # seconds
        
        # Action management
        self.pending_actions: List[PreventiveAction] = []
        self.executing_actions: Dict[str, PreventiveAction] = {}
        self.completed_actions: List[PreventiveAction] = []
        self.failed_actions: List[PreventiveAction] = []
        
        # Execution state
        self.is_executing = False
        self.execution_task = None
        self.action_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "total_execution_time": 0.0,
            "start_time": time.time()
        }
        
        self.logger.info("Preventive Action Executor initialized")
    
    async def start_execution(self):
        """Start the preventive action execution loop."""
        if self.is_executing:
            return
        
        self.is_executing = True
        self.execution_task = asyncio.create_task(self._execution_loop())
        self.logger.info("Preventive action execution started")
    
    async def stop_execution(self):
        """Stop the preventive action execution loop."""
        self.is_executing = False
        if self.execution_task:
            self.execution_task.cancel()
            try:
                await self.execution_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Preventive action execution stopped")
    
    async def _execution_loop(self):
        """Main execution loop for preventive actions."""
        while self.is_executing:
            try:
                # Check for pending actions
                await self._process_pending_actions()
                
                # Monitor executing actions
                await self._monitor_executing_actions()
                
                # Clean up old completed actions
                await self._cleanup_old_actions()
                
                await asyncio.sleep(1.0)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in execution loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_pending_actions(self):
        """Process pending actions."""
        try:
            # Check if we can execute more actions
            if len(self.executing_actions) >= self.max_concurrent_actions:
                return
            
            # Get next action to execute
            next_action = self._get_next_action()
            if not next_action:
                return
            
            # Execute the action
            await self._execute_action(next_action)
            
        except Exception as e:
            self.logger.error(f"Error processing pending actions: {e}")
    
    def _get_next_action(self) -> Optional[PreventiveAction]:
        """Get next action to execute based on priority."""
        try:
            if not self.pending_actions:
                return None
            
            # Sort by priority (high, medium, low)
            priority_order = {"high": 0, "medium": 1, "low": 2}
            
            # Sort by priority and creation time
            sorted_actions = sorted(
                self.pending_actions,
                key=lambda x: (priority_order.get(x.priority, 3), x.created_time)
            )
            
            return sorted_actions[0]
            
        except Exception as e:
            self.logger.error(f"Error getting next action: {e}")
            return None
    
    async def _execute_action(self, action: PreventiveAction):
        """Execute a preventive action."""
        try:
            # Move to executing state
            self.pending_actions.remove(action)
            self.executing_actions[action.action_id] = action
            action.status = "executing"
            action.execution_time = time.time()
            
            self.logger.info(f"Executing preventive action: {action.description}")
            
            # Execute the action
            result = await self._perform_action(action)
            
            # Update action status
            if result:
                action.status = "completed"
                action.result = result
                self.stats["successful_actions"] += 1
                self.logger.info(f"Preventive action completed: {action.description}")
            else:
                action.status = "failed"
                action.error = "Action execution failed"
                self.stats["failed_actions"] += 1
                self.logger.error(f"Preventive action failed: {action.description}")
            
            # Move to completed/failed list
            self.executing_actions.pop(action.action_id)
            if action.status == "completed":
                self.completed_actions.append(action)
            else:
                self.failed_actions.append(action)
            
            # Update statistics
            if action.execution_time:
                execution_duration = time.time() - action.execution_time
                self.stats["total_execution_time"] += execution_duration
            
        except Exception as e:
            self.logger.error(f"Error executing action {action.action_id}: {e}")
            action.status = "failed"
            action.error = str(e)
            self.stats["failed_actions"] += 1
            
            # Move to failed list
            self.executing_actions.pop(action.action_id, None)
            self.failed_actions.append(action)
    
    async def _perform_action(self, action: PreventiveAction) -> bool:
        """Perform the actual preventive action."""
        try:
            # Get action handler
            handler = self.action_handlers.get(action.action_type)
            if not handler:
                self.logger.warning(f"No handler for action type: {action.action_type}")
                return False
            
            # Execute with timeout
            try:
                result = await asyncio.wait_for(
                    handler(action), 
                    timeout=action.timeout
                )
                return result
            except asyncio.TimeoutError:
                self.logger.error(f"Action {action.action_id} timed out")
                return False
                
        except Exception as e:
            self.logger.error(f"Error performing action {action.action_id}: {e}")
            return False
    
    async def _monitor_executing_actions(self):
        """Monitor executing actions for timeouts."""
        try:
            current_time = time.time()
            timed_out_actions = []
            
            for action_id, action in self.executing_actions.items():
                if action.execution_time and (current_time - action.execution_time) > action.timeout:
                    timed_out_actions.append(action_id)
            
            # Handle timed out actions
            for action_id in timed_out_actions:
                action = self.executing_actions[action_id]
                action.status = "failed"
                action.error = "Action timed out"
                self.stats["failed_actions"] += 1
                
                self.logger.error(f"Action {action_id} timed out: {action.description}")
                
                # Move to failed list
                self.executing_actions.pop(action_id)
                self.failed_actions.append(action)
                
        except Exception as e:
            self.logger.error(f"Error monitoring executing actions: {e}")
    
    async def _cleanup_old_actions(self):
        """Clean up old completed and failed actions."""
        try:
            current_time = time.time()
            max_age = 3600  # 1 hour
            
            # Clean up completed actions
            self.completed_actions = [
                action for action in self.completed_actions
                if (current_time - action.created_time) < max_age
            ]
            
            # Clean up failed actions
            self.failed_actions = [
                action for action in self.failed_actions
                if (current_time - action.created_time) < max_age
            ]
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old actions: {e}")
    
    def add_action(self, action: PreventiveAction):
        """Add a preventive action to the queue."""
        try:
            self.pending_actions.append(action)
            self.stats["total_actions"] += 1
            self.logger.info(f"Added preventive action: {action.description}")
            
        except Exception as e:
            self.logger.error(f"Error adding action: {e}")
    
    def register_action_handler(self, action_type: str, handler: Callable):
        """Register a handler for a specific action type."""
        try:
            self.action_handlers[action_type] = handler
            self.logger.info(f"Registered handler for action type: {action_type}")
            
        except Exception as e:
            self.logger.error(f"Error registering action handler: {e}")
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        return {
            "is_executing": self.is_executing,
            "pending_actions": len(self.pending_actions),
            "executing_actions": len(self.executing_actions),
            "completed_actions": len(self.completed_actions),
            "failed_actions": len(self.failed_actions),
            "max_concurrent_actions": self.max_concurrent_actions,
            "stats": self.stats
        }
    
    def get_action_history(self, action_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get action execution history."""
        try:
            all_actions = self.completed_actions + self.failed_actions
            
            if action_type:
                all_actions = [action for action in all_actions if action.action_type == action_type]
            
            # Sort by execution time (most recent first)
            sorted_actions = sorted(all_actions, key=lambda x: x.execution_time or 0, reverse=True)
            
            # Convert to dictionary format
            history = []
            for action in sorted_actions[:limit]:
                history.append({
                    "action_id": action.action_id,
                    "action_type": action.action_type,
                    "description": action.description,
                    "status": action.status,
                    "result": action.result,
                    "error": action.error,
                    "created_time": action.created_time,
                    "execution_time": action.execution_time
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting action history: {e}")
            return []
    
    def set_execution_parameters(self, max_concurrent: int, timeout: float, retry_attempts: int, retry_delay: float):
        """Set execution parameters."""
        try:
            self.max_concurrent_actions = max_concurrent
            self.action_timeout = timeout
            self.retry_attempts = retry_attempts
            self.retry_delay = retry_delay
            
            self.logger.info(f"Execution parameters updated: max_concurrent={max_concurrent}, timeout={timeout}s, retry_attempts={retry_attempts}, retry_delay={retry_delay}s")
            
        except Exception as e:
            self.logger.error(f"Error setting execution parameters: {e}")
    
    async def initialize_actions(self):
        """Initialize preventive actions and handlers."""
        try:
            self.logger.info("✅ Preventive actions initialized")
            self.logger.info(f"✅ Max concurrent actions: {self.max_concurrent_actions}")
            self.logger.info(f"✅ Action timeout: {self.action_timeout}s")
            self.logger.info(f"✅ Retry attempts: {self.retry_attempts}")
            
            # Initialize default action handlers
            self.action_handlers = {
                "system_cleanup": self._execute_system_cleanup,
                "memory_optimization": self._execute_memory_optimization,
                "connection_reset": self._execute_connection_reset,
                "cache_cleanup": self._execute_cache_cleanup,
                "resource_balancing": self._execute_resource_balancing
            }
            
            # Clear existing actions
            self.pending_actions.clear()
            self.executing_actions.clear()
            self.completed_actions.clear()
            self.failed_actions.clear()
            
            # Reset statistics
            self.stats = {
                "total_actions": 0,
                "successful_actions": 0,
                "failed_actions": 0,
                "total_execution_time": 0.0,
                "start_time": time.time()
            }
            
            self.logger.info(f"✅ Initialized {len(self.action_handlers)} action handlers")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing preventive actions: {e}")
            raise
    
    async def _execute_system_cleanup(self, action: PreventiveAction) -> Dict[str, Any]:
        """Execute system cleanup action."""
        self.logger.info("Executing system cleanup action")
        await asyncio.sleep(0.1)  # Simulate cleanup
        return {"status": "completed", "details": "System cleanup completed"}
    
    async def _execute_memory_optimization(self, action: PreventiveAction) -> Dict[str, Any]:
        """Execute memory optimization action."""
        self.logger.info("Executing memory optimization action")
        await asyncio.sleep(0.1)  # Simulate optimization
        return {"status": "completed", "details": "Memory optimization completed"}
    
    async def _execute_connection_reset(self, action: PreventiveAction) -> Dict[str, Any]:
        """Execute connection reset action."""
        self.logger.info("Executing connection reset action")
        await asyncio.sleep(0.1)  # Simulate reset
        return {"status": "completed", "details": "Connection reset completed"}
    
    async def _execute_cache_cleanup(self, action: PreventiveAction) -> Dict[str, Any]:
        """Execute cache cleanup action."""
        self.logger.info("Executing cache cleanup action")
        await asyncio.sleep(0.1)  # Simulate cleanup
        return {"status": "completed", "details": "Cache cleanup completed"}
    
    async def _execute_resource_balancing(self, action: PreventiveAction) -> Dict[str, Any]:
        """Execute resource balancing action."""
        self.logger.info("Executing resource balancing action")
        await asyncio.sleep(0.1)  # Simulate balancing
        return {"status": "completed", "details": "Resource balancing completed"}
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            await self.stop_execution()
            self.pending_actions.clear()
            self.executing_actions.clear()
            self.completed_actions.clear()
            self.failed_actions.clear()
            self.action_handlers.clear()
            self.logger.info("Preventive Action Executor cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
