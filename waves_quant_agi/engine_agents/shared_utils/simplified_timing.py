#!/usr/bin/env python3
"""
Simplified Timing Coordination System
Replaces the over-engineered 4-tier timing with clean, simple intervals.
"""

import asyncio
import time
from typing import Dict, Any, List, Callable, Coroutine
from enum import Enum

class TimingTier(Enum):
    """Simplified timing tiers."""
    REALTIME = 0.001    # 1ms - Ultra-fast operations
    FAST = 0.1          # 100ms - Fast operations  
    TACTICAL = 30       # 30s - Tactical operations
    STRATEGIC = 300     # 300s - Strategic operations

class SimplifiedTimingCoordinator:
    """Simplified timing coordinator for all agents."""
    
    def __init__(self):
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_registry: Dict[str, Dict[str, Any]] = {}
    
    def register_task(self, task_name: str, coro: Coroutine, tier: TimingTier, 
                     agent_name: str, auto_start: bool = True) -> str:
        """Register a task with simplified timing."""
        task_id = f"{agent_name}_{task_name}"
        
        self.task_registry[task_id] = {
            "name": task_name,
            "coro": coro,
            "tier": tier,
            "agent_name": agent_name,
            "interval": tier.value,
            "created_at": time.time()
        }
        
        if auto_start:
            self.start_task(task_id)
        
        return task_id
    
    def start_task(self, task_id: str):
        """Start a registered task."""
        if task_id not in self.task_registry:
            raise ValueError(f"Task {task_id} not registered")
        
        if task_id in self.active_tasks:
            return  # Already running
        
        task_info = self.task_registry[task_id]
        
        # Create the task with proper timing
        task = asyncio.create_task(
            self._run_timed_task(task_id, task_info),
            name=task_id
        )
        
        self.active_tasks[task_id] = task
    
    def stop_task(self, task_id: str):
        """Stop a running task."""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if not task.done():
                task.cancel()
            del self.active_tasks[task_id]
    
    def stop_all_tasks(self):
        """Stop all running tasks."""
        for task_id in list(self.active_tasks.keys()):
            self.stop_task(task_id)
    
    async def _run_timed_task(self, task_id: str, task_info: Dict[str, Any]):
        """Run a task with simplified timing."""
        try:
            while True:
                start_time = time.time()
                
                # Execute the task coroutine
                if asyncio.iscoroutine(task_info["coro"]):
                    await task_info["coro"]
                else:
                    # If it's a coroutine function, call it
                    await task_info["coro"]()
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Sleep for the remaining interval
                sleep_time = max(0, task_info["interval"] - execution_time)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    
        except asyncio.CancelledError:
            # Task was cancelled
            pass
        except Exception as e:
            print(f"Error in timed task {task_id}: {e}")
            # Continue running the task despite errors
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all tasks."""
        status = {}
        for task_id, task_info in self.task_registry.items():
            is_running = task_id in self.active_tasks
            task = self.active_tasks.get(task_id)
            
            status[task_id] = {
                "name": task_info["name"],
                "agent_name": task_info["agent_name"],
                "tier": task_info["tier"].name,
                "interval": task_info["interval"],
                "is_running": is_running,
                "created_at": task_info["created_at"],
                "task_status": task.status() if task else "not_started"
            }
        
        return status

# Global timing coordinator instance
_timing_coordinator: SimplifiedTimingCoordinator = None

def get_timing_coordinator() -> SimplifiedTimingCoordinator:
    """Get the global timing coordinator instance."""
    global _timing_coordinator
    
    if _timing_coordinator is None:
        _timing_coordinator = SimplifiedTimingCoordinator()
    
    return _timing_coordinator

def register_timed_task(task_name: str, coro: Coroutine, tier: TimingTier, 
                       agent_name: str, auto_start: bool = True) -> str:
    """Register a timed task."""
    return get_timing_coordinator().register_task(task_name, coro, tier, agent_name, auto_start)

# Add static method for shared access
@staticmethod
def get_shared_timing_coordinator():
    """Get shared timing coordinator instance - static method for external access."""
    return get_timing_coordinator()
