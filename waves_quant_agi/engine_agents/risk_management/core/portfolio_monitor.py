#!/usr/bin/env python3
"""
Portfolio Monitor - INTEGRATED WITH NEW FOUNDATION
Handles portfolio health monitoring and risk assessment
Integrates with CircuitBreaker and PerformanceMonitor
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from .circuit_breaker import CircuitBreaker
# PerformanceMonitor removed - now handled by Core Agent

class PortfolioMonitor:
    """
    Portfolio monitoring engine - integrated with new foundation classes.
    Uses CircuitBreaker for fault tolerance and PerformanceMonitor for metrics.
    """
    
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
        
        # Initialize new foundation components
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            name="portfolio_monitor"
        )
        # self.performance_monitor = PerformanceMonitor(config)  # Removed - handled by Core Agent
        
        # Portfolio monitoring state
        self.monitor_stats = {
            "health_checks_performed": 0,
            "alerts_generated": 0,
            "drawdown_alerts": 0,
            "exposure_alerts": 0,
            "position_alerts": 0,
            "average_portfolio_health": 0.8
        }
        
        # Portfolio health thresholds (configurable)
        self.health_thresholds = config.get('portfolio_health_thresholds', {
            "max_total_drawdown": 0.10,        # 10% max portfolio drawdown
            "max_position_concentration": 0.25, # 25% max single position
            "max_sector_exposure": 0.40,       # 40% max sector exposure
            "min_diversification_score": 0.6,  # 60% min diversification
            "max_correlation_risk": 0.8,       # 80% max correlation risk
            "min_liquidity_ratio": 0.2         # 20% min liquid positions
        })
        
        # Portfolio history for trend analysis
        self.portfolio_history = []
        self.max_history_length = 1000  # Keep last 1000 portfolio snapshots
        
        # Current portfolio metrics
        self.current_metrics = {
            "total_value": 100000.0,
            "total_pnl": 0.0,
            "unrealized_pnl": 0.0,
            "realized_pnl": 0.0,
            "current_drawdown": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "sharpe_ratio": 0.0,
            "portfolio_health_score": 0.8
        }
        
    async def assess_portfolio_health(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess overall portfolio health and generate alerts if needed.
        Uses circuit breaker for fault tolerance.
        """
        start_time = time.time()
        
        try:
            # Use circuit breaker for fault tolerance
            result = await self.circuit_breaker.call(
                self._perform_health_assessment,
                portfolio_data
            )
            
            # Record performance metrics
            duration_ms = (time.time() - start_time) * 1000
            # await self.performance_monitor.record_operation(  # Removed - handled by Core Agent
            #     operation_type='portfolio_health_assessment',
            #     duration_ms=duration_ms,
            #     success=True,
            #     component='portfolio_monitor',
            #     metadata={'portfolio_size': len(portfolio_data.get('positions', {}))}
            # )
            
            # Update statistics
            self._update_monitor_stats(result)
            
            return result
            
        except Exception as e:
            # Record failure
            duration_ms = (time.time() - start_time) * 1000
            # await self.performance_monitor.record_operation(  # Removed - handled by Core Agent
            #     operation_type='portfolio_health_assessment',
            #     duration_ms=duration_ms,
            #     success=False,
            #     component='portfolio_monitor',
            #     metadata={'error': str(e)}
            # )
            
            # Return error result
            return {
                "health_assessment": {"overall_health": "error"},
                "alerts": [{"type": "system_error", "message": f"Assessment failed: {str(e)}"}],
                "current_metrics": self.current_metrics,
                "recommendations": ["Contact system administrator"],
                "timestamp": time.time()
            }
    
    async def _perform_health_assessment(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive portfolio health assessment.
        """
        try:
            # Update current metrics
            self._update_current_metrics(portfolio_data)
            
            # Perform health assessments
            health_scores = {
                "drawdown_health": self._assess_drawdown_health(portfolio_data),
                "concentration_health": self._assess_concentration_health(
                    portfolio_data.get('positions', {}), 
                    portfolio_data.get('total_value', 0)
                ),
                "diversification_health": self._assess_diversification_health(
                    portfolio_data.get('positions', {})
                ),
                "liquidity_health": self._assess_liquidity_health(
                    portfolio_data.get('positions', {}), 
                    portfolio_data.get('total_value', 0)
                ),
                "performance_health": self._assess_performance_health(portfolio_data),
                "risk_exposure_health": self._assess_risk_exposure_health(
                    portfolio_data.get('positions', {}), 
                    portfolio_data.get('total_value', 0)
                )
            }
            
            # Calculate overall health score
            overall_health = sum(health_scores.values()) / len(health_scores)
            health_level = self._determine_health_level(overall_health)
            
            # Generate alerts
            alerts = await self._generate_health_alerts(health_scores, portfolio_data)
            
            # Update portfolio history
            self._update_portfolio_history(portfolio_data, health_scores)
            
            # Update monitor statistics
            self.monitor_stats["health_checks_performed"] += 1
            self.monitor_stats["alerts_generated"] += len(alerts)
            self.monitor_stats["average_portfolio_health"] = overall_health
            
            return {
                "health_assessment": {
                    "overall_health": health_level,
                    "health_score": overall_health,
                    "component_scores": health_scores
                },
                "alerts": alerts,
                "current_metrics": self.current_metrics,
                "recommendations": self._generate_health_recommendations(health_scores),
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Portfolio health assessment error: {e}")
            raise
    
    def _assess_drawdown_health(self, portfolio_data: Dict[str, Any]) -> float:
        """Assess portfolio drawdown health."""
        try:
            current_drawdown = abs(portfolio_data.get('current_drawdown', 0))
            max_allowed = self.health_thresholds['max_total_drawdown']
            
            if current_drawdown <= max_allowed * 0.5:
                return 1.0  # Excellent
            elif current_drawdown <= max_allowed:
                return 0.7  # Good
            elif current_drawdown <= max_allowed * 1.5:
                return 0.4  # Poor
            else:
                return 0.0  # Critical
                
        except Exception as e:
            print(f"Error assessing drawdown health: {e}")
            return 0.5  # Neutral on error
    
    def _assess_concentration_health(self, positions: Dict[str, Any], total_value: float) -> float:
        """Assess position concentration health."""
        try:
            if not positions or total_value <= 0:
                return 1.0  # No positions = no concentration risk
            
            max_concentration = 0.0
            for position in positions.values():
                position_value = position.get('value', 0)
                concentration = position_value / total_value
                max_concentration = max(max_concentration, concentration)
            
            max_allowed = self.health_thresholds['max_position_concentration']
            
            if max_concentration <= max_allowed * 0.7:
                return 1.0  # Excellent
            elif max_concentration <= max_allowed:
                return 0.7  # Good
            elif max_concentration <= max_allowed * 1.3:
                return 0.4  # Poor
            else:
                return 0.0  # Critical
                
        except Exception as e:
            print(f"Error assessing concentration health: {e}")
            return 0.5
    
    def _assess_diversification_health(self, positions: Dict[str, Any]) -> float:
        """Assess portfolio diversification health."""
        try:
            if len(positions) <= 1:
                return 0.3  # Poor diversification
            
            # Simple diversification score based on number of positions
            # In a real system, this would consider sector distribution, correlation, etc.
            diversification_score = min(1.0, len(positions) / 20.0)  # 20+ positions = excellent
            
            min_required = self.health_thresholds['min_diversification_score']
            
            if diversification_score >= min_required * 1.2:
                return 1.0  # Excellent
            elif diversification_score >= min_required:
                return 0.7  # Good
            elif diversification_score >= min_required * 0.8:
                return 0.4  # Poor
            else:
                return 0.0  # Critical
                
        except Exception as e:
            print(f"Error assessing diversification health: {e}")
            return 0.5
    
    def _assess_liquidity_health(self, positions: Dict[str, Any], total_value: float) -> float:
        """Assess portfolio liquidity health."""
        try:
            if not positions or total_value <= 0:
                return 1.0  # No positions = no liquidity concerns
            
            # Mock liquidity assessment - replace with actual implementation
            # In a real system, this would check bid-ask spreads, trading volume, etc.
            liquidity_score = 0.8  # Mock value
            
            min_required = self.health_thresholds['min_liquidity_ratio']
            
            if liquidity_score >= min_required * 1.2:
                return 1.0  # Excellent
            elif liquidity_score >= min_required:
                return 0.7  # Good
            elif liquidity_score >= min_required * 0.8:
                return 0.4  # Poor
            else:
                return 0.0  # Critical
                
        except Exception as e:
            print(f"Error assessing liquidity health: {e}")
            return 0.5
    
    def _assess_performance_health(self, portfolio_data: Dict[str, Any]) -> float:
        """Assess portfolio performance health."""
        try:
            # Mock performance assessment - replace with actual implementation
            # In a real system, this would check Sharpe ratio, win rate, etc.
            performance_score = 0.75  # Mock value
            
            if performance_score >= 0.8:
                return 1.0  # Excellent
            elif performance_score >= 0.6:
                return 0.7  # Good
            elif performance_score >= 0.4:
                return 0.4  # Poor
            else:
                return 0.0  # Critical
                
        except Exception as e:
            print(f"Error assessing performance health: {e}")
            return 0.5
    
    def _assess_risk_exposure_health(self, positions: Dict[str, Any], total_value: float) -> float:
        """Assess portfolio risk exposure health."""
        try:
            if not positions or total_value <= 0:
                return 1.0  # No positions = no risk exposure
            
            # Mock risk exposure assessment - replace with actual implementation
            # In a real system, this would check VaR, correlation, sector exposure, etc.
            risk_score = 0.6  # Mock value
            
            if risk_score <= 0.3:
                return 1.0  # Excellent
            elif risk_score <= 0.6:
                return 0.7  # Good
            elif risk_score <= 0.8:
                return 0.4  # Poor
            else:
                return 0.0  # Critical
                
        except Exception as e:
            print(f"Error assessing risk exposure health: {e}")
            return 0.5
    
    def _determine_health_level(self, health_score: float) -> str:
        """Determine health level based on health score."""
        if health_score >= 0.8:
            return "excellent"
        elif health_score >= 0.6:
            return "good"
        elif health_score >= 0.4:
            return "fair"
        elif health_score >= 0.2:
            return "poor"
        else:
            return "critical"
    
    async def _generate_health_alerts(self, health_scores: Dict[str, float], 
                                    portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate health alerts based on assessment results."""
        alerts = []
        
        try:
            # Check drawdown alerts
            if health_scores['drawdown_health'] <= 0.4:
                alerts.append({
                    "type": "drawdown_alert",
                    "severity": "high" if health_scores['drawdown_health'] == 0.0 else "medium",
                    "message": f"Portfolio drawdown health is poor: {health_scores['drawdown_health']:.2f}",
                    "timestamp": time.time()
                })
                self.monitor_stats["drawdown_alerts"] += 1
            
            # Check concentration alerts
            if health_scores['concentration_health'] <= 0.4:
                alerts.append({
                    "type": "concentration_alert",
                    "severity": "high" if health_scores['concentration_health'] == 0.0 else "medium",
                    "message": f"Position concentration health is poor: {health_scores['concentration_health']:.2f}",
                    "timestamp": time.time()
                })
                self.monitor_stats["position_alerts"] += 1
            
            # Check diversification alerts
            if health_scores['diversification_health'] <= 0.4:
                alerts.append({
                    "type": "diversification_alert",
                    "severity": "medium",
                    "message": f"Portfolio diversification health is poor: {health_scores['diversification_health']:.2f}",
                    "timestamp": time.time()
                })
                self.monitor_stats["exposure_alerts"] += 1
            
            # Check overall health alert
            overall_health = sum(health_scores.values()) / len(health_scores)
            if overall_health <= 0.4:
                alerts.append({
                    "type": "overall_health_alert",
                    "severity": "critical" if overall_health <= 0.2 else "high",
                    "message": f"Overall portfolio health is poor: {overall_health:.2f}",
                    "timestamp": time.time()
                })
            
        except Exception as e:
            print(f"Error generating health alerts: {e}")
            alerts.append({
                "type": "system_error",
                "severity": "high",
                "message": f"Error generating alerts: {str(e)}",
                "timestamp": time.time()
            })
        
        return alerts
    
    def _generate_health_recommendations(self, health_scores: Dict[str, float]) -> List[str]:
        """Generate health improvement recommendations."""
        recommendations = []
        
        try:
            # Drawdown recommendations
            if health_scores['drawdown_health'] <= 0.4:
                recommendations.append("Consider reducing position sizes to limit drawdown risk")
                recommendations.append("Review stop-loss levels and risk management parameters")
            
            # Concentration recommendations
            if health_scores['concentration_health'] <= 0.4:
                recommendations.append("Reduce exposure to largest positions")
                recommendations.append("Consider rebalancing portfolio for better diversification")
            
            # Diversification recommendations
            if health_scores['diversification_health'] <= 0.4:
                recommendations.append("Add new positions to increase diversification")
                recommendations.append("Consider different asset classes or sectors")
            
            # General recommendations
            if any(score <= 0.4 for score in health_scores.values()):
                recommendations.append("Schedule portfolio review with risk management team")
                recommendations.append("Consider reducing overall portfolio risk exposure")
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            recommendations.append("Contact risk management team for portfolio review")
        
        return recommendations
    
    def _update_current_metrics(self, portfolio_data: Dict[str, Any]):
        """Update current portfolio metrics."""
        try:
            for key, value in portfolio_data.items():
                if key in self.current_metrics:
                    self.current_metrics[key] = value
            
            # Update portfolio health score
            self.current_metrics['portfolio_health_score'] = self.monitor_stats.get('average_portfolio_health', 0.8)
            
        except Exception as e:
            print(f"Error updating current metrics: {e}")
    
    def _update_portfolio_history(self, portfolio_data: Dict[str, Any], health_scores: Dict[str, float]):
        """Update portfolio history for trend analysis."""
        try:
            history_entry = {
                "timestamp": time.time(),
                "portfolio_data": portfolio_data,
                "health_scores": health_scores,
                "overall_health": sum(health_scores.values()) / len(health_scores)
            }
            
            self.portfolio_history.append(history_entry)
            
            # Keep only recent history
            if len(self.portfolio_history) > self.max_history_length:
                self.portfolio_history = self.portfolio_history[-self.max_history_length:]
                
        except Exception as e:
            print(f"Error updating portfolio history: {e}")
    
    def _update_monitor_stats(self, assessment_result: Dict[str, Any]):
        """Update monitor statistics."""
        try:
            # Update average portfolio health
            if 'health_assessment' in assessment_result:
                health_score = assessment_result['health_assessment'].get('health_score', 0.8)
                self.monitor_stats['average_portfolio_health'] = health_score
            
        except Exception as e:
            print(f"Error updating monitor stats: {e}")
    
    def get_portfolio_trend(self, lookback_periods: int = 20) -> Dict[str, Any]:
        """Get portfolio trend analysis."""
        try:
            if len(self.portfolio_history) < 2:
                return {"trend": "insufficient_data", "message": "Need more history for trend analysis"}
            
            # Get recent history
            recent_history = self.portfolio_history[-lookback_periods:] if lookback_periods > 0 else self.portfolio_history
            
            if len(recent_history) < 2:
                return {"trend": "insufficient_data", "message": "Need more history for trend analysis"}
            
            # Calculate trend
            first_health = recent_history[0]['overall_health']
            last_health = recent_history[-1]['overall_health']
            
            health_change = last_health - first_health
            
            if health_change > 0.1:
                trend = "improving"
            elif health_change < -0.1:
                trend = "declining"
            else:
                trend = "stable"
            
            return {
                "trend": trend,
                "health_change": health_change,
                "first_health": first_health,
                "last_health": last_health,
                "periods_analyzed": len(recent_history),
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error analyzing portfolio trend: {e}")
            return {"trend": "error", "message": str(e)}
    
    def get_monitor_stats(self) -> Dict[str, Any]:
        """Get portfolio monitor statistics."""
        try:
            return {
                **self.monitor_stats,
                "portfolio_history_size": len(self.portfolio_history),
                "circuit_breaker_state": self.circuit_breaker.get_state().value,
                "performance_metrics": {},  # Removed - handled by Core Agent
                "current_metrics": self.current_metrics,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error getting monitor stats: {e}")
            return {"error": str(e)}
    
    def reset_monitor_stats(self):
        """Reset monitor statistics."""
        self.monitor_stats = {
            "health_checks_performed": 0,
            "alerts_generated": 0,
            "drawdown_alerts": 0,
            "exposure_alerts": 0,
            "position_alerts": 0,
            "average_portfolio_health": 0.8
        }
    
    def clear_portfolio_history(self):
        """Clear portfolio history."""
        self.portfolio_history.clear()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health information."""
        try:
            return {
                "portfolio_monitor": {
                    "status": "operational",
                    "stats": self.get_monitor_stats()
                },
                "circuit_breaker": self.circuit_breaker.get_stats(),
                "performance_monitor": {},  # Removed - handled by Core Agent
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
