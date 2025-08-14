#!/usr/bin/env python3
"""
Macro Trend Tracker Strategy - HTF
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


class MacroTrendTrackerStrategy:
    """Macro trend tracker strategy for high time frame analysis."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.trend_period = config.get("trend_period", 200)  # 200 periods
        self.trend_threshold = config.get("trend_threshold", 0.05)  # 5% threshold
        self.confirmation_periods = config.get("confirmation_periods", 5)  # 5 periods confirmation
        self.volume_threshold = config.get("volume_threshold", 1.2)  # 1.2x average volume
        
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
                self.logger.error(f"Failed to initialize macro trend tracker strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect macro trend opportunities."""
        if not market_data or len(market_data) < self.trend_period:
            return []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').tail(self.trend_period)
            
            opportunities = []
            
            for _, row in df.iterrows():
                symbol = row.get("symbol", "BTCUSD")
                current_price = float(row.get("close", 0.0))
                current_volume = float(row.get("volume", 0.0))
                
                # Get historical data for analysis
                historical_data = await self._get_historical_data(symbol)
                if not historical_data:
                    continue
                
                # Calculate macro trend metrics
                trend_metrics = await self._calculate_macro_trend_metrics(
                    current_price, current_volume, historical_data
                )
                
                # Check if macro trend signal meets criteria
                if self._is_valid_macro_trend_signal(trend_metrics):
                    signal = self._generate_macro_trend_signal(
                        symbol, current_price, trend_metrics
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
                            self.logger.info(f"Macro trend signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting macro trend opportunities: {e}")
            return []

    async def _get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get historical data for macro trend analysis."""
        try:
            # Get recent signals from trading context
            signals = await self.trading_context.get_recent_signals(symbol, limit=self.trend_period * 2)
            
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

    async def _calculate_macro_trend_metrics(self, current_price: float, current_volume: float, 
                                           historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate macro trend metrics."""
        try:
            if historical_data.empty or len(historical_data) < self.trend_period:
                return {}
            
            # Get recent prices and volumes
            recent_prices = historical_data["price"].tail(self.trend_period)
            recent_volumes = historical_data["volume"].tail(self.trend_period)
            
            # Calculate trend indicators
            price_trend = (current_price - recent_prices.iloc[0]) / recent_prices.iloc[0] if recent_prices.iloc[0] > 0 else 0
            volume_trend = current_volume / recent_volumes.mean() if recent_volumes.mean() > 0 else 0
            
            # Calculate trend strength using linear regression
            x = np.arange(len(recent_prices))
            y = recent_prices.values
            if len(x) > 1:
                slope, intercept = np.polyfit(x, y, 1)
                trend_strength = abs(slope) / recent_prices.std() if recent_prices.std() > 0 else 0
            else:
                trend_strength = 0.0
            
            # Calculate trend consistency
            price_changes = recent_prices.pct_change().dropna()
            positive_changes = (price_changes > 0).sum()
            total_changes = len(price_changes)
            trend_consistency = abs(positive_changes / total_changes - 0.5) * 2 if total_changes > 0 else 0
            
            return {
                "price_trend": price_trend,
                "volume_trend": volume_trend,
                "trend_strength": trend_strength,
                "trend_consistency": trend_consistency,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating macro trend metrics: {e}")
            return {}

    def _is_valid_macro_trend_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if macro trend signal meets criteria."""
        try:
            if not metrics:
                return False
            
            price_trend = metrics.get("price_trend", 0.0)
            volume_trend = metrics.get("volume_trend", 0.0)
            trend_strength = metrics.get("trend_strength", 0.0)
            trend_consistency = metrics.get("trend_consistency", 0.0)
            
            # Check price trend
            if abs(price_trend) < self.trend_threshold:
                return False
            
            # Check volume confirmation
            if volume_trend < self.volume_threshold:
                return False
            
            # Check trend strength
            if trend_strength < 0.5:
                return False
            
            # Check trend consistency
            if trend_consistency < 0.3:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating macro trend signal: {e}")
            return False

    def _generate_macro_trend_signal(self, symbol: str, current_price: float, 
                                    metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate macro trend trading signal."""
        try:
            price_trend = metrics.get("price_trend", 0.0)
            volume_trend = metrics.get("volume_trend", 0.0)
            trend_strength = metrics.get("trend_strength", 0.0)
            trend_consistency = metrics.get("trend_consistency", 0.0)
            
            # Determine signal type
            if price_trend > 0:
                signal_type = "MACRO_TREND_UP"
                confidence = min(abs(price_trend) / self.trend_threshold, 1.0)
            else:
                signal_type = "MACRO_TREND_DOWN"
                confidence = min(abs(price_trend) / self.trend_threshold, 1.0)
            
            # Adjust confidence based on volume and trend strength
            volume_confidence = min(volume_trend / self.volume_threshold, 1.0)
            strength_confidence = min(trend_strength, 1.0)
            consistency_confidence = min(trend_consistency, 1.0)
            final_confidence = (confidence + volume_confidence + strength_confidence + consistency_confidence) / 4
            
            signal = {
                "signal_id": f"macro_trend_{int(time.time())}",
                "strategy_id": "macro_trend_tracker",
                "strategy_type": "htf",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": final_confidence,
                "metadata": {
                    "price_trend": price_trend,
                    "volume_trend": volume_trend,
                    "trend_strength": trend_strength,
                    "trend_consistency": trend_consistency
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating macro trend signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")