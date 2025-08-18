#!/usr/bin/env python3
"""
Session Management System
Manages trading sessions and optimizes strategy selection based on current market conditions
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ...configs.strategy_configs import (
    get_session_config, 
    get_current_session, 
    get_strategy_config
)

class SessionManager:
    """Manage trading sessions and strategy optimization."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = None
        
        # Session configurations
        self.london_session_hours = config.get("london_session_hours", [8, 16])
        self.ny_session_hours = config.get("ny_session_hours", [13, 21])
        self.asia_session_hours = config.get("asia_session_hours", [0, 8])
        
        # Session tracking
        self.current_session = None
        self.session_start_time = None
        self.session_volume_multiplier = 1.0
        self.session_volatility_multiplier = 1.0
        
        # Strategy session preferences
        self.strategy_session_preferences = {
            "arbitrage": ["london", "new_york"],
            "market_making": ["london", "new_york"],
            "trend_following": ["london", "new_york", "asia"],
            "htf": ["asia", "london"],
            "news_driven": ["new_york", "london"],
            "statistical_arbitrage": ["asia", "london"]
        }
    
    def set_logger(self, logger):
        """Set logger for this session manager."""
        self.logger = logger
    
    def get_current_session_info(self) -> Dict[str, Any]:
        """Get detailed information about the current trading session."""
        try:
            current_hour = datetime.utcnow().hour
            session_name = self._determine_session(current_hour)
            session_config = get_session_config(session_name)
            
            # Calculate session progress
            session_progress = self._calculate_session_progress(session_name, current_hour)
            
            # Determine next session
            next_session = self._get_next_session(session_name)
            time_to_next = self._calculate_time_to_next_session(session_name, current_hour)
            
            session_info = {
                "current_session": session_name,
                "session_config": session_config,
                "current_hour_gmt": current_hour,
                "session_progress": session_progress,
                "next_session": next_session,
                "time_to_next_session_minutes": time_to_next,
                "is_active_session": self._is_active_session(session_name, current_hour),
                "volume_multiplier": session_config.get("volatility_multiplier", 1.0),
                "volatility_multiplier": session_config.get("volatility_multiplier", 1.0)
            }
            
            # Update internal state
            if self.current_session != session_name:
                self.current_session = session_name
                self.session_start_time = datetime.utcnow()
                self.session_volume_multiplier = session_config.get("volatility_multiplier", 1.0)
                self.session_volatility_multiplier = session_config.get("volatility_multiplier", 1.0)
                
                if self.logger:
                    self.logger.info(f"🌍 Trading session changed to: {session_name}")
            
            return session_info
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting session info: {e}")
            return {
                "current_session": "unknown",
                "error": str(e)
            }
    
    def _determine_session(self, current_hour: int) -> str:
        """Determine current trading session based on GMT hour."""
        if self.london_session_hours[0] <= current_hour <= self.london_session_hours[1]:
            return "london"
        elif self.ny_session_hours[0] <= current_hour <= self.ny_session_hours[1]:
            return "new_york"
        elif self.asia_session_hours[0] <= current_hour <= self.asia_session_hours[1]:
            return "asia"
        else:
            return "overlap"
    
    def _calculate_session_progress(self, session_name: str, current_hour: int) -> float:
        """Calculate how far through the current session we are (0.0 to 1.0)."""
        try:
            if session_name == "london":
                start_hour, end_hour = self.london_session_hours
            elif session_name == "new_york":
                start_hour, end_hour = self.ny_session_hours
            elif session_name == "asia":
                start_hour, end_hour = self.asia_session_hours
            else:
                return 0.5  # Overlap sessions
            
            session_duration = end_hour - start_hour
            if session_duration <= 0:
                return 0.5
            
            progress = (current_hour - start_hour) / session_duration
            return max(0.0, min(1.0, progress))
            
        except Exception:
            return 0.5
    
    def _get_next_session(self, current_session: str) -> str:
        """Get the next trading session."""
        session_order = ["asia", "london", "new_york"]
        
        try:
            current_index = session_order.index(current_session)
            next_index = (current_index + 1) % len(session_order)
            return session_order[next_index]
        except ValueError:
            return "london"  # Default
    
    def _calculate_time_to_next_session(self, current_session: str, current_hour: int) -> int:
        """Calculate minutes until next session starts."""
        try:
            if current_session == "london":
                next_start = self.ny_session_hours[0]
            elif current_session == "new_york":
                next_start = self.asia_session_hours[0]
            elif current_session == "asia":
                next_start = self.london_session_hours[0]
            else:
                return 0
            
            # Handle day boundary
            if next_start < current_hour:
                next_start += 24
            
            hours_until_next = next_start - current_hour
            return hours_until_next * 60
            
        except Exception:
            return 0
    
    def _is_active_session(self, session_name: str, current_hour: int) -> bool:
        """Check if the current session is active."""
        if session_name == "london":
            return self.london_session_hours[0] <= current_hour <= self.london_session_hours[1]
        elif session_name == "new_york":
            return self.ny_session_hours[0] <= current_hour <= self.ny_session_hours[1]
        elif session_name == "asia":
            return self.asia_session_hours[0] <= current_hour <= self.asia_session_hours[1]
        else:
            return True  # Overlap sessions are always active
    
    def select_session_appropriate_strategy(self, strategy_type: str) -> str:
        """Select the most appropriate strategy based on current market session."""
        try:
            current_session = get_current_session()
            session_config = get_session_config(current_session)
            
            # Get strategy configuration
            strategy_config = get_strategy_config(strategy_type)
            
            # Check if strategy prefers current session
            session_preference = strategy_config.get("session_preference", [])
            is_preferred_session = current_session in session_preference
            
            # Determine optimization level based on session and strategy
            if strategy_type in ["arbitrage", "market_making"]:
                if current_session in ["london", "new_york"]:
                    return "HFT_OPTIMIZED"  # Ultra-fast execution during active sessions
                else:
                    return "HFT_CONSERVATIVE"  # Slower execution during quiet sessions
            
            elif strategy_type == "trend_following":
                if current_session == "london":
                    return "MOMENTUM_DRIVEN"  # Follow London momentum
                elif current_session == "new_york":
                    return "TREND_AGGRESSIVE"  # Follow NY momentum
                elif current_session == "asia":
                    return "TREND_CONSERVATIVE"  # Conservative during Asia session
                else:
                    return "TREND_STANDARD"
            
            elif strategy_type == "htf":
                if current_session == "asia":
                    return "HTF_OPTIMIZED"  # High time frame analysis during Asia
                else:
                    return "HTF_STANDARD"
            
            elif strategy_type == "news_driven":
                if current_session == "new_york":
                    return "NEWS_OPTIMIZED"  # React to US news
                elif current_session == "london":
                    return "NEWS_EUROPE"  # React to European news
                else:
                    return "NEWS_CONSERVATIVE"
            
            elif strategy_type == "statistical_arbitrage":
                if current_session == "asia":
                    return "MEAN_REVERSION_OPTIMIZED"  # Asia tends to mean revert
                else:
                    return "MEAN_REVERSION_STANDARD"
            
            else:
                return "STANDARD"
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error selecting session strategy: {e}")
            return "STANDARD"
    
    def get_session_optimization_parameters(self, strategy_type: str) -> Dict[str, Any]:
        """Get optimization parameters for current session and strategy."""
        try:
            current_session = get_current_session()
            session_config = get_session_config(current_session)
            strategy_config = get_strategy_config(strategy_type)
            
            # Base parameters
            optimization_params = {
                "session": current_session,
                "session_config": session_config,
                "strategy_config": strategy_config,
                "volume_multiplier": session_config.get("volatility_multiplier", 1.0),
                "volatility_multiplier": session_config.get("volatility_multiplier", 1.0),
                "spread_multiplier": session_config.get("spread_multiplier", 1.0)
            }
            
            # Strategy-specific session adjustments
            if strategy_type in ["arbitrage", "market_making"]:
                if current_session in ["london", "new_york"]:
                    optimization_params["execution_speed"] = "ULTRA_FAST"
                    optimization_params["slippage_tolerance"] = 0.0005
                    optimization_params["max_hold_time"] = 300  # 5 minutes
                else:
                    optimization_params["execution_speed"] = "FAST"
                    optimization_params["slippage_tolerance"] = 0.001
                    optimization_params["max_hold_time"] = 600  # 10 minutes
            
            elif strategy_type == "trend_following":
                if current_session == "london":
                    optimization_params["momentum_threshold"] = 0.02
                    optimization_params["trend_strength_required"] = 0.7
                elif current_session == "new_york":
                    optimization_params["momentum_threshold"] = 0.025
                    optimization_params["trend_strength_required"] = 0.75
                else:
                    optimization_params["momentum_threshold"] = 0.03
                    optimization_params["trend_strength_required"] = 0.8
            
            elif strategy_type == "htf":
                if current_session == "asia":
                    optimization_params["timeframe_preference"] = "DAILY"
                    optimization_params["volatility_threshold"] = 0.04
                else:
                    optimization_params["timeframe_preference"] = "WEEKLY"
                    optimization_params["volatility_threshold"] = 0.03
            
            elif strategy_type == "news_driven":
                if current_session == "new_york":
                    optimization_params["news_sensitivity"] = "HIGH"
                    optimization_params["reaction_time"] = 30  # seconds
                else:
                    optimization_params["news_sensitivity"] = "MEDIUM"
                    optimization_params["reaction_time"] = 60  # seconds
            
            elif strategy_type == "statistical_arbitrage":
                if current_session == "asia":
                    optimization_params["mean_reversion_threshold"] = 0.02
                    optimization_params["correlation_threshold"] = 0.8
                else:
                    optimization_params["mean_reversion_threshold"] = 0.025
                    optimization_params["correlation_threshold"] = 0.75
            
            return optimization_params
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting session optimization parameters: {e}")
            return {
                "session": "unknown",
                "error": str(e)
            }
    
    def is_strategy_optimal_for_session(self, strategy_type: str) -> Dict[str, Any]:
        """Check if a strategy is optimal for the current session."""
        try:
            current_session = get_current_session()
            strategy_config = get_strategy_config(strategy_type)
            
            session_preference = strategy_config.get("session_preference", [])
            is_preferred = current_session in session_preference
            
            # Calculate session score
            session_score = 0
            if is_preferred:
                session_score += 100
            elif current_session == "overlap":
                session_score += 75  # Overlap sessions are good for all strategies
            else:
                session_score += 50  # Non-preferred sessions still work
            
            # Adjust score based on session characteristics
            session_config = get_session_config(current_session)
            if "High volume" in session_config.get("description", ""):
                session_score += 25
            elif "Lower volume" in session_config.get("description", ""):
                session_score -= 25
            
            return {
                "strategy_type": strategy_type,
                "current_session": current_session,
                "is_optimal": session_score >= 75,
                "session_score": session_score,
                "is_preferred_session": is_preferred,
                "recommendation": "OPTIMAL" if session_score >= 75 else "SUBOPTIMAL"
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking strategy session optimality: {e}")
            return {
                "strategy_type": strategy_type,
                "error": str(e),
                "is_optimal": False
            }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary."""
        try:
            current_info = self.get_current_session_info()
            
            # Get all strategy types
            from ..configs.strategy_configs import get_all_strategy_configs
            all_strategies = get_all_strategy_configs()
            
            # Assess each strategy for current session
            strategy_assessments = {}
            for strategy_type in all_strategies:
                assessment = self.is_strategy_optimal_for_session(strategy_type)
                strategy_assessments[strategy_type] = assessment
            
            return {
                "current_session": current_info,
                "strategy_assessments": strategy_assessments,
                "recommended_strategies": [
                    strategy for strategy, assessment in strategy_assessments.items()
                    if assessment.get("is_optimal", False)
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting session summary: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
