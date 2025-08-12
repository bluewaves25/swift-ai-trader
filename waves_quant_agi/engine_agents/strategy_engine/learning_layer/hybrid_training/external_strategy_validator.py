#!/usr/bin/env python3
"""
External Strategy Validator
Validates external strategies for integration into the strategy engine.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from engine_agents.shared_utils import get_shared_logger, get_shared_redis

class ExternalStrategyValidator:
    """Validates external strategies for integration."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "external_validator")
        self.redis_conn = get_shared_redis()
        
        # Validation configuration
        self.validation_threshold = config.get("validation_threshold", 0.7)
        self.min_performance_history = config.get("min_performance_history", 30)
        self.max_validation_age = config.get("max_validation_age", 86400)  # 24 hours
        
        # Validation state
        self.validation_history: List[Dict[str, Any]] = []
        self.validated_strategies: Dict[str, Dict[str, Any]] = {}
        
        # Validation statistics
        self.stats = {
            "validations_performed": 0,
            "strategies_validated": 0,
            "strategies_rejected": 0,
            "validation_errors": 0,
            "start_time": time.time()
        }

    async def validate_strategy(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an external strategy for integration."""
        try:
            strategy_id = strategy_data.get("strategy_id", "unknown")
            strategy_name = strategy_data.get("strategy_name", "unknown")
            strategy_type = strategy_data.get("strategy_type", "unknown")
            
            self.logger.info(f"Validating external strategy: {strategy_name} ({strategy_id})")
            
            # Perform comprehensive validation
            validation_result = await self._perform_validation(strategy_data)
            
            if validation_result["is_valid"]:
                # Store validated strategy
                await self._store_validated_strategy(strategy_id, strategy_data, validation_result)
                
                # Update statistics
                self.stats["strategies_validated"] += 1
                self.stats["validations_performed"] += 1
                
                self.logger.info(f"Strategy {strategy_name} validated successfully")
                
                # Notify strategy registry
                await self._notify_strategy_registry(strategy_id, strategy_data, validation_result)
                
            else:
                # Update statistics
                self.stats["strategies_rejected"] += 1
                self.stats["validations_performed"] += 1
                
                self.logger.warning(f"Strategy {strategy_name} failed validation: {validation_result['rejection_reason']}")
            
            # Store validation result
            await self._store_validation_result(strategy_id, validation_result)
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating external strategy: {e}")
            self.stats["validation_errors"] += 1
            
            return {
                "is_valid": False,
                "validation_score": 0.0,
                "rejection_reason": f"Validation error: {str(e)}",
                "timestamp": int(time.time())
            }

    async def _perform_validation(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive strategy validation."""
        try:
            validation_score = 0.0
            rejection_reasons = []
            
            # 1. Performance validation
            performance_score = await self._validate_performance(strategy_data)
            if performance_score >= self.validation_threshold:
                validation_score += performance_score * 0.4  # 40% weight
            else:
                rejection_reasons.append(f"Insufficient performance: {performance_score:.2f}")
            
            # 2. Risk validation
            risk_score = await self._validate_risk(strategy_data)
            if risk_score >= 0.6:  # Risk threshold
                validation_score += risk_score * 0.3  # 30% weight
            else:
                rejection_reasons.append(f"Risk too high: {risk_score:.2f}")
            
            # 3. Technical validation
            technical_score = await self._validate_technical(strategy_data)
            if technical_score >= 0.7:  # Technical threshold
                validation_score += technical_score * 0.2  # 20% weight
            else:
                rejection_reasons.append(f"Technical issues: {technical_score:.2f}")
            
            # 4. Compliance validation
            compliance_score = await self._validate_compliance(strategy_data)
            if compliance_score >= 0.8:  # Compliance threshold
                validation_score += compliance_score * 0.1  # 10% weight
            else:
                rejection_reasons.append(f"Compliance issues: {compliance_score:.2f}")
            
            # Determine if strategy is valid
            is_valid = validation_score >= self.validation_threshold and len(rejection_reasons) == 0
            
            return {
                "is_valid": is_valid,
                "validation_score": validation_score,
                "rejection_reason": "; ".join(rejection_reasons) if rejection_reasons else None,
                "performance_score": performance_score,
                "risk_score": risk_score,
                "technical_score": technical_score,
                "compliance_score": compliance_score,
                "timestamp": int(time.time())
            }
            
        except Exception as e:
            self.logger.error(f"Error performing validation: {e}")
            return {
                "is_valid": False,
                "validation_score": 0.0,
                "rejection_reason": f"Validation error: {str(e)}",
                "timestamp": int(time.time())
            }

    async def _validate_performance(self, strategy_data: Dict[str, Any]) -> float:
        """Validate strategy performance."""
        try:
            # Get performance metrics
            performance_metrics = strategy_data.get("performance_metrics", {})
            
            # Calculate performance score
            sharpe_ratio = performance_metrics.get("sharpe_ratio", 0.0)
            max_drawdown = performance_metrics.get("max_drawdown", 1.0)
            win_rate = performance_metrics.get("win_rate", 0.0)
            profit_factor = performance_metrics.get("profit_factor", 0.0)
            
            # Normalize metrics
            sharpe_score = min(1.0, max(0.0, (sharpe_ratio + 2) / 4))  # -2 to 2 range
            drawdown_score = max(0.0, 1.0 - max_drawdown)  # 0% to 100%
            win_rate_score = win_rate  # Already 0-1
            profit_factor_score = min(1.0, profit_factor / 2)  # 0 to 2+ range
            
            # Weighted average
            performance_score = (
                sharpe_score * 0.3 +
                drawdown_score * 0.3 +
                win_rate_score * 0.2 +
                profit_factor_score * 0.2
            )
            
            return performance_score
            
        except Exception as e:
            self.logger.error(f"Error validating performance: {e}")
            return 0.0

    async def _validate_risk(self, strategy_data: Dict[str, Any]) -> float:
        """Validate strategy risk profile."""
        try:
            # Get risk metrics
            risk_metrics = strategy_data.get("risk_metrics", {})
            
            # Calculate risk score
            volatility = risk_metrics.get("volatility", 1.0)
            var_95 = risk_metrics.get("var_95", 1.0)
            max_position_size = risk_metrics.get("max_position_size", 1.0)
            correlation = risk_metrics.get("correlation", 0.0)
            
            # Normalize metrics (lower is better for risk)
            volatility_score = max(0.0, 1.0 - min(volatility, 1.0))
            var_score = max(0.0, 1.0 - min(var_95, 1.0))
            position_score = max(0.0, 1.0 - min(max_position_size, 1.0))
            correlation_score = max(0.0, 1.0 - abs(correlation))
            
            # Weighted average
            risk_score = (
                volatility_score * 0.3 +
                var_score * 0.3 +
                position_score * 0.2 +
                correlation_score * 0.2
            )
            
            return risk_score
            
        except Exception as e:
            self.logger.error(f"Error validating risk: {e}")
            return 0.0

    async def _validate_technical(self, strategy_data: Dict[str, Any]) -> float:
        """Validate technical implementation."""
        try:
            # Get technical details
            technical_details = strategy_data.get("technical_details", {})
            
            # Calculate technical score
            code_quality = technical_details.get("code_quality", 0.0)
            test_coverage = technical_details.get("test_coverage", 0.0)
            documentation = technical_details.get("documentation", 0.0)
            error_handling = technical_details.get("error_handling", 0.0)
            
            # Weighted average
            technical_score = (
                code_quality * 0.4 +
                test_coverage * 0.3 +
                documentation * 0.2 +
                error_handling * 0.1
            )
            
            return technical_score
            
        except Exception as e:
            self.logger.error(f"Error validating technical: {e}")
            return 0.0

    async def _validate_compliance(self, strategy_data: Dict[str, Any]) -> float:
        """Validate compliance requirements."""
        try:
            # Get compliance details
            compliance_details = strategy_data.get("compliance_details", {})
            
            # Calculate compliance score
            regulatory_compliance = compliance_details.get("regulatory_compliance", 0.0)
            risk_limits = compliance_details.get("risk_limits", 0.0)
            audit_trail = compliance_details.get("audit_trail", 0.0)
            reporting = compliance_details.get("reporting", 0.0)
            
            # Weighted average
            compliance_score = (
                regulatory_compliance * 0.4 +
                risk_limits * 0.3 +
                audit_trail * 0.2 +
                reporting * 0.1
            )
            
            return compliance_score
            
        except Exception as e:
            self.logger.error(f"Error validating compliance: {e}")
            return 0.0

    async def _store_validated_strategy(self, strategy_id: str, strategy_data: Dict[str, Any], 
                                      validation_result: Dict[str, Any]):
        """Store validated strategy in Redis."""
        try:
            # Store strategy data
            strategy_key = f"strategy_engine:validated_strategies:{strategy_id}"
            strategy_info = {
                **strategy_data,
                "validation_result": validation_result,
                "validated_at": int(time.time()),
                "status": "validated"
            }
            
            self.redis_conn.set(strategy_key, str(strategy_info), ex=604800)  # 7 days
            
            # Update local cache
            self.validated_strategies[strategy_id] = strategy_info
            
            # Add to validation history
            self.validation_history.append({
                "strategy_id": strategy_id,
                "validation_result": validation_result,
                "timestamp": int(time.time())
            })
            
            # Limit history size
            if len(self.validation_history) > 1000:
                self.validation_history = self.validation_history[-1000:]
                
        except Exception as e:
            self.logger.error(f"Error storing validated strategy: {e}")

    async def _store_validation_result(self, strategy_id: str, validation_result: Dict[str, Any]):
        """Store validation result in Redis."""
        try:
            # Store validation result
            validation_key = f"strategy_engine:validation_results:{strategy_id}"
            self.redis_conn.set(validation_key, str(validation_result), ex=604800)  # 7 days
            
        except Exception as e:
            self.logger.error(f"Error storing validation result: {e}")

    async def _notify_strategy_registry(self, strategy_id: str, strategy_data: Dict[str, Any], 
                                      validation_result: Dict[str, Any]):
        """Notify strategy registry of validated strategy."""
        try:
            # Create notification
            notification = {
                "type": "strategy_validated",
                "strategy_id": strategy_id,
                "strategy_name": strategy_data.get("strategy_name", "unknown"),
                "strategy_type": strategy_data.get("strategy_type", "unknown"),
                "validation_score": validation_result["validation_score"],
                "timestamp": int(time.time())
            }
            
            # Publish to strategy updates channel
            self.redis_conn.publish("strategy_engine:strategy_updates", str(notification))
            
            # Store notification
            notification_key = f"strategy_engine:notifications:{int(time.time())}"
            self.redis_conn.set(notification_key, str(notification), ex=86400)  # 24 hours
            
        except Exception as e:
            self.logger.error(f"Error notifying strategy registry: {e}")

    async def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return {
            **self.stats,
            "validation_history_size": len(self.validation_history),
            "validated_strategies_count": len(self.validated_strategies),
            "uptime": time.time() - self.stats["start_time"]
        }

    async def get_validated_strategies(self) -> List[Dict[str, Any]]:
        """Get list of validated strategies."""
        return list(self.validated_strategies.values())

    async def reset_validation_state(self):
        """Reset validation state."""
        try:
            self.validation_history.clear()
            self.validated_strategies.clear()
            
            # Reset stats
            self.stats = {
                "validations_performed": 0,
                "strategies_validated": 0,
                "strategies_rejected": 0,
                "validation_errors": 0,
                "start_time": time.time()
            }
            
            self.logger.info("Validation state reset")
            
        except Exception as e:
            self.logger.error(f"Error resetting validation state: {e}")