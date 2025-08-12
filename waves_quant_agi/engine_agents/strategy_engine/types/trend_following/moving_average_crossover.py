#!/usr/bin/env python3
"""
Moving Average Crossover Strategy - Fixed and Enhanced
Uses multiple moving average crossovers for trend detection.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from engine_agents.shared_utils import get_shared_redis

class MovingAverageCrossoverStrategy:
    """Moving average crossover strategy for trend detection."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.fast_period = config.get("fast_period", 10)
        self.slow_period = config.get("slow_period", 20)
        self.signal_period = config.get("signal_period", 9)
        self.crossover_threshold = config.get("crossover_threshold", 0.001)
        self.volume_confirmation = config.get("volume_confirmation", True)
        self.rsi_period = config.get("rsi_period", 14)
        self.rsi_overbought = config.get("rsi_overbought", 70)
        self.rsi_oversold = config.get("rsi_oversold", 30)

    async def detect_crossover(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect moving average crossover opportunities."""
        try:
            opportunities = []
            
            if market_data.empty:
                return opportunities
                
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTCUSD")
                close = float(row.get("close", 0.0))
                volume = float(row.get("volume", 0.0))
                
                # Get historical data for MA calculation
                historical_data = await self._get_historical_data(symbol)
                if not historical_data:
                    continue
                
                # Calculate moving averages and signals
                ma_signals = await self._calculate_ma_signals(historical_data)
                
                if ma_signals['signal_strength'] > self.crossover_threshold:
                    # Get RSI for confirmation
                    rsi = await self._calculate_rsi(historical_data)
                    
                    # Determine entry conditions
                    entry_conditions = await self._check_entry_conditions(
                        ma_signals, rsi, volume, historical_data
                    )
                    
                    if entry_conditions['should_enter']:
                        opportunity = {
                            "type": "ma_crossover",
                            "strategy": "moving_average",
                            "symbol": symbol,
                            "action": entry_conditions['action'],
                            "entry_price": close,
                            "stop_loss": entry_conditions['stop_loss'],
                            "take_profit": entry_conditions['take_profit'],
                            "confidence": min(ma_signals['signal_strength'] / self.crossover_threshold, 0.85),
                            "signal_strength": ma_signals['signal_strength'],
                            "ma_fast": ma_signals['fast_ma'],
                            "ma_slow": ma_signals['slow_ma'],
                            "rsi": rsi,
                            "volume_confirmation": entry_conditions['volume_confirmed'],
                            "timestamp": int(time.time()),
                            "description": f"MA Crossover for {symbol}: Signal {ma_signals['signal_strength']:.4f}"
                        }
                        opportunities.append(opportunity)
                        
                        # Store in Redis for tracking with proper JSON serialization
                        if self.redis_conn:
                            try:
                                import json
                                self.redis_conn.set(
                                    f"strategy_engine:ma_crossover:{symbol}:{int(time.time())}", 
                                    json.dumps(opportunity), 
                                    ex=3600
                                )
                            except json.JSONEncodeError as e:
                                if self.logger:
                                    self.logger.error(f"JSON encoding error storing MA crossover opportunity: {e}")
                            except ConnectionError as e:
                                if self.logger:
                                    self.logger.error(f"Redis connection error storing MA crossover opportunity: {e}")
                            except Exception as e:
                                if self.logger:
                                    self.logger.error(f"Unexpected error storing MA crossover opportunity: {e}")
                        
                        if self.logger:
                            self.logger.info(f"MA Crossover opportunity: {opportunity['description']}")

            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting MA crossover: {e}")
            return []

    async def _get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get historical data for MA calculation."""
        try:
            if not self.redis_conn:
                return None
                
            historical_key = f"market_data:{symbol}:history"
            historical_data = self.redis_conn.get(historical_key)
            
            if historical_data:
                import json
                return pd.DataFrame(json.loads(historical_data))
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting historical data: {e}")
            return None

    async def _calculate_ma_signals(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate moving average signals and crossover strength."""
        try:
            if historical_data.empty or len(historical_data) < self.slow_period:
                return {"signal_strength": 0.0, "fast_ma": 0.0, "slow_ma": 0.0}
            
            # Calculate moving averages
            fast_ma = historical_data['close'].rolling(window=self.fast_period).mean()
            slow_ma = historical_data['close'].rolling(window=self.slow_period).mean()
            
            # Get current values
            current_fast = fast_ma.iloc[-1]
            current_slow = slow_ma.iloc[-1]
            prev_fast = fast_ma.iloc[-2] if len(fast_ma) > 1 else current_fast
            prev_slow = slow_ma.iloc[-2] if len(slow_ma) > 1 else current_slow
            
            # Calculate crossover strength
            current_diff = current_fast - current_slow
            prev_diff = prev_fast - prev_slow
            
            # Signal strength based on crossover magnitude and direction change
            if (current_diff > 0 and prev_diff <= 0) or (current_diff < 0 and prev_diff >= 0):
                # Crossover occurred
                signal_strength = abs(current_diff) / current_slow if current_slow > 0 else 0
            else:
                # No crossover, but check signal strength
                signal_strength = abs(current_diff) / current_slow if current_slow > 0 else 0
                signal_strength *= 0.5  # Reduce strength if no crossover
            
            return {
                "signal_strength": signal_strength,
                "fast_ma": current_fast,
                "slow_ma": current_slow,
                "crossover_occurred": (current_diff > 0 and prev_diff <= 0) or (current_diff < 0 and prev_diff >= 0)
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating MA signals: {e}")
            return {"signal_strength": 0.0, "fast_ma": 0.0, "slow_ma": 0.0}

    async def _calculate_rsi(self, historical_data: pd.DataFrame) -> float:
        """Calculate RSI for trend confirmation."""
        try:
            if historical_data.empty or len(historical_data) < self.rsi_period + 1:
                return 50.0
            
            # Calculate price changes
            price_changes = historical_data['close'].diff()
            
            # Separate gains and losses
            gains = price_changes.where(price_changes > 0, 0)
            losses = -price_changes.where(price_changes < 0, 0)
            
            # Calculate average gains and losses
            avg_gains = gains.rolling(window=self.rsi_period).mean()
            avg_losses = losses.rolling(window=self.rsi_period).mean()
            
            # Calculate RSI
            rs = avg_gains.iloc[-1] / avg_losses.iloc[-1] if avg_losses.iloc[-1] > 0 else 0
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating RSI: {e}")
            return 50.0

    async def _check_entry_conditions(self, ma_signals: Dict[str, Any], rsi: float, 
                                    volume: float, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Check if entry conditions are met."""
        try:
            should_enter = False
            action = "hold"
            stop_loss = 0.0
            take_profit = 0.0
            volume_confirmed = False
            
            # Volume confirmation
            if self.volume_confirmation:
                avg_volume = historical_data['volume'].tail(20).mean()
                volume_confirmed = volume > avg_volume * 1.2
            
            # Entry logic based on MA signals and RSI
            if ma_signals['crossover_occurred'] and ma_signals['signal_strength'] > self.crossover_threshold:
                if ma_signals['fast_ma'] > ma_signals['slow_ma']:  # Bullish crossover
                    if rsi < self.rsi_overbought:  # Not overbought
                        should_enter = True
                        action = "buy"
                        current_price = historical_data['close'].iloc[-1]
                        stop_loss = current_price * 0.98
                        take_profit = current_price * 1.03
                        
                elif ma_signals['fast_ma'] < ma_signals['slow_ma']:  # Bearish crossover
                    if rsi > self.rsi_oversold:  # Not oversold
                        should_enter = True
                        action = "sell"
                        current_price = historical_data['close'].iloc[-1]
                        stop_loss = current_price * 1.02
                        take_profit = current_price * 0.97
            
            return {
                "should_enter": should_enter,
                "action": action,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "volume_confirmed": volume_confirmed
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking entry conditions: {e}")
            return {
                "should_enter": False,
                "action": "hold",
                "stop_loss": 0.0,
                "take_profit": 0.0,
                "volume_confirmed": False
            }

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Moving Average Crossover Strategy",
            "type": "trend_following",
            "description": "Uses multiple moving average crossovers for trend detection",
            "parameters": {
                "fast_period": self.fast_period,
                "slow_period": self.slow_period,
                "signal_period": self.signal_period,
                "crossover_threshold": self.crossover_threshold,
                "volume_confirmation": self.volume_confirmation,
                "rsi_period": self.rsi_period,
                "rsi_overbought": self.rsi_overbought,
                "rsi_oversold": self.rsi_oversold
            },
            "timeframe": "fast",  # 100ms tier
            "asset_types": ["crypto", "forex", "indices", "stocks"]
        }