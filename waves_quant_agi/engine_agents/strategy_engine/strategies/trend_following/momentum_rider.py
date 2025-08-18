#!/usr/bin/env python3
"""
Momentum Rider Strategy - Trend Following
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


class MomentumRiderStrategy:
    """Momentum rider strategy for trend following."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.momentum_period = config.get("momentum_period", 14)  # 14 periods
        self.momentum_threshold = config.get("momentum_threshold", 0.02)  # 2% threshold
        self.volume_multiplier = config.get("volume_multiplier", 1.5)  # 1.5x average volume
        self.trend_confirmation = config.get("trend_confirmation", 3)  # 3 periods confirmation
        
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
                self.logger.error(f"Failed to initialize momentum rider strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect momentum opportunities."""
        if not market_data or len(market_data) < self.momentum_period:
            return []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').tail(self.momentum_period)
            
            opportunities = []
            
            for _, row in df.iterrows():
                symbol = row.get("symbol", "BTCUSD")
                current_price = float(row.get("close", 0.0))
                current_volume = float(row.get("volume", 0.0))
                
                # Get historical data for analysis
                historical_data = await self._get_historical_data(symbol)
                if not historical_data:
                    continue
                
                # Calculate momentum metrics
                momentum_metrics = await self._calculate_momentum_metrics(
                    current_price, current_volume, historical_data
                )
                
                # Check if momentum signal meets criteria
                if self._is_valid_momentum_signal(momentum_metrics):
                    signal = self._generate_momentum_signal(
                        symbol, current_price, momentum_metrics
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
                            self.logger.info(f"Momentum signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting momentum opportunities: {e}")
            return []

    async def _get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get historical data for momentum analysis."""
        try:
            # Get recent signals from trading context
            signals = await self.trading_context.get_recent_signals(symbol, limit=self.momentum_period * 2)
            
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

    async def _calculate_momentum_metrics(self, current_price: float, current_volume: float, 
                                        historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate momentum metrics."""
        try:
            if historical_data.empty or len(historical_data) < self.momentum_period:
                return {}
            
            # Get recent prices and volumes
            recent_prices = historical_data["price"].tail(self.momentum_period)
            recent_volumes = historical_data["volume"].tail(self.momentum_period)
            
            # Calculate momentum indicators
            price_momentum = (current_price - recent_prices.iloc[0]) / recent_prices.iloc[0] if recent_prices.iloc[0] > 0 else 0
            volume_momentum = current_volume / recent_volumes.mean() if recent_volumes.mean() > 0 else 0
            
            # Calculate trend strength
            price_changes = recent_prices.pct_change().dropna()
            trend_strength = abs(price_changes.mean()) / price_changes.std() if price_changes.std() > 0 else 0
            
            # Calculate RSI-like momentum
            gains = price_changes[price_changes > 0].sum()
            losses = abs(price_changes[price_changes < 0].sum())
            momentum_ratio = gains / (gains + losses) if (gains + losses) > 0 else 0.5
            
            return {
                "price_momentum": price_momentum,
                "volume_momentum": volume_momentum,
                "trend_strength": trend_strength,
                "momentum_ratio": momentum_ratio,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating momentum metrics: {e}")
            return {}

    def _is_valid_momentum_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if momentum signal meets criteria."""
        try:
            if not metrics:
                return False
            
            price_momentum = metrics.get("price_momentum", 0.0)
            volume_momentum = metrics.get("volume_momentum", 0.0)
            trend_strength = metrics.get("trend_strength", 0.0)
            momentum_ratio = metrics.get("momentum_ratio", 0.5)
            
            # Check price momentum
            if abs(price_momentum) < self.momentum_threshold:
                return False
            
            # Check volume confirmation
            if volume_momentum < self.volume_multiplier:
                return False
            
            # Check trend strength
            if trend_strength < 0.5:
                return False
            
            # Check momentum ratio
            if momentum_ratio < 0.6 and momentum_ratio > 0.4:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating momentum signal: {e}")
            return False

    def _generate_momentum_signal(self, symbol: str, current_price: float, 
                                 metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate momentum trading signal."""
        try:
            price_momentum = metrics.get("price_momentum", 0.0)
            volume_momentum = metrics.get("volume_momentum", 0.0)
            trend_strength = metrics.get("trend_strength", 0.0)
            momentum_ratio = metrics.get("momentum_ratio", 0.5)
            
            # Determine signal type
            if price_momentum > 0 and momentum_ratio > 0.6:
                signal_type = "MOMENTUM_UP"
                confidence = min(abs(price_momentum) / self.momentum_threshold, 1.0)
            elif price_momentum < 0 and momentum_ratio < 0.4:
                signal_type = "MOMENTUM_DOWN"
                confidence = min(abs(price_momentum) / self.momentum_threshold, 1.0)
            else:
                return None
            
            # Adjust confidence based on volume and trend
            volume_confidence = min(volume_momentum / self.volume_multiplier, 1.0)
            trend_confidence = min(trend_strength, 1.0)
            final_confidence = (confidence + volume_confidence + trend_confidence) / 3
            
            signal = {
                "signal_id": f"momentum_{int(time.time())}",
                "strategy_id": "momentum_rider",
                "strategy_type": "trend_following",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": final_confidence,
                "metadata": {
                    "price_momentum": price_momentum,
                    "volume_momentum": volume_momentum,
                    "trend_strength": trend_strength,
                    "momentum_ratio": momentum_ratio
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating momentum signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")