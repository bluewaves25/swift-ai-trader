#!/usr/bin/env python3
"""
HFT Trading Module
Ultra-fast trading operations for arbitrage and market making strategies
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...configs.strategy_configs import get_strategy_config
from ...risk_management.rate_limiting.rate_limiter import RateLimiter
from ...risk_management.signal_quality.signal_quality_assessor import SignalQualityAssessor
from ...execution.session_management.session_manager import SessionManager

class HFTTradingModule:
    """High-Frequency Trading module for ultra-fast operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = None
        
        # HFT Configuration
        self.max_signals_per_minute = config.get("max_signals_per_minute", 7)
        self.min_signal_interval = config.get("min_signal_interval", 8.5)
        self.daily_signal_limit = config.get("daily_signal_limit", 10000)
        
        # Initialize sub-modules
        self.rate_limiter = RateLimiter(config)
        self.signal_quality_assessor = SignalQualityAssessor(config)
        self.session_manager = SessionManager(config)
        
        # HFT state tracking
        self.hft_state = {
            "active_hft_trades": {},
            "profit_locking": {
                "big_trades_fund": 0.0,
                "weekly_target_fund": 0.0,
                "compound_fund": 0.0
            },
            "daily_pnl": 0.0,
            "trade_count": 0
        }
    
    def set_logger(self, logger):
        """Set logger for this module."""
        self.logger = logger
        self.rate_limiter.set_logger(logger)
        self.signal_quality_assessor.set_logger(logger)
        self.session_manager.set_logger(logger)
    
    async def process_hft_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Process HFT trading signal with ultra-fast execution."""
        try:
            start_time = time.time()
            
            # 1. Rate limiting check
            if not self._check_hft_rate_limits(signal):
                return {"status": "REJECTED", "reason": "Rate limited"}
            
            # 2. Signal quality assessment
            quality_result = self._assess_hft_signal_quality(signal)
            if not quality_result["is_acceptable"]:
                return {"status": "REJECTED", "reason": "Poor quality", "details": quality_result}
            
            # 3. Session optimization
            session_optimization = self._optimize_for_session(signal)
            
            # 4. Execute HFT trade
            trade_result = await self._execute_hft_trade(signal, session_optimization)
            
            # 5. Update rate limits
            self._update_hft_rate_limits(signal)
            
            # 6. Update profit locking
            self._update_profit_locking(trade_result)
            
            execution_time = time.time() - start_time
            
            return {
                "status": "EXECUTED",
                "execution_time_ms": round(execution_time * 1000, 2),
                "trade_result": trade_result,
                "quality_score": quality_result["quality_score"],
                "session_optimization": session_optimization
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in HFT signal processing: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def _check_hft_rate_limits(self, signal: Dict[str, Any]) -> bool:
        """Check HFT-specific rate limits."""
        symbol = signal.get("symbol", "")
        strategy_type = signal.get("strategy_type", "arbitrage")
        
        # Check if we can generate a new HFT signal
        can_generate = self.rate_limiter.check_rate_limits(symbol, strategy_type)
        
        if not can_generate and self.logger:
            self.logger.warning(f"❌ HFT rate limited for {symbol} ({strategy_type})")
        
        return can_generate
    
    def _assess_hft_signal_quality(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Assess HFT signal quality with strict criteria."""
        # Set current stats for quality assessment
        self.signal_quality_assessor.set_stats({
            "daily_pnl": self.hft_state["daily_pnl"]
        })
        
        # Assess signal quality
        quality_result = self.signal_quality_assessor.assess_signal_quality(signal)
        
        # Additional HFT-specific checks
        if quality_result["is_acceptable"]:
            hft_quality = self._additional_hft_quality_checks(signal)
            quality_result["hft_specific"] = hft_quality
            
            # Reject if HFT-specific checks fail
            if not hft_quality["passes"]:
                quality_result["is_acceptable"] = False
                quality_result["rejection_reasons"].extend(hft_quality["reasons"])
        
        return quality_result
    
    def _additional_hft_quality_checks(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Additional quality checks specific to HFT strategies."""
        strategy_type = signal.get("strategy_type", "")
        strategy_config = get_strategy_config(strategy_type)
        
        checks = {
            "passes": True,
            "reasons": [],
            "score": 0
        }
        
        # Check if strategy supports HFT
        if strategy_type not in ["arbitrage", "market_making"]:
            checks["passes"] = False
            checks["reasons"].append("Strategy type not suitable for HFT")
            return checks
        
        # Check confidence threshold
        confidence = signal.get("confidence", 0)
        min_confidence = strategy_config.get("min_confidence", 0.65)
        if confidence < min_confidence:
            checks["passes"] = False
            checks["reasons"].append(f"Confidence {confidence:.2f} below HFT threshold {min_confidence}")
        
        # Check volatility threshold
        volatility = signal.get("sltp_metadata", {}).get("volatility", 0)
        max_volatility = strategy_config.get("volatility_threshold", 0.02)
        if volatility > max_volatility:
            checks["passes"] = False
            checks["reasons"].append(f"Volatility {volatility:.3f} above HFT threshold {max_volatility}")
        
        # Check risk-reward ratio
        risk_reward = signal.get("sltp_metadata", {}).get("risk_reward_ratio", 0)
        min_rr = strategy_config.get("risk_reward_ratio", 1.2)
        if risk_reward < min_rr:
            checks["passes"] = False
            checks["reasons"].append(f"R:R ratio {risk_reward:.2f} below HFT minimum {min_rr}")
        
        if checks["passes"]:
            checks["score"] = 100
        
        return checks
    
    def _optimize_for_session(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize HFT strategy for current trading session."""
        strategy_type = signal.get("strategy_type", "")
        
        # Get session optimization parameters
        optimization_params = self.session_manager.get_session_optimization_parameters(strategy_type)
        
        # Check if strategy is optimal for current session
        optimality = self.session_manager.is_strategy_optimal_for_session(strategy_type)
        
        return {
            "session": optimization_params.get("session", "unknown"),
            "is_optimal": optimality.get("is_optimal", False),
            "session_score": optimality.get("session_score", 0),
            "execution_speed": optimization_params.get("execution_speed", "STANDARD"),
            "slippage_tolerance": optimization_params.get("slippage_tolerance", 0.001),
            "max_hold_time": optimization_params.get("max_hold_time", 300)
        }
    
    async def _execute_hft_trade(self, signal: Dict[str, Any], session_optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HFT trade with session optimization."""
        try:
            # Simulate ultra-fast trade execution
            await asyncio.sleep(0.001)  # 1ms execution time
            
            # Calculate trade parameters
            trade_params = self._calculate_hft_trade_params(signal, session_optimization)
            
            # Execute trade (simulated)
            trade_result = {
                "trade_id": f"HFT_{int(time.time() * 1000)}",
                "symbol": signal.get("symbol", ""),
                "action": signal.get("action", ""),
                "entry_price": trade_params["entry_price"],
                "stop_loss": trade_params["stop_loss"],
                "take_profit": trade_params["take_profit"],
                "volume": trade_params["volume"],
                "execution_time": trade_params["execution_time"],
                "session_optimization": session_optimization
            }
            
            # Update HFT state
            self.hft_state["trade_count"] += 1
            self.hft_state["active_hft_trades"][trade_result["trade_id"]] = trade_result
            
            if self.logger:
                self.logger.info(f"✅ HFT trade executed: {trade_result['trade_id']} for {signal.get('symbol', '')}")
            
            return trade_result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error executing HFT trade: {e}")
            raise
    
    def _calculate_hft_trade_params(self, signal: Dict[str, Any], session_optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate HFT trade parameters."""
        strategy_type = signal.get("strategy_type", "")
        strategy_config = get_strategy_config(strategy_type)
        
        # Get current market data (simulated)
        entry_price = 100.0  # This would come from real market data
        bid = entry_price * 0.9995
        ask = entry_price * 1.0005
        
        # Calculate SL/TP based on strategy
        from ..sltp_calculators import StrategySLTPCalculator
        sltp_calculator = StrategySLTPCalculator()
        
        sltp_result = sltp_calculator.calculate_sltp(
            strategy_type=strategy_type,
            action=signal.get("action", "BUY"),
            entry_price=entry_price,
            bid=bid,
            ask=ask,
            volatility=signal.get("sltp_metadata", {}).get("volatility", 0.02)
        )
        
        # Calculate volume based on risk management
        volume = self._calculate_hft_volume(signal, strategy_config)
        
        # Calculate execution time based on session optimization
        execution_time = self._calculate_execution_time(session_optimization)
        
        return {
            "entry_price": entry_price,
            "stop_loss": sltp_result["stop_loss"],
            "take_profit": sltp_result["take_profit"],
            "volume": volume,
            "execution_time": execution_time
        }
    
    def _calculate_hft_volume(self, signal: Dict[str, Any], strategy_config: Dict[str, Any]) -> float:
        """Calculate HFT trade volume based on risk management."""
        # Base volume calculation (simplified)
        base_volume = 0.01  # 0.01 lot
        
        # Adjust based on confidence
        confidence = signal.get("confidence", 0.65)
        confidence_multiplier = min(confidence * 1.5, 2.0)
        
        # Adjust based on risk-reward ratio
        risk_reward = signal.get("sltp_metadata", {}).get("risk_reward_ratio", 1.2)
        rr_multiplier = min(risk_reward / 1.2, 2.0)
        
        final_volume = base_volume * confidence_multiplier * rr_multiplier
        
        return round(final_volume, 4)
    
    def _calculate_execution_time(self, session_optimization: Dict[str, Any]) -> float:
        """Calculate execution time based on session optimization."""
        base_time = 0.001  # 1ms base
        
        if session_optimization.get("execution_speed") == "ULTRA_FAST":
            return base_time * 0.5  # 0.5ms
        elif session_optimization.get("execution_speed") == "FAST":
            return base_time * 1.0  # 1ms
        else:
            return base_time * 2.0  # 2ms
    
    def _update_hft_rate_limits(self, signal: Dict[str, Any]):
        """Update HFT rate limiting tracking."""
        symbol = signal.get("symbol", "")
        strategy_type = signal.get("strategy_type", "")
        
        self.rate_limiter.update_rate_limits(symbol, strategy_type)
    
    def _update_profit_locking(self, trade_result: Dict[str, Any]):
        """Update profit locking mechanism."""
        # This would be updated based on actual trade P&L
        # For now, simulate profit generation
        simulated_profit = 0.001  # 0.1% profit
        
        # Allocate profits according to strategy
        self.hft_state["profit_locking"]["big_trades_fund"] += simulated_profit * 0.5
        self.hft_state["profit_locking"]["weekly_target_fund"] += simulated_profit * 0.3
        self.hft_state["profit_locking"]["compound_fund"] += simulated_profit * 0.2
    
    def get_hft_status(self) -> Dict[str, Any]:
        """Get current HFT module status."""
        return {
            "module": "HFT Trading Module",
            "is_active": True,
            "hft_state": self.hft_state,
            "rate_limiting": self.rate_limiter.get_rate_limit_status(),
            "session_info": self.session_manager.get_current_session_info()
        }
    
    def get_profit_locking_status(self) -> Dict[str, Any]:
        """Get profit locking mechanism status."""
        return {
            "big_trades_fund": self.hft_state["profit_locking"]["big_trades_fund"],
            "weekly_target_fund": self.hft_state["profit_locking"]["weekly_target_fund"],
            "compound_fund": self.hft_state["profit_locking"]["compound_fund"],
            "total_profit_locked": sum(self.hft_state["profit_locking"].values())
        }
