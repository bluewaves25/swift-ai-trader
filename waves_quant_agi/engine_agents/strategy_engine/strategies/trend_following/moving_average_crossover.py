#!/usr/bin/env python3
"""
Moving Average Crossover Strategy - Trend Following
Focuses purely on strategy-specific tasks, delegating risk management to the risk management agent.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from datetime import datetime

# Import consolidated trading components (updated paths for new structure)
from ...core.memory.trading_context import TradingContext
from ...core.learning.trading_research_engine import TradingResearchEngine


class MovingAverageCrossoverStrategy:
    """Moving average crossover strategy for trend following."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.fast_period = config.get("fast_period", 10)  # 10 periods
        self.slow_period = config.get("slow_period", 20)  # 20 periods
        self.crossover_threshold = config.get("crossover_threshold", 0.001)  # 0.1% threshold
        self.volume_confirmation = config.get("volume_confirmation", 1.2)  # 1.2x average volume
        self.lookback_period = config.get("lookback_period", 50)  # 50 periods
        
        # Strategy state
        self.last_signal_time = None
        self.strategy_performance = {"total_signals": 0, "average_confidence": 0.0}

    async def initialize(self) -> bool:
        """Initialize the strategy and trading components."""
        try:
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize moving average crossover strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect moving average crossover opportunities."""
        if not market_data or len(market_data) < self.slow_period:
            return []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').tail(self.slow_period)
            
            opportunities = []
            
            for _, row in df.iterrows():
                symbol = row.get("symbol", "BTCUSD")
                current_price = float(row.get("close", 0.0))
                current_volume = float(row.get("volume", 0.0))
                
                # Calculate REAL moving average metrics (not placeholder)
                ma_metrics = self._calculate_real_moving_average_metrics(
                    current_price, current_volume, market_data
                )
                
                # Check if crossover signal meets criteria with real calculations
                if self._is_valid_crossover_signal(ma_metrics):
                    signal = self._generate_real_crossover_signal(
                        symbol, current_price, ma_metrics, current_volume
                    )
                    if signal:
                        self.trading_context.store_signal(signal)
                        opportunities.append(signal)
                        
                        # Update strategy performance
                        self.strategy_performance["total_signals"] += 1
                        self.strategy_performance["average_confidence"] = (
                            (self.strategy_performance["average_confidence"] * 
                             (self.strategy_performance["total_signals"] - 1) + signal["confidence"]) /
                            self.strategy_performance["total_signals"]
                        )
                        
                        self.last_signal_time = datetime.now()
                        
                        if self.logger:
                            self.logger.info(f"Moving average crossover signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting moving average crossover opportunities: {e}")
            return []

    def _calculate_real_moving_average_metrics(self, current_price: float, current_volume: float, 
                                             market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate REAL moving average metrics with actual statistical analysis.
        Not a placeholder - real moving average calculations.
        """
        try:
            if len(market_data) < self.slow_period:
                return {}
            
            # Extract prices and volumes from market data
            prices = [float(d.get("close", 0.0)) for d in market_data if d.get("close")]
            volumes = [float(d.get("volume", 0.0)) for d in market_data if d.get("volume")]
            
            if len(prices) < self.slow_period:
                return {}
            
            # Calculate REAL moving averages with advanced methods
            recent_prices = prices[-self.slow_period:]
            recent_volumes = volumes[-self.slow_period:]
            
            # Calculate weighted moving averages (more recent data has higher weight)
            fast_weights = np.linspace(0.5, 1.0, self.fast_period)
            slow_weights = np.linspace(0.3, 1.0, self.slow_period)
            
            fast_ma = np.average(recent_prices[-self.fast_period:], weights=fast_weights)
            slow_ma = np.average(recent_prices, weights=slow_weights)
            
            # Calculate REAL crossover metrics
            ma_diff = fast_ma - slow_ma
            ma_ratio = (ma_diff / slow_ma) * 100 if slow_ma > 0 else 0  # Convert to percentage
            
            # Calculate volume confirmation with advanced analysis
            avg_volume = np.mean(recent_volumes)
            volume_std = np.std(recent_volumes)
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            volume_zscore = (current_volume - avg_volume) / volume_std if volume_std > 0 else 0
            
            # Calculate REAL trend strength using multiple timeframes
            if len(prices) > 30:
                # Short-term trend (10 periods)
                short_trend = (prices[-1] - prices[-10]) / prices[-10] if prices[-10] > 0 else 0
                # Medium-term trend (20 periods)
                medium_trend = (prices[-1] - prices[-20]) / prices[-20] if prices[-20] > 0 else 0
                # Long-term trend (30 periods)
                long_trend = (prices[-1] - prices[-30]) / prices[-30] if prices[-30] > 0 else 0
                
                # Calculate trend consistency
                trend_directions = [1 if t > 0 else -1 for t in [short_trend, medium_trend, long_trend]]
                trend_consistency = sum(trend_directions) / len(trend_directions)  # -1 to 1
                
                # Calculate weighted trend strength
                trend_strength = (abs(short_trend) * 0.5 + abs(medium_trend) * 0.3 + abs(long_trend) * 0.2)
            else:
                trend_strength = 0.0
                trend_consistency = 0.0
            
            # Calculate REAL crossover momentum with advanced indicators
            if len(prices) >= 5:
                # Calculate momentum using price acceleration
                price_acceleration = []
                for i in range(2, len(prices[-5:])):
                    momentum = (prices[-i] - prices[-i-1]) / prices[-i-1] if prices[-i-1] > 0 else 0
                    price_acceleration.append(momentum)
                
                if price_acceleration:
                    crossover_momentum = np.mean(price_acceleration)
                    momentum_volatility = np.std(price_acceleration)
                else:
                    crossover_momentum = 0.0
                    momentum_volatility = 0.0
            else:
                crossover_momentum = 0.0
                momentum_volatility = 0.0
            
            # Calculate moving average convergence/divergence (MACD-like)
            ema_fast = self._calculate_ema(prices[-self.fast_period:], self.fast_period)
            ema_slow = self._calculate_ema(prices[-self.slow_period:], self.slow_period)
            macd_line = ema_fast - ema_slow
            
            # Calculate signal line (EMA of MACD)
            if len(prices) >= self.slow_period * 2:
                macd_history = []
                for i in range(self.slow_period, len(prices)):
                    fast_ema = self._calculate_ema(prices[i-self.fast_period:i], self.fast_period)
                    slow_ema = self._calculate_ema(prices[i-self.slow_period:i], self.slow_period)
                    macd_history.append(fast_ema - slow_ema)
                
                if macd_history:
                    signal_line = self._calculate_ema(macd_history, min(9, len(macd_history)))
                    macd_histogram = macd_line - signal_line
                else:
                    signal_line = 0.0
                    macd_histogram = 0.0
            else:
                signal_line = 0.0
                macd_histogram = 0.0
            
            # Calculate support and resistance levels
            if len(prices) >= 20:
                support_level = np.percentile(prices[-20:], 20)  # 20th percentile
                resistance_level = np.percentile(prices[-20:], 80)  # 80th percentile
                price_position = (current_price - support_level) / (resistance_level - support_level) if (resistance_level - support_level) > 0 else 0.5
            else:
                support_level = min(prices)
                resistance_level = max(prices)
                price_position = 0.5
            
            return {
                "fast_ma": fast_ma,
                "slow_ma": slow_ma,
                "ma_diff": ma_diff,
                "ma_ratio": ma_ratio,
                "crossover_momentum": crossover_momentum,
                "momentum_volatility": momentum_volatility,
                "volume_ratio": volume_ratio,
                "volume_zscore": volume_zscore,
                "trend_strength": trend_strength,
                "trend_consistency": trend_consistency,
                "macd_line": macd_line,
                "signal_line": signal_line,
                "macd_histogram": macd_histogram,
                "support_level": support_level,
                "resistance_level": resistance_level,
                "price_position": price_position,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating real moving average metrics: {e}")
            return {}
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        try:
            if len(prices) < period:
                return np.mean(prices) if prices else 0.0
            
            alpha = 2.0 / (period + 1)
            ema = prices[0]
            
            for price in prices[1:]:
                ema = alpha * price + (1 - alpha) * ema
            
            return ema
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating EMA: {e}")
            return np.mean(prices) if prices else 0.0

    def _is_valid_crossover_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if crossover signal meets criteria."""
        try:
            if not metrics:
                return False
            
            ma_ratio = metrics.get("ma_ratio", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            trend_strength = metrics.get("trend_strength", 0.0)
            crossover_momentum = metrics.get("crossover_momentum", 0.0)
            
            # Check moving average crossover
            if abs(ma_ratio) < self.crossover_threshold:
                return False
            
            # Check volume confirmation
            if volume_ratio < self.volume_confirmation:
                return False
            
            # Check trend strength
            if trend_strength < 0.3:
                return False
            
            # Check crossover momentum
            if abs(crossover_momentum) < self.crossover_threshold * 0.5:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating crossover signal: {e}")
            return False

    def _generate_crossover_signal(self, symbol: str, current_price: float, 
                                  metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate moving average crossover trading signal."""
        try:
            ma_ratio = metrics.get("ma_ratio", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            trend_strength = metrics.get("trend_strength", 0.0)
            crossover_momentum = metrics.get("crossover_momentum", 0.0)
            
            # Determine signal type
            if ma_ratio > 0 and crossover_momentum > 0:
                signal_type = "MA_CROSSOVER_BULLISH"
                confidence = min(abs(ma_ratio) / self.crossover_threshold, 1.0)
            elif ma_ratio < 0 and crossover_momentum < 0:
                signal_type = "MA_CROSSOVER_BEARISH"
                confidence = min(abs(ma_ratio) / self.crossover_threshold, 1.0)
            else:
                return None
            
            # Adjust confidence based on other factors
            volume_confidence = min(volume_ratio / self.volume_confirmation, 1.0)
            strength_confidence = min(trend_strength, 1.0)
            momentum_confidence = min(abs(crossover_momentum) / self.crossover_threshold, 1.0)
            final_confidence = (confidence + volume_confidence + strength_confidence + momentum_confidence) / 4
            
            signal = {
                "signal_id": f"ma_crossover_{int(time.time())}",
                "strategy_id": "moving_average_crossover",
                "strategy_type": "trend_following",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": final_confidence,
                "metadata": {
                    "ma_ratio": ma_ratio,
                    "volume_ratio": volume_ratio,
                    "trend_strength": trend_strength,
                    "crossover_momentum": crossover_momentum,
                    "fast_ma": metrics.get("fast_ma", 0.0),
                    "slow_ma": metrics.get("slow_ma", 0.0)
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating moving average crossover signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")