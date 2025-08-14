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

# Import consolidated trading components
from ....trading.memory.trading_context import TradingContext
from ....trading.learning.trading_research_engine import TradingResearchEngine


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
                
                # Get historical data for analysis
                historical_data = await self._get_historical_data(symbol)
                if not historical_data:
                    continue
                
                # Calculate moving average metrics
                ma_metrics = await self._calculate_moving_average_metrics(
                    current_price, current_volume, historical_data
                )
                
                # Check if crossover signal meets criteria
                if self._is_valid_crossover_signal(ma_metrics):
                    signal = self._generate_crossover_signal(
                        symbol, current_price, ma_metrics
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

    async def _get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get historical data for moving average analysis."""
        try:
            # Get recent signals from trading context
            signals = await self.trading_context.get_recent_signals(symbol, limit=self.slow_period * 2)
            
            if not signals:
                return None
            
            # Convert signals to DataFrame
            data = []
            for signal in signals:
                if "price" in signal:
                    data.append({
                        "timestamp": signal.get("timestamp", 0),
                        "price": signal.get("price", 0.0),
                        "volume": signal.get("volume", 0.0)
                    })
            
            if not data:
                return None
            
            # Create DataFrame and sort by timestamp
            df = pd.DataFrame(data)
            df = df.sort_values("timestamp").reset_index(drop=True)
            
            return df
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting historical data: {e}")
            return None

    async def _calculate_moving_average_metrics(self, current_price: float, current_volume: float, 
                                              historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate moving average metrics."""
        try:
            if historical_data.empty or len(historical_data) < self.slow_period:
                return {}
            
            # Get recent prices and volumes
            recent_prices = historical_data["price"].tail(self.slow_period)
            recent_volumes = historical_data["volume"].tail(self.slow_period)
            
            # Calculate moving averages
            fast_ma = recent_prices.tail(self.fast_period).mean()
            slow_ma = recent_prices.tail(self.slow_period).mean()
            
            # Calculate crossover metrics
            ma_diff = fast_ma - slow_ma
            ma_ratio = ma_diff / slow_ma if slow_ma > 0 else 0
            
            # Calculate volume metrics
            volume_ratio = current_volume / recent_volumes.mean() if recent_volumes.mean() > 0 else 1.0
            
            # Calculate trend strength
            price_changes = recent_prices.pct_change().dropna()
            if len(price_changes) > 0:
                trend_strength = abs(price_changes.mean()) / price_changes.std() if price_changes.std() > 0 else 0
            else:
                trend_strength = 0.0
            
            # Calculate crossover momentum
            if len(recent_prices) >= 2:
                crossover_momentum = (ma_diff - (recent_prices.iloc[-2] - recent_prices.iloc[-3])) / recent_prices.iloc[-2] if recent_prices.iloc[-2] > 0 else 0
            else:
                crossover_momentum = 0.0
            
            return {
                "fast_ma": fast_ma,
                "slow_ma": slow_ma,
                "ma_diff": ma_diff,
                "ma_ratio": ma_ratio,
                "crossover_momentum": crossover_momentum,
                "volume_ratio": volume_ratio,
                "trend_strength": trend_strength,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating moving average metrics: {e}")
            return {}

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