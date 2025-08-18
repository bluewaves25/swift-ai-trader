#!/usr/bin/env python3
"""
Strategy-Specific Configuration File
Contains all parameters for each strategy type including:
- Trade frequency limits
- Risk profiles
- SL/TP calculations
- Session preferences
- Hold time management
"""

from typing import Dict, Any, List

# ============================================================================
# HFT STRATEGIES (Ultra-Fast, High Frequency)
# ============================================================================

ARBITRAGE_CONFIG = {
    "strategy_type": "arbitrage",
    "max_daily_trades": 10000,
    "max_trades_per_minute": 7,
    "min_signal_interval_seconds": 8.5,
    "min_hold_time_seconds": 5,
    "max_hold_time_minutes": 5,
    "risk_reward_ratio": 1.2,
    "stop_loss_percentage": 0.003,  # 0.3%
    "take_profit_percentage": 0.001,  # 0.1%
    "partial_exit_levels": [
        {"percentage": 50, "target_multiplier": 1.1},
        {"percentage": 30, "target_multiplier": 1.3},
        {"percentage": 20, "target_multiplier": 1.5}
    ],
    "trailing_stop": False,
    "session_preference": ["london", "new_york"],
    "volatility_threshold": 0.02,
    "min_confidence": 0.65,
    "execution_priority": "HIGH",
    "slippage_tolerance": 0.001,
    "profit_locking": {
        "enabled": True,
        "big_trades_percentage": 50,
        "weekly_target_percentage": 30,
        "compound_percentage": 20
    }
}

MARKET_MAKING_CONFIG = {
    "strategy_type": "market_making",
    "max_daily_trades": 10000,
    "max_trades_per_minute": 7,
    "min_signal_interval_seconds": 8.5,
    "min_hold_time_seconds": 3,
    "max_hold_time_minutes": 2,
    "risk_reward_ratio": 1.1,
    "stop_loss_percentage": 0.005,  # 0.5%
    "take_profit_percentage": 0.002,  # 0.2%
    "partial_exit_levels": [
        {"percentage": 60, "target_multiplier": 1.05},
        {"percentage": 40, "target_multiplier": 1.1}
    ],
    "trailing_stop": False,
    "session_preference": ["london", "new_york"],
    "volatility_threshold": 0.015,
    "min_confidence": 0.7,
    "execution_priority": "HIGH",
    "slippage_tolerance": 0.0005,
    "profit_locking": {
        "enabled": True,
        "big_trades_percentage": 50,
        "weekly_target_percentage": 30,
        "compound_percentage": 20
    }
}

# ============================================================================
# TREND FOLLOWING STRATEGIES (Medium-Hold, Momentum)
# ============================================================================

TREND_FOLLOWING_CONFIG = {
    "strategy_type": "trend_following",
    "max_daily_trades": 100,
    "max_trades_per_minute": None,  # No rate limit
    "min_signal_interval_seconds": 0,
    "min_hold_time_minutes": 60,
    "max_hold_time_hours": 48,
    "risk_reward_ratio": 3.0,
    "stop_loss_percentage": 0.02,  # 2%
    "take_profit_percentage": 0.06,  # 6%
    "partial_exit_levels": [
        {"percentage": 25, "target_multiplier": 1.5},
        {"percentage": 25, "target_multiplier": 2.0},
        {"percentage": 50, "target_multiplier": 3.0}
    ],
    "trailing_stop": True,
    "trailing_distance": 0.02,
    "session_preference": ["london", "new_york", "asia"],
    "volatility_threshold": 0.03,
    "min_confidence": 0.75,
    "execution_priority": "MEDIUM",
    "slippage_tolerance": 0.005,
    "profit_locking": {
        "enabled": False,
        "big_trades_percentage": 0,
        "weekly_target_percentage": 0,
        "compound_percentage": 0
    }
}

# ============================================================================
# HIGH TIME FRAME STRATEGIES (Long-Hold, Major Trends)
# ============================================================================

HTF_CONFIG = {
    "strategy_type": "htf",
    "max_daily_trades": 20,
    "max_trades_per_minute": None,  # No rate limit
    "min_signal_interval_seconds": 0,
    "min_hold_time_hours": 24,
    "max_hold_time_days": 7,
    "risk_reward_ratio": 5.0,
    "stop_loss_percentage": 0.05,  # 5%
    "take_profit_percentage": 0.25,  # 25%
    "partial_exit_levels": [
        {"percentage": 20, "target_multiplier": 2.0},
        {"percentage": 30, "target_multiplier": 3.0},
        {"percentage": 50, "target_multiplier": 5.0}
    ],
    "trailing_stop": True,
    "trailing_distance": 0.05,
    "session_preference": ["asia", "london", "new_york"],
    "volatility_threshold": 0.04,
    "min_confidence": 0.8,
    "execution_priority": "LOW",
    "slippage_tolerance": 0.01,
    "profit_locking": {
        "enabled": False,
        "big_trades_percentage": 0,
        "weekly_target_percentage": 0,
        "compound_percentage": 0
    }
}

# ============================================================================
# NEWS DRIVEN STRATEGIES (Event-Based, Quick Reactions)
# ============================================================================

NEWS_DRIVEN_CONFIG = {
    "strategy_type": "news_driven",
    "max_daily_trades": 50,
    "max_trades_per_minute": None,  # No rate limit
    "min_signal_interval_seconds": 0,
    "min_hold_time_minutes": 15,
    "max_hold_time_hours": 4,
    "risk_reward_ratio": 2.0,
    "stop_loss_percentage": 0.015,  # 1.5%
    "take_profit_percentage": 0.03,  # 3%
    "partial_exit_levels": [
        {"percentage": 40, "target_multiplier": 1.3},
        {"percentage": 30, "target_multiplier": 1.6},
        {"percentage": 30, "target_multiplier": 2.0}
    ],
    "trailing_stop": False,
    "session_preference": ["new_york", "london"],
    "volatility_threshold": 0.025,
    "min_confidence": 0.7,
    "execution_priority": "HIGH",
    "slippage_tolerance": 0.003,
    "profit_locking": {
        "enabled": False,
        "big_trades_percentage": 0,
        "weekly_target_percentage": 0,
        "compound_percentage": 0
    }
}

# ============================================================================
# STATISTICAL ARBITRAGE STRATEGIES (Mean Reversion, Pairs)
# ============================================================================

STATISTICAL_ARBITRAGE_CONFIG = {
    "strategy_type": "statistical_arbitrage",
    "max_daily_trades": 200,
    "max_trades_per_minute": None,  # No rate limit
    "min_signal_interval_seconds": 0,
    "min_hold_time_minutes": 30,
    "max_hold_time_hours": 6,
    "risk_reward_ratio": 1.5,
    "stop_loss_percentage": 0.025,  # 2.5%
    "take_profit_percentage": 0.0375,  # 3.75%
    "partial_exit_levels": [
        {"percentage": 50, "target_multiplier": 1.2},
        {"percentage": 30, "target_multiplier": 1.4},
        {"percentage": 20, "target_multiplier": 1.5}
    ],
    "trailing_stop": False,
    "session_preference": ["asia", "london"],
    "volatility_threshold": 0.02,
    "min_confidence": 0.7,
    "execution_priority": "MEDIUM",
    "slippage_tolerance": 0.004,
    "profit_locking": {
        "enabled": False,
        "big_trades_percentage": 0,
        "weekly_target_percentage": 0,
        "compound_percentage": 0
    }
}

# ============================================================================
# SESSION CONFIGURATIONS
# ============================================================================

SESSION_CONFIGS = {
    "london": {
        "hours": [8, 16],  # 8 AM - 4 PM GMT
        "description": "High volume, best for HFT and trend following",
        "volatility_multiplier": 1.0,
        "spread_multiplier": 0.8
    },
    "new_york": {
        "hours": [13, 21],  # 1 PM - 9 PM GMT
        "description": "News-driven, best for event trading",
        "volatility_multiplier": 1.2,
        "spread_multiplier": 0.9
    },
    "asia": {
        "hours": [0, 8],  # 12 AM - 8 AM GMT
        "description": "Lower volume, best for HTF and mean reversion",
        "volatility_multiplier": 0.8,
        "spread_multiplier": 1.2
    },
    "overlap": {
        "hours": [16, 17, 8, 9],  # London-NY overlap, Asia-London overlap
        "description": "Highest volume, best for all strategies",
        "volatility_multiplier": 1.1,
        "spread_multiplier": 0.7
    }
}

# ============================================================================
# STRATEGY MAPPING
# ============================================================================

STRATEGY_CONFIG_MAP = {
    "arbitrage": ARBITRAGE_CONFIG,
    "market_making": MARKET_MAKING_CONFIG,
    "trend_following": TREND_FOLLOWING_CONFIG,
    "htf": HTF_CONFIG,
    "news_driven": NEWS_DRIVEN_CONFIG,
    "statistical_arbitrage": STATISTICAL_ARBITRAGE_CONFIG
}

def get_strategy_config(strategy_type: str) -> Dict[str, Any]:
    """Get configuration for a specific strategy type."""
    return STRATEGY_CONFIG_MAP.get(strategy_type, TREND_FOLLOWING_CONFIG)

def get_all_strategy_configs() -> Dict[str, Dict[str, Any]]:
    """Get all strategy configurations."""
    return STRATEGY_CONFIG_MAP

def get_session_config(session_name: str) -> Dict[str, Any]:
    """Get configuration for a specific trading session."""
    return SESSION_CONFIGS.get(session_name, SESSION_CONFIGS["london"])

def get_current_session() -> str:
    """Get current trading session based on GMT time."""
    from datetime import datetime
    current_hour = datetime.utcnow().hour
    
    if 8 <= current_hour <= 16:
        return "london"
    elif 13 <= current_hour <= 21:
        return "new_york"
    elif 0 <= current_hour <= 8:
        return "asia"
    else:
        return "overlap"
