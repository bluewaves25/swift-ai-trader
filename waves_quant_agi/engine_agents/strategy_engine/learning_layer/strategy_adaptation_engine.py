#!/usr/bin/env python3
"""
Strategy Adaptation Engine
Handles dynamic strategy adaptation based on market conditions and performance.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from engine_agents.shared_utils import get_shared_logger, get_shared_redis
import numpy as np

class StrategyAdaptationEngine:
    """Engine for adapting strategies based on market conditions and performance."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "adaptation_engine")
        self.redis_conn = get_shared_redis()
        
        # Adaptation configuration
        self.adaptation_threshold = config.get("adaptation_threshold", 0.7)
        self.min_adaptation_interval = config.get("min_adaptation_interval", 300)  # 5 minutes
        self.max_adaptations_per_cycle = config.get("max_adaptations_per_cycle", 5)
        
        # Adaptation state
        self.adaptation_history: List[Dict[str, Any]] = []
        self.current_adaptations: Dict[str, Dict[str, Any]] = {}
        self.last_adaptation = 0
        
        # Strategy adaptation rules
        self.adaptation_rules = {
            "trending_market": {
                "trend_following": {"boost": 1.5, "priority": "high"},
                "mean_reversion": {"boost": 0.7, "priority": "low"},
                "arbitrage": {"boost": 1.0, "priority": "medium"}
            },
            "volatile_market": {
                "volatility_trading": {"boost": 1.8, "priority": "high"},
                "risk_management": {"boost": 1.6, "priority": "high"},
                "mean_reversion": {"boost": 1.2, "priority": "medium"}
            },
            "sideways_market": {
                "mean_reversion": {"boost": 1.4, "priority": "high"},
                "market_making": {"boost": 1.3, "priority": "high"},
                "arbitrage": {"boost": 1.1, "priority": "medium"}
            },
            "normal_market": {
                "trend_following": {"boost": 1.0, "priority": "medium"},
                "mean_reversion": {"boost": 1.0, "priority": "medium"},
                "arbitrage": {"boost": 1.0, "priority": "medium"}
            }
        }
        
        # Adaptation statistics
        self.stats = {
            "adaptations_triggered": 0,
            "strategies_adapted": 0,
            "adaptation_errors": 0,
            "start_time": time.time()
        }

    async def check_adaptation_needed(self, market_conditions: Dict[str, Any], 
                                    strategy_performance: Dict[str, Any]) -> bool:
        """Check if strategy adaptation is needed."""
        try:
            # Check minimum time interval
            current_time = time.time()
            if (current_time - self.last_adaptation) < self.min_adaptation_interval:
                return False
            
            # Check market condition changes
            if await self._detect_market_change(market_conditions):
                return True
            
            # Check performance degradation
            if await self._detect_performance_degradation(strategy_performance):
                return True
            
            # Check strategy coverage gaps
            if await self._detect_coverage_gaps(market_conditions, strategy_performance):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking adaptation need: {e}")
            return False

    async def adapt_strategies(self, market_conditions: Dict[str, Any], 
                             strategy_performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Adapt strategies based on current conditions."""
        try:
            self.logger.info("Starting strategy adaptation process...")
            
            # Determine market regime
            market_regime = self._determine_market_regime(market_conditions)
            
            # Get adaptation recommendations
            adaptation_recommendations = await self._generate_adaptation_recommendations(
                market_regime, market_conditions, strategy_performance
            )
            
            # Apply adaptations
            applied_adaptations = []
            for recommendation in adaptation_recommendations[:self.max_adaptations_per_cycle]:
                if await self._apply_strategy_adaptation(recommendation):
                    applied_adaptations.append(recommendation)
                    self.stats["strategies_adapted"] += 1
            
            # Record adaptation
            if applied_adaptations:
                await self._record_adaptation(market_regime, applied_adaptations)
                self.last_adaptation = time.time()
                self.stats["adaptations_triggered"] += 1
            
            self.logger.info(f"Applied {len(applied_adaptations)} strategy adaptations")
            return applied_adaptations
            
        except Exception as e:
            self.logger.error(f"Error adapting strategies: {e}")
            self.stats["adaptation_errors"] += 1
            return []

    async def _detect_market_change(self, market_conditions: Dict[str, Any]) -> bool:
        """Detect significant market condition changes."""
        try:
            # Get previous market conditions
            previous_conditions = await self._get_previous_market_conditions()
            
            if not previous_conditions:
                return False
            
            # Calculate change score
            change_score = self._calculate_market_change_score(
                previous_conditions, market_conditions
            )
            
            return change_score > self.adaptation_threshold
            
        except Exception as e:
            self.logger.error(f"Error detecting market change: {e}")
            return False

    async def _detect_performance_degradation(self, strategy_performance: Dict[str, Any]) -> bool:
        """Detect performance degradation across strategies."""
        try:
            if not strategy_performance:
                return False
            
            # Calculate overall performance
            overall_performance = self._calculate_overall_performance(strategy_performance)
            
            # Check if performance is below threshold
            return overall_performance < self.adaptation_threshold
            
        except Exception as e:
            self.logger.error(f"Error detecting performance degradation: {e}")
            return False

    async def _detect_coverage_gaps(self, market_conditions: Dict[str, Any], 
                                  strategy_performance: Dict[str, Any]) -> bool:
        """Detect gaps in strategy coverage."""
        try:
            # Get current strategy coverage
            current_coverage = await self._get_current_strategy_coverage()
            
            # Get required coverage based on market conditions
            required_coverage = self._get_required_coverage(market_conditions)
            
            # Calculate coverage gap
            coverage_gap = self._calculate_coverage_gap(current_coverage, required_coverage)
            
            return coverage_gap > 0.3  # 30% gap threshold
            
        except Exception as e:
            self.logger.error(f"Error detecting coverage gaps: {e}")
            return False

    def _determine_market_regime(self, market_conditions: Dict[str, Any]) -> str:
        """Determine current market regime."""
        try:
            volatility = market_conditions.get("volatility", 0.0)
            trend_strength = market_conditions.get("trend_strength", 0.0)
            volume_profile = market_conditions.get("volume_profile", {})
            
            # Regime determination logic
            if volatility > 0.05 and trend_strength > 0.1:
                return "trending_market"
            elif volatility > 0.05 and trend_strength < 0.05:
                return "volatile_market"
            elif volatility < 0.02 and trend_strength < 0.05:
                return "sideways_market"
            else:
                return "normal_market"
                
        except Exception as e:
            self.logger.error(f"Error determining market regime: {e}")
            return "normal_market"

    async def _generate_adaptation_recommendations(self, market_regime: str, 
                                                market_conditions: Dict[str, Any], 
                                                strategy_performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate adaptation recommendations."""
        try:
            recommendations = []
            
            # Get regime-specific rules
            regime_rules = self.adaptation_rules.get(market_regime, {})
            
            # Generate recommendations for each strategy type
            for strategy_type, rule in regime_rules.items():
                recommendation = await self._create_adaptation_recommendation(
                    strategy_type, rule, market_conditions, strategy_performance
                )
                
                if recommendation:
                    recommendations.append(recommendation)
            
            # Sort by priority
            recommendations.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating adaptation recommendations: {e}")
            return []

    async def _create_adaptation_recommendation(self, strategy_type: str, rule: Dict[str, Any], 
                                              market_conditions: Dict[str, Any], 
                                              strategy_performance: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create adaptation recommendation for a strategy type."""
        try:
            # Get current strategy performance
            current_performance = strategy_performance.get(strategy_type, {})
            
            # Calculate adaptation score
            adaptation_score = self._calculate_adaptation_score(
                strategy_type, rule, market_conditions, current_performance
            )
            
            if adaptation_score > 0.5:  # Only recommend if score is good
                recommendation = {
                    "strategy_type": strategy_type,
                    "adaptation_type": "parameter_adjustment",
                    "boost_factor": rule.get("boost", 1.0),
                    "priority": rule.get("priority", "medium"),
                    "priority_score": adaptation_score,
                    "current_performance": current_performance,
                    "market_conditions": market_conditions,
                    "timestamp": int(time.time())
                }
                
                return recommendation
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating adaptation recommendation: {e}")
            return None

    def _calculate_adaptation_score(self, strategy_type: str, rule: Dict[str, Any], 
                                  market_conditions: Dict[str, Any], 
                                  current_performance: Dict[str, Any]) -> float:
        """Calculate adaptation score for a strategy."""
        try:
            score = 0.0
            
            # Base score from rule
            base_score = 0.5
            
            # Performance-based adjustment
            if current_performance:
                success_rate = current_performance.get("success_rate", 0.5)
                avg_pnl = current_performance.get("avg_pnl", 0.0)
                
                # Adjust based on performance
                if success_rate < 0.4:
                    score += 0.3  # Boost underperforming strategies
                elif success_rate > 0.8:
                    score += 0.1  # Slight boost for good performers
                else:
                    score += 0.2
                
                # PnL adjustment
                if avg_pnl < 0:
                    score += 0.2  # Boost losing strategies
                elif avg_pnl > 0.01:
                    score += 0.1  # Slight boost for profitable strategies
            
            # Market condition adjustment
            volatility = market_conditions.get("volatility", 0.0)
            trend_strength = market_conditions.get("trend_strength", 0.0)
            
            # Strategy-specific adjustments
            if strategy_type == "trend_following" and trend_strength > 0.1:
                score += 0.2
            elif strategy_type == "volatility_trading" and volatility > 0.05:
                score += 0.2
            elif strategy_type == "mean_reversion" and volatility < 0.03:
                score += 0.2
            
            return min(1.0, base_score + score)
            
        except Exception as e:
            self.logger.error(f"Error calculating adaptation score: {e}")
            return 0.5

    async def _apply_strategy_adaptation(self, recommendation: Dict[str, Any]) -> bool:
        """Apply a strategy adaptation."""
        try:
            strategy_type = recommendation["strategy_type"]
            adaptation_type = recommendation["adaptation_type"]
            boost_factor = recommendation["boost_factor"]
            
            # Get current strategy parameters
            current_params = await self._get_strategy_parameters(strategy_type)
            
            # Generate adapted parameters
            adapted_params = await self._generate_adapted_parameters(
                strategy_type, current_params, recommendation
            )
            
            if adapted_params:
                # Apply adaptation
                success = await self._apply_adapted_parameters(strategy_type, adapted_params)
                
                if success:
                    # Store adaptation record
                    adaptation_record = {
                        "strategy_type": strategy_type,
                        "adaptation_type": adaptation_type,
                        "previous_params": current_params,
                        "adapted_params": adapted_params,
                        "boost_factor": boost_factor,
                        "timestamp": int(time.time())
                    }
                    
                    self.current_adaptations[strategy_type] = adaptation_record
                    self.adaptation_history.append(adaptation_record)
                    
                    self.logger.info(f"Applied adaptation for {strategy_type}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error applying strategy adaptation: {e}")
            return False

    async def _generate_adapted_parameters(self, strategy_type: str, 
                                        current_params: Dict[str, Any], 
                                        recommendation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate adapted parameters for strategy."""
        try:
            adapted_params = current_params.copy()
            boost_factor = recommendation.get("boost_factor", 1.0)
            
            # Apply boost factor to relevant parameters
            if "confidence_threshold" in adapted_params:
                adapted_params["confidence_threshold"] = min(0.9, adapted_params["confidence_threshold"] * boost_factor)
            
            if "risk_tolerance" in adapted_params:
                if boost_factor > 1.0:
                    adapted_params["risk_tolerance"] = min(0.9, adapted_params["risk_tolerance"] * boost_factor)
                else:
                    adapted_params["risk_tolerance"] = max(0.1, adapted_params["risk_tolerance"] * boost_factor)
            
            if "position_size" in adapted_params:
                adapted_params["position_size"] = min(0.2, adapted_params["position_size"] * boost_factor)
            
            # Strategy-specific adaptations
            if strategy_type == "trend_following":
                adapted_params["trend_sensitivity"] = adapted_params.get("trend_sensitivity", 0.5) * boost_factor
            elif strategy_type == "volatility_trading":
                adapted_params["volatility_threshold"] = adapted_params.get("volatility_threshold", 0.05) / boost_factor
            elif strategy_type == "mean_reversion":
                adapted_params["reversion_threshold"] = adapted_params.get("reversion_threshold", 0.7) * boost_factor
            
            return adapted_params
            
        except Exception as e:
            self.logger.error(f"Error generating adapted parameters: {e}")
            return None

    async def _apply_adapted_parameters(self, strategy_type: str, adapted_params: Dict[str, Any]) -> bool:
        """Apply adapted parameters to strategy."""
        try:
            # Store adapted parameters in Redis with proper JSON serialization
            try:
                import json
                params_key = f"strategy_engine:adaptation:adapted_params:{strategy_type}"
                self.redis_conn.set(params_key, json.dumps(adapted_params), ex=604800)
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing adapted parameters: {e}")
                return False
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing adapted parameters: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Unexpected error storing adapted parameters: {e}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying adapted parameters: {e}")
            return False

    async def _record_adaptation(self, market_regime: str, adaptations: List[Dict[str, Any]]):
        """Record adaptation event."""
        try:
            adaptation_record = {
                "market_regime": market_regime,
                "adaptations": adaptations,
                "timestamp": int(time.time()),
                "adaptation_count": len(adaptations)
            }
            
            # Store adaptation record in Redis with proper JSON serialization
            try:
                import json
                record_key = f"strategy_engine:adaptation:record:{int(time.time())}"
                self.redis_conn.set(record_key, json.dumps(adaptation_record), ex=604800)
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing adaptation record: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing adaptation record: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing adaptation record: {e}")

    # Helper methods
    async def _get_previous_market_conditions(self) -> Optional[Dict[str, Any]]:
        """Get previous market conditions from Redis."""
        try:
            conditions_key = "strategy_engine:adaptation:previous_market_conditions"
            conditions = self.redis_conn.get(conditions_key)
            
            if conditions:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(conditions, bytes):
                        conditions = conditions.decode('utf-8')
                    elif not isinstance(conditions, str):
                        return None
                        
                    parsed_conditions = json.loads(conditions)
                    if isinstance(parsed_conditions, dict):
                        return parsed_conditions
                    else:
                        return None
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for previous market conditions: {e}")
                    return None
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing previous market conditions: {e}")
                    return None
            
            return None
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting previous market conditions: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting previous market conditions: {e}")
            return None

    async def _get_current_strategy_coverage(self) -> List[str]:
        """Get current strategy coverage from Redis."""
        try:
            coverage_key = "strategy_engine:adaptation:current_coverage"
            coverage = self.redis_conn.get(coverage_key)
            
            if coverage:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(coverage, bytes):
                        coverage = coverage.decode('utf-8')
                    elif not isinstance(coverage, str):
                        return []
                        
                    parsed_coverage = json.loads(coverage)
                    if isinstance(parsed_coverage, list):
                        return parsed_coverage
                    else:
                        return []
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for current strategy coverage: {e}")
                    return []
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing current strategy coverage: {e}")
                    return []
            
            return []
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting current strategy coverage: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting current strategy coverage: {e}")
            return []

    def _get_required_coverage(self, market_conditions: Dict[str, Any]) -> List[str]:
        """Get required strategy coverage based on market conditions."""
        try:
            required = []
            
            # Basic coverage requirements
            required.extend(["trend_following", "mean_reversion", "risk_management"])
            
            # Add specific strategies based on conditions
            if market_conditions.get("volatility", 0.0) > 0.05:
                required.extend(["volatility_trading", "risk_management"])
            
            if market_conditions.get("trend_strength", 0.0) > 0.1:
                required.extend(["trend_following", "momentum_trading"])
            
            return list(set(required))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error getting required coverage: {e}")
            return ["trend_following", "mean_reversion", "risk_management"]

    async def _get_strategy_parameters(self, strategy_type: str) -> Dict[str, Any]:
        """Get strategy parameters from Redis."""
        try:
            if not isinstance(strategy_type, str):
                self.logger.error(f"Invalid strategy_type: {type(strategy_type)}, expected string")
                return {}
                
            params_key = f"strategy_engine:adaptation:parameters:{strategy_type}"
            params = self.redis_conn.get(params_key)
            
            if params:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(params, bytes):
                        params = params.decode('utf-8')
                    elif not isinstance(params, str):
                        return {}
                        
                    parsed_params = json.loads(params)
                    if isinstance(parsed_params, dict):
                        return parsed_params
                    else:
                        return {}
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for strategy parameters: {e}")
                    return {}
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing strategy parameters: {e}")
                    return {}
            
            return {}
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting strategy parameters: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error getting strategy parameters: {e}")
            return {}

    def _calculate_market_change_score(self, previous: Dict[str, Any], current: Dict[str, Any]) -> float:
        """Calculate market change score."""
        try:
            if not previous or not current:
                return 0.0
            
            change_score = 0.0
            
            # Compare key metrics
            for key in ["volatility", "trend_strength"]:
                prev_val = previous.get(key, 0.0)
                curr_val = current.get(key, 0.0)
                
                if prev_val != 0:
                    change = abs(curr_val - prev_val) / abs(prev_val)
                    change_score += change
            
            return change_score / 2  # Average change score
            
        except Exception as e:
            self.logger.error(f"Error calculating market change score: {e}")
            return 0.0

    def _calculate_overall_performance(self, strategy_performance: Dict[str, Any]) -> float:
        """Calculate overall strategy performance."""
        try:
            if not strategy_performance:
                return 0.5
            
            scores = []
            for strategy, perf in strategy_performance.items():
                if isinstance(perf, dict):
                    success_rate = perf.get("success_rate", 0.5)
                    avg_pnl = perf.get("avg_pnl", 0.0)
                    
                    # Normalize PnL to 0-1 range
                    normalized_pnl = max(0, min(1, (avg_pnl + 0.1) / 0.2))
                    
                    # Combined score
                    combined_score = (success_rate + normalized_pnl) / 2
                    scores.append(combined_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception as e:
            self.logger.error(f"Error calculating overall performance: {e}")
            return 0.5

    def _calculate_coverage_gap(self, current: List[str], required: List[str]) -> float:
        """Calculate coverage gap between current and required strategies."""
        try:
            if not required:
                return 0.0
            
            missing_strategies = set(required) - set(current)
            gap_ratio = len(missing_strategies) / len(required)
            
            return gap_ratio
            
        except Exception as e:
            self.logger.error(f"Error calculating coverage gap: {e}")
            return 0.0

    async def get_adaptation_insights(self) -> Dict[str, Any]:
        """Get insights from adaptation data."""
        try:
            insights = {
                "total_adaptations": self.stats["adaptations_triggered"],
                "strategies_adapted": self.stats["strategies_adapted"],
                "current_adaptations": len(self.current_adaptations),
                "adaptation_history_size": len(self.adaptation_history),
                "last_adaptation": self.last_adaptation,
                "uptime": time.time() - self.stats["start_time"]
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error getting adaptation insights: {e}")
            return {"error": str(e)}

    def get_adaptation_stats(self) -> Dict[str, Any]:
        """Get adaptation statistics."""
        return {
            **self.stats,
            "current_adaptations": len(self.current_adaptations),
            "adaptation_history_size": len(self.adaptation_history)
        }

    async def reset_adaptations(self):
        """Reset adaptation state."""
        try:
            self.adaptation_history.clear()
            self.current_adaptations.clear()
            self.last_adaptation = 0
            
            # Reset stats
            self.stats = {
                "adaptations_triggered": 0,
                "strategies_adapted": 0,
                "adaptation_errors": 0,
                "start_time": time.time()
            }
            
            self.logger.info("Adaptation state reset")
            
        except Exception as e:
            self.logger.error(f"Error resetting adaptations: {e}")

    async def force_adaptation(self, strategy_type: str):
        """Force adaptation for a specific strategy type."""
        try:
            self.logger.info(f"Forcing adaptation for {strategy_type}")
            
            # Create forced adaptation recommendation
            recommendation = {
                "strategy_type": strategy_type,
                "adaptation_type": "forced",
                "boost_factor": 1.2,
                "priority": "high",
                "priority_score": 0.8,
                "timestamp": int(time.time())
            }
            
            # Apply adaptation
            if await self._apply_strategy_adaptation(recommendation):
                self.logger.info(f"Forced adaptation applied for {strategy_type}")
            else:
                self.logger.warning(f"Failed to apply forced adaptation for {strategy_type}")
                
        except Exception as e:
            self.logger.error(f"Error forcing adaptation: {e}")
