#!/usr/bin/env python3
"""
Pattern Analyzer - CORE REFACTORED MODULE
Handles pattern recognition and market intelligence analysis
Separated from main agent for better manageability

REFACTORED FOR SIMPLICITY:
- Core pattern recognition functionality
- Market intelligence analysis
- Clean separation of pattern logic
"""

import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from ...shared_utils import get_shared_logger

class PatternAnalyzer:
    """
    Core pattern analysis engine - handles market pattern recognition.
    Separated from main agent for better code organization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("intelligence", "pattern_analyzer")
        # self.learner = get_agent_learner("intelligence", LearningType.PATTERN_RECOGNITION, 10)
        
        # Pattern analysis state
        self.analysis_stats = {
            "patterns_analyzed": 0,
            "patterns_detected": 0,
            "accuracy_score": 0.0,
            "false_positives": 0,
            "pattern_cache_hits": 0
        }
        
        # Pattern cache for performance
        self.pattern_cache = {}
        self.cache_ttl = config.get("pattern_cache_ttl", 300)  # 5 minutes
        
        # Pattern detection thresholds
        self.pattern_thresholds = {
            "trend_strength": 0.3,      # 30% trend confidence
            "breakout_strength": 0.4,   # 40% breakout confidence
            "reversal_strength": 0.35,  # 35% reversal confidence
            "support_resistance": 0.5,  # 50% S&R confidence
            "correlation_strength": 0.6 # 60% correlation confidence
        }
        
    async def analyze_patterns(self, market_data: Dict[str, Any], 
                             strategy_type: str = "general") -> Dict[str, Any]:
        """
        Analyze market patterns for specific strategy type.
        This is the main pattern analysis method.
        """
        start_time = time.time()
        
        try:
            self.analysis_stats["patterns_analyzed"] += 1
            
            # Check cache first
            cache_key = self._generate_cache_key(market_data, strategy_type)
            cached_result = self._get_from_cache(cache_key)
            
            if cached_result:
                self.analysis_stats["pattern_cache_hits"] += 1
                return cached_result
            
            # Perform pattern analysis based on strategy type
            pattern_analysis = await self._perform_pattern_analysis(market_data, strategy_type)
            
            # Enhance with market intelligence
            intelligence_analysis = await self._add_market_intelligence(pattern_analysis, market_data)
            
            # Learn from analysis (removed - handled by Strategy Engine)
            # await self._learn_from_analysis(market_data, intelligence_analysis, start_time)
            
            # Cache results
            self._cache_result(cache_key, intelligence_analysis)
            
            # Update statistics
            if intelligence_analysis.get("patterns_found", 0) > 0:
                self.analysis_stats["patterns_detected"] += 1
            
            return intelligence_analysis
            
        except Exception as e:
            self.logger.error(f"Error in pattern analysis: {e}")
            return {"error": str(e), "patterns_found": 0}
    
    async def _perform_pattern_analysis(self, market_data: Dict[str, Any], 
                                      strategy_type: str) -> Dict[str, Any]:
        """Perform core pattern analysis based on strategy type."""
        
        patterns = {
            "trend_patterns": [],
            "reversal_patterns": [],
            "breakout_patterns": [],
            "support_resistance": [],
            "correlation_patterns": []
        }
        
        try:
            # Analyze different pattern types based on strategy
            if strategy_type in ["trend_following", "general"]:
                trend_patterns = await self._detect_trend_patterns(market_data)
                patterns["trend_patterns"] = trend_patterns
            
            if strategy_type in ["statistical", "mean_reversion", "general"]:
                reversal_patterns = await self._detect_reversal_patterns(market_data)
                patterns["reversal_patterns"] = reversal_patterns
            
            if strategy_type in ["breakout", "momentum", "general"]:
                breakout_patterns = await self._detect_breakout_patterns(market_data)
                patterns["breakout_patterns"] = breakout_patterns
            
            if strategy_type in ["support_resistance", "technical", "general"]:
                sr_patterns = await self._detect_support_resistance(market_data)
                patterns["support_resistance"] = sr_patterns
            
            if strategy_type in ["correlation", "arbitrage", "general"]:
                correlation_patterns = await self._detect_correlation_patterns(market_data)
                patterns["correlation_patterns"] = correlation_patterns
            
            # Calculate overall pattern strength
            total_patterns = sum(len(pattern_list) for pattern_list in patterns.values())
            
            analysis_result = {
                "patterns": patterns,
                "patterns_found": total_patterns,
                "pattern_strength": self._calculate_pattern_strength(patterns),
                "strategy_type": strategy_type,
                "timestamp": time.time()
            }
            
            return analysis_result
            
        except Exception as e:
            self.logger.warning(f"Error in core pattern analysis: {e}")
            return {"patterns": patterns, "patterns_found": 0, "error": str(e)}
    
    async def _detect_trend_patterns(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect trend patterns in market data."""
        trends = []
        
        try:
            # Simple trend detection using price data
            prices = market_data.get("price_history", [market_data.get("price", 0)])
            
            if len(prices) < 3:
                return trends
            
            # Calculate trend strength
            price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            positive_changes = sum(1 for change in price_changes if change > 0)
            trend_ratio = positive_changes / len(price_changes) if price_changes else 0.5
            
            # Detect uptrend
            if trend_ratio > 0.6:  # 60% positive moves
                trend_strength = (trend_ratio - 0.5) * 2  # Normalize to 0-1
                if trend_strength > self.pattern_thresholds["trend_strength"]:
                    trends.append({
                        "type": "uptrend",
                        "strength": trend_strength,
                        "confidence": min(0.9, trend_strength + 0.1),
                        "duration": len(prices),
                        "details": {
                            "trend_ratio": trend_ratio,
                            "price_changes": len(price_changes)
                        }
                    })
            
            # Detect downtrend
            elif trend_ratio < 0.4:  # 40% positive moves (60% negative)
                trend_strength = (0.5 - trend_ratio) * 2  # Normalize to 0-1
                if trend_strength > self.pattern_thresholds["trend_strength"]:
                    trends.append({
                        "type": "downtrend",
                        "strength": trend_strength,
                        "confidence": min(0.9, trend_strength + 0.1),
                        "duration": len(prices),
                        "details": {
                            "trend_ratio": trend_ratio,
                            "price_changes": len(price_changes)
                        }
                    })
                    
        except Exception as e:
            self.logger.warning(f"Error detecting trend patterns: {e}")
        
        return trends
    
    async def _detect_reversal_patterns(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect reversal patterns in market data."""
        reversals = []
        
        try:
            current_price = market_data.get("price", 0)
            volatility = market_data.get("volatility", 0.02)
            volume = market_data.get("volume", 0)
            average_volume = market_data.get("average_volume", volume)
            
            # Detect potential reversal based on volatility and volume
            volume_ratio = volume / average_volume if average_volume > 0 else 1.0
            
            # High volatility + high volume = potential reversal
            if volatility > 0.05 and volume_ratio > 1.5:  # 5% volatility, 1.5x volume
                reversal_strength = min(1.0, (volatility * 10 + volume_ratio - 1) / 2)
                
                if reversal_strength > self.pattern_thresholds["reversal_strength"]:
                    reversals.append({
                        "type": "potential_reversal",
                        "strength": reversal_strength,
                        "confidence": min(0.8, reversal_strength),
                        "trigger_factors": ["high_volatility", "high_volume"],
                        "details": {
                            "volatility": volatility,
                            "volume_ratio": volume_ratio,
                            "current_price": current_price
                        }
                    })
                    
        except Exception as e:
            self.logger.warning(f"Error detecting reversal patterns: {e}")
        
        return reversals
    
    async def _detect_breakout_patterns(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect breakout patterns in market data."""
        breakouts = []
        
        try:
            current_price = market_data.get("price", 0)
            high_price = market_data.get("high_24h", current_price)
            low_price = market_data.get("low_24h", current_price)
            volume = market_data.get("volume", 0)
            average_volume = market_data.get("average_volume", volume)
            
            # Calculate price range
            price_range = high_price - low_price if high_price > low_price else 0
            range_ratio = (current_price - low_price) / price_range if price_range > 0 else 0.5
            
            volume_ratio = volume / average_volume if average_volume > 0 else 1.0
            
            # Detect breakout above resistance
            if range_ratio > 0.95 and volume_ratio > 1.2:  # Near high with volume
                breakout_strength = min(1.0, range_ratio * volume_ratio / 1.2)
                
                if breakout_strength > self.pattern_thresholds["breakout_strength"]:
                    breakouts.append({
                        "type": "upward_breakout",
                        "strength": breakout_strength,
                        "confidence": min(0.85, breakout_strength),
                        "direction": "up",
                        "details": {
                            "range_ratio": range_ratio,
                            "volume_ratio": volume_ratio,
                            "price_range": price_range
                        }
                    })
            
            # Detect breakout below support
            elif range_ratio < 0.05 and volume_ratio > 1.2:  # Near low with volume
                breakout_strength = min(1.0, (1 - range_ratio) * volume_ratio / 1.2)
                
                if breakout_strength > self.pattern_thresholds["breakout_strength"]:
                    breakouts.append({
                        "type": "downward_breakout",
                        "strength": breakout_strength,
                        "confidence": min(0.85, breakout_strength),
                        "direction": "down",
                        "details": {
                            "range_ratio": range_ratio,
                            "volume_ratio": volume_ratio,
                            "price_range": price_range
                        }
                    })
                    
        except Exception as e:
            self.logger.warning(f"Error detecting breakout patterns: {e}")
        
        return breakouts
    
    async def _detect_support_resistance(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect support and resistance levels."""
        sr_levels = []
        
        try:
            current_price = market_data.get("price", 0)
            high_price = market_data.get("high_24h", current_price)
            low_price = market_data.get("low_24h", current_price)
            
            # Simple S&R detection using 24h high/low
            price_range = high_price - low_price if high_price > low_price else 0
            
            if price_range > 0:
                # Resistance level confidence
                distance_to_high = (high_price - current_price) / price_range
                resistance_strength = 1.0 - distance_to_high
                
                if resistance_strength > self.pattern_thresholds["support_resistance"]:
                    sr_levels.append({
                        "type": "resistance",
                        "level": high_price,
                        "strength": resistance_strength,
                        "confidence": min(0.8, resistance_strength),
                        "distance": distance_to_high,
                        "details": {
                            "price_range": price_range,
                            "current_price": current_price
                        }
                    })
                
                # Support level confidence
                distance_to_low = (current_price - low_price) / price_range
                support_strength = 1.0 - distance_to_low
                
                if support_strength > self.pattern_thresholds["support_resistance"]:
                    sr_levels.append({
                        "type": "support",
                        "level": low_price,
                        "strength": support_strength,
                        "confidence": min(0.8, support_strength),
                        "distance": distance_to_low,
                        "details": {
                            "price_range": price_range,
                            "current_price": current_price
                        }
                    })
                    
        except Exception as e:
            self.logger.warning(f"Error detecting support/resistance: {e}")
        
        return sr_levels
    
    async def _detect_correlation_patterns(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect correlation patterns across markets."""
        correlations = []
        
        try:
            # Get correlation data from market data
            correlation_data = market_data.get("correlations", {})
            
            for asset_pair, correlation in correlation_data.items():
                correlation_strength = abs(correlation)
                
                if correlation_strength > self.pattern_thresholds["correlation_strength"]:
                    correlations.append({
                        "type": "strong_correlation",
                        "asset_pair": asset_pair,
                        "correlation": correlation,
                        "strength": correlation_strength,
                        "confidence": min(0.9, correlation_strength),
                        "direction": "positive" if correlation > 0 else "negative",
                        "details": {
                            "raw_correlation": correlation,
                            "absolute_strength": correlation_strength
                        }
                    })
                    
        except Exception as e:
            self.logger.warning(f"Error detecting correlation patterns: {e}")
        
        return correlations
    
    async def _add_market_intelligence(self, pattern_analysis: Dict[str, Any], 
                                     market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add market intelligence to pattern analysis."""
        
        try:
            # Calculate market intelligence metrics
            intelligence = {
                "market_regime": self._assess_market_regime(pattern_analysis, market_data),
                "volatility_regime": self._assess_volatility_regime(market_data),
                "liquidity_conditions": self._assess_liquidity_conditions(market_data),
                "pattern_quality": self._assess_pattern_quality(pattern_analysis),
                "trading_opportunities": self._identify_trading_opportunities(pattern_analysis)
            }
            
            # Add intelligence to analysis
            enhanced_analysis = {
                **pattern_analysis,
                "intelligence": intelligence,
                "analysis_confidence": self._calculate_analysis_confidence(pattern_analysis, intelligence)
            }
            
            return enhanced_analysis
            
        except Exception as e:
            self.logger.warning(f"Error adding market intelligence: {e}")
            return pattern_analysis
    
    def _assess_market_regime(self, pattern_analysis: Dict[str, Any], 
                            market_data: Dict[str, Any]) -> str:
        """Assess current market regime."""
        patterns = pattern_analysis.get("patterns", {})
        
        trend_count = len(patterns.get("trend_patterns", []))
        reversal_count = len(patterns.get("reversal_patterns", []))
        breakout_count = len(patterns.get("breakout_patterns", []))
        
        volatility = market_data.get("volatility", 0.02)
        
        if trend_count > 0 and volatility < 0.03:
            return "trending"
        elif reversal_count > 0 or volatility > 0.06:
            return "volatile"
        elif breakout_count > 0:
            return "breakout"
        else:
            return "ranging"
    
    def _assess_volatility_regime(self, market_data: Dict[str, Any]) -> str:
        """Assess volatility regime."""
        volatility = market_data.get("volatility", 0.02)
        
        if volatility > 0.06:
            return "high"
        elif volatility > 0.03:
            return "medium"
        else:
            return "low"
    
    def _assess_liquidity_conditions(self, market_data: Dict[str, Any]) -> str:
        """Assess liquidity conditions."""
        spread = market_data.get("spread", 0.001)
        volume_ratio = market_data.get("volume_ratio", 1.0)
        
        if spread < 0.0005 and volume_ratio > 1.2:
            return "high"
        elif spread < 0.002 and volume_ratio > 0.8:
            return "normal"
        else:
            return "low"
    
    def _assess_pattern_quality(self, pattern_analysis: Dict[str, Any]) -> str:
        """Assess overall pattern quality."""
        patterns_found = pattern_analysis.get("patterns_found", 0)
        pattern_strength = pattern_analysis.get("pattern_strength", 0.0)
        
        if patterns_found >= 3 and pattern_strength > 0.7:
            return "excellent"
        elif patterns_found >= 2 and pattern_strength > 0.5:
            return "good"
        elif patterns_found >= 1 and pattern_strength > 0.3:
            return "fair"
        else:
            return "poor"
    
    def _identify_trading_opportunities(self, pattern_analysis: Dict[str, Any]) -> List[str]:
        """Identify trading opportunities from patterns."""
        opportunities = []
        patterns = pattern_analysis.get("patterns", {})
        
        if patterns.get("trend_patterns"):
            opportunities.append("trend_following")
        
        if patterns.get("breakout_patterns"):
            opportunities.append("breakout_trading")
        
        if patterns.get("reversal_patterns"):
            opportunities.append("reversal_trading")
        
        if patterns.get("support_resistance"):
            opportunities.append("range_trading")
        
        if patterns.get("correlation_patterns"):
            opportunities.append("arbitrage")
        
        return opportunities
    
    def _calculate_pattern_strength(self, patterns: Dict[str, List]) -> float:
        """Calculate overall pattern strength."""
        total_strength = 0.0
        total_patterns = 0
        
        for pattern_list in patterns.values():
            for pattern in pattern_list:
                total_strength += pattern.get("strength", 0.0)
                total_patterns += 1
        
        return total_strength / max(total_patterns, 1)
    
    def _calculate_analysis_confidence(self, pattern_analysis: Dict[str, Any], 
                                     intelligence: Dict[str, Any]) -> float:
        """Calculate overall analysis confidence."""
        patterns_found = pattern_analysis.get("patterns_found", 0)
        pattern_strength = pattern_analysis.get("pattern_strength", 0.0)
        pattern_quality = intelligence.get("pattern_quality", "poor")
        
        # Base confidence from patterns
        base_confidence = min(0.8, patterns_found * 0.2 + pattern_strength * 0.5)
        
        # Quality adjustment
        quality_multiplier = {
            "excellent": 1.2,
            "good": 1.0,
            "fair": 0.8,
            "poor": 0.6
        }.get(pattern_quality, 0.6)
        
        return min(1.0, base_confidence * quality_multiplier)
    
    # ============= CACHING AND LEARNING =============
    
    def _generate_cache_key(self, market_data: Dict[str, Any], strategy_type: str) -> str:
        """Generate cache key for pattern analysis."""
        price = market_data.get("price", 0)
        volatility = market_data.get("volatility", 0)
        return f"{strategy_type}_{int(price)}_{int(volatility*1000)}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get analysis from cache if valid."""
        if cache_key in self.pattern_cache:
            cached_data, timestamp = self.pattern_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                del self.pattern_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache analysis result."""
        self.pattern_cache[cache_key] = (result, time.time())
        
        # Limit cache size
        if len(self.pattern_cache) > 100:
            oldest_key = min(self.pattern_cache.keys(), 
                           key=lambda k: self.pattern_cache[k][1])
            del self.pattern_cache[oldest_key]
    
    # async def _learn_from_analysis(self, market_data: Dict[str, Any], 
    #                              analysis: Dict[str, Any], start_time: float):
    #     """Learn from pattern analysis for improvement (removed - handled by Strategy Engine)."""
    #     pass
    
    # ============= UTILITY METHODS =============
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get pattern analysis statistics."""
        return {
            **self.analysis_stats,
            "detection_rate": self.analysis_stats["patterns_detected"] / max(self.analysis_stats["patterns_analyzed"], 1),
            "cache_hit_rate": self.analysis_stats["pattern_cache_hits"] / max(self.analysis_stats["patterns_analyzed"], 1),
            "current_thresholds": self.pattern_thresholds,
            "cache_size": len(self.pattern_cache)
        }
    
    def adjust_thresholds(self, threshold_adjustments: Dict[str, float]):
        """Adjust pattern detection thresholds."""
        for threshold_type, adjustment in threshold_adjustments.items():
            if threshold_type in self.pattern_thresholds:
                self.pattern_thresholds[threshold_type] = adjustment
        
        self.logger.info(f"Adjusted pattern thresholds: {threshold_adjustments}")
    
    def clear_cache(self):
        """Clear pattern analysis cache."""
        self.pattern_cache.clear()
        self.logger.info("Pattern analysis cache cleared")
    
    def reset_stats(self):
        """Reset analysis statistics."""
        self.analysis_stats = {
            "patterns_analyzed": 0,
            "patterns_detected": 0,
            "accuracy_score": 0.0,
            "false_positives": 0,
            "pattern_cache_hits": 0
        }
