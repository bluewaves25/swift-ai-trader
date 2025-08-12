#!/usr/bin/env python3
"""
Communication Hub - Central Nervous System for All Agents
Handles inter-agent communication, signal routing, and coordination.
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, List, Optional, Callable

from ..shared_utils.base_agent import BaseAgent

class CommunicationHub(BaseAgent):
    """Central communication hub for all agents and trading engine."""
    
    def __init__(self, agent_name: str, config: Dict[str, Any]):
        # Call parent constructor
        super().__init__(agent_name, config)
        
        # Agent registrations
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.signal_handlers: Dict[str, List[Callable]] = {}
        
        # Communication channels
        self.channels = {
            "trading_signals": "trading_signals",
            "execution_orders": "execution_orders", 
            "position_updates": "position_updates",
            "market_data": "market_data",
            "risk_alerts": "risk_alerts",
            "system_commands": "system_commands",
            "agent_status": "agent_status"
        }
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
    
    def _initialize_agent_components(self):
        """Initialize agent-specific components."""
        # Communication hub specific initialization
        pass
    
    async def _agent_specific_startup(self):
        """Agent-specific startup logic."""
        # Start background tasks
        self._background_tasks = [
            asyncio.create_task(self._signal_router()),
            asyncio.create_task(self._status_monitor()),
            asyncio.create_task(self._health_checker())
        ]
        self.logger.info("✅ Communication Hub background tasks started")
    
    async def _agent_specific_shutdown(self):
        """Agent-specific shutdown logic."""
        # Stop background tasks
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._background_tasks.clear()
        self.logger.info("✅ Communication Hub background tasks stopped")
    
    def set_redis_connection(self, redis_conn):
        """Set Redis connection after initialization to avoid circular imports."""
        self.redis_conn = redis_conn
    
    # start() and stop() methods are now handled by BaseAgent
    
    def register_agent(self, agent_name: str, agent_info: Dict[str, Any]):
        """Register an agent with the communication hub."""
        self.registered_agents[agent_name] = {
            **agent_info,
            "registered_at": time.time(),
            "last_heartbeat": time.time()
        }
        self.logger.info(f"✅ Registered agent: {agent_name}")
    
    def register_signal_handler(self, signal_type: str, handler: Callable):
        """Register a signal handler for a specific signal type."""
        if signal_type not in self.signal_handlers:
            self.signal_handlers[signal_type] = []
        self.signal_handlers[signal_type].append(handler)
    
    async def broadcast_signal(self, signal_type: str, signal_data: Dict[str, Any]):
        """Broadcast a signal to all registered handlers."""
        if signal_type in self.signal_handlers:
            for handler in self.signal_handlers[signal_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(signal_data)
                    else:
                        handler(signal_data)
                except Exception as e:
                    self.logger.error(f"Error in signal handler {handler.__name__}: {e}")
    
    async def _signal_router(self):
        """Route signals between agents."""
        while self.is_running:
            try:
                # Simple signal routing logic
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in signal router: {e}")
                await asyncio.sleep(1)
    
    async def _status_monitor(self):
        """Monitor agent status."""
        while self.is_running:
            try:
                # Simple status monitoring
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error(f"Error in status monitor: {e}")
                await asyncio.sleep(5)
    
    async def _health_checker(self):
        """Check health of registered agents."""
        while self.is_running:
            try:
                current_time = time.time()
                for agent_name, agent_info in self.registered_agents.items():
                    # Check if agent is still alive (simple heartbeat check)
                    if current_time - agent_info.get("last_heartbeat", 0) > 60:
                        self.logger.warning(f"Agent {agent_name} may be unresponsive")
                
                await asyncio.sleep(30)
            except Exception as e:
                self.logger.error(f"Error in health checker: {e}")
                await asyncio.sleep(30)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the current status of the communication hub."""
        return {
            "agent_name": "communication_hub",
            "is_running": self.is_running,
            "registered_agents": len(self.registered_agents),
            "active_channels": len(self.channels),
            "background_tasks": len(self._background_tasks),
            "timestamp": time.time()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get communication hub status."""
        return self.get_agent_status()

# Global instance - now managed by parallel runner
_communication_hub = None

def get_communication_hub() -> CommunicationHub:
    """Get the global communication hub instance."""
    global _communication_hub
    return _communication_hub

def set_communication_hub(hub: CommunicationHub):
    """Set the global communication hub instance."""
    global _communication_hub
    _communication_hub = hub


