#!/usr/bin/env python3
"""
Strategy-Specific SL/TP Calculator
Provides SL/TP calculations for each strategy type with their unique characteristics
"""

import math
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from ...configs.strategy_configs import (
    get_strategy_config, 
    get_session_config, 
    get_current_session
)

class StrategySLTPCalculator:
    """Calculate SL/TP for different strategy types."""
    
    def __init__(self):
        self.logger = None  # Will be set by parent class
        
    def set_logger(self, logger):
        """Set logger for this calculator."""
        self.logger = logger
    
    def calculate_sltp(
        self, 
        strategy_type: str, 
        action: str, 
        entry_price: float, 
        bid: float, 
        ask: float,
        volatility: float = 0.02,
        pattern_strength: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate SL/TP based on strategy type."""
        
        # Get strategy configuration
        strategy_config = get_strategy_config(strategy_type)
        current_session = get_current_session()
        session_config = get_session_config(current_session)
        
        # Apply session adjustments
        volatility = volatility * session_config.get("volatility_multiplier", 1.0)
        
        # Calculate based on strategy type
        if strategy_type == "arbitrage":
            return self._calculate_arbitrage_sltp(
                action, entry_price, bid, ask, volatility, strategy_config, session_config
            )
        elif strategy_type == "market_making":
            return self._calculate_market_making_sltp(
                action, entry_price, bid, ask, volatility, strategy_config, session_config
            )
        elif strategy_type == "trend_following":
            return self._calculate_trend_following_sltp(
                action, entry_price, bid, ask, volatility, strategy_config, session_config
            )
        elif strategy_type == "htf":
            return self._calculate_htf_sltp(
                action, entry_price, bid, ask, volatility, strategy_config, session_config
            )
        elif strategy_type == "news_driven":
            return self._calculate_news_driven_sltp(
                action, entry_price, bid, ask, volatility, strategy_config, session_config
            )
        elif strategy_type == "statistical_arbitrage":
            return self._calculate_statistical_arbitrage_sltp(
                action, entry_price, bid, ask, volatility, strategy_config, session_config
            )
        else:
            # Default to trend following
            return self._calculate_trend_following_sltp(
                action, entry_price, bid, ask, volatility, strategy_config, session_config
            )
    
    def _calculate_arbitrage_sltp(
        self, 
        action: str, 
        entry_price: float, 
        bid: float, 
        ask: float,
        volatility: float,
        strategy_config: Dict[str, Any],
        session_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate ultra-tight SL/TP for HFT arbitrage."""
        
        spread = ask - bid
        base_sl_distance = entry_price * strategy_config["stop_loss_percentage"]
        base_tp_distance = entry_price * strategy_config["take_profit_percentage"]
        
        # Adjust for session (tighter during active sessions)
        session_multiplier = 0.8 if session_config["description"].startswith("High volume") else 1.0
        
        if action.upper() == "BUY":
            stop_loss = entry_price - (base_sl_distance * session_multiplier)
            take_profit = entry_price + (base_tp_distance * session_multiplier)
        else:
            stop_loss = entry_price + (base_sl_distance * session_multiplier)
            take_profit = entry_price - (base_tp_distance * session_multiplier)
        
        # Calculate risk-reward ratio
        sl_distance = abs(entry_price - stop_loss)
        tp_distance = abs(take_profit - entry_price)
        risk_reward_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
        
        return {
            "stop_loss": round(stop_loss, 6),
            "take_profit": round(take_profit, 6),
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "volatility": volatility,  # Add volatility to the return value
            "exit_strategy": "hft_arbitrage",
            "partial_exits": strategy_config["partial_exit_levels"],
            "trailing_stop": strategy_config["trailing_stop"],
            "hold_time_seconds": strategy_config["min_hold_time_seconds"],
            "strategy_config": strategy_config
        }
    
    def _calculate_market_making_sltp(
        self, 
        action: str, 
        entry_price: float, 
        bid: float, 
        ask: float,
        volatility: float,
        strategy_config: Dict[str, Any],
        session_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate spread-based SL/TP for market making."""
        
        spread = ask - bid
        spread_percentage = spread / entry_price
        
        # SL/TP based on spread and volatility
        sl_distance = max(
            entry_price * strategy_config["stop_loss_percentage"],
            spread * 2  # At least 2x spread
        )
        tp_distance = max(
            entry_price * strategy_config["take_profit_percentage"],
            spread * 1.5  # At least 1.5x spread
        )
        
        if action.upper() == "BUY":
            stop_loss = entry_price - sl_distance
            take_profit = entry_price + tp_distance
        else:
            stop_loss = entry_price + sl_distance
            take_profit = entry_price - tp_distance
        
        risk_reward_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
        
        return {
            "stop_loss": round(stop_loss, 6),
            "take_profit": round(take_profit, 6),
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "volatility": volatility,  # Add volatility to the return value
            "exit_strategy": "market_making",
            "partial_exits": strategy_config["partial_exit_levels"],
            "trailing_stop": strategy_config["trailing_stop"],
            "hold_time_seconds": strategy_config["min_hold_time_seconds"],
            "strategy_config": strategy_config
        }
    
    def _calculate_trend_following_sltp(
        self, 
        action: str, 
        entry_price: float, 
        bid: float, 
        ask: float,
        volatility: float,
        strategy_config: Dict[str, Any],
        session_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate trend-following SL/TP with trailing stops."""
        
        # Use ATR-based SL/TP for trend following
        atr_distance = entry_price * volatility
        sl_distance = entry_price * strategy_config["stop_loss_percentage"]
        tp_distance = entry_price * strategy_config["take_profit_percentage"]
        
        # Use the larger of ATR or configured percentage
        final_sl_distance = max(sl_distance, atr_distance)
        final_tp_distance = max(tp_distance, atr_distance * strategy_config["risk_reward_ratio"])
        
        if action.upper() == "BUY":
            stop_loss = entry_price - final_sl_distance
            take_profit = entry_price + final_tp_distance
        else:
            stop_loss = entry_price + final_sl_distance
            take_profit = entry_price - final_tp_distance
        
        risk_reward_ratio = final_tp_distance / final_sl_distance if final_sl_distance > 0 else 0
        
        return {
            "stop_loss": round(stop_loss, 6),
            "take_profit": round(take_profit, 6),
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "volatility": volatility,  # Add volatility to the return value
            "exit_strategy": "trend_following",
            "partial_exits": strategy_config["partial_exit_levels"],
            "trailing_stop": strategy_config["trailing_stop"],
            "trailing_distance": strategy_config.get("trailing_distance", 0.02),
            "hold_time_minutes": strategy_config["min_hold_time_minutes"],
            "strategy_config": strategy_config
        }
    
    def _calculate_htf_sltp(
        self, 
        action: str, 
        entry_price: float, 
        bid: float, 
        ask: float,
        volatility: float,
        strategy_config: Dict[str, Any],
        session_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate HTF SL/TP with wide targets and trailing stops."""
        
        # HTF uses wider SL/TP for major trends
        sl_distance = entry_price * strategy_config["stop_loss_percentage"]
        tp_distance = entry_price * strategy_config["take_profit_percentage"]
        
        # Adjust for session (wider during quiet sessions)
        session_multiplier = 1.2 if "Lower volume" in session_config["description"] else 1.0
        
        if action.upper() == "BUY":
            stop_loss = entry_price - (sl_distance * session_multiplier)
            take_profit = entry_price + (tp_distance * session_multiplier)
        else:
            stop_loss = entry_price + (sl_distance * session_multiplier)
            take_profit = entry_price - (tp_distance * session_multiplier)
        
        risk_reward_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
        
        return {
            "stop_loss": round(stop_loss, 6),
            "take_profit": round(take_profit, 6),
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "volatility": volatility,  # Add volatility to the return value
            "exit_strategy": "htf",
            "partial_exits": strategy_config["partial_exit_levels"],
            "trailing_stop": strategy_config["trailing_stop"],
            "trailing_distance": strategy_config.get("trailing_distance", 0.05),
            "hold_time_hours": strategy_config["min_hold_time_hours"],
            "strategy_config": strategy_config
        }
    
    def _calculate_news_driven_sltp(
        self, 
        action: str, 
        entry_price: float, 
        bid: float, 
        ask: float,
        volatility: float,
        strategy_config: Dict[str, Any],
        session_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate news-driven SL/TP with event-based exits."""
        
        # News-driven uses tighter SL/TP for quick reactions
        sl_distance = entry_price * strategy_config["stop_loss_percentage"]
        tp_distance = entry_price * strategy_config["take_profit_percentage"]
        
        # Adjust for news session (NY session gets tighter SL/TP)
        session_multiplier = 0.8 if "News-driven" in session_config["description"] else 1.0
        
        if action.upper() == "BUY":
            stop_loss = entry_price - (sl_distance * session_multiplier)
            take_profit = entry_price + (tp_distance * session_multiplier)
        else:
            stop_loss = entry_price + (sl_distance * session_multiplier)
            take_profit = entry_price - (tp_distance * session_multiplier)
        
        risk_reward_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
        
        return {
            "stop_loss": round(stop_loss, 6),
            "take_profit": round(take_profit, 6),
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "volatility": volatility,  # Add volatility to the return value
            "exit_strategy": "news_driven",
            "partial_exits": strategy_config["partial_exit_levels"],
            "trailing_stop": strategy_config["trailing_stop"],
            "hold_time_minutes": strategy_config["min_hold_time_minutes"],
            "strategy_config": strategy_config
        }
    
    def _calculate_statistical_arbitrage_sltp(
        self, 
        action: str, 
        entry_price: float, 
        bid: float, 
        ask: float,
        volatility: float,
        strategy_config: Dict[str, Any],
        session_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate statistical arbitrage SL/TP with mean reversion exits."""
        
        # Statistical arbitrage uses mean reversion logic
        sl_distance = entry_price * strategy_config["stop_loss_percentage"]
        tp_distance = entry_price * strategy_config["take_profit_percentage"]
        
        # Adjust for Asia session (better for mean reversion)
        session_multiplier = 0.9 if "Lower volume" in session_config["description"] else 1.0
        
        if action.upper() == "BUY":
            stop_loss = entry_price - (sl_distance * session_multiplier)
            take_profit = entry_price + (tp_distance * session_multiplier)
        else:
            stop_loss = entry_price + (sl_distance * session_multiplier)
            take_profit = entry_price - (tp_distance * session_multiplier)
        
        risk_reward_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
        
        return {
            "stop_loss": round(stop_loss, 6),
            "take_profit": round(take_profit, 6),
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "volatility": volatility,  # Add volatility to the return value
            "exit_strategy": "statistical_arbitrage",
            "partial_exits": strategy_config["partial_exit_levels"],
            "trailing_stop": strategy_config["trailing_stop"],
            "hold_time_minutes": strategy_config["min_hold_time_minutes"],
            "strategy_config": strategy_config
        }
