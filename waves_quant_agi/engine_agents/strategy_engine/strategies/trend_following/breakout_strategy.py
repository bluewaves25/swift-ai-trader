#!/usr/bin/env python3
"""
Breakout Strategy - Trend Following
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


class BreakoutStrategy:
    """Breakout strategy for trend following."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.breakout_threshold = config.get("breakout_threshold", 0.02)  # 2% breakout
        self.lookback_period = config.get("lookback_period", 20)  # 20 periods
        self.volume_threshold = config.get("volume_threshold", 1.5)  # 1.5x average volume
        self.confirmation_periods = config.get("confirmation_periods", 3)  # 3 periods confirmation
        
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
                self.logger.error(f"Failed to initialize breakout strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect breakout opportunities."""
        if not market_data or len(market_data) < self.lookback_period:
            return []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').tail(self.lookback_period)
            
            opportunities = []
            
            for _, row in df.iterrows():
                symbol = row.get("symbol", "BTCUSD")
                current_price = float(row.get("close", 0.0))
                current_volume = float(row.get("volume", 0.0))
                
                # Get historical data for analysis
                historical_data = await self._get_historical_data(symbol)
                if not historical_data:
                    continue
                
                # Calculate breakout metrics
                breakout_metrics = await self._calculate_breakout_metrics(
                    current_price, current_volume, historical_data
                )
                
                # Check if breakout signal meets criteria
                if self._is_valid_breakout_signal(breakout_metrics):
                    signal = self._generate_breakout_signal(
                        symbol, current_price, breakout_metrics
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
                            self.logger.info(f"Breakout signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting breakout opportunities: {e}")
            return []

    async def _get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get historical data for breakout analysis."""
        try:
            # Get recent signals from trading context
            signals = await self.trading_context.get_recent_signals(symbol, limit=self.lookback_period * 2)
            
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

    async def _calculate_breakout_metrics(self, current_price: float, current_volume: float, 
                                        historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate breakout metrics."""
        try:
            if historical_data.empty or len(historical_data) < self.lookback_period:
                return {}
            
            # Get recent prices and volumes
            recent_prices = historical_data["price"].tail(self.lookback_period)
            recent_volumes = historical_data["volume"].tail(self.lookback_period)
            
            # Calculate resistance and support levels
            resistance = recent_prices.max()
            support = recent_prices.min()
            
            # Calculate breakout levels
            breakout_up = resistance * (1 + self.breakout_threshold)
            breakout_down = support * (1 - self.breakout_threshold)
            
            # Calculate volume metrics
            avg_volume = recent_volumes.mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # Determine breakout direction
            if current_price > breakout_up:
                breakout_direction = "UP"
                breakout_strength = (current_price - resistance) / resistance
            elif current_price < breakout_down:
                breakout_direction = "DOWN"
                breakout_strength = (support - current_price) / support
            else:
                breakout_direction = "NONE"
                breakout_strength = 0.0
            
            return {
                "breakout_direction": breakout_direction,
                "breakout_strength": breakout_strength,
                "resistance": resistance,
                "support": support,
                "breakout_up": breakout_up,
                "breakout_down": breakout_down,
                "volume_ratio": volume_ratio,
                "current_price": current_price
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating breakout metrics: {e}")
            return {}

    def _is_valid_breakout_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if breakout signal meets criteria."""
        try:
            if not metrics:
                return False
            
            breakout_direction = metrics.get("breakout_direction", "NONE")
            breakout_strength = metrics.get("breakout_strength", 0.0)
            volume_ratio = metrics.get("volume_ratio", 0.0)
            
            # Check breakout direction
            if breakout_direction == "NONE":
                return False
            
            # Check breakout strength
            if breakout_strength < self.breakout_threshold:
                return False
            
            # Check volume confirmation
            if volume_ratio < self.volume_threshold:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating breakout signal: {e}")
            return False

    def _generate_breakout_signal(self, symbol: str, current_price: float, 
                                 metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate breakout trading signal."""
        try:
            breakout_direction = metrics.get("breakout_direction", "NONE")
            breakout_strength = metrics.get("breakout_strength", 0.0)
            volume_ratio = metrics.get("volume_ratio", 0.0)
            
            if breakout_direction == "NONE":
                return None
            
            # Determine signal type
            if breakout_direction == "UP":
                signal_type = "BREAKOUT_UP"
                confidence = min(breakout_strength / self.breakout_threshold, 1.0)
            else:
                signal_type = "BREAKOUT_DOWN"
                confidence = min(breakout_strength / self.breakout_threshold, 1.0)
            
            # Adjust confidence based on volume
            volume_confidence = min(volume_ratio / self.volume_threshold, 1.0)
            final_confidence = (confidence + volume_confidence) / 2
            
            signal = {
                "signal_id": f"breakout_{int(time.time())}",
                "strategy_id": "breakout_strategy",
                "strategy_type": "trend_following",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": final_confidence,
                "metadata": {
                    "breakout_direction": breakout_direction,
                    "breakout_strength": breakout_strength,
                    "volume_ratio": volume_ratio,
                    "resistance": metrics.get("resistance", 0.0),
                    "support": metrics.get("support", 0.0)
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating breakout signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")