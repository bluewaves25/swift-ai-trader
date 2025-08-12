#!/usr/bin/env python3
"""
Risk Validator - INTEGRATED WITH NEW FOUNDATION
Handles risk validation using the new streamlined architecture
Integrates with DynamicRiskLimits, CircuitBreaker, and PerformanceMonitor
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from .dynamic_risk_limits import DynamicRiskLimits
from .circuit_breaker import CircuitBreaker
from .performance_monitor import PerformanceMonitor

class RiskValidator:
    """
    Core risk validation engine - integrated with new foundation classes.
    Uses DynamicRiskLimits instead of hardcoded values.
    """
    
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
        
        # Initialize new foundation components
        self.dynamic_risk_limits = DynamicRiskLimits(connection_manager, config)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            name="risk_validator"
        )
        self.performance_monitor = PerformanceMonitor(config)
        
        # Risk validation state
        self.validation_stats = {
            "fast_validations": 0,
            "comprehensive_validations": 0,
            "risks_blocked": 0,
            "risks_approved": 0,
            "average_validation_time_ms": 0.0
        }
        
        # Current portfolio state
        self.portfolio_state = {
            "total_value": 100000.0,  # $100K default
            "available_capital": 100000.0,
            "positions": {},
            "total_exposure": 0.0,
            "current_drawdown": 0.0
        }
        
        # Performance tracking
        self.validation_times = []
        self.max_history = 1000
    
    async def validate_trade_request(self, trade_request: Dict[str, Any], 
                                   strategy_type: str = "general") -> Dict[str, Any]:
        """
        Validate trade request using dynamic risk limits.
        Returns comprehensive validation result.
        """
        start_time = time.time()
        
        try:
            # Use circuit breaker for fault tolerance
            result = await self.circuit_breaker.call(
                self._perform_risk_validation,
                trade_request,
                strategy_type
            )
            
            # Record performance metrics
            duration_ms = (time.time() - start_time) * 1000
            await self.performance_monitor.record_operation(
                operation_type='risk_validation',
                duration_ms=duration_ms,
                success=True,
                component='risk_validator',
                metadata={'strategy_type': strategy_type, 'symbol': trade_request.get('symbol', 'unknown')}
            )
            
            # Update validation statistics
            self._update_validation_stats(result, duration_ms)
            
            return result
            
        except Exception as e:
            # Record failure
            duration_ms = (time.time() - start_time) * 1000
            await self.performance_monitor.record_operation(
                operation_type='risk_validation',
                duration_ms=duration_ms,
                success=False,
                component='risk_validator',
                metadata={'strategy_type': strategy_type, 'error': str(e)}
            )
            
            # Return error result
            return {
                "validation_passed": False,
                "risk_level": "critical",
                "risk_score": 1.0,
                "blocked_reasons": [f"Validation error: {str(e)}"],
                "recommendations": ["Contact system administrator"],
                "timestamp": time.time()
            }
    
    async def _perform_risk_validation(self, trade_request: Dict[str, Any], 
                                     strategy_type: str) -> Dict[str, Any]:
        """
        Perform comprehensive risk validation using dynamic limits.
        """
        try:
            symbol = trade_request.get('symbol', 'unknown')
            
            # Get dynamic risk limits for this strategy and symbol
            risk_limits = await self.dynamic_risk_limits.get_strategy_risk_limits(
                strategy_type, symbol
            )
            
            # Perform validation checks
            validation_results = {
                "position_size_check": await self._check_position_size_limit(
                    trade_request, risk_limits
                ),
                "leverage_check": await self._check_leverage_limit(
                    trade_request, risk_limits
                ),
                "portfolio_exposure_check": await self._check_portfolio_exposure(
                    trade_request
                ),
                "stop_loss_check": await self._check_stop_loss_compliance(
                    trade_request, risk_limits
                )
            }
            
            # Determine overall validation result
            all_checks_passed = all(
                result.get('passed', False) for result in validation_results.values()
            )
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(validation_results)
            risk_level = self._determine_risk_level(risk_score)
            
            # Generate recommendations
            recommendations = self._generate_validation_recommendations(
                validation_results, risk_level
            )
            
            return {
                "validation_passed": all_checks_passed,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "validation_details": validation_results,
                "risk_limits_used": risk_limits,
                "recommendations": recommendations,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Risk validation error: {e}")
            raise
    
    async def _check_position_size_limit(self, trade_request: Dict[str, Any], 
                                       risk_limits: Dict[str, Any]) -> Dict[str, Any]:
        """Check position size against dynamic limits."""
        try:
            position_size = trade_request.get('position_size', 0)
            max_position = risk_limits.get('max_position_size', 0.1)
            
            passed = position_size <= max_position
            
            return {
                "passed": passed,
                "current": position_size,
                "limit": max_position,
                "message": f"Position size {'within' if passed else 'exceeds'} limit"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _check_leverage_limit(self, trade_request: Dict[str, Any], 
                                  risk_limits: Dict[str, Any]) -> Dict[str, Any]:
        """Check leverage against dynamic limits."""
        try:
            leverage = trade_request.get('leverage', 1.0)
            max_leverage = risk_limits.get('max_leverage', 1.0)
            
            passed = leverage <= max_leverage
            
            return {
                "passed": passed,
                "current": leverage,
                "limit": max_leverage,
                "message": f"Leverage {'within' if passed else 'exceeds'} limit"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _check_portfolio_exposure(self, trade_request: Dict[str, Any]) -> Dict[str, Any]:
        """Check portfolio exposure limits."""
        try:
            # Mock portfolio check - replace with actual implementation
            return {
                "passed": True,
                "message": "Portfolio exposure within limits"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _check_stop_loss_compliance(self, trade_request: Dict[str, Any], 
                                        risk_limits: Dict[str, Any]) -> Dict[str, Any]:
        """Check stop loss compliance."""
        try:
            stop_loss = trade_request.get('stop_loss', 0)
            max_stop_loss = risk_limits.get('stop_loss', 0.02)
            
            passed = stop_loss <= max_stop_loss
            
            return {
                "passed": passed,
                "current": stop_loss,
                "limit": max_stop_loss,
                "message": f"Stop loss {'within' if passed else 'exceeds'} limit"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _calculate_risk_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate overall risk score based on validation results."""
        try:
            # Count failed checks
            failed_checks = sum(
                1 for result in validation_results.values() 
                if not result.get('passed', True)
            )
            
            total_checks = len(validation_results)
            
            if total_checks == 0:
                return 0.0
            
            # Risk score is proportion of failed checks
            risk_score = failed_checks / total_checks
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            print(f"Error calculating risk score: {e}")
            return 1.0  # Maximum risk on error
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on risk score."""
        if risk_score == 0.0:
            return "low"
        elif risk_score <= 0.25:
            return "medium"
        elif risk_score <= 0.5:
            return "high"
        else:
            return "critical"
    
    def _generate_validation_recommendations(self, validation_results: Dict[str, Any], 
                                           risk_level: str) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Add specific recommendations for failed checks
        for check_name, result in validation_results.items():
            if not result.get('passed', True):
                if check_name == "position_size_check":
                    recommendations.append("Reduce position size to comply with limits")
                elif check_name == "leverage_check":
                    recommendations.append("Reduce leverage to comply with limits")
                elif check_name == "stop_loss_check":
                    recommendations.append("Adjust stop loss to comply with limits")
        
        # Add general recommendations based on risk level
        if risk_level == "high":
            recommendations.append("Review risk parameters before proceeding")
        elif risk_level == "critical":
            recommendations.append("Immediate action required - do not proceed with trade")
        
        return recommendations
    
    def _update_validation_stats(self, validation_result: Dict[str, Any], duration_ms: float):
        """Update validation statistics."""
        try:
            # Update validation counts
            if validation_result.get('validation_passed', False):
                self.validation_stats['risks_approved'] += 1
            else:
                self.validation_stats['risks_blocked'] += 1
            
            # Update timing statistics
            self.validation_times.append(duration_ms)
            if len(self.validation_times) > self.max_history:
                self.validation_times = self.validation_times[-self.max_history:]
            
            # Calculate average validation time
            self.validation_stats['average_validation_time_ms'] = sum(self.validation_times) / len(self.validation_times)
            
        except Exception as e:
            print(f"Error updating validation stats: {e}")
    
    def update_portfolio_state(self, portfolio_update: Dict[str, Any]):
        """Update current portfolio state."""
        try:
            for key, value in portfolio_update.items():
                if key in self.portfolio_state:
                    self.portfolio_state[key] = value
            
            # Recalculate derived values
            self.portfolio_state['total_exposure'] = sum(
                pos.get('value', 0) for pos in self.portfolio_state['positions'].values()
            )
            
        except Exception as e:
            print(f"Error updating portfolio state: {e}")
    
    def get_portfolio_risk_summary(self) -> Dict[str, Any]:
        """Get portfolio risk summary."""
        try:
            return {
                "portfolio_state": self.portfolio_state,
                "risk_metrics": {
                    "exposure_ratio": self.portfolio_state['total_exposure'] / max(self.portfolio_state['total_value'], 1),
                    "available_capital_ratio": self.portfolio_state['available_capital'] / max(self.portfolio_state['total_value'], 1),
                    "current_drawdown": self.portfolio_state['current_drawdown']
                },
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error getting portfolio risk summary: {e}")
            return {"error": str(e)}
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        try:
            total_validations = self.validation_stats['risks_approved'] + self.validation_stats['risks_blocked']
            
            return {
                **self.validation_stats,
                "total_validations": total_validations,
                "approval_rate": self.validation_stats['risks_approved'] / max(total_validations, 1),
                "block_rate": self.validation_stats['risks_blocked'] / max(total_validations, 1),
                "circuit_breaker_state": self.circuit_breaker.get_state().value,
                "performance_metrics": self.performance_monitor.get_performance_summary(
                    component='risk_validator', time_window=3600
                )
            }
            
        except Exception as e:
            print(f"Error getting validation stats: {e}")
            return {"error": str(e)}
    
    def reset_validation_stats(self):
        """Reset validation statistics."""
        self.validation_stats = {
            "fast_validations": 0,
            "comprehensive_validations": 0,
            "risks_blocked": 0,
            "risks_approved": 0,
            "average_validation_time_ms": 0.0
        }
        self.validation_times = []
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health information."""
        try:
            return {
                "risk_validator": {
                    "status": "operational",
                    "stats": self.get_validation_stats()
                },
                "circuit_breaker": self.circuit_breaker.get_stats(),
                "performance_monitor": self.performance_monitor.get_monitor_stats(),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
