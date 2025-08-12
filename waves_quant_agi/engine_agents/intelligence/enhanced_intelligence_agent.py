#!/usr/bin/env python3
"""
Enhanced Intelligence Agent - REFACTORED TO USE BASE AGENT
Eliminates duplicate start/stop methods and Redis connection logic.
"""

import asyncio
import time
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedIntelligenceAgent(BaseAgent):
    """Enhanced intelligence agent using base class."""
    
    def _initialize_agent_components(self):
        """Initialize intelligence specific components."""
        # Initialize intelligence components
        self.pattern_recognizer = None  # Will be initialized in specific startup
        self.learning_engine = None
        self.comm_hub = None
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Intelligence specific startup logic."""
        # Initialize pattern recognition and learning systems
        # ... intelligence specific initialization ...
        pass
    
    async def _agent_specific_shutdown(self):
        """Intelligence specific shutdown logic."""
        # Cleanup intelligence specific resources
        pass
    
    # ============= PATTERN RECOGNITION LOOP =============
    
    async def _pattern_recognition_loop(self):
        """Main pattern recognition loop."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Get market data using base class method
                market_data = self.get_market_data()
                
                if market_data:
                    # Perform pattern recognition
                    patterns = await self._recognize_patterns(market_data)
                    
                    if patterns:
                        await self._process_patterns(patterns)
                    
                    # Record operation for monitoring
                    duration_ms = (time.time() - start_time) * 1000
                    self.status_monitor.record_operation(duration_ms, len(patterns) > 0)
                
                # Wait for next cycle
                await asyncio.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error in pattern recognition loop: {e}")
                await asyncio.sleep(1.0)
    
    # ... rest of the intelligence specific methods remain the same ...
    # (keeping only the unique functionality, removing all duplicate methods)
