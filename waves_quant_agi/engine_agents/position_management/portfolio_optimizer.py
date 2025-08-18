#!/usr/bin/env python3
"""
Portfolio Optimizer - Advanced Portfolio Optimization Strategies
"""

import asyncio
import time
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class OptimizationResult:
    """Result of portfolio optimization."""
    strategy_type: str
    target_allocation: float
    current_allocation: float
    recommended_action: str
    priority: str
    expected_return: float
    risk_score: float
    sharpe_ratio: float

@dataclass
class RiskMetrics:
    """Risk metrics for portfolio optimization."""
    volatility: float
    var_95: float  # Value at Risk at 95% confidence
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float

class PortfolioOptimizer:
    """Advanced portfolio optimization system implementing multiple strategies."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        self.optimization_history = []
        self.performance_metrics = {
            "optimizations_performed": 0,
            "rebalancing_actions": 0,
            "risk_adjustments": 0,
            "last_optimization": None
        }
        
        # Optimization parameters
        self.optimization_params = {
            "risk_free_rate": 0.02,  # 2% risk-free rate
            "target_volatility": 0.15,  # 15% target volatility
            "max_position_concentration": 0.25,  # 25% max position concentration
            "rebalancing_threshold": 0.05,  # 5% rebalancing threshold
            "correlation_threshold": 0.7,  # 70% correlation threshold
            "momentum_lookback": 30,  # 30-day momentum lookback
            "volatility_lookback": 60  # 60-day volatility lookback
        }
        
    async def optimize_portfolio(self, portfolio_data: Dict[str, Any], 
                               market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive portfolio optimization."""
        try:
            start_time = time.time()
            
            # Extract portfolio information
            positions = portfolio_data.get("positions", {})
            current_allocations = portfolio_data.get("strategy_allocations", {})
            risk_metrics = portfolio_data.get("risk_metrics", {})
            
            # Perform different optimization strategies
            risk_parity_result = await self._risk_parity_optimization(
                positions, current_allocations, risk_metrics
            )
            
            mean_variance_result = await self._mean_variance_optimization(
                positions, current_allocations, market_data
            )
            
            sharpe_optimization_result = await self._sharpe_ratio_optimization(
                positions, current_allocations, risk_metrics
            )
            
            # Combine and rank optimization results
            combined_results = await self._combine_optimization_results(
                risk_parity_result, mean_variance_result, sharpe_optimization_result
            )
            
            # Generate actionable recommendations
            recommendations = await self._generate_recommendations(combined_results)
            
            # Calculate optimization metrics
            optimization_time = time.time() - start_time
            self.performance_metrics["optimizations_performed"] += 1
            self.performance_metrics["last_optimization"] = time.time()
            
            # Store optimization history
            optimization_record = {
                "timestamp": time.time(),
                "optimization_time": optimization_time,
                "results": combined_results,
                "recommendations": recommendations,
                "portfolio_state": {
                    "total_positions": len(positions),
                    "current_allocations": current_allocations,
                    "risk_metrics": risk_metrics
                }
            }
            self.optimization_history.append(optimization_record)
            
            if self.logger:
                self.logger.info(f"🎯 Portfolio optimization completed in {optimization_time:.3f}s: "
                               f"{len(recommendations)} recommendations generated")
            
            return {
                "optimization_results": combined_results,
                "recommendations": recommendations,
                "optimization_metrics": {
                    "time_taken": optimization_time,
                    "strategies_analyzed": 3,
                    "recommendations_count": len(recommendations)
                },
                "timestamp": time.time()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error in portfolio optimization: {e}")
            return {"error": str(e), "timestamp": time.time()}
    
    async def _risk_parity_optimization(self, positions: Dict[str, Any], 
                                       current_allocations: Dict[str, float],
                                       risk_metrics: Dict[str, Any]) -> List[OptimizationResult]:
        """Perform risk parity optimization."""
        try:
            results = []
            
            # Calculate risk contribution for each strategy
            total_risk = sum(risk_metrics.get("strategy_risks", {}).values())
            
            if total_risk > 0:
                target_risk_per_strategy = total_risk / len(current_allocations)
                
                for strategy_type, current_allocation in current_allocations.items():
                    current_risk = risk_metrics.get("strategy_risks", {}).get(strategy_type, 0)
                    
                    if current_risk > 0:
                        # Calculate target allocation for equal risk contribution
                        target_allocation = target_risk_per_strategy / current_risk
                        
                        # Ensure within bounds
                        target_allocation = max(0.05, min(0.35, target_allocation))
                        
                        deviation = abs(current_allocation - target_allocation)
                        priority = "high" if deviation > 0.1 else "medium"
                        
                        results.append(OptimizationResult(
                            strategy_type=strategy_type,
                            target_allocation=target_allocation,
                            current_allocation=current_allocation,
                            recommended_action="increase" if current_allocation < target_allocation else "decrease",
                            priority=priority,
                            expected_return=risk_metrics.get("strategy_returns", {}).get(strategy_type, 0),
                            risk_score=current_risk,
                            sharpe_ratio=risk_metrics.get("strategy_sharpe", {}).get(strategy_type, 0)
                        ))
            
            return results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error in risk parity optimization: {e}")
            return []
    
    async def _mean_variance_optimization(self, positions: Dict[str, Any],
                                         current_allocations: Dict[str, float],
                                         market_data: Dict[str, Any]) -> List[OptimizationResult]:
        """Perform mean-variance optimization."""
        try:
            results = []
            
            # Calculate expected returns and covariance matrix
            strategy_returns = {}
            strategy_volatilities = {}
            
            for strategy_type in current_allocations.keys():
                # Extract historical returns from market data
                historical_returns = market_data.get("strategy_historical_returns", {}).get(strategy_type, [])
                
                if historical_returns:
                    # Calculate expected return and volatility
                    returns_array = np.array(historical_returns)
                    expected_return = np.mean(returns_array)
                    volatility = np.std(returns_array)
                    
                    strategy_returns[strategy_type] = expected_return
                    strategy_volatilities[strategy_type] = volatility
            
            if strategy_returns and strategy_volatilities:
                # Simple mean-variance optimization
                for strategy_type, current_allocation in current_allocations.items():
                    if strategy_type in strategy_returns:
                        expected_return = strategy_returns[strategy_type]
                        volatility = strategy_volatilities[strategy_type]
                        
                        # Calculate Sharpe ratio
                        sharpe_ratio = (expected_return - self.optimization_params["risk_free_rate"]) / volatility if volatility > 0 else 0
                        
                        # Determine target allocation based on Sharpe ratio
                        if sharpe_ratio > 1.0:
                            target_allocation = min(0.35, current_allocation * 1.2)  # Increase allocation
                        elif sharpe_ratio < 0.5:
                            target_allocation = max(0.05, current_allocation * 0.8)  # Decrease allocation
                        else:
                            target_allocation = current_allocation  # Maintain allocation
                        
                        deviation = abs(current_allocation - target_allocation)
                        priority = "high" if deviation > 0.1 else "medium"
                        
                        results.append(OptimizationResult(
                            strategy_type=strategy_type,
                            target_allocation=target_allocation,
                            current_allocation=current_allocation,
                            recommended_action="increase" if target_allocation > current_allocation else "decrease",
                            priority=priority,
                            expected_return=expected_return,
                            risk_score=volatility,
                            sharpe_ratio=sharpe_ratio
                        ))
            
            return results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error in mean-variance optimization: {e}")
            return []
    
    async def _sharpe_ratio_optimization(self, positions: Dict[str, Any],
                                         current_allocations: Dict[str, float],
                                         risk_metrics: Dict[str, Any]) -> List[OptimizationResult]:
        """Perform Sharpe ratio optimization."""
        try:
            results = []
            
            # Get Sharpe ratios for each strategy
            strategy_sharpe = risk_metrics.get("strategy_sharpe", {})
            
            if strategy_sharpe:
                # Sort strategies by Sharpe ratio
                sorted_strategies = sorted(strategy_sharpe.items(), key=lambda x: x[1], reverse=True)
                
                # Calculate optimal allocation based on Sharpe ratio ranking
                total_sharpe = sum(max(0, sharpe) for _, sharpe in sorted_strategies)
                
                for strategy_type, current_allocation in current_allocations.items():
                    sharpe_ratio = strategy_sharpe.get(strategy_type, 0)
                    
                    if total_sharpe > 0 and sharpe_ratio > 0:
                        # Allocate based on Sharpe ratio proportion
                        target_allocation = (sharpe_ratio / total_sharpe) * 0.8  # Use 80% of portfolio
                        
                        # Ensure within bounds
                        target_allocation = max(0.05, min(0.35, target_allocation))
                        
                        deviation = abs(current_allocation - target_allocation)
                        priority = "high" if deviation > 0.1 else "medium"
                        
                        results.append(OptimizationResult(
                            strategy_type=strategy_type,
                            target_allocation=target_allocation,
                            current_allocation=current_allocation,
                            recommended_action="increase" if target_allocation > current_allocation else "decrease",
                            priority=priority,
                            expected_return=risk_metrics.get("strategy_returns", {}).get(strategy_type, 0),
                            risk_score=risk_metrics.get("strategy_risks", {}).get(strategy_type, 0),
                            sharpe_ratio=sharpe_ratio
                        ))
            
            return results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error in Sharpe ratio optimization: {e}")
            return []
    
    async def _combine_optimization_results(self, risk_parity_results: List[OptimizationResult],
                                           mean_variance_results: List[OptimizationResult],
                                           sharpe_results: List[OptimizationResult]) -> Dict[str, Any]:
        """Combine results from different optimization strategies."""
        try:
            combined_results = {
                "risk_parity": risk_parity_results,
                "mean_variance": mean_variance_results,
                "sharpe_optimization": sharpe_results,
                "consensus_recommendations": []
            }
            
            # Find consensus recommendations across strategies
            strategy_recommendations = {}
            
            for result in risk_parity_results + mean_variance_results + sharpe_results:
                strategy_type = result.strategy_type
                if strategy_type not in strategy_recommendations:
                    strategy_recommendations[strategy_type] = {
                        "actions": [],
                        "target_allocations": [],
                        "priorities": []
                    }
                
                strategy_recommendations[strategy_type]["actions"].append(result.recommended_action)
                strategy_recommendations[strategy_type]["target_allocations"].append(result.target_allocation)
                strategy_recommendations[strategy_type]["priorities"].append(result.priority)
            
            # Generate consensus recommendations
            for strategy_type, recommendations in strategy_recommendations.items():
                actions = recommendations["actions"]
                target_allocations = recommendations["target_allocations"]
                priorities = recommendations["priorities"]
                
                # Most common action
                most_common_action = max(set(actions), key=actions.count)
                
                # Average target allocation
                avg_target_allocation = sum(target_allocations) / len(target_allocations)
                
                # Highest priority
                highest_priority = max(priorities, key=lambda p: {"low": 1, "medium": 2, "high": 3}[p])
                
                consensus = {
                    "strategy_type": strategy_type,
                    "recommended_action": most_common_action,
                    "target_allocation": avg_target_allocation,
                    "priority": highest_priority,
                    "confidence": actions.count(most_common_action) / len(actions),
                    "strategy_agreement": len(set(actions)) == 1
                }
                
                combined_results["consensus_recommendations"].append(consensus)
            
            return combined_results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error combining optimization results: {e}")
            return {"error": str(e)}
    
    async def _generate_recommendations(self, combined_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations from optimization results."""
        try:
            recommendations = []
            consensus_recommendations = combined_results.get("consensus_recommendations", [])
            
            for consensus in consensus_recommendations:
                if consensus["confidence"] >= 0.6:  # Only recommend if 60%+ confidence
                    recommendation = {
                        "type": "portfolio_rebalancing",
                        "strategy_type": consensus["strategy_type"],
                        "action": consensus["recommended_action"],
                        "target_allocation": consensus["target_allocation"],
                        "priority": consensus["priority"],
                        "confidence": consensus["confidence"],
                        "implementation": self._get_implementation_plan(consensus),
                        "expected_impact": self._calculate_expected_impact(consensus),
                        "timestamp": time.time()
                    }
                    
                    recommendations.append(recommendation)
            
            # Sort by priority and confidence
            recommendations.sort(key=lambda x: (
                {"low": 1, "medium": 2, "high": 3}[x["priority"]],
                x["confidence"]
            ), reverse=True)
            
            return recommendations
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error generating recommendations: {e}")
            return []
    
    def _get_implementation_plan(self, consensus: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation plan for a recommendation."""
        try:
            action = consensus["recommended_action"]
            strategy_type = consensus["strategy_type"]
            target_allocation = consensus["target_allocation"]
            
            if action == "increase":
                implementation = {
                    "method": "position_sizing",
                    "description": f"Increase {strategy_type} strategy allocation to {target_allocation:.1%}",
                    "steps": [
                        "Identify underperforming positions in other strategies",
                        "Close or reduce positions to free up capital",
                        "Open new positions in target strategy",
                        "Monitor allocation balance"
                    ],
                    "timeline": "1-3 trading days",
                    "risk_level": "medium"
                }
            elif action == "decrease":
                implementation = {
                    "method": "position_reduction",
                    "description": f"Reduce {strategy_type} strategy allocation to {target_allocation:.1%}",
                    "steps": [
                        "Identify positions to close or reduce",
                        "Execute partial exits or full closures",
                        "Reallocate capital to other strategies",
                        "Monitor risk exposure"
                    ],
                    "timeline": "1-2 trading days",
                    "risk_level": "low"
                }
            else:
                implementation = {
                    "method": "maintain",
                    "description": f"Maintain current {strategy_type} strategy allocation",
                    "steps": ["Continue monitoring performance", "No action required"],
                    "timeline": "ongoing",
                    "risk_level": "low"
                }
            
            return implementation
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error generating implementation plan: {e}")
            return {"error": str(e)}
    
    def _calculate_expected_impact(self, consensus: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate expected impact of implementing a recommendation."""
        try:
            action = consensus["recommended_action"]
            strategy_type = consensus["strategy_type"]
            confidence = consensus["confidence"]
            
            if action == "increase":
                impact = {
                    "expected_return_improvement": "2-5%",
                    "risk_adjustment": "Moderate increase in strategy-specific risk",
                    "portfolio_diversification": "Improved if strategy is uncorrelated",
                    "implementation_cost": "Low to medium",
                    "time_to_realize": "1-2 weeks"
                }
            elif action == "decrease":
                impact = {
                    "expected_return_improvement": "1-3%",
                    "risk_adjustment": "Reduced strategy-specific risk",
                    "portfolio_diversification": "May reduce if strategy was diversifying",
                    "implementation_cost": "Low",
                    "time_to_realize": "Immediate"
                }
            else:
                impact = {
                    "expected_return_improvement": "0%",
                    "risk_adjustment": "No change",
                    "portfolio_diversification": "Maintained",
                    "implementation_cost": "None",
                    "time_to_realize": "N/A"
                }
            
            # Adjust based on confidence
            if confidence < 0.8:
                impact["expected_return_improvement"] = "Reduced due to low confidence"
                impact["risk_adjustment"] = "Higher uncertainty"
            
            return impact
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error calculating expected impact: {e}")
            return {"error": str(e)}
    
    async def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Get optimization history."""
        try:
            return self.optimization_history[-10:]  # Last 10 optimizations
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting optimization history: {e}")
            return []
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get optimization performance metrics."""
        try:
            return {
                "performance_metrics": self.performance_metrics,
                "optimization_params": self.optimization_params,
                "timestamp": time.time()
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup portfolio optimizer resources."""
        try:
            self.optimization_history.clear()
            
            if self.logger:
                self.logger.info("✅ Portfolio optimizer cleaned up")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error cleaning up portfolio optimizer: {e}")
