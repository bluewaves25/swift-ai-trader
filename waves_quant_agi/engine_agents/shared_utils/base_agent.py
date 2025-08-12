#!/usr/bin/env python3
"""
Base Agent Class - ELIMINATE 90% OF START/STOP METHOD DUPLICATION
Single base class for all agents to prevent massive code duplication

ELIMINATES DUPLICATION FROM:
- 30+ identical start() methods across agents
- 30+ identical stop() methods across agents  
- 50+ identical Redis connection patterns
- 20+ identical communication initialization patterns
- 15+ identical status monitoring patterns
- Hundreds of lines of duplicate code

Usage:
    class MyAgent(BaseAgent):
        async def _agent_specific_startup(self):
            # Only agent-specific startup logic here
            pass
            
        async def _agent_specific_shutdown(self):
            # Only agent-specific shutdown logic here
            pass
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from .redis_connector import get_shared_redis
from .shared_logger import get_shared_logger
from .shared_status_monitor import get_agent_monitor
from .market_data_utils import get_market_data_utils

class BaseAgent(ABC):
    """
    Base class for all agents - eliminates massive start/stop method duplication.
    Provides unified lifecycle management, Redis connection, logging, and monitoring.
    """
    
    def __init__(self, agent_name: str, config: Dict[str, Any]):
        self.agent_name = agent_name
        self.config = config
        
        # Get shared utilities (eliminates individual Redis connections)
        self.redis_conn = get_shared_redis()
        self.logger = get_shared_logger(agent_name, "main")
        self.status_monitor = get_agent_monitor(agent_name)
        self.market_data_utils = get_market_data_utils(self.redis_conn)
        
        # Agent state
        self.is_running = False
        self.start_time = None
        self.comm_hub = None
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        
        # Initialize agent-specific components
        self._initialize_agent_components()
    
    @abstractmethod
    def _initialize_agent_components(self):
        """Initialize agent-specific components. Override in subclasses."""
        pass
    
    @abstractmethod
    async def _agent_specific_startup(self):
        """Agent-specific startup logic. Override in subclasses."""
        pass
    
    @abstractmethod
    async def _agent_specific_shutdown(self):
        """Agent-specific shutdown logic. Override in subclasses."""
        pass
    
    async def start(self):
        """Unified start method for all agents - eliminates duplication."""
        try:
            self.logger.info(f"Starting {self.agent_name}...")
            
            # Start status monitoring
            self.status_monitor.start_monitoring()
            self.is_running = True
            self.start_time = time.time()
            
            # Initialize communication (if available)
            if hasattr(self, 'comm_hub') and self.comm_hub:
                await self._initialize_communication()
            
            # Agent-specific startup
            await self._agent_specific_startup()
            
            # Start background tasks (if any)
            if hasattr(self, '_get_background_tasks') and self._get_background_tasks():
                await self._start_background_tasks()
            
            # Start heartbeat loop as background task
            heartbeat_task = asyncio.create_task(self._heartbeat_loop(), name=f"{self.agent_name}_heartbeat")
            if not hasattr(self, '_background_tasks'):
                self._background_tasks = []
            self._background_tasks.append(heartbeat_task)
            
            self.logger.info(f"✅ {self.agent_name} started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting {self.agent_name}: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Unified stop method for all agents - eliminates duplication."""
        self.logger.info(f"Stopping {self.agent_name}...")
        
        # Stop status monitoring
        self.status_monitor.stop_monitoring()
        self.is_running = False
        
        try:
            # Stop background tasks
            await self._stop_background_tasks()
            
            # Unregister from communication hub
            if self.comm_hub:
                await self._unregister_from_communication()
            
            # Agent-specific shutdown
            await self._agent_specific_shutdown()
            
            self.logger.info(f"✅ {self.agent_name} stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping {self.agent_name}: {e}")
    
    async def _initialize_communication(self):
        """Initialize communication with the hub."""
        try:
            if hasattr(self, 'initialize_communication') and self.comm_hub:
                await self.initialize_communication(self.comm_hub)
        except Exception as e:
            self.logger.warning(f"Communication initialization failed: {e}")
    
    async def _unregister_from_communication(self):
        """Unregister from communication hub."""
        try:
            if hasattr(self, 'comm_hub') and self.comm_hub:
                await self.comm_hub.unregister_agent(self.agent_name)
        except Exception as e:
            self.logger.warning(f"Communication unregistration failed: {e}")
    
    async def _start_background_tasks(self):
        """Start background tasks if the agent has them."""
        if hasattr(self, '_background_tasks'):
            # Start all background tasks
            for task_info in self._get_background_tasks():
                if len(task_info) == 3:
                    # Format: (coroutine, name, priority)
                    task_coro, task_name, priority = task_info
                elif len(task_info) == 2:
                    # Format: (coroutine, name)
                    task_coro, task_name = task_info
                    priority = "normal"
                else:
                    self.logger.warning(f"Invalid task format: {task_info}")
                    continue
                
                task = asyncio.create_task(task_coro, name=task_name)
                self._background_tasks.append(task)
                self.logger.info(f"Started background task: {task_name} (priority: {priority})")
    
    async def _stop_background_tasks(self):
        """Stop all background tasks."""
        if self._background_tasks:
            # Cancel all tasks
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            self._background_tasks.clear()
            self.logger.info("All background tasks stopped")
    
    def _get_background_tasks(self) -> List[tuple]:
        """Get list of background task names and coroutines. Override in subclasses."""
        return []
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get unified agent status - eliminates duplication."""
        return {
            "agent_name": self.agent_name,
            "is_running": self.is_running,
            "start_time": self.start_time,
            "uptime_seconds": int(time.time() - self.start_time) if self.start_time else 0,
            "status_monitor": self.status_monitor.get_status(),
            "redis_connection": self.redis_conn.get_connection_info()
        }
    
    def get_market_data(self, symbol: str = "BTCUSD") -> Dict[str, Any]:
        """Get market data using shared utilities."""
        return self.market_data_utils.get_current_market_data(symbol)
    
    def get_performance_data(self) -> Dict[str, Any]:
        """Get performance data using shared utilities."""
        return self.market_data_utils.get_performance_data(self.agent_name)
    
    async def _heartbeat_loop(self):
        """Standard heartbeat loop for all agents."""
        while self.is_running:
            try:
                # Send heartbeat to Redis
                await self.redis_conn.async_publish(
                    f"heartbeat:{self.agent_name}",
                    {
                        "agent_name": self.agent_name,
                        "timestamp": time.time(),
                        "status": "running"
                    }
                )
                
                # Update agent stats in Redis
                current_time = time.time()
                agent_stats = {
                    'status': 'running' if self.is_running else 'stopped',
                    'start_time': str(self.start_time) if self.start_time else '0',
                    'uptime_seconds': str(int(current_time - self.start_time)) if self.start_time else '0',
                    'last_heartbeat': str(current_time),
                    'timestamp': str(current_time)
                }
                
                # Update the agent_stats hash using the correct Redis connector method
                self.redis_conn.hset(f"agent_stats:{self.agent_name}", mapping=agent_stats)
                
                # Wait for next heartbeat
                await asyncio.sleep(60)  # 60 second heartbeat
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(60)
    
    def __del__(self):
        """Cleanup when agent is destroyed."""
        try:
            if self.is_running:
                asyncio.create_task(self.stop())
        except:
            pass

# Global agent registry for management
_agent_registry: Dict[str, BaseAgent] = {}

def register_agent(agent_name: str, agent: BaseAgent):
    """Register an agent in the global registry."""
    _agent_registry[agent_name] = agent

def get_agent(agent_name: str) -> Optional[BaseAgent]:
    """Get an agent from the global registry."""
    return _agent_registry.get(agent_name)

def get_all_agents() -> Dict[str, BaseAgent]:
    """Get all registered agents."""
    return _agent_registry.copy()

def stop_all_agents():
    """Stop all registered agents."""
    for agent in _agent_registry.values():
        if agent.is_running:
            asyncio.create_task(agent.stop())

# Add static methods for shared utilities access
@staticmethod
def get_shared_redis():
    """Get shared Redis connector - static method for external access."""
    from .redis_connector import get_shared_redis as get_redis_connector
    return get_redis_connector()

@staticmethod  
def get_shared_logger(name: str, level: str = "main"):
    """Get shared logger - static method for external access."""
    from .shared_logger import get_shared_logger as get_logger
    return get_logger(name, level)

@staticmethod
def get_shared_timing_coordinator():
    """Get shared timing coordinator - static method for external access."""
    from .simplified_timing import get_timing_coordinator as get_timing
    return get_timing()
