#!/usr/bin/env python3
"""
Strategy Engine Core Module
Extracted from enhanced_strategy_engine_agent.py to provide core initialization and state management
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from engine_agents.shared_utils import BaseAgent

class StrategyEngineCore(BaseAgent):
    """
    Core Strategy Engine - Extracted from enhanced_strategy_engine_agent.py
    
    This module contains the core initialization and state management functionality
    that was previously in the large enhanced_strategy_engine_agent.py file.
    
    Preserves ALL original functionality while making it more manageable.
    """
    
    def _initialize_agent_components(self):
        """Initialize strategy engine specific components (extracted from original)."""
        # Initialize strategy engine components
        self.strategy_manager = None
        self.optimization_engine = None
        self.learning_coordinator = None
        self.order_manager = None
        
        # Strategy engine state (preserved from original)
        self.strategy_state = {
            "active_strategies": {},
            "strategy_performance": {},
            "strategy_optimization_queue": [],  # Only strategy optimization, not cost optimization
            "learning_events": [],
            "order_queue": [],
            "last_strategy_update": time.time()
        }
        
        # Strategy engine statistics (preserved from original)
        self.stats = {
            "total_strategies_executed": 0,
            "optimizations_applied": 0,
            "learning_events_processed": 0,
            "orders_managed": 0,
            "start_time": time.time()
        }
    
    async def _agent_specific_startup(self):
        """Strategy engine specific startup logic (extracted from original)."""
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
            
            self.logger.info("✅ Strategy Engine Core: Central coordination systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in strategy engine core startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Strategy engine specific shutdown logic (extracted from original)."""
        try:
            # Cleanup strategy engine resources
            await self._cleanup_strategy_components()
            
            self.logger.info("✅ Strategy Engine Core: Central coordination systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in strategy engine core shutdown: {e}")
    
    # ============= STRATEGY MANAGEMENT INITIALIZATION =============
    # Extracted from original enhanced_strategy_engine_agent.py
    
    async def _initialize_strategy_management(self):
        """Initialize strategy management components (extracted from original)."""
        try:
            # Initialize strategy manager
            from ..core.strategy_manager import StrategyManager
            self.strategy_manager = StrategyManager(self.config)
            await self.strategy_manager.initialize()
            
            self.logger.info("✅ Strategy management initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing strategy management: {e}")
            raise
    
    async def _initialize_optimization_engine(self):
        """Initialize optimization engine (extracted from original)."""
        try:
            # Initialize optimization engine
            from ..core.optimization_engine import OptimizationEngine
            self.optimization_engine = OptimizationEngine(self.config)
            await self.optimization_engine.initialize()
            
            self.logger.info("✅ Optimization engine initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing optimization engine: {e}")
            raise
    
    async def _initialize_learning_coordination(self):
        """Initialize learning coordination (extracted from original)."""
        try:
            # Initialize learning coordinator
            from ..core.learning_coordinator import LearningCoordinator
            self.learning_coordinator = LearningCoordinator(self.config)
            await self.learning_coordinator.initialize()
            
            self.logger.info("✅ Learning coordination initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing learning coordination: {e}")
            raise
    
    async def _initialize_order_management(self):
        """Initialize order management (extracted from original)."""
        try:
            # Initialize order manager
            from ..core.order_manager import OrderManager
            self.order_manager = OrderManager(self.config)
            await self.order_manager.initialize()
            
            self.logger.info("✅ Order management initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing order management: {e}")
            raise
    
    async def _initialize_strategy_composer(self):
        """Initialize strategy composer (extracted from original)."""
        try:
            # Initialize strategy composer
            from ..core.strategy_composer import StrategyComposer
            self.strategy_composer = StrategyComposer(self.config)
            await self.strategy_composer.initialize()
            
            self.logger.info("✅ Strategy composer initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing strategy composer: {e}")
            raise
    
    async def _initialize_strategy_applicator(self):
        """Initialize strategy applicator (extracted from original)."""
        try:
            # Initialize strategy applicator
            from ..core.strategy_applicator import StrategyApplicator
            self.strategy_applicator = StrategyApplicator(self.config)
            await self.strategy_applicator.initialize()
            
            self.logger.info("✅ Strategy applicator initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing strategy applicator: {e}")
            raise
    
    # ============= UTILITY METHODS =============
    # Extracted from original enhanced_strategy_engine_agent.py
    
    def _update_strategy_state(self):
        """Update strategy state with current information (extracted from original)."""
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
        """Cleanup strategy engine components (extracted from original)."""
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
    
    # ============= PUBLIC INTERFACE =============
    # Extracted from original enhanced_strategy_engine_agent.py
    
    async def get_strategy_engine_status(self) -> Dict[str, Any]:
        """Get current strategy engine status (extracted from original)."""
        return {
            "strategy_state": self.strategy_state,
            "stats": self.stats,
            "last_update": time.time()
        }
    
    async def get_active_strategies(self) -> Dict[str, Any]:
        """Get active strategies (extracted from original)."""
        return self.strategy_state.get("active_strategies", {})
    
    async def get_strategy_performance(self) -> Dict[str, Any]:
        """Get strategy performance metrics (extracted from original)."""
        return self.strategy_state.get("strategy_performance", {})
    
    async def get_optimization_queue(self) -> List[Dict[str, Any]]:
        """Get optimization queue (extracted from original)."""
        return self.strategy_state.get("strategy_optimization_queue", [])
    
    def get_status(self) -> Dict[str, Any]:
        """Get module status for health checking."""
        return {
            "module": "Strategy Engine Core",
            "is_active": self.is_running,
            "components": {
                "strategy_manager": self.strategy_manager is not None,
                "optimization_engine": self.optimization_engine is not None,
                "learning_coordinator": self.learning_coordinator is not None,
                "order_manager": self.order_manager is not None
            },
            "strategy_state": self.strategy_state,
            "stats": self.stats
        }
