#!/usr/bin/env python3
"""
Strategy Engine - CONSOLIDATED TRADING STRATEGY SYSTEM
Provides integrated strategy management, execution, and optimization.
NOW INCLUDES all trading functionality consolidated from Core Agent.
"""

# Core components
from .core.strategy_applicator import StrategyApplicator
from .core.strategy_composer import StrategyComposer

# Manager components
from .manager.strategy_registry import StrategyRegistry
from .manager.performance_tracker import PerformanceTracker
from .manager.deployment_manager import DeploymentManager

# Composer components
from .composers.ml_composer import MLComposer
from .composers.online_generator import OnlineGenerator

# Learning layer components
from .learning_layer.strategy_learning_manager import StrategyLearningManager
from .learning_layer.strategy_adaptation_engine import StrategyAdaptationEngine

# Integration and main agent
from .strategy_engine_integration import StrategyEngineIntegration
from .enhanced_strategy_engine_agent import EnhancedStrategyEngineAgent

# CONSOLIDATED TRADING FUNCTIONALITY (moved from Core Agent)
# Trading signal processing and flow management
try:
    from .trading.signal_processor import TradingSignalProcessor
    from .trading.flow_manager import TradingFlowManager
    from .trading.logic_executor import TradingLogicExecutor

    # Trading interfaces and models
    from .trading.interfaces.trade_model import TradeCommand
    from .trading.interfaces.agent_io import TradingAgentIO

    # Trading pipeline and execution
    from .trading.pipeline.execution_pipeline import TradingExecutionPipeline

    # Trading memory and context
    from .trading.memory.trading_context import TradingContext

    # Trading learning and research
    from .trading.learning.trading_research_engine import TradingResearchEngine
    from .trading.learning.trading_training_module import TradingTrainingModule
    from .trading.learning.trading_retraining_loop import TradingRetrainingLoop
except ImportError:
    # Fallback for when running from pipeline runner
    TradingSignalProcessor = None
    TradingFlowManager = None
    TradingLogicExecutor = None
    TradeCommand = None
    TradingAgentIO = None
    TradingExecutionPipeline = None
    TradingContext = None
    TradingResearchEngine = None
    TradingTrainingModule = None
    TradingRetrainingLoop = None

# Strategy types (all categories)
try:
    from .types.trend_following.breakout_strategy import BreakoutStrategy
    from .types.trend_following.momentum_rider import MomentumRiderStrategy
    from .types.trend_following.moving_average_crossover import MovingAverageCrossoverStrategy

    from .types.arbitrage_based.latency_arbitrage import LatencyArbitrageStrategy
    from .types.arbitrage_based.funding_rate_arbitrage import FundingRateArbitrageStrategy
    from .types.arbitrage_based.triangular_arbitrage import TriangularArbitrageStrategy

    from .types.statistical_arbitrage.pairs_trading import PairsTradingStrategy
    from .types.statistical_arbitrage.mean_reversion import MeanReversionStrategy
    from .types.statistical_arbitrage.cointegration_model import CointegrationModelStrategy

    from .types.market_making.adaptive_quote import AdaptiveQuoteStrategy
    from .types.market_making.spread_adjuster import SpreadAdjusterStrategy
    from .types.market_making.volatility_responsive_mm import VolatilityResponsiveMMStrategy

    from .types.news_driven.sentiment_analysis import SentimentAnalysisStrategy
    from .types.news_driven.earnings_reaction import EarningsReactionStrategy
    from .types.news_driven.fed_policy_detector import FedPolicyDetectorStrategy

    from .types.htf.regime_shift_detector import RegimeShiftDetectorStrategy
    from .types.htf.global_liquidity_signal import GlobalLiquiditySignalStrategy
    from .types.htf.macro_trend_tracker import MacroTrendTrackerStrategy
except ImportError:
    # Fallback for when running from pipeline runner
    BreakoutStrategy = None
    MomentumRiderStrategy = None
    MovingAverageCrossoverStrategy = None
    LatencyArbitrageStrategy = None
    FundingRateArbitrageStrategy = None
    TriangularArbitrageStrategy = None
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
    
    # Manager components
    'StrategyRegistry',
    'PerformanceTracker',
    'DeploymentManager',
    
    # Composer components
    'MLComposer',
    'OnlineGenerator',
    
    # Learning layer components
    'StrategyLearningManager',
    'StrategyAdaptationEngine',
    
    # Integration and main agent
    'StrategyEngineIntegration',
    'EnhancedStrategyEngineAgent',
    
    # CONSOLIDATED TRADING FUNCTIONALITY
    'TradingSignalProcessor',
    'TradingFlowManager',
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
    'LatencyArbitrageStrategy',
    'FundingRateArbitrageStrategy',
    'TriangularArbitrageStrategy',
    
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
