#!/usr/bin/env python3
"""
Shared MT5 Manager - Single MT5 instance for all agents
Eliminates connection conflicts and ensures consistent trading execution
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from .mt5_plugin import MT5Broker

class SharedMT5Manager:
    """Shared MT5 manager for all agents to use the same connection."""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedMT5Manager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.mt5_adapter = None
        self.connection_status = "disconnected"
        self.last_connection_check = 0
        self.connection_check_interval = 5.0  # 5 seconds
        self.logger = logging.getLogger(__name__)
        
        # Connection parameters
        self.login = None
        self.password = None
        self.server = None
        
        # Usage tracking
        self.agents_using = set()
        self.last_activity = time.time()
    
    async def initialize(self, login: int, password: str, server: str) -> bool:
        """Initialize the shared MT5 connection."""
        async with self._lock:
            try:
                if self.mt5_adapter and self.connection_status == "connected":
                    self.logger.info("✅ MT5 already connected and initialized")
                    return True
                
                self.login = login
                self.password = password
                self.server = server
                
                # Create new MT5 adapter
                self.mt5_adapter = MT5Broker(
                    login=login,
                    password=password,
                    server=server
                )
                
                # Connect to MT5
                if self.mt5_adapter.connect():
                    self.connection_status = "connected"
                    self.last_connection_check = time.time()
                    self.logger.info("✅ Shared MT5 connection established successfully")
                    return True
                else:
                    self.connection_status = "failed"
                    self.logger.error("❌ Failed to establish shared MT5 connection")
                    return False
                    
            except Exception as e:
                self.connection_status = "error"
                self.logger.error(f"❌ Error initializing shared MT5: {e}")
                return False
    
    async def get_adapter(self, agent_name: str) -> Optional[MT5Broker]:
        """Get the MT5 adapter for an agent to use."""
        async with self._lock:
            try:
                # Check connection health
                await self._check_connection_health()
                
                if self.connection_status == "connected" and self.mt5_adapter:
                    # Track agent usage
                    self.agents_using.add(agent_name)
                    self.last_activity = time.time()
                    return self.mt5_adapter
                else:
                    self.logger.warning(f"⚠️ MT5 not available for {agent_name} - status: {self.connection_status}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"❌ Error getting MT5 adapter for {agent_name}: {e}")
                return None
    
    async def _check_connection_health(self):
        """Check and maintain MT5 connection health."""
        current_time = time.time()
        
        # Only check periodically to avoid excessive checks
        if current_time - self.last_connection_check < self.connection_check_interval:
            return
        
        try:
            if self.mt5_adapter and hasattr(self.mt5_adapter, 'is_connected'):
                if self.mt5_adapter.is_connected:
                    self.connection_status = "connected"
                else:
                    self.connection_status = "disconnected"
                    self.logger.warning("⚠️ MT5 connection lost - attempting reconnection")
                    
                    # Try to reconnect
                    if self.mt5_adapter.connect():
                        self.connection_status = "connected"
                        self.logger.info("✅ MT5 reconnection successful")
                    else:
                        self.connection_status = "failed"
                        self.logger.error("❌ MT5 reconnection failed")
            
            self.last_connection_check = current_time
            
        except Exception as e:
            self.logger.error(f"❌ Error checking MT5 connection health: {e}")
            self.connection_status = "error"
    
    async def release_adapter(self, agent_name: str):
        """Release the MT5 adapter usage by an agent."""
        async with self._lock:
            if agent_name in self.agents_using:
                self.agents_using.remove(agent_name)
                self.logger.debug(f"🔓 {agent_name} released MT5 adapter")
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status."""
        async with self._lock:
            await self._check_connection_health()
            
            return {
                "status": self.connection_status,
                "connected": self.connection_status == "connected",
                "agents_using": list(self.agents_using),
                "last_activity": self.last_activity,
                "last_check": self.last_connection_check
            }
    
    async def shutdown(self):
        """Shutdown the shared MT5 connection."""
        async with self._lock:
            try:
                if self.mt5_adapter:
                    self.mt5_adapter.disconnect()
                    self.mt5_adapter = None
                
                self.connection_status = "disconnected"
                self.agents_using.clear()
                self.logger.info("✅ Shared MT5 manager shutdown completed")
                
            except Exception as e:
                self.logger.error(f"❌ Error shutting down shared MT5 manager: {e}")

# Global instance
shared_mt5_manager = SharedMT5Manager()
