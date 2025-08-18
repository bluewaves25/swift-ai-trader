#!/usr/bin/env python3
"""
Signal Processing Module
Handles trading signal generation, validation, and processing
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...configs.strategy_configs import get_strategy_config
from ...risk_management.signal_quality.signal_quality_assessor import SignalQualityAssessor
from ...risk_management.rate_limiting.rate_limiter import RateLimiter
from ...execution.session_management.session_manager import SessionManager

class TradingSignalProcessor:
    """Process and validate trading signals."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = None
        
        # Initialize sub-modules
        self.signal_quality_assessor = SignalQualityAssessor(config)
        self.rate_limiter = RateLimiter(config)
        self.session_manager = SessionManager(config)
        
        # Signal processing state
        self.signal_state = {
            "processed_signals": [],
            "rejected_signals": [],
            "signal_correlation_cache": {},
            "last_signal_time": None
        }
    
    def set_logger(self, logger):
        """Set logger for this module."""
        self.logger = logger
        self.signal_quality_assessor.set_logger(logger)
        self.rate_limiter.set_logger(logger)
        self.session_manager.set_logger(logger)
    
    async def process_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Process a trading signal through the complete pipeline."""
        try:
            start_time = time.time()
            
            # 1. Basic signal validation
            validation_result = self._validate_basic_signal(signal)
            if not validation_result["is_valid"]:
                return self._create_rejection_response(signal, validation_result["reasons"])
            
            # 2. Rate limiting check
            if not self._check_signal_rate_limits(signal):
                return self._create_rejection_response(signal, ["Rate limited"])
            
            # 3. Signal quality assessment
            quality_result = self._assess_signal_quality(signal)
            if not quality_result["is_acceptable"]:
                return self._create_rejection_response(signal, quality_result["rejection_reasons"])
            
            # 4. Signal correlation check
            correlation_result = self._check_signal_correlation(signal)
            if correlation_result["has_conflicts"] and not correlation_result["is_legitimate_hedging"]:
                return self._create_rejection_response(signal, ["Signal correlation conflict"])
            
            # 5. Session optimization
            session_optimization = self._optimize_signal_for_session(signal)
            
            # 6. Final signal processing
            processed_signal = self._create_processed_signal(signal, quality_result, session_optimization)
            
            # 7. Update state and rate limits
            self._update_signal_processing_state(processed_signal)
            self._update_rate_limits(signal)
            
            processing_time = time.time() - start_time
            
            return {
                "status": "PROCESSED",
                "processing_time_ms": round(processing_time * 1000, 2),
                "signal_id": processed_signal["signal_id"],
                "quality_score": quality_result["quality_score"],
                "session_optimization": session_optimization,
                "processed_signal": processed_signal
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing signal: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def _validate_basic_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Validate basic signal structure and required fields."""
        required_fields = ["symbol", "action", "strategy_type", "confidence"]
        
        validation_result = {
            "is_valid": True,
            "reasons": []
        }
        
        # Check required fields
        for field in required_fields:
            if field not in signal or signal[field] is None:
                validation_result["is_valid"] = False
                validation_result["reasons"].append(f"Missing required field: {field}")
        
        # Validate action
        if "action" in signal and signal["action"] not in ["BUY", "SELL"]:
            validation_result["is_valid"] = False
            validation_result["reasons"].append("Invalid action: must be BUY or SELL")
        
        # Validate confidence range
        if "confidence" in signal:
            confidence = signal["confidence"]
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                validation_result["is_valid"] = False
                validation_result["reasons"].append("Invalid confidence: must be between 0 and 1")
        
        # Validate strategy type
        if "strategy_type" in signal:
            valid_strategies = ["arbitrage", "market_making", "trend_following", "htf", "news_driven", "statistical_arbitrage"]
            if signal["strategy_type"] not in valid_strategies:
                validation_result["is_valid"] = False
                validation_result["reasons"].append(f"Invalid strategy type: {signal['strategy_type']}")
        
        return validation_result
    
    def _check_signal_rate_limits(self, signal: Dict[str, Any]) -> bool:
        """Check if signal generation is allowed by rate limits."""
        symbol = signal.get("symbol", "")
        strategy_type = signal.get("strategy_type", "")
        
        can_generate = self.rate_limiter.check_rate_limits(symbol, strategy_type)
        
        if not can_generate and self.logger:
            self.logger.warning(f"❌ Signal rate limited for {symbol} ({strategy_type})")
        
        return can_generate
    
    def _assess_signal_quality(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Assess signal quality using the quality assessor."""
        # Set current stats for quality assessment
        self.signal_quality_assessor.set_stats({
            "daily_pnl": 0.0  # This would come from actual trading stats
        })
        
        # Assess signal quality
        quality_result = self.signal_quality_assessor.assess_signal_quality(signal)
        
        return quality_result
    
    def _check_signal_correlation(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Check for signal correlation conflicts."""
        # Get existing signals for correlation check
        existing_signals = self.signal_state["processed_signals"]
        
        # Assess correlation
        correlation_result = self.signal_quality_assessor.assess_signal_correlation(signal, existing_signals)
        
        return correlation_result
    
    def _optimize_signal_for_session(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize signal for current trading session."""
        strategy_type = signal.get("strategy_type", "")
        
        # Get session optimization parameters
        optimization_params = self.session_manager.get_session_optimization_parameters(strategy_type)
        
        # Check if strategy is optimal for current session
        optimality = self.session_manager.is_strategy_optimal_for_session(strategy_type)
        
        return {
            "session": optimization_params.get("session", "unknown"),
            "is_optimal": optimality.get("is_optimal", False),
            "session_score": optimality.get("session_score", 0),
            "optimization_params": optimization_params
        }
    
    def _create_processed_signal(self, signal: Dict[str, Any], quality_result: Dict[str, Any], session_optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Create the final processed signal."""
        # Generate unique signal ID
        signal_id = f"SIG_{int(time.time() * 1000)}_{signal.get('symbol', 'UNKNOWN')}"
        
        # Create processed signal
        processed_signal = {
            "signal_id": signal_id,
            "original_signal": signal,
            "quality_assessment": quality_result,
            "session_optimization": session_optimization,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "status": "PROCESSED"
        }
        
        return processed_signal
    
    def _update_signal_processing_state(self, processed_signal: Dict[str, Any]):
        """Update signal processing state."""
        # Add to processed signals
        self.signal_state["processed_signals"].append(processed_signal)
        
        # Update last signal time
        self.signal_state["last_signal_time"] = time.time()
        
        # Keep only last 1000 processed signals
        if len(self.signal_state["processed_signals"]) > 1000:
            self.signal_state["processed_signals"] = self.signal_state["processed_signals"][-1000:]
    
    def _update_rate_limits(self, signal: Dict[str, Any]):
        """Update rate limiting tracking."""
        symbol = signal.get("symbol", "")
        strategy_type = signal.get("strategy_type", "")
        
        self.rate_limiter.update_rate_limits(symbol, strategy_type)
    
    def _create_rejection_response(self, signal: Dict[str, Any], reasons: List[str]) -> Dict[str, Any]:
        """Create a rejection response for invalid signals."""
        # Add to rejected signals
        rejected_signal = {
            "signal": signal,
            "rejection_reasons": reasons,
            "rejection_timestamp": datetime.utcnow().isoformat()
        }
        self.signal_state["rejected_signals"].append(rejected_signal)
        
        # Keep only last 1000 rejected signals
        if len(self.signal_state["rejected_signals"]) > 1000:
            self.signal_state["rejected_signals"] = self.signal_state["rejected_signals"][-1000:]
        
        return {
            "status": "REJECTED",
            "reasons": reasons,
            "signal_id": None
        }
    
    def get_signal_processing_status(self) -> Dict[str, Any]:
        """Get current signal processing status."""
        return {
            "module": "Signal Processor",
            "is_active": True,
            "signal_state": {
                "processed_count": len(self.signal_state["processed_signals"]),
                "rejected_count": len(self.signal_state["rejected_signals"]),
                "last_signal_time": self.signal_state["last_signal_time"]
            },
            "rate_limiting": self.rate_limiter.get_rate_limit_status(),
            "session_info": self.session_manager.get_current_session_info()
        }
    
    def get_signal_statistics(self) -> Dict[str, Any]:
        """Get signal processing statistics."""
        processed_signals = self.signal_state["processed_signals"]
        rejected_signals = self.signal_state["rejected_signals"]
        
        # Calculate statistics
        total_signals = len(processed_signals) + len(rejected_signals)
        acceptance_rate = len(processed_signals) / total_signals if total_signals > 0 else 0
        
        # Strategy distribution
        strategy_distribution = {}
        for signal in processed_signals:
            strategy = signal["original_signal"].get("strategy_type", "unknown")
            strategy_distribution[strategy] = strategy_distribution.get(strategy, 0) + 1
        
        # Quality score distribution
        quality_scores = [signal["quality_assessment"].get("quality_score", 0) for signal in processed_signals]
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "total_signals": total_signals,
            "processed_signals": len(processed_signals),
            "rejected_signals": len(rejected_signals),
            "acceptance_rate": round(acceptance_rate * 100, 2),
            "strategy_distribution": strategy_distribution,
            "average_quality_score": round(avg_quality_score, 2),
            "quality_score_range": {
                "min": min(quality_scores) if quality_scores else 0,
                "max": max(quality_scores) if quality_scores else 0
            }
        }
