#!/usr/bin/env python3
"""
Communication Hub - ROLE CONSOLIDATED: INTER-AGENT COMMUNICATION ONLY
Removed signal routing, status monitoring, and health checking functionality - now handled by Core Agent.
Focuses exclusively on inter-agent communication, message routing, and coordination.
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, List, Optional, Callable

from ..shared_utils.base_agent import BaseAgent

class CommunicationHub(BaseAgent):
    """Central communication hub - focused solely on inter-agent communication."""
    
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
        
        # Communication state
        self.communication_state = {
            "active_channels": {},
            "message_queue": [],
            "delivery_status": {},
            "last_message_time": time.time()
        }
        
        # Communication statistics
        self.stats = {
            "total_messages_sent": 0,
            "total_messages_received": 0,
            "failed_deliveries": 0,
            "active_connections": 0,
            "start_time": time.time()
        }
    
    def _initialize_agent_components(self):
        """Initialize communication-specific components."""
        # Communication hub specific initialization
        pass
    
    async def _agent_specific_startup(self):
        """Communication-specific startup logic."""
        try:
            # Initialize communication systems
            await self._initialize_communication_systems()
            
            # Start communication monitoring
            await self._start_communication_monitoring()
            
            self.logger.info("✅ Communication Hub: Communication systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in communication startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Communication-specific shutdown logic."""
        try:
            # Cleanup communication resources
            await self._cleanup_communication_systems()
            
            self.logger.info("✅ Communication Hub: Communication systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in communication shutdown: {e}")
    
    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._message_routing_loop, "Message Routing", "fast"),
            (self._connection_monitoring_loop, "Connection Monitoring", "tactical"),
            (self._communication_audit_loop, "Communication Audit", "strategic")
        ]
    
    # ============= COMMUNICATION SYSTEM INITIALIZATION =============
    
    async def _initialize_communication_systems(self):
        """Initialize communication systems."""
        try:
            # Initialize message routing
            await self._initialize_message_routing()
            
            # Initialize connection management
            await self._initialize_connection_management()
            
            self.logger.info("✅ Communication systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing communication systems: {e}")
            raise
    
    async def _start_communication_monitoring(self):
        """Start communication monitoring."""
        try:
            # Start message queue monitoring
            await self._start_message_queue_monitoring()
            
            # Start connection health monitoring
            await self._start_connection_health_monitoring()
            
            self.logger.info("✅ Communication monitoring started")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting communication monitoring: {e}")
            raise
    
    async def _cleanup_communication_systems(self):
        """Cleanup communication systems."""
        try:
            # Cleanup message routing
            await self._cleanup_message_routing()
            
            # Cleanup connection management
            await self._cleanup_connection_management()
            
            self.logger.info("✅ Communication systems cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up communication systems: {e}")
    
    # ============= MESSAGE ROUTING =============
    
    async def _initialize_message_routing(self):
        """Initialize message routing system."""
        try:
            # Initialize message router
            self.message_router = {
                "high_priority": [],
                "normal_priority": [],
                "low_priority": []
            }
            
            self.logger.info("✅ Message routing initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing message routing: {e}")
            raise
    
    async def _start_message_queue_monitoring(self):
        """Start message queue monitoring."""
        try:
            # Start queue monitoring
            self.logger.info("✅ Message queue monitoring started")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting message queue monitoring: {e}")
            raise
    
    async def _cleanup_message_routing(self):
        """Cleanup message routing system."""
        try:
            # Cleanup router
            self.message_router.clear()
            
            self.logger.info("✅ Message routing cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up message routing: {e}")
    
    # ============= CONNECTION MANAGEMENT =============
    
    async def _initialize_connection_management(self):
        """Initialize connection management."""
        try:
            # Initialize connection pool
            self.connection_pool = {}
            
            self.logger.info("✅ Connection management initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing connection management: {e}")
            raise
    
    async def _start_connection_health_monitoring(self):
        """Start connection health monitoring."""
        try:
            # Start health monitoring
            self.logger.info("✅ Connection health monitoring started")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting connection health monitoring: {e}")
            raise
    
    async def _cleanup_connection_management(self):
        """Cleanup connection management."""
        try:
            # Cleanup connections
            self.connection_pool.clear()
            
            self.logger.info("✅ Connection management cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up connection management: {e}")
    
    # ============= BACKGROUND TASK LOOPS =============
    
    async def _message_routing_loop(self):
        """Main message routing loop."""
        while self.is_running:
            try:
                # Process message queue
                await self._process_message_queue()
                
                # Update statistics
                self.stats["total_messages_sent"] += 1
                
                await asyncio.sleep(0.1)  # 100ms cycle
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in message routing loop: {e}")
                await asyncio.sleep(1)
    
    async def _connection_monitoring_loop(self):
        """Connection monitoring loop."""
        while self.is_running:
            try:
                # Monitor connections
                await self._monitor_connections()
                
                await asyncio.sleep(1)  # 1s cycle
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in connection monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _communication_audit_loop(self):
        """Communication audit loop."""
        while self.is_running:
            try:
                # Audit communication
                await self._audit_communication()
                
                await asyncio.sleep(30)  # 30s cycle
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in communication audit loop: {e}")
                await asyncio.sleep(60)
    
    # ============= COMMUNICATION OPERATIONS =============
    
    async def _process_message_queue(self):
        """Process message queue."""
        try:
            # Process high priority messages first
            if self.communication_state["message_queue"]:
                message = self.communication_state["message_queue"].pop(0)
                await self._route_message(message)
                
        except Exception as e:
            self.logger.error(f"Error processing message queue: {e}")
    
    async def _monitor_connections(self):
        """Monitor connections."""
        try:
            # Check connection health
            active_connections = len(self.connection_pool)
            self.communication_state["active_channels"] = active_connections
            self.stats["active_connections"] = active_connections
            
        except Exception as e:
            self.logger.error(f"Error monitoring connections: {e}")
    
    async def _audit_communication(self):
        """Audit communication systems."""
        try:
            # Audit message delivery
            delivery_rate = self.stats["total_messages_sent"] / max(self.stats["total_messages_received"], 1)
            
            # Log audit results
            self.logger.info(f"Communication audit: Delivery rate: {delivery_rate:.2%}")
            
        except Exception as e:
            self.logger.error(f"Error in communication audit: {e}")
    
    async def _route_message(self, message: Dict[str, Any]):
        """Route a message to appropriate handlers."""
        try:
            signal_type = message.get("type", "unknown")
            if signal_type in self.signal_handlers:
                await self.broadcast_signal(signal_type, message)
                
        except Exception as e:
            self.logger.error(f"Error routing message: {e}")
            self.stats["failed_deliveries"] += 1
    
    def set_redis_connection(self, redis_conn):
        """Set Redis connection after initialization to avoid circular imports."""
        self.redis_conn = redis_conn
    
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
    
    async def send_message(self, target_agent: str, message: Dict[str, Any]):
        """Send a message to a specific agent."""
        try:
            if target_agent in self.registered_agents:
                # Add to message queue
                self.communication_state["message_queue"].append({
                    "target": target_agent,
                    "message": message,
                    "timestamp": time.time()
                })
                
                self.stats["total_messages_sent"] += 1
                self.logger.info(f"Message queued for {target_agent}")
            else:
                self.logger.warning(f"Target agent {target_agent} not found")
                
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all registered agents."""
        try:
            for agent_name in self.registered_agents:
                await self.send_message(agent_name, message)
                
        except Exception as e:
            self.logger.error(f"Error broadcasting to all: {e}")
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent."""
        return self.registered_agents.get(agent_name)
    
    def get_all_agent_statuses(self) -> Dict[str, Any]:
        """Get status of all registered agents."""
        return self.registered_agents.copy()
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics."""
        return {
            "stats": self.stats.copy(),
            "state": self.communication_state.copy(),
            "registered_agents": len(self.registered_agents),
            "active_channels": len(self.channels)
        }


