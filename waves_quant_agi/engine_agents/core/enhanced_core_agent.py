#!/usr/bin/env python3
"""
Enhanced Core Agent - REFACTORED TO USE BASE AGENT
Eliminates duplicate start/stop methods and Redis connection logic.
"""

import asyncio
import time
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedCoreAgent(BaseAgent):
    """Enhanced core agent using base class."""
    
    def _initialize_agent_components(self):
        """Initialize core agent specific components."""
        # Initialize core agent components
        self.signal_router = None  # Will be initialized in specific startup
        self.agent_coordinator = None
        self.learning_coordinator = None
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Core agent specific startup logic."""
        # Initialize core coordination systems
        # ... core agent specific initialization ...
        pass
    
    async def _agent_specific_shutdown(self):
        """Core agent specific shutdown logic."""
        # Cleanup core agent specific resources
        pass
    
    # REAL-TIME: SIGNAL ROUTING (continuous)
    
    async def _realtime_signal_routing_loop(self):
        """Real-time signal routing without any trading decisions."""
        while self.is_running:
            try:
                # This loop processes routing requests from message handlers
                # No trading decisions - pure routing only
                await asyncio.sleep(0.001)  # 1ms for real-time responsiveness
                
            except Exception as e:
                self.logger.error(f"Error in real-time signal routing: {e}")
                await asyncio.sleep(0.1)
    
    # TIER 3: AGENT COORDINATION (30s intervals)
    
    async def _agent_health_monitoring_loop(self):
        """TIER 3: Monitor health of all agents (30s)."""
        while self.is_running:
            try:
                # Check all agent connectivity
                connectivity_status = await self._check_all_agent_connectivity()
                
                # Update agent health metrics
                self._update_agent_health_metrics(connectivity_status)
                
                # Send system alerts if needed
                await self._send_agent_health_alerts(connectivity_status)
                
                await asyncio.sleep(30)  # 30s
                
            except Exception as e:
                self.logger.error(f"Error in agent health monitoring: {e}")
                await asyncio.sleep(30)
    
    # ... rest of the core agent specific methods remain the same ...
    # (keeping only the unique functionality, removing all duplicate methods)
