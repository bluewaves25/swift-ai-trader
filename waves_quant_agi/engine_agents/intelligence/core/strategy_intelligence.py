#!/usr/bin/env python3
"""
Strategy Intelligence - CORE REFACTORED MODULE
Handles strategy-specific intelligence and analysis
Separated from main agent for better manageability

REFACTORED FOR SIMPLICITY:
- Strategy-specific analysis for 6 strategy types
- Intelligence routing and optimization
- Clean separation of strategy logic
"""

import time
from typing import Dict, Any, List, Optional
from ...shared_utils import get_shared_logger

class StrategyIntelligence:
    """
    Strategy-specific intelligence engine - provides tailored analysis for different strategies.
    Separated from main agent for better code organization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("intelligence", "strategy_intelligence")
        # self.learner = get_agent_learner("intelligence", LearningType.STRATEGY_ADAPTATION, 8)
        
        # Strategy intelligence state
        self.intelligence_stats = {
            "arbitrage_analyses": 0,
            "statistical_analyses": 0,
            "trend_analyses": 0,
            "market_making_analyses": 0,
            "news_analyses": 0,
            "htf_analyses": 0,
            "total_recommendations": 0,
            "accuracy_by_strategy": {}
        }
        
        # Strategy-specific configurations
        self.strategy_configs = {
            "arbitrage": {
                "focus": ["spread_analysis", "latency_optimization", "cross_market"],
                "time_sensitivity": "ultra_high",  # 1ms decisions
                "risk_tolerance": "low"
            },
            "statistical": {
                "focus": ["correlation_analysis", "mean_reversion", "pairs_trading"],
                "time_sensitivity": "medium",  # 1s-60s decisions
                "risk_tolerance": "medium"
            },
            "trend_following": {
                "focus": ["momentum_analysis", "breakout_detection", "trend_strength"],
                "time_sensitivity": "medium",  # 1s-60s decisions
                "risk_tolerance": "medium"
            },
            "market_making": {
                "focus": ["spread_optimization", "inventory_management", "quote_adjustment"],
                "time_sensitivity": "high",  # 100ms decisions
                "risk_tolerance": "low"
            },
            "news_driven": {
                "focus": ["sentiment_analysis", "event_impact", "reaction_timing"],
                "time_sensitivity": "high",  # 100ms-1s decisions
                "risk_tolerance": "high"
            },
            "htf": {
                "focus": ["regime_analysis", "macro_trends", "long_term_patterns"],
                "time_sensitivity": "low",  # 60s+ decisions
                "risk_tolerance": "medium"
            }
        }
        
        # Intelligence cache for each strategy
        self.strategy_cache = {strategy: {} for strategy in self.strategy_configs.keys()}
        
    async def provide_strategy_intelligence(self, strategy_type: str, market_data: Dict[str, Any], 
                                          pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide tailored intelligence for specific strategy type.
        This is the main method for strategy-specific analysis.
        """
        start_time = time.time()
        
        try:
            if strategy_type not in self.strategy_configs:
                self.logger.warning(f"Unknown strategy type: {strategy_type}")
                return {"error": f"Unknown strategy type: {strategy_type}"}
            
            # Get strategy-specific analysis
            intelligence = await self._analyze_for_strategy(strategy_type, market_data, pattern_analysis)
            
            # Add strategy-specific recommendations
            recommendations = await self._generate_strategy_recommendations(
                strategy_type, intelligence, market_data
            )
            
            # Learn from this intelligence provision
            # await self._learn_from_intelligence(strategy_type, market_data, intelligence, start_time)
            
            # Update statistics
            self._update_strategy_stats(strategy_type)
            
            return {
                "strategy_type": strategy_type,
                "intelligence": intelligence,
                "recommendations": recommendations,
                "confidence": intelligence.get("confidence", 0.5),
                "timestamp": time.time(),
                "analysis_time_ms": (time.time() - start_time) * 1000
            }
            
        except Exception as e:
            self.logger.error(f"Error providing {strategy_type} intelligence: {e}")
            return {"error": str(e), "strategy_type": strategy_type}
    
    async def _analyze_for_strategy(self, strategy_type: str, market_data: Dict[str, Any], 
                                  pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform strategy-specific analysis."""
        
        config = self.strategy_configs[strategy_type]
        intelligence = {"confidence": 0.5}
        
        try:
            # Route to strategy-specific analyzer
            if strategy_type == "arbitrage":
                intelligence = await self._analyze_arbitrage(market_data, pattern_analysis, config)
            elif strategy_type == "statistical":
                intelligence = await self._analyze_statistical(market_data, pattern_analysis, config)
            elif strategy_type == "trend_following":
                intelligence = await self._analyze_trend_following(market_data, pattern_analysis, config)
            elif strategy_type == "market_making":
                intelligence = await self._analyze_market_making(market_data, pattern_analysis, config)
            elif strategy_type == "news_driven":
                intelligence = await self._analyze_news_driven(market_data, pattern_analysis, config)
            elif strategy_type == "htf":
                intelligence = await self._analyze_htf(market_data, pattern_analysis, config)
            
            return intelligence
            
        except Exception as e:
            self.logger.warning(f"Error in {strategy_type} analysis: {e}")
            return {"confidence": 0.0, "error": str(e)}
    
    async def _analyze_arbitrage(self, market_data: Dict[str, Any], 
                               pattern_analysis: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze for arbitrage strategies."""
        
        # Focus on spread analysis and cross-market opportunities
        current_spread = market_data.get("spread", 0.001)
        normal_spread = 0.001  # Baseline
        spread_opportunity = max(0, current_spread - normal_spread)
        
        # Look for correlation patterns (arbitrage opportunities)
        correlation_patterns = pattern_analysis.get("patterns", {}).get("correlation_patterns", [])
        cross_market_opportunities = len(correlation_patterns)
        
        # Calculate arbitrage confidence
        spread_score = min(1.0, spread_opportunity * 1000)  # Scale spread
        correlation_score = min(1.0, cross_market_opportunities / 3.0)  # Normalize
        
        confidence = (spread_score + correlation_score) / 2
        
        intelligence = {
            "spread_opportunity": spread_opportunity,
            "cross_market_score": correlation_score,
            "latency_requirements": "ultra_low",  # 1ms
            "opportunity_count": cross_market_opportunities,
            "confidence": confidence,
            "focus_areas": config["focus"],
            "risk_level": "low"
        }
        
        return intelligence
    
    async def _analyze_statistical(self, market_data: Dict[str, Any], 
                                 pattern_analysis: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze for statistical arbitrage strategies."""
        
        # Focus on mean reversion and correlation analysis
        price_deviation = market_data.get("price_deviation", 0.0)
        correlation_strength = 0.0
        
        # Get correlation patterns
        correlation_patterns = pattern_analysis.get("patterns", {}).get("correlation_patterns", [])
        if correlation_patterns:
            correlation_strength = sum(p.get("strength", 0) for p in correlation_patterns) / len(correlation_patterns)
        
        # Look for reversal patterns (mean reversion opportunities)
        reversal_patterns = pattern_analysis.get("patterns", {}).get("reversal_patterns", [])
        mean_reversion_score = min(1.0, len(reversal_patterns) / 2.0)
        
        # Calculate statistical confidence
        deviation_score = min(1.0, abs(price_deviation) * 10)  # Scale deviation
        pairs_score = min(1.0, correlation_strength)
        
        confidence = (deviation_score + pairs_score + mean_reversion_score) / 3
        
        intelligence = {
            "mean_reversion_score": mean_reversion_score,
            "correlation_strength": correlation_strength,
            "price_deviation": price_deviation,
            "pairs_opportunities": len(correlation_patterns),
            "confidence": confidence,
            "focus_areas": config["focus"],
            "optimal_timeframe": "5min-1h"
        }
        
        return intelligence
    
    async def _analyze_trend_following(self, market_data: Dict[str, Any], 
                                     pattern_analysis: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze for trend following strategies."""
        
        # Focus on momentum and trend strength
        trend_patterns = pattern_analysis.get("patterns", {}).get("trend_patterns", [])
        breakout_patterns = pattern_analysis.get("patterns", {}).get("breakout_patterns", [])
        
        # Calculate trend strength
        trend_strength = 0.0
        if trend_patterns:
            trend_strength = sum(p.get("strength", 0) for p in trend_patterns) / len(trend_patterns)
        
        # Calculate momentum score
        momentum_score = min(1.0, len(breakout_patterns) / 2.0)
        
        # Check market regime
        market_regime = pattern_analysis.get("intelligence", {}).get("market_regime", "ranging")
        regime_favorability = 1.0 if market_regime in ["trending", "breakout"] else 0.3
        
        confidence = (trend_strength + momentum_score + regime_favorability) / 3
        
        intelligence = {
            "trend_strength": trend_strength,
            "momentum_score": momentum_score,
            "market_regime": market_regime,
            "regime_favorability": regime_favorability,
            "trend_direction": trend_patterns[0].get("type", "unknown") if trend_patterns else "unknown",
            "confidence": confidence,
            "focus_areas": config["focus"],
            "optimal_timeframe": "15min-4h"
        }
        
        return intelligence
    
    async def _analyze_market_making(self, market_data: Dict[str, Any], 
                                   pattern_analysis: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze for market making strategies."""
        
        # Focus on spread optimization and inventory management
        current_spread = market_data.get("spread", 0.001)
        volatility = market_data.get("volatility", 0.02)
        volume_ratio = market_data.get("volume_ratio", 1.0)
        
        # Market making works best in stable conditions
        market_regime = pattern_analysis.get("intelligence", {}).get("market_regime", "ranging")
        volatility_regime = pattern_analysis.get("intelligence", {}).get("volatility_regime", "medium")
        
        # Calculate market making viability
        stability_score = 1.0 if market_regime == "ranging" else 0.5
        volatility_score = {"low": 1.0, "medium": 0.7, "high": 0.3}.get(volatility_regime, 0.5)
        liquidity_score = min(1.0, volume_ratio)
        
        confidence = (stability_score + volatility_score + liquidity_score) / 3
        
        intelligence = {
            "spread_efficiency": min(1.0, current_spread * 1000),  # Scale spread
            "volatility_suitability": volatility_score,
            "liquidity_conditions": liquidity_score,
            "market_stability": stability_score,
            "optimal_spread": current_spread * 0.8,  # Tighter spread
            "confidence": confidence,
            "focus_areas": config["focus"],
            "quote_frequency": "high"  # Frequent quote updates
        }
        
        return intelligence
    
    async def _analyze_news_driven(self, market_data: Dict[str, Any], 
                                 pattern_analysis: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze for news-driven strategies."""
        
        # Focus on sentiment and event impact
        sentiment_score = market_data.get("sentiment_score", 0.0)
        news_impact = market_data.get("news_impact", 0.0)
        volatility = market_data.get("volatility", 0.02)
        
        # News strategies work well with high volatility and strong sentiment
        volatility_favorability = min(1.0, volatility * 20)  # Scale volatility
        sentiment_strength = abs(sentiment_score)  # Strong positive or negative
        
        # Look for breakout patterns (news reaction)
        breakout_patterns = pattern_analysis.get("patterns", {}).get("breakout_patterns", [])
        reaction_score = min(1.0, len(breakout_patterns) / 2.0)
        
        confidence = (volatility_favorability + sentiment_strength + reaction_score) / 3
        
        intelligence = {
            "sentiment_strength": sentiment_strength,
            "news_impact_score": news_impact,
            "volatility_opportunity": volatility_favorability,
            "reaction_patterns": len(breakout_patterns),
            "timing_urgency": "high" if volatility > 0.05 else "medium",
            "confidence": confidence,
            "focus_areas": config["focus"],
            "reaction_window": "5min-30min"
        }
        
        return intelligence
    
    async def _analyze_htf(self, market_data: Dict[str, Any], 
                         pattern_analysis: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze for high-timeframe (HTF) strategies."""
        
        # Focus on regime analysis and macro trends
        market_regime = pattern_analysis.get("intelligence", {}).get("market_regime", "ranging")
        pattern_quality = pattern_analysis.get("intelligence", {}).get("pattern_quality", "poor")
        
        # HTF strategies work best with clear, strong patterns
        regime_clarity = {"trending": 1.0, "breakout": 0.8, "volatile": 0.6, "ranging": 0.4}.get(market_regime, 0.5)
        pattern_reliability = {"excellent": 1.0, "good": 0.8, "fair": 0.6, "poor": 0.3}.get(pattern_quality, 0.3)
        
        # Long-term trend strength
        trend_patterns = pattern_analysis.get("patterns", {}).get("trend_patterns", [])
        long_term_trend = sum(p.get("strength", 0) for p in trend_patterns) / max(len(trend_patterns), 1)
        
        confidence = (regime_clarity + pattern_reliability + long_term_trend) / 3
        
        intelligence = {
            "regime_clarity": regime_clarity,
            "pattern_reliability": pattern_reliability,
            "long_term_trend_strength": long_term_trend,
            "macro_environment": market_regime,
            "position_horizon": "days-weeks",
            "confidence": confidence,
            "focus_areas": config["focus"],
            "optimal_timeframe": "4h-1d"
        }
        
        return intelligence
    
    async def _generate_strategy_recommendations(self, strategy_type: str, 
                                               intelligence: Dict[str, Any], 
                                               market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate strategy-specific recommendations."""
        recommendations = []
        
        try:
            confidence = intelligence.get("confidence", 0.5)
            
            # Only generate recommendations if confidence is reasonable
            if confidence < 0.3:
                return recommendations
            
            # Strategy-specific recommendation logic
            if strategy_type == "arbitrage":
                spread_opportunity = intelligence.get("spread_opportunity", 0)
                if spread_opportunity > 0.0001:  # 0.01% spread opportunity
                    recommendations.append({
                        "action": "execute_arbitrage",
                        "priority": "high",
                        "reasoning": f"Spread opportunity detected: {spread_opportunity*10000:.1f} bps",
                        "urgency": "immediate",
                        "confidence": confidence
                    })
            
            elif strategy_type == "trend_following":
                trend_strength = intelligence.get("trend_strength", 0)
                trend_direction = intelligence.get("trend_direction", "unknown")
                if trend_strength > 0.5 and trend_direction != "unknown":
                    action = "buy" if "up" in trend_direction else "sell"
                    recommendations.append({
                        "action": action,
                        "priority": "medium",
                        "reasoning": f"Strong {trend_direction} trend detected",
                        "urgency": "within_hour",
                        "confidence": confidence
                    })
            
            elif strategy_type == "market_making":
                market_stability = intelligence.get("market_stability", 0)
                if market_stability > 0.7:
                    recommendations.append({
                        "action": "provide_liquidity",
                        "priority": "medium",
                        "reasoning": "Stable market conditions favor market making",
                        "urgency": "continuous",
                        "confidence": confidence
                    })
            
            # Add more strategy-specific recommendations...
            
            # Generic high-confidence recommendation
            if confidence > 0.8:
                recommendations.append({
                    "action": "increase_allocation",
                    "priority": "high",
                    "reasoning": f"High confidence {strategy_type} opportunity",
                    "urgency": "soon",
                    "confidence": confidence
                })
            
            self.intelligence_stats["total_recommendations"] += len(recommendations)
            
        except Exception as e:
            self.logger.warning(f"Error generating {strategy_type} recommendations: {e}")
        
        return recommendations
    
    # async def _learn_from_intelligence(self, strategy_type: str, market_data: Dict[str, Any], 
    #                                  intelligence: Dict[str, Any], start_time: float):
    #     """Learn from strategy intelligence provision (removed - handled by Strategy Engine)."""
    #     pass
    
    def _update_strategy_stats(self, strategy_type: str):
        """Update strategy-specific statistics."""
        stat_key = f"{strategy_type}_analyses"
        if stat_key in self.intelligence_stats:
            self.intelligence_stats[stat_key] += 1
    
    def get_intelligence_stats(self) -> Dict[str, Any]:
        """Get strategy intelligence statistics."""
        total_analyses = sum(
            count for key, count in self.intelligence_stats.items() 
            if key.endswith("_analyses")
        )
        
        return {
            **self.intelligence_stats,
            "total_analyses": total_analyses,
            "average_recommendations_per_analysis": (
                self.intelligence_stats["total_recommendations"] / max(total_analyses, 1)
            ),
            "strategy_distribution": {
                strategy: self.intelligence_stats.get(f"{strategy}_analyses", 0) 
                for strategy in self.strategy_configs.keys()
            }
        }
    
    def get_strategy_config(self, strategy_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific strategy type."""
        return self.strategy_configs.get(strategy_type)
    
    def reset_stats(self):
        """Reset intelligence statistics."""
        self.intelligence_stats = {
            "arbitrage_analyses": 0,
            "statistical_analyses": 0,
            "trend_analyses": 0,
            "market_making_analyses": 0,
            "news_analyses": 0,
            "htf_analyses": 0,
            "total_recommendations": 0,
            "accuracy_by_strategy": {}
        }
