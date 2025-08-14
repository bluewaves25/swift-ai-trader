from typing import Dict, Any, List
from ..logs.strategy_engine_logger import StrategyEngineLogger
import time

class TradingSignalProcessor:
    """Trading signal processor - consolidated from Core Agent."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = StrategyEngineLogger("trading_signal_processor")
        
        # Trading signal validation rules
        self.required_fields = {
            "signal_id": str, 
            "strategy": str, 
            "params": dict, 
            "timestamp": float
        }
        
        self.valid_strategies = {
            "momentum", "mean_reversion", "arbitrage", "breakout",
            "pairs_trading", "market_making", "sentiment", "regime_shift"
        }
        
        # Signal processing statistics
        self.stats = {
            "total_signals_processed": 0,
            "valid_signals": 0,
            "invalid_signals": 0,
            "strategy_distribution": {},
            "start_time": time.time()
        }
        
    async def initialize(self):
        """Initialize the trading signal processor."""
        try:
            self.logger.log_action("initialize", {"status": "started"})
            return True
        except Exception as e:
            self.logger.log_action("initialize_error", {"error": str(e)})
            return False
            
    async def cleanup(self):
        """Clean up the trading signal processor."""
        try:
            self.logger.log_action("cleanup", {"status": "started"})
            # Reset statistics
            self.stats = {
                "total_signals_processed": 0,
                "valid_signals": 0,
                "invalid_signals": 0,
                "strategy_distribution": {},
                "start_time": time.time()
            }
            self.logger.log_action("cleanup", {"status": "completed"})
            return True
        except Exception as e:
            self.logger.log_action("cleanup_error", {"error": str(e)})
            return False

    def validate_trading_signal(self, signal: Dict[str, Any]) -> bool:
        """Validate trading signal format and content."""
        try:
            # Check required fields and types
            for field, expected_type in self.required_fields.items():
                if field not in signal or not isinstance(signal[field], expected_type):
                    self.logger.log_action("validate_trading_signal", {
                        "result": "failed", 
                        "reason": f"Invalid {field}"
                    })
                    return False
            
            # Check strategy validity
            if signal["strategy"] not in self.valid_strategies:
                self.logger.log_action("validate_trading_signal", {
                    "result": "failed", 
                    "reason": f"Invalid strategy: {signal['strategy']}"
                })
                return False
            
            # Check params content
            params = signal["params"]
            if not all(key in params for key in ["amount", "base", "quote"]):
                self.logger.log_action("validate_trading_signal", {
                    "result": "failed", 
                    "reason": "Missing required params"
                })
                return False
            
            self.logger.log_action("validate_trading_signal", {"result": "passed"})
            return True
            
        except Exception as e:
            self.logger.log_action("validate_trading_signal", {
                "result": "failed", 
                "reason": str(e)
            })
            return False

    def process_trading_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Process a trading signal through validation and enrichment."""
        try:
            self.stats["total_signals_processed"] += 1
            
            # Validate signal
            if not self.validate_trading_signal(signal):
                self.stats["invalid_signals"] += 1
                return {
                    "valid": False,
                    "reason": "Signal validation failed",
                    "signal_id": signal.get("signal_id")
                }
            
            # Enrich signal with additional data
            enriched_signal = self._enrich_signal(signal)
            
            # Update strategy distribution
            strategy = signal["strategy"]
            self.stats["strategy_distribution"][strategy] = (
                self.stats["strategy_distribution"].get(strategy, 0) + 1
            )
            
            self.stats["valid_signals"] += 1
            
            return {
                "valid": True,
                "enriched_signal": enriched_signal,
                "signal_id": signal.get("signal_id")
            }
            
        except Exception as e:
            self.logger.log_action("process_trading_signal_error", {"error": str(e)})
            return {
                "valid": False,
                "reason": f"Processing error: {str(e)}",
                "signal_id": signal.get("signal_id")
            }

    def _enrich_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich trading signal with additional metadata."""
        try:
            enriched = signal.copy()
            
            # Add processing metadata
            enriched["processed_at"] = time.time()
            enriched["processor_version"] = "1.0.0"
            enriched["validation_status"] = "passed"
            
            # Add strategy metadata
            strategy = signal["strategy"]
            enriched["strategy_category"] = self._get_strategy_category(strategy)
            enriched["risk_level"] = self._assess_risk_level(signal)
            
            # Add market context (placeholder for real implementation)
            enriched["market_context"] = {
                "volatility": "medium",  # Placeholder
                "trend": "neutral",      # Placeholder
                "liquidity": "high"      # Placeholder
            }
            
            return enriched
            
        except Exception as e:
            self.logger.log_action("enrich_signal_error", {"error": str(e)})
            return signal

    def _get_strategy_category(self, strategy: str) -> str:
        """Get strategy category based on strategy name."""
        if strategy in ["momentum", "breakout"]:
            return "trend_following"
        elif strategy in ["mean_reversion", "pairs_trading"]:
            return "statistical_arbitrage"
        elif strategy in ["arbitrage"]:
            return "arbitrage_based"
        elif strategy in ["market_making"]:
            return "market_making"
        elif strategy in ["sentiment"]:
            return "news_driven"
        elif strategy in ["regime_shift"]:
            return "high_time_frame"
        else:
            return "unknown"

    def _assess_risk_level(self, signal: Dict[str, Any]) -> str:
        """Assess risk level of trading signal."""
        try:
            params = signal.get("params", {})
            amount = params.get("amount", 0)
            
            # Simple risk assessment based on position size
            if amount <= 0.01:
                return "low"
            elif amount <= 0.05:
                return "medium"
            else:
                return "high"
                
        except Exception:
            return "unknown"

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get signal processing statistics."""
        try:
            stats = self.stats.copy()
            
            # Calculate success rate
            if stats["total_signals_processed"] > 0:
                stats["success_rate"] = (
                    stats["valid_signals"] / stats["total_signals_processed"]
                )
            else:
                stats["success_rate"] = 0.0
            
            # Calculate uptime
            stats["uptime_seconds"] = time.time() - stats["start_time"]
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}

    def reset_stats(self):
        """Reset signal processing statistics."""
        try:
            self.stats = {
                "total_signals_processed": 0,
                "valid_signals": 0,
                "invalid_signals": 0,
                "strategy_distribution": {},
                "start_time": time.time()
            }
            
            self.logger.log_action("reset_signal_processing_stats", {})
            
        except Exception as e:
            self.logger.log_action("reset_stats_error", {"error": str(e)})
