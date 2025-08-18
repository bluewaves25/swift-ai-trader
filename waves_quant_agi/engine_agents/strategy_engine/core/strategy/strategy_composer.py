#!/usr/bin/env python3
"""
Strategy Composer - Core Strategy Composition Component
Composes trading strategies and integrates with consolidated trading functionality.
Focuses purely on strategy-specific tasks, delegating risk management to the risk management agent.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from collections import deque

# Import consolidated trading functionality
from ..execution.signal_processor import TradingSignalProcessor
from ..execution.flow_manager import FlowManager
from ..memory.trading_context import TradingContext

@dataclass
class StrategyComponent:
    """A component of a trading strategy."""
    component_id: str
    name: str
    component_type: str  # signal_generator, execution_engine, etc.
    parameters: Dict[str, Any]
    dependencies: List[str]
    enabled: bool = True
    weight: float = 1.0

@dataclass
class ComposedStrategy:
    """A composed trading strategy."""
    strategy_id: str
    name: str
    description: str
    components: List[StrategyComponent]
    composition_rules: Dict[str, Any]
    strategy_parameters: Dict[str, Any]  # Strategy-specific parameters only
    performance_targets: Dict[str, float]
    created_at: float
    status: str = "draft"  # draft, active, inactive, archived

class StrategyComposer:
    """Composes trading strategies from individual components.
    
    Focuses purely on strategy-specific tasks:
    - Strategy composition and assembly
    - Component management and validation
    - Strategy parameter configuration
    - Performance target setting
    
    Risk management is delegated to the risk management agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize consolidated trading components
        self.trading_signal_processor = TradingSignalProcessor(config)
        self.trading_flow_manager = TradingFlowManager(config)
        self.trading_context = TradingContext(max_history=1000)  # Fixed: pass integer instead of config
        
        # Strategy composition state
        self.available_components: Dict[str, StrategyComponent] = {}
        self.composed_strategies: Dict[str, ComposedStrategy] = {}
        self.composition_queue: deque = deque(maxlen=100)
        self.composition_history: deque = deque(maxlen=1000)
        
        # Composition settings (strategy-specific only)
        self.composition_settings = {
            "max_components_per_strategy": 10,
            "max_strategies": 100,
            "auto_validation": True,
            "composition_timeout": 600,  # 10 minutes
            "strategy_parameters": {
                "max_position_size": 100000,  # Strategy-level position sizing
                "signal_confidence_threshold": 0.7,
                "strategy_timeout": 60
            }
        }
        
    async def initialize(self):
        """Initialize the strategy composer."""
        try:
            # Initialize trading components
            await self.trading_signal_processor.initialize()
            await self.trading_flow_manager.initialize()
            await self.trading_context.initialize()
            
            # Load composition settings
            await self._load_composition_settings()
            
            # Load available components
            await self._load_available_components()
            
            print("✅ Strategy Composer initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Strategy Composer: {e}")
            raise
    
    async def _load_composition_settings(self):
        """Load strategy composition settings from configuration."""
        try:
            composer_config = self.config.get("strategy_engine", {}).get("composer", {})
            self.composition_settings.update(composer_config)
        except Exception as e:
            print(f"❌ Error loading composition settings: {e}")
    
    async def _load_available_components(self):
        """Load available strategy components."""
        try:
            # Load predefined strategy components
            self.available_components = {
                "trend_following": StrategyComponent(
                    component_id="trend_following",
                    name="Trend Following",
                    component_type="signal_generator",
                    parameters={"lookback_period": 20, "trend_threshold": 0.6},
                    dependencies=[]
                ),
                "mean_reversion": StrategyComponent(
                    component_id="mean_reversion",
                    name="Mean Reversion",
                    component_type="signal_generator",
                    parameters={"reversion_threshold": 2.0, "mean_lookback": 50},
                    dependencies=[]
                ),
                "breakout": StrategyComponent(
                    component_id="breakout",
                    name="Breakout Strategy",
                    component_type="signal_generator",
                    parameters={"breakout_threshold": 0.02, "confirmation_period": 3},
                    dependencies=[]
                ),
                "momentum": StrategyComponent(
                    component_id="momentum",
                    name="Momentum Strategy",
                    component_type="signal_generator",
                    parameters={"momentum_period": 10, "momentum_threshold": 0.015},
                    dependencies=[]
                )
            }
            
            print(f"✅ Loaded {len(self.available_components)} strategy components")
            
        except Exception as e:
            print(f"❌ Error loading available components: {e}")

    async def create_strategy(self, name: str, description: str, component_ids: List[str], 
                            composition_rules: Dict[str, Any], performance_targets: Dict[str, float]) -> ComposedStrategy:
        """Create a new composed strategy.
        
        This focuses purely on strategy composition, not risk management.
        """
        try:
            # Validate components
            if not await self._validate_strategy_components(component_ids):
                raise ValueError("Invalid strategy components")
            
            # Create strategy ID
            strategy_id = f"composed_{name.lower().replace(' ', '_')}_{int(time.time())}"
            
            # Get components
            components = [self.available_components[cid] for cid in component_ids if cid in self.available_components]
            
            # Create composed strategy
            strategy = ComposedStrategy(
                strategy_id=strategy_id,
                name=name,
                description=description,
                components=components,
                composition_rules=composition_rules,
                strategy_parameters=self._generate_strategy_parameters(components),
                performance_targets=performance_targets,
                created_at=time.time()
            )
            
            # Store strategy
            self.composed_strategies[strategy_id] = strategy
            
            # Store in trading context
            await self.trading_context.store_signal({
                "type": "strategy_composition",
                "strategy_id": strategy_id,
                "composition_data": {
                    "name": name,
                    "components": component_ids,
                    "composition_rules": composition_rules
                },
                "timestamp": int(time.time())
            })
            
            # Add to composition history
            self.composition_history.append({
                "strategy_id": strategy_id,
                "action": "created",
                "timestamp": int(time.time())
            })
            
            print(f"✅ Created composed strategy: {strategy_id}")
            return strategy
            
        except Exception as e:
            print(f"❌ Error creating strategy: {e}")
            raise

    async def _validate_strategy_components(self, component_ids: List[str]) -> bool:
        """Validate strategy components for composition."""
        try:
            # Check if all components exist
            for cid in component_ids:
                if cid not in self.available_components:
                    print(f"❌ Component {cid} not found")
                    return False
            
            # Check component dependencies
            for cid in component_ids:
                component = self.available_components[cid]
                for dep in component.dependencies:
                    if dep not in component_ids:
                        print(f"❌ Missing dependency {dep} for component {cid}")
                        return False
            
            # Check component count limit
            if len(component_ids) > self.composition_settings["max_components_per_strategy"]:
                print(f"❌ Too many components: {len(component_ids)} > {self.composition_settings['max_components_per_strategy']}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating components: {e}")
            return False

    def _generate_strategy_parameters(self, components: List[StrategyComponent]) -> Dict[str, Any]:
        """Generate strategy parameters based on components.
        
        Focuses on strategy-specific parameters, not risk parameters.
        """
        try:
            strategy_params = {
                "signal_confidence_threshold": 0.7,
                "strategy_timeout": 60,
                "component_weights": {}
            }
            
            # Set component weights
            for component in components:
                strategy_params["component_weights"][component.component_id] = component.weight
            
            # Adjust parameters based on component types
            signal_generators = [c for c in components if c.component_type == "signal_generator"]
            if len(signal_generators) > 1:
                strategy_params["signal_aggregation"] = "weighted_average"
                strategy_params["signal_consensus_threshold"] = 0.6
            
            return strategy_params
            
        except Exception as e:
            print(f"❌ Error generating strategy parameters: {e}")
            return {}

    async def activate_strategy(self, strategy_id: str) -> bool:
        """Activate a composed strategy."""
        try:
            if strategy_id not in self.composed_strategies:
                print(f"❌ Strategy {strategy_id} not found")
                return False
            
            strategy = self.composed_strategies[strategy_id]
            strategy.status = "active"
            
            # Store activation in trading context
            await self.trading_context.store_signal({
                "type": "strategy_activation",
                "strategy_id": strategy_id,
                "activation_data": {
                    "status": "active",
                    "timestamp": int(time.time())
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Activated strategy: {strategy_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error activating strategy: {e}")
            return False

    async def deactivate_strategy(self, strategy_id: str) -> bool:
        """Deactivate a composed strategy."""
        try:
            if strategy_id not in self.composed_strategies:
                print(f"❌ Strategy {strategy_id} not found")
                return False
            
            strategy = self.composed_strategies[strategy_id]
            strategy.status = "inactive"
            
            # Store deactivation in trading context
            await self.trading_context.store_signal({
                "type": "strategy_deactivation",
                "strategy_id": strategy_id,
                "deactivation_data": {
                    "status": "inactive",
                    "timestamp": int(time.time())
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Deactivated strategy: {strategy_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deactivating strategy: {e}")
            return False

    async def get_strategy(self, strategy_id: str) -> Optional[ComposedStrategy]:
        """Get a specific composed strategy."""
        return self.composed_strategies.get(strategy_id)

    async def get_all_strategies(self) -> List[ComposedStrategy]:
        """Get all composed strategies."""
        return list(self.composed_strategies.values())

    async def get_available_components(self) -> List[StrategyComponent]:
        """Get all available strategy components."""
        return list(self.available_components.values())

    async def get_composition_summary(self) -> Dict[str, Any]:
        """Get composition summary and statistics."""
        return {
            "total_strategies": len(self.composed_strategies),
            "active_strategies": len([s for s in self.composed_strategies.values() if s.status == "active"]),
            "available_components": len(self.available_components),
            "composition_queue_size": len(self.composition_queue),
            "composition_history_size": len(self.composition_history),
            "composition_settings": self.composition_settings
        }

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_signal_processor.cleanup()
            await self.trading_flow_manager.cleanup()
            await self.trading_context.cleanup()
            print("✅ Strategy Composer cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up Strategy Composer: {e}")
