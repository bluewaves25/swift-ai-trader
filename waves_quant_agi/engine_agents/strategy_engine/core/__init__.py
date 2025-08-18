#!/usr/bin/env python3
"""
Core Engine Module - Consolidated Core Components
Contains all core engine functionality organized by responsibility.
"""

# Core engine components
from .engine import (
    StrategyEngineCore,
    StrategyManager
)

# Execution components
from .execution import (
    FlowManager,
    TradingLogicExecutor,
    TradingSignalProcessor,
    OrderManager
)

# Strategy components
from .strategy import (
    StrategyApplicator,
    StrategyComposer,
    PerformanceTracker
)

# Optimization components
from .optimization import (
    OptimizationEngine,
    LearningCoordinator
)

# Deployment components
from .deployment import (
    DeploymentManager
)

__all__ = [
    # Core engine components
    'StrategyEngineCore',
    'StrategyManager',
    
    # Execution components
    'FlowManager',
    'TradingLogicExecutor',
    'TradingSignalProcessor',
    'OrderManager',
    
    # Strategy components
    'StrategyApplicator',
    'StrategyComposer',
    'PerformanceTracker',
    
    # Optimization components
    'OptimizationEngine',
    'LearningCoordinator',
    
    # Deployment components
    'DeploymentManager'
]
