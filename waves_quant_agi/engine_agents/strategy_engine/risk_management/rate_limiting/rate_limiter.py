#!/usr/bin/env python3
"""
Rate Limiting System
Controls signal generation frequency based on strategy type and overall limits
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ...configs.strategy_configs import get_strategy_config

class RateLimiter:
    """Manage rate limiting for different strategy types."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = None
        
        # Global rate limiting
        self.max_signals_per_minute = config.get("max_signals_per_minute", 7)
        self.min_signal_interval = config.get("min_signal_interval", 8.5)
        self.daily_signal_limit = config.get("daily_signal_limit", 10000)
        
        # Tracking
        self.signal_timestamps = []
        self.symbol_last_signal = {}
        self.strategy_daily_counts = {}
        self.daily_signal_count = 0
        self.last_reset_date = datetime.now().date()
        
        # Strategy-specific rate limiting
        self.strategy_rate_limits = {}
        self._initialize_strategy_limits()
    
    def set_logger(self, logger):
        """Set logger for this rate limiter."""
        self.logger = logger
    
    def _initialize_strategy_limits(self):
        """Initialize rate limits for each strategy type."""
        from ...configs.strategy_configs import get_all_strategy_configs
        
        all_configs = get_all_strategy_configs()
        
        for strategy_type, config in all_configs.items():
            self.strategy_rate_limits[strategy_type] = {
                "max_daily_trades": config.get("max_daily_trades", 100),
                "max_trades_per_minute": config.get("max_trades_per_minute", None),
                "min_signal_interval": config.get("min_signal_interval_seconds", 0),
                "daily_count": 0,
                "last_signal_time": 0
            }
    
    def check_rate_limits(self, symbol: str, strategy_name: str) -> bool:
        """Check if we can generate a new signal based on rate limits."""
        try:
            current_time = time.time()
            
            # Reset daily counters if it's a new day
            self._reset_daily_counters_if_needed()
            
            # Check global daily limit
            if self.daily_signal_count >= self.daily_signal_limit:
                if self.logger:
                    self.logger.warning(f"❌ Daily signal limit reached: {self.daily_signal_count}/{self.daily_signal_limit}")
                return False
            
            # Check global per-minute limit
            current_minute = int(current_time / 60)
            minute_signals = [ts for ts in self.signal_timestamps if int(ts / 60) == current_minute]
            
            if len(minute_signals) >= self.max_signals_per_minute:
                if self.logger:
                    self.logger.warning(f"❌ Per-minute signal limit reached: {len(minute_signals)}/{self.max_signals_per_minute}")
                return False
            
            # Check global minimum interval
            if self.signal_timestamps and (current_time - self.signal_timestamps[-1]) < self.min_signal_interval:
                if self.logger:
                    self.logger.warning(f"❌ Signal interval too short: {current_time - self.signal_timestamps[-1]:.1f}s < {self.min_signal_interval}s")
                return False
            
            # Check symbol-specific rate limiting
            if not self._check_symbol_rate_limits(symbol, current_time):
                return False
            
            # Check strategy-specific rate limiting
            if not self._check_strategy_rate_limits(strategy_name, current_time):
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking rate limits: {e}")
            return False
    
    def _check_symbol_rate_limits(self, symbol: str, current_time: float) -> bool:
        """Check symbol-specific rate limits."""
        if symbol in self.symbol_last_signal:
            last_signal_time = self.symbol_last_signal[symbol]
            time_since_last = current_time - last_signal_time
            
            # Minimum 8.5 seconds between signals for same symbol
            if time_since_last < 8.5:
                if self.logger:
                    self.logger.warning(f"❌ Symbol {symbol} rate limited: {time_since_last:.1f}s < 8.5s")
                return False
        
        return True
    
    def _check_strategy_rate_limits(self, strategy_name: str, current_time: float) -> bool:
        """Check strategy-specific rate limits."""
        # Extract strategy type from strategy name
        strategy_type = self._extract_strategy_type(strategy_name)
        
        if strategy_type in self.strategy_rate_limits:
            limits = self.strategy_rate_limits[strategy_type]
            
            # Check daily limit
            if limits["daily_count"] >= limits["max_daily_trades"]:
                if self.logger:
                    self.logger.warning(f"❌ Strategy {strategy_type} daily limit reached: {limits['daily_count']}/{limits['max_daily_trades']}")
                return False
            
            # Check per-minute limit (if applicable)
            if limits["max_trades_per_minute"]:
                current_minute = int(current_time / 60)
                minute_signals = [ts for ts in self.signal_timestamps if int(ts / 60) == current_minute]
                
                if len(minute_signals) >= limits["max_trades_per_minute"]:
                    if self.logger:
                        self.logger.warning(f"❌ Strategy {strategy_type} per-minute limit reached")
                    return False
            
            # Check minimum interval (if applicable)
            if limits["min_signal_interval"] > 0:
                if limits["last_signal_time"] > 0:
                    time_since_last = current_time - limits["last_signal_time"]
                    if time_since_last < limits["min_signal_interval"]:
                        if self.logger:
                            self.logger.warning(f"❌ Strategy {strategy_type} interval too short: {time_since_last:.1f}s < {limits['min_signal_interval']}s")
                        return False
        
        return True
    
    def _extract_strategy_type(self, strategy_name: str) -> str:
        """Extract strategy type from strategy name."""
        strategy_name_lower = strategy_name.lower()
        
        if "arbitrage" in strategy_name_lower:
            return "arbitrage"
        elif "market_making" in strategy_name_lower or "market" in strategy_name_lower:
            return "market_making"
        elif "trend" in strategy_name_lower or "moving_average" in strategy_name_lower:
            return "trend_following"
        elif "htf" in strategy_name_lower or "high_time" in strategy_name_lower:
            return "htf"
        elif "news" in strategy_name_lower:
            return "news_driven"
        elif "statistical" in strategy_name_lower or "mean_reversion" in strategy_name_lower:
            return "statistical_arbitrage"
        else:
            return "trend_following"  # Default
    
    def update_rate_limits(self, symbol: str, strategy_name: str):
        """Update rate limiting tracking after signal generation."""
        try:
            current_time = time.time()
            
            # Update global tracking
            self.signal_timestamps.append(current_time)
            self.daily_signal_count += 1
            
            # Update symbol tracking
            self.symbol_last_signal[symbol] = current_time
            
            # Update strategy tracking
            strategy_type = self._extract_strategy_type(strategy_name)
            if strategy_type in self.strategy_rate_limits:
                self.strategy_rate_limits[strategy_type]["daily_count"] += 1
                self.strategy_rate_limits[strategy_type]["last_signal_time"] = current_time
            
            # Clean up old timestamps (keep only last 24 hours)
            self._cleanup_old_timestamps()
            
            if self.logger:
                self.logger.info(f"✅ Rate limits updated for {symbol} ({strategy_name})")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error updating rate limits: {e}")
    
    def _reset_daily_counters_if_needed(self):
        """Reset daily counters if it's a new day."""
        current_date = datetime.now().date()
        
        if current_date != self.last_reset_date:
            # Reset global daily counter
            self.daily_signal_count = 0
            self.last_reset_date = current_date
            
            # Reset strategy daily counters
            for strategy_type in self.strategy_rate_limits:
                self.strategy_rate_limits[strategy_type]["daily_count"] = 0
            
            if self.logger:
                self.logger.info(f"🔄 Daily counters reset for {current_date}")
    
    def _cleanup_old_timestamps(self):
        """Remove timestamps older than 24 hours."""
        current_time = time.time()
        cutoff_time = current_time - (24 * 60 * 60)  # 24 hours ago
        
        # Remove old timestamps
        self.signal_timestamps = [ts for ts in self.signal_timestamps if ts > cutoff_time]
        
        # Remove old symbol timestamps
        old_symbols = [symbol for symbol, timestamp in self.symbol_last_signal.items() if timestamp < cutoff_time]
        for symbol in old_symbols:
            del self.symbol_last_signal[symbol]
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        current_time = time.time()
        current_minute = int(current_time / 60)
        minute_signals = [ts for ts in self.signal_timestamps if int(ts / 60) == current_minute]
        
        return {
            "global_limits": {
                "daily_signal_count": self.daily_signal_count,
                "daily_signal_limit": self.daily_signal_limit,
                "signals_this_minute": len(minute_signals),
                "max_signals_per_minute": self.max_signals_per_minute,
                "min_signal_interval": self.min_signal_interval
            },
            "strategy_limits": self.strategy_rate_limits,
            "symbol_tracking": {
                symbol: {
                    "last_signal": datetime.fromtimestamp(timestamp).strftime("%H:%M:%S"),
                    "time_since_last": f"{current_time - timestamp:.1f}s"
                }
                for symbol, timestamp in self.symbol_last_signal.items()
            }
        }
    
    def can_generate_signal(self, symbol: str, strategy_name: str) -> Dict[str, Any]:
        """Check if signal can be generated and return detailed status."""
        can_generate = self.check_rate_limits(symbol, strategy_name)
        
        status = {
            "can_generate": can_generate,
            "symbol": symbol,
            "strategy": strategy_name,
            "timestamp": time.time(),
            "rate_limit_status": self.get_rate_limit_status()
        }
        
        if not can_generate:
            status["blocking_reason"] = self._get_blocking_reason(symbol, strategy_name)
        
        return status
    
    def _get_blocking_reason(self, symbol: str, strategy_name: str) -> str:
        """Get the reason why signal generation is blocked."""
        current_time = time.time()
        
        # Check global daily limit
        if self.daily_signal_count >= self.daily_signal_limit:
            return f"Daily signal limit reached: {self.daily_signal_count}/{self.daily_signal_limit}"
        
        # Check global per-minute limit
        current_minute = int(current_time / 60)
        minute_signals = [ts for ts in self.signal_timestamps if int(ts / 60) == current_minute]
        if len(minute_signals) >= self.max_signals_per_minute:
            return f"Per-minute limit reached: {len(minute_signals)}/{self.max_signals_per_minute}"
        
        # Check symbol interval
        if symbol in self.symbol_last_signal:
            time_since_last = current_time - self.symbol_last_signal[symbol]
            if time_since_last < 8.5:
                return f"Symbol interval too short: {time_since_last:.1f}s < 8.5s"
        
        # Check strategy limits
        strategy_type = self._extract_strategy_type(strategy_name)
        if strategy_type in self.strategy_rate_limits:
            limits = self.strategy_rate_limits[strategy_type]
            if limits["daily_count"] >= limits["max_daily_trades"]:
                return f"Strategy {strategy_type} daily limit reached: {limits['daily_count']}/{limits['max_daily_trades']}"
        
        return "Unknown blocking reason"
