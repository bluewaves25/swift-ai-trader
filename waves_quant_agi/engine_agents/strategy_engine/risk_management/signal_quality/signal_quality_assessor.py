#!/usr/bin/env python3
"""
Signal Quality Assessment System
Evaluates trading signals based on multiple criteria and strategy-specific requirements
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...configs.strategy_configs import (
    get_strategy_config, 
    get_session_config, 
    get_current_session
)

class SignalQualityAssessor:
    """Assess signal quality and reject poor signals."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = None
        self.stats = {"daily_pnl": 0}
        
        # Quality thresholds
        self.min_signal_confidence = config.get("min_signal_confidence", 0.65)
        self.min_risk_reward_ratio = config.get("min_risk_reward_ratio", 1.2)
        self.max_daily_loss_percentage = config.get("max_daily_loss_percentage", 2.0)
        
        # Session hours
        self.london_session_hours = config.get("london_session_hours", [8, 16])
        self.ny_session_hours = config.get("ny_session_hours", [13, 21])
        self.asia_session_hours = config.get("asia_session_hours", [0, 8])
    
    def set_logger(self, logger):
        """Set logger for this assessor."""
        self.logger = logger
    
    def set_stats(self, stats: Dict[str, Any]):
        """Set current trading statistics."""
        self.stats = stats
    
    def assess_signal_quality(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Assess signal quality and reject poor signals."""
        try:
            quality_score = 0
            rejection_reasons = []
            
            # 1. Confidence Check
            confidence = signal.get("confidence", 0)
            if confidence < self.min_signal_confidence:
                rejection_reasons.append(f"Low confidence: {confidence:.2f} < {self.min_signal_confidence}")
                quality_score -= 30
            else:
                quality_score += confidence * 20
            
            # 2. Risk-Reward Ratio Check
            sltp_metadata = signal.get("sltp_metadata", {})
            risk_reward = sltp_metadata.get("risk_reward_ratio", 0)
            strategy_type = signal.get("strategy_type", "unknown")
            
            # HFT strategies (arbitrage, market making) have different R:R requirements
            if strategy_type in ["arbitrage", "market_making"]:
                # HFT strategies can have lower R:R ratios but need higher confidence
                min_rr_for_hft = 0.3  # Allow lower R:R for HFT
                if risk_reward < min_rr_for_hft:
                    rejection_reasons.append(f"Poor R:R ratio for HFT: {risk_reward:.2f} < {min_rr_for_hft}")
                    quality_score -= 15  # Smaller penalty for HFT
                else:
                    quality_score += min(risk_reward * 15, 25)  # Cap at 25 points for HFT
            else:
                # Standard strategies need higher R:R ratios
                if risk_reward < self.min_risk_reward_ratio:
                    rejection_reasons.append(f"Poor R:R ratio: {risk_reward:.2f} < {self.min_risk_reward_ratio}")
                    quality_score -= 25
                else:
                    quality_score += min(risk_reward * 10, 30)  # Cap at 30 points
            
            # 3. Session Timing Check
            current_hour = datetime.now().hour
            strategy_type = signal.get("strategy_type", "unknown")
            
            # HFT strategies work best during London/NY sessions
            if strategy_type in ["arbitrage", "market_making"]:
                if self.london_session_hours[0] <= current_hour <= self.london_session_hours[1] or \
                   self.ny_session_hours[0] <= current_hour <= self.ny_session_hours[1]:
                    quality_score += 15  # Bonus for active sessions
                else:
                    quality_score -= 10  # Penalty for quiet sessions
                    rejection_reasons.append("HFT strategy during quiet session")
            
            # 4. Volatility Check
            volatility = sltp_metadata.get("volatility", 0)
            if volatility > 0.05:  # 5% volatility threshold
                quality_score -= 15
                rejection_reasons.append(f"High volatility: {volatility:.3f}")
            elif volatility < 0.001:  # 0.1% volatility threshold
                quality_score -= 10
                rejection_reasons.append(f"Low volatility: {volatility:.3f}")
            else:
                quality_score += 10
            
            # 5. Daily Loss Limit Check
            daily_pnl = self.stats.get("daily_pnl", 0)
            if daily_pnl < -(self.max_daily_loss_percentage / 100):  # Convert percentage to decimal
                rejection_reasons.append(f"Daily loss limit reached: {daily_pnl:.2f}%")
                quality_score -= 50  # Heavy penalty
            
            # 6. Pattern Strength Check (for pattern-based signals)
            pattern_strength = signal.get("pattern_strength", 0)
            if pattern_strength < 0.5:
                quality_score -= 20
                rejection_reasons.append(f"Weak pattern: {pattern_strength:.2f}")
            else:
                quality_score += pattern_strength * 15
            
            # 7. Strategy-Specific Quality Check
            strategy_quality = self._assess_strategy_specific_quality(signal)
            quality_score += strategy_quality["score"]
            rejection_reasons.extend(strategy_quality["reasons"])
            
            # Final Quality Assessment
            is_acceptable = quality_score >= 50  # Minimum quality threshold
            
            quality_assessment = {
                "quality_score": quality_score,
                "is_acceptable": is_acceptable,
                "rejection_reasons": rejection_reasons,
                "recommendation": "ACCEPT" if is_acceptable else "REJECT",
                "session_timing": "ACTIVE" if (self.london_session_hours[0] <= current_hour <= self.london_session_hours[1] or 
                                             self.ny_session_hours[0] <= current_hour <= self.ny_session_hours[1]) else "QUIET",
                "strategy_quality": strategy_quality
            }
            
            if not is_acceptable:
                if self.logger:
                    self.logger.warning(f"❌ Signal rejected for {signal.get('symbol', 'unknown')}: {', '.join(rejection_reasons)}")
            else:
                if self.logger:
                    self.logger.info(f"✅ Signal accepted for {signal.get('symbol', 'unknown')}: Quality score {quality_score}")
            
            return quality_assessment
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error assessing signal quality: {e}")
            return {
                "quality_score": 0,
                "is_acceptable": False,
                "rejection_reasons": [f"Error in quality assessment: {e}"],
                "recommendation": "REJECT",
                "session_timing": "UNKNOWN"
            }
    
    def _assess_strategy_specific_quality(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality based on strategy-specific requirements."""
        strategy_type = signal.get("strategy_type", "unknown")
        strategy_config = get_strategy_config(strategy_type)
        
        score = 0
        reasons = []
        
        # Check strategy-specific confidence requirements
        min_confidence = strategy_config.get("min_confidence", 0.65)
        confidence = signal.get("confidence", 0)
        
        if confidence < min_confidence:
            reasons.append(f"Below strategy confidence threshold: {confidence:.2f} < {min_confidence}")
            score -= 20
        else:
            score += 10
        
        # Check volatility thresholds
        volatility = signal.get("sltp_metadata", {}).get("volatility", 0)
        volatility_threshold = strategy_config.get("volatility_threshold", 0.05)
        
        if volatility > volatility_threshold:
            reasons.append(f"Volatility exceeds strategy threshold: {volatility:.3f} > {volatility_threshold}")
            score -= 15
        elif volatility < volatility_threshold * 0.1:  # Too low volatility
            reasons.append(f"Volatility too low for strategy: {volatility:.3f} < {volatility_threshold * 0.1}")
            score -= 10
        else:
            score += 5
        
        # Check session preference
        current_session = get_current_session()
        session_preference = strategy_config.get("session_preference", [])
        
        if session_preference and current_session not in session_preference:
            reasons.append(f"Strategy prefers {', '.join(session_preference)} sessions, current: {current_session}")
            score -= 10
        else:
            score += 5
        
        # Check risk-reward ratio against strategy requirement
        strategy_rr = strategy_config.get("risk_reward_ratio", 1.0)
        signal_rr = signal.get("sltp_metadata", {}).get("risk_reward_ratio", 0)
        
        if signal_rr < strategy_rr:
            reasons.append(f"R:R ratio below strategy requirement: {signal_rr:.2f} < {strategy_rr}")
            score -= 15
        else:
            score += 10
        
        return {
            "score": score,
            "reasons": reasons,
            "strategy_config": strategy_config
        }
    
    def assess_signal_correlation(self, new_signal: Dict[str, Any], existing_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess if new signal conflicts with existing signals."""
        try:
            symbol = new_signal.get("symbol", "")
            action = new_signal.get("action", "")
            strategy_type = new_signal.get("strategy_type", "")
            
            conflicts = []
            is_legitimate_hedging = False
            
            for existing_signal in existing_signals:
                if existing_signal.get("symbol") == symbol:
                    existing_action = existing_signal.get("action", "")
                    existing_strategy = existing_signal.get("strategy_type", "")
                    
                    # Check for direct conflict
                    if existing_action != action:
                        # Check if this is legitimate hedging
                        if self._is_legitimate_hedging(strategy_type, existing_strategy, action, existing_action):
                            is_legitimate_hedging = True
                        else:
                            conflicts.append({
                                "existing_action": existing_action,
                                "existing_strategy": existing_strategy,
                                "conflict_type": "contradictory_action"
                            })
            
            return {
                "has_conflicts": len(conflicts) > 0 and not is_legitimate_hedging,
                "conflicts": conflicts,
                "is_legitimate_hedging": is_legitimate_hedging,
                "recommendation": "ACCEPT" if not conflicts or is_legitimate_hedging else "REJECT"
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error assessing signal correlation: {e}")
            return {
                "has_conflicts": True,
                "conflicts": [{"error": str(e)}],
                "is_legitimate_hedging": False,
                "recommendation": "REJECT"
            }
    
    def _is_legitimate_hedging(self, new_strategy: str, existing_strategy: str, new_action: str, existing_action: str) -> bool:
        """Determine if hedging is legitimate based on strategy types."""
        
        # HFT strategies can hedge with each other
        if new_strategy in ["arbitrage", "market_making"] and existing_strategy in ["arbitrage", "market_making"]:
            return True
        
        # Statistical arbitrage can hedge with mean reversion
        if new_strategy == "statistical_arbitrage" and existing_strategy == "statistical_arbitrage":
            return True
        
        # News-driven strategies can hedge with each other
        if new_strategy == "news_driven" and existing_strategy == "news_driven":
            return True
        
        # HTF strategies can hedge with each other
        if new_strategy == "htf" and existing_strategy == "htf":
            return True
        
        return False
