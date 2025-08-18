#!/usr/bin/env python3
"""
Strategy Engine - CONSOLIDATED TRADING STRATEGY SYSTEM
Provides integrated strategy management, execution, and optimization.
NOW INCLUDES all trading functionality consolidated from Core Agent.
"""

# Core components (consolidated structure)
from .core.strategy import (
    StrategyApplicator,
    StrategyComposer,
    PerformanceTracker
)
from .core.deployment import DeploymentManager

# Strategy components (consolidated)
from .strategies.composers.ml_composer import MLComposer
from .strategies.composers.online_generator import OnlineGenerator

# Learning components (consolidated)
from .learning.strategy_learning_manager import StrategyLearningManager
from .learning.strategy_adaptation_engine import StrategyAdaptationEngine

# Main Strategy Enhancement Manager
from .strategy_enhancement_manager import StrategyEnhancementManager

# Integration and main agent
# Note: These have been consolidated into the core structure
# StrategyEngineIntegration = None  # Consolidated into core
# EnhancedStrategyEngineAgent = None  # Consolidated into core

# CONSOLIDATED TRADING FUNCTIONALITY (consolidated structure)
# Trading signal processing and flow management
try:
    from .core.signal_processor import TradingSignalProcessor
    from .core.flow_manager import FlowManager
    from .core.logic_executor import TradingLogicExecutor

    # Trading interfaces and models
    from .core.interfaces.trade_model import TradeCommand
    from .core.interfaces.agent_io import TradingAgentIO

    # Trading pipeline and execution
    from .core.pipeline.execution_pipeline import TradingExecutionPipeline

    # Trading memory and context
    from .core.memory.trading_context import TradingContext

    # Trading learning and research
    from .core.learning.trading_research_engine import TradingResearchEngine
    from .core.learning.trading_training_module import TradingTrainingModule
    from .core.learning.trading_retraining_loop import TradingRetrainingLoop
except ImportError:
    # Fallback for when running from pipeline runner
    TradingSignalProcessor = None
    FlowManager = None
    TradingLogicExecutor = None
    TradeCommand = None
    TradingAgentIO = None
    TradingExecutionPipeline = None
    TradingContext = None
    TradingResearchEngine = None
    TradingTrainingModule = None
    TradingRetrainingLoop = None

# Strategy types (consolidated structure)
try:
    from .strategies.trend_following.breakout_strategy import BreakoutStrategy
    from .strategies.trend_following.momentum_rider import MomentumRiderStrategy
    from .strategies.trend_following.moving_average_crossover import MovingAverageCrossoverStrategy

    from .strategies.arbitrage_based.triangular_arbitrage import TriangularArbitrage
    from .strategies.arbitrage_based.latency_arbitrage import LatencyArbitrage
    from .strategies.arbitrage_based.funding_rate_arbitrage import FundingRateArbitrage

    from .strategies.statistical_arbitrage.pairs_trading import PairsTradingStrategy
    from .strategies.statistical_arbitrage.mean_reversion import MeanReversionStrategy
    from .strategies.statistical_arbitrage.cointegration_model import CointegrationModelStrategy

    from .strategies.market_making.adaptive_quote import AdaptiveQuoteStrategy
    from .strategies.market_making.spread_adjuster import SpreadAdjusterStrategy
    from .strategies.market_making.volatility_responsive_mm import VolatilityResponsiveMMStrategy

    from .strategies.news_driven.sentiment_analysis import SentimentAnalysisStrategy
    from .strategies.news_driven.earnings_reaction import EarningsReactionStrategy
    from .strategies.news_driven.fed_policy_detector import FedPolicyDetectorStrategy

    from .strategies.htf.regime_shift_detector import RegimeShiftDetectorStrategy
    from .strategies.htf.global_liquidity_signal import GlobalLiquiditySignalStrategy
    from .strategies.htf.macro_trend_tracker import MacroTrendTrackerStrategy
except ImportError:
    # Fallback for when running from pipeline runner
    BreakoutStrategy = None
    MomentumRiderStrategy = None
    MovingAverageCrossoverStrategy = None
    TriangularArbitrage = None
    LatencyArbitrage = None
    FundingRateArbitrage = None
    PairsTradingStrategy = None
    MeanReversionStrategy = None
    CointegrationModelStrategy = None
    AdaptiveQuoteStrategy = None
    SpreadAdjusterStrategy = None
    VolatilityResponsiveMMStrategy = None
    SentimentAnalysisStrategy = None
    EarningsReactionStrategy = None
    FedPolicyDetectorStrategy = None
    RegimeShiftDetectorStrategy = None
    GlobalLiquiditySignalStrategy = None
    MacroTrendTrackerStrategy = None

__all__ = [
    # Core components
    'StrategyApplicator',
    'StrategyComposer',
    'PerformanceTracker',
    'DeploymentManager',
    
    # Composer components
    'MLComposer',
    'OnlineGenerator',
    
    # Learning layer components
    'StrategyLearningManager',
    'StrategyAdaptationEngine',
    
    # Main Strategy Enhancement Manager
    'StrategyEnhancementManager',
    
    # Integration and main agent
    # Note: These have been consolidated into the core structure
    
    # CONSOLIDATED TRADING FUNCTIONALITY
    'TradingSignalProcessor',
    'FlowManager',
    'TradingLogicExecutor',
    'TradeCommand',
    'TradingAgentIO',
    'TradingExecutionPipeline',
    'TradingContext',
    'TradingResearchEngine',
    'TradingTrainingModule',
    'TradingRetrainingLoop',
    
    # Strategy types - Trend Following
    'BreakoutStrategy',
    'MomentumRiderStrategy',
    'MovingAverageCrossoverStrategy',
    
    # Strategy types - Arbitrage Based
    'TriangularArbitrage',
    'LatencyArbitrage',
    'FundingRateArbitrage',
    
    # Strategy types - Statistical Arbitrage
    'PairsTradingStrategy',
    'MeanReversionStrategy',
    'CointegrationModelStrategy',
    
    # Strategy types - Market Making
    'AdaptiveQuoteStrategy',
    'SpreadAdjusterStrategy',
    'VolatilityResponsiveMMStrategy',
    
    # Strategy types - News Driven
    'SentimentAnalysisStrategy',
    'EarningsReactionStrategy',
    'FedPolicyDetectorStrategy',
    
    # Strategy types - High Time Frame
    'RegimeShiftDetectorStrategy',
    'GlobalLiquiditySignalStrategy',
    'MacroTrendTrackerStrategy',
]
