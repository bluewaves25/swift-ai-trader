#!/usr/bin/env python3
"""
Enhanced Risk Management Agent - ROLE CONSOLIDATED: RISK VALIDATION ONLY
Removed health monitoring functionality - now handled by Core Agent.
Removed system performance monitoring - now handled by Core Agent.
Focuses exclusively on risk validation and portfolio monitoring.
"""

import asyncio
import time
import json
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedRiskManagementAgent(BaseAgent):
    """Enhanced risk management agent - focused solely on risk validation."""
    
    def _initialize_agent_components(self):
        """Initialize risk management specific components."""
        # Initialize risk management components
        self.risk_validator = None
        self.portfolio_monitor = None
        self.circuit_breaker = None
        self.performance_tracker = None
        self.position_manager = None
        
        # Risk management state
        self.risk_state = {
            "active_circuit_breakers": {},
            "risk_limits": {},
            "portfolio_exposure": {},
            "last_risk_assessment": time.time()
        }
        
        # Risk statistics
        self.stats = {
            "total_requests_processed": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "circuit_breakers_triggered": 0,
            "risk_limit_violations": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Risk management specific startup logic."""
        try:
            # Initialize risk management components
            await self._initialize_risk_components()
            
            # Initialize circuit breakers
            await self._initialize_circuit_breakers()
            
            # Initialize risk limits
            await self._initialize_risk_limits()
            
            self.logger.info("✅ Risk Management Agent: Risk validation systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in risk management startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Risk management specific shutdown logic."""
        try:
            # Cleanup risk management resources
            await self._cleanup_risk_components()
            
            self.logger.info("✅ Risk Management Agent: Risk validation systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in risk management shutdown: {e}")
    
    # ============= BACKGROUND TASKS =============
    
    async def _portfolio_monitoring_loop(self):
        """Portfolio monitoring loop."""
        while self.is_running:
            try:
                # Monitor portfolio
                await self._monitor_portfolio()
                
                await asyncio.sleep(5.0)  # 5 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in portfolio monitoring loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _risk_validation_loop(self):
        """Risk validation loop."""
        while self.is_running:
            try:
                # Validate risk
                await self._validate_risk()
                
                await asyncio.sleep(1.0)  # 1 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in risk validation loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _risk_reporting_loop(self):
        """Risk reporting loop."""
        while self.is_running:
            try:
                # Report risk
                await self._report_risk()
                
                await asyncio.sleep(30.0)  # 30 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in risk reporting loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _monitor_portfolio(self):
        """Monitor portfolio."""
        try:
            # Placeholder for portfolio monitoring
            pass
        except Exception as e:
            self.logger.error(f"Error monitoring portfolio: {e}")
    
    async def _validate_risk(self):
        """Validate risk."""
        try:
            # Placeholder for risk validation
            pass
        except Exception as e:
            self.logger.error(f"Error validating risk: {e}")
    
    async def _report_risk(self):
        """Report risk."""
        try:
            # Placeholder for risk reporting
            pass
        except Exception as e:
            self.logger.error(f"Error reporting risk: {e}")

    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._risk_monitoring_loop, "Risk Monitoring", "fast"),
            (self._portfolio_monitoring_loop, "Portfolio Monitoring", "tactical"),
            (self._risk_validation_loop, "Risk Validation", "fast"),
            (self._risk_reporting_loop, "Risk Reporting", "strategic")
        ]
    
    # ============= RISK COMPONENT INITIALIZATION =============
    
    async def _initialize_risk_components(self):
        """Initialize risk management components."""
        try:
            # Initialize risk validator
            from .core.risk_validator import RiskValidator
            from .core.connection_manager import ConnectionManager
            connection_manager = ConnectionManager(self.config)
            self.risk_validator = RiskValidator(connection_manager, self.config)
            
            # Initialize portfolio monitor
            from .core.portfolio_monitor import PortfolioMonitor
            self.portfolio_monitor = PortfolioMonitor(self.config)
            
            # Initialize portfolio performance tracker (risk-focused only, not system performance)
            from .core.portfolio_performance_tracker import PortfolioPerformanceTracker
            self.performance_tracker = PortfolioPerformanceTracker(self.config)
            
            # Initialize position manager
            from .core.position_manager import PositionManager
            self.position_manager = PositionManager(connection_manager, self.config)
            
            self.logger.info("✅ Risk management components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing risk components: {e}")
            raise
    
    async def _initialize_circuit_breakers(self):
        """Initialize circuit breakers for risk management."""
        try:
            from .core.circuit_breaker import CircuitBreakerManager
            self.circuit_breaker = CircuitBreakerManager(self.config)
            
            # Set up default circuit breakers
            await self._setup_default_circuit_breakers()
            
            self.logger.info("✅ Circuit breakers initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing circuit breakers: {e}")
            raise
    
    async def _initialize_risk_limits(self):
        """Initialize risk limits for different asset classes."""
        try:
            from .core.dynamic_risk_limits import DynamicRiskLimits
            self.risk_limits = DynamicRiskLimits(self.config)
            
            # Set up default risk limits
            await self._setup_default_risk_limits()
            
            self.logger.info("✅ Risk limits initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing risk limits: {e}")
            raise
    
    async def _setup_default_circuit_breakers(self):
        """Set up default circuit breakers."""
        try:
            # Set up circuit breakers for different risk scenarios
            circuit_breakers_config = {
                "max_daily_loss": {"threshold": -0.05, "timeout": 86400},  # 5% daily loss
                "max_position_size": {"threshold": 0.1, "timeout": 3600},   # 10% position size
                "max_drawdown": {"threshold": -0.15, "timeout": 86400},     # 15% drawdown
                "max_correlation": {"threshold": 0.8, "timeout": 3600}      # 80% correlation
            }
            
            for name, config in circuit_breakers_config.items():
                await self.circuit_breaker.create_circuit_breaker(
                    name=name,
                    threshold=config["threshold"],
                    timeout=config["timeout"]
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error setting up circuit breakers: {e}")
    
    async def _setup_default_risk_limits(self):
        """Set up default risk limits."""
        try:
            # Set up risk limits for different asset classes
            risk_limits_config = {
                "forex": {"max_exposure": 0.2, "max_leverage": 50},
                "crypto": {"max_exposure": 0.15, "max_leverage": 20},
                "indices": {"max_exposure": 0.25, "max_leverage": 10},
                "stocks": {"max_exposure": 0.1, "max_leverage": 5}
            }
            
            for asset_class, limits in risk_limits_config.items():
                await self.risk_limits.set_risk_limits(
                    asset_class=asset_class,
                    max_exposure=limits["max_exposure"],
                    max_leverage=limits["max_leverage"]
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error setting up risk limits: {e}")
    
    # ============= RISK MONITORING LOOP =============
    
    async def _risk_monitoring_loop(self):
        """Main risk monitoring loop (30s intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Monitor portfolio risk
                await self._monitor_portfolio_risk()
                
                # Check risk limits
                await self._check_risk_limits()
                
                # Update risk state
                self._update_risk_state()
                
                # Record operation
                duration_ms = (time.time() - start_time) * 1000
                if hasattr(self, 'status_monitor') and self.status_monitor:
                    self.status_monitor.record_operation(duration_ms, True)
                
                await asyncio.sleep(30)  # 30s risk monitoring cycle
                
            except Exception as e:
                self.logger.error(f"Error in risk monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_portfolio_risk(self):
        """Monitor overall portfolio risk."""
        try:
            if self.portfolio_monitor:
                # Get portfolio risk metrics
                risk_metrics = await self.portfolio_monitor.get_portfolio_risk_metrics()
                
                # Update risk state
                self.risk_state["portfolio_exposure"] = risk_metrics.get("exposure", {})
                self.risk_state["last_risk_assessment"] = time.time()
                
                # Check for risk alerts
                await self._check_risk_alerts(risk_metrics)
                
        except Exception as e:
            self.logger.error(f"Error monitoring portfolio risk: {e}")
    
    async def _check_risk_limits(self):
        """Check risk limits for all asset classes."""
        try:
            if self.risk_limits:
                # Check all risk limits
                limit_violations = await self.risk_limits.check_all_limits()
                
                if limit_violations:
                    self.stats["risk_limit_violations"] += len(limit_violations)
                    await self._handle_risk_limit_violations(limit_violations)
                    
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {e}")
    
    async def _check_risk_alerts(self, risk_metrics: Dict[str, Any]):
        """Check for risk alerts and trigger circuit breakers if needed."""
        try:
            # Check daily loss
            daily_loss = risk_metrics.get("daily_loss", 0)
            if daily_loss < -0.05:  # 5% daily loss
                await self.circuit_breaker.trigger("max_daily_loss")
                self.stats["circuit_breakers_triggered"] += 1
            
            # Check position size
            max_position = risk_metrics.get("max_position_size", 0)
            if max_position > 0.1:  # 10% position size
                await self.circuit_breaker.trigger("max_position_size")
                self.stats["circuit_breakers_triggered"] += 1
            
            # Check drawdown
            drawdown = risk_metrics.get("drawdown", 0)
            if drawdown < -0.15:  # 15% drawdown
                await self.circuit_breaker.trigger("max_drawdown")
                self.stats["circuit_breakers_triggered"] += 1
                
        except Exception as e:
            self.logger.error(f"Error checking risk alerts: {e}")
    
    async def _handle_risk_limit_violations(self, violations: List[Dict[str, Any]]):
        """Handle risk limit violations."""
        try:
            for violation in violations:
                self.logger.warning(f"Risk limit violation: {violation}")
                
                # Trigger appropriate circuit breaker
                if violation.get("type") == "exposure":
                    await self.circuit_breaker.trigger("max_position_size")
                elif violation.get("type") == "leverage":
                    await self.circuit_breaker.trigger("max_leverage")
                    
        except Exception as e:
            self.logger.error(f"Error handling risk limit violations: {e}")
    
    # ============= PORTFOLIO EXPOSURE TRACKING =============
    
    async def _portfolio_exposure_tracking(self):
        """Track portfolio exposure (30s intervals)."""
        while self.is_running:
            try:
                if self.portfolio_monitor:
                    # Update portfolio exposure
                    exposure_data = await self.portfolio_monitor.get_current_exposure()
                    
                    # Update risk state
                    self.risk_state["portfolio_exposure"] = exposure_data
                    
                    # Publish exposure update
                    await self._publish_exposure_update(exposure_data)
                
                await asyncio.sleep(30)  # 30s exposure tracking cycle
                
            except Exception as e:
                self.logger.error(f"Error in portfolio exposure tracking: {e}")
                await asyncio.sleep(30)
    
    async def _publish_exposure_update(self, exposure_data: Dict[str, Any]):
        """Publish portfolio exposure update."""
        try:
            exposure_update = {
                "timestamp": time.time(),
                "exposure_data": exposure_data,
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("risk:exposure_updates", json.dumps(exposure_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing exposure update: {e}")
    
    # ============= CIRCUIT BREAKER MONITORING =============
    
    async def _circuit_breaker_monitoring(self):
        """Monitor circuit breakers (100ms intervals)."""
        while self.is_running:
            try:
                if self.circuit_breaker:
                    # Check circuit breaker status
                    circuit_status = await self.circuit_breaker.get_status()
                    
                    # Update risk state
                    self.risk_state["active_circuit_breakers"] = circuit_status
                    
                    # Check for circuit breaker resets
                    await self._check_circuit_breaker_resets(circuit_status)
                
                await asyncio.sleep(0.1)  # 100ms circuit breaker monitoring
                
            except Exception as e:
                self.logger.error(f"Error in circuit breaker monitoring: {e}")
                await asyncio.sleep(0.1)
    
    async def _check_circuit_breaker_resets(self, circuit_status: Dict[str, Any]):
        """Check if circuit breakers can be reset."""
        try:
            for circuit_name, status in circuit_status.items():
                if status.get("state") == "open" and status.get("can_reset", False):
                    await self.circuit_breaker.reset(circuit_name)
                    self.logger.info(f"Circuit breaker {circuit_name} reset")
                    
        except Exception as e:
            self.logger.error(f"Error checking circuit breaker resets: {e}")
    
    # ============= RISK VALIDATION METHODS =============
    
    async def validate_trade_request(self, trade_request: Dict[str, Any], 
                                   strategy_type: str = "general") -> Dict[str, Any]:
        """Validate trade request using risk management systems."""
        try:
            self.stats["total_requests_processed"] += 1
            
            # Check circuit breakers first
            if await self._check_circuit_breakers_for_trade(trade_request):
                return {
                    "validation_passed": False,
                    "reason": "circuit_breaker_active",
                    "risk_level": "critical",
                    "timestamp": time.time()
                }
            
            # Validate trade using risk validator
            if self.risk_validator:
                validation_result = await self.risk_validator.validate_trade(trade_request)
                
                if validation_result.get("valid", False):
                    self.stats["successful_validations"] += 1
                else:
                    self.stats["failed_validations"] += 1
                
                return validation_result
            
            # Fallback validation
            return await self._fallback_validation(trade_request)
            
        except Exception as e:
            self.stats["failed_validations"] += 1
            self.logger.error(f"Trade validation error: {e}")
            
            return {
                "validation_passed": False,
                "risk_level": "critical",
                "risk_score": 1.0,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _check_circuit_breakers_for_trade(self, trade_request: Dict[str, Any]) -> bool:
        """Check if any circuit breakers would prevent this trade."""
        try:
            if not self.circuit_breaker:
                return False
            
            # Check if any circuit breakers are active
            circuit_status = await self.circuit_breaker.get_status()
            
            for circuit_name, status in circuit_status.items():
                if status.get("state") == "open":
                    # Check if this trade would violate the circuit breaker
                    if await self._trade_violates_circuit_breaker(trade_request, circuit_name):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking circuit breakers: {e}")
            return False
    
    async def _trade_violates_circuit_breaker(self, trade_request: Dict[str, Any], circuit_name: str) -> bool:
        """Check if a trade would violate a specific circuit breaker."""
        try:
            if circuit_name == "max_daily_loss":
                # Check if trade would exceed daily loss limit
                return await self._would_exceed_daily_loss(trade_request)
            
            elif circuit_name == "max_position_size":
                # Check if trade would exceed position size limit
                return await self._would_exceed_position_size(trade_request)
            
            elif circuit_name == "max_drawdown":
                # Check if trade would exceed drawdown limit
                return await self._would_exceed_drawdown(trade_request)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking circuit breaker violation: {e}")
            return False
    
    async def _fallback_validation(self, trade_request: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback validation when risk validator is not available."""
        try:
            # Basic validation checks
            symbol = trade_request.get('symbol', '')
            volume = trade_request.get('volume', 0)
            
            if not symbol or volume <= 0:
                return {
                    "validation_passed": False,
                    "reason": "invalid_request_data",
                    "risk_level": "high",
                    "timestamp": time.time()
                }
            
            # Basic risk assessment
            risk_score = 0.3  # Default moderate risk
            
            return {
                "validation_passed": True,
                "risk_level": "moderate",
                "risk_score": risk_score,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in fallback validation: {e}")
            return {
                "validation_passed": False,
                "risk_level": "critical",
                "error": str(e),
                "timestamp": time.time()
            }
    
    # ============= UTILITY METHODS =============
    
    def _update_risk_state(self):
        """Update risk state with current information."""
        try:
            # Update risk state timestamp
            self.risk_state["last_risk_assessment"] = time.time()
            
        except Exception as e:
            self.logger.error(f"Error updating risk state: {e}")
    
    async def _cleanup_risk_components(self):
        """Cleanup risk management components."""
        try:
            # Cleanup circuit breakers
            if self.circuit_breaker:
                await self.circuit_breaker.cleanup()
            
            # Cleanup risk limits
            if hasattr(self, 'risk_limits') and self.risk_limits:
                await self.risk_limits.cleanup()
            
            self.logger.info("✅ Risk management components cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up risk components: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_risk_status(self) -> Dict[str, Any]:
        """Get current risk management status."""
        return {
            "risk_state": self.risk_state,
            "stats": self.stats,
            "circuit_breakers": self.risk_state.get("active_circuit_breakers", {}),
            "risk_limits": self.risk_state.get("risk_limits", {}),
            "last_update": time.time()
        }
    
    async def get_portfolio_exposure(self) -> Dict[str, Any]:
        """Get current portfolio exposure."""
        return {
            "exposure": self.risk_state.get("portfolio_exposure", {}),
            "last_assessment": self.risk_state.get("last_risk_assessment", 0),
            "timestamp": time.time()
        }
    
    async def reset_circuit_breaker(self, circuit_name: str) -> bool:
        """Reset a specific circuit breaker."""
        try:
            if self.circuit_breaker:
                return await self.circuit_breaker.reset(circuit_name)
            return False
            
        except Exception as e:
            self.logger.error(f"Error resetting circuit breaker: {e}")
            return False
