#!/usr/bin/env python3
"""
Strategy Engine - Comprehensive Trading Strategy System
Provides integrated strategy management, execution, and optimization.
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

# Strategy types (all categories)
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
