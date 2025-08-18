#!/usr/bin/env python3
"""
Regime Shift Detector Strategy - HTF
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


class RegimeShiftDetectorStrategy:
    """Regime shift detector strategy for high time frame analysis."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.regime_threshold = config.get("regime_threshold", 0.1)  # 10% regime change
        self.confirmation_periods = config.get("confirmation_periods", 10)  # 10 periods confirmation
        self.volume_threshold = config.get("volume_threshold", 1.5)  # 1.5x average volume
        self.lookback_period = config.get("lookback_period", 200)  # 200 periods
        
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
                self.logger.error(f"Failed to initialize regime shift detector strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect regime shift opportunities."""
        if not market_data or len(market_data) < self.lookback_period:
            return []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').tail(self.lookback_period)
            
            opportunities = []
            
            for _, row in df.iterrows():
                symbol = row.get("symbol", "SPX")
                current_price = float(row.get("close", 0.0))
                current_volume = float(row.get("volume", 0.0))
                
                # Get historical data for analysis
                historical_data = await self._get_historical_data(symbol)
                if not historical_data:
                    continue
                
                # Calculate regime shift metrics
                regime_metrics = await self._calculate_regime_shift_metrics(
                    current_price, current_volume, historical_data
                )
                
                # Check if regime shift signal meets criteria
                if self._is_valid_regime_shift_signal(regime_metrics):
                    signal = self._generate_regime_shift_signal(
                        symbol, current_price, regime_metrics
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
                            self.logger.info(f"Regime shift signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting regime shift opportunities: {e}")
            return []

    async def _get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get historical data for regime shift analysis."""
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

    async def _calculate_regime_shift_metrics(self, current_price: float, current_volume: float, 
                                            historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate regime shift metrics."""
        try:
            if historical_data.empty or len(historical_data) < self.lookback_period:
                return {}
            
            # Get recent prices and volumes
            recent_prices = historical_data["price"].tail(self.lookback_period)
            recent_volumes = historical_data["volume"].tail(self.lookback_period)
            
            # Calculate regime indicators
            price_regime = (current_price - recent_prices.iloc[0]) / recent_prices.iloc[0] if recent_prices.iloc[0] > 0 else 0
            volume_regime = current_volume / recent_volumes.mean() if recent_volumes.mean() > 0 else 0
            
            # Calculate regime strength using linear regression
            x = np.arange(len(recent_prices))
            y = recent_prices.values
            if len(x) > 1:
                slope, intercept = np.polyfit(x, y, 1)
                regime_strength = abs(slope) / recent_prices.std() if recent_prices.std() > 0 else 0
            else:
                regime_strength = 0.0
            
            # Calculate regime consistency
            price_changes = recent_prices.pct_change().dropna()
            positive_changes = (price_changes > 0).sum()
            total_changes = len(price_changes)
            regime_consistency = abs(positive_changes / total_changes - 0.5) * 2 if total_changes > 0 else 0
            
            # Calculate regime duration
            regime_duration = len(recent_prices)
            
            return {
                "price_regime": price_regime,
                "volume_regime": volume_regime,
                "regime_strength": regime_strength,
                "regime_consistency": regime_consistency,
                "regime_duration": regime_duration,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating regime shift metrics: {e}")
            return {}

    def _is_valid_regime_shift_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if regime shift signal meets criteria."""
        try:
            if not metrics:
                return False
            
            price_regime = metrics.get("price_regime", 0.0)
            volume_regime = metrics.get("volume_regime", 0.0)
            regime_strength = metrics.get("regime_strength", 0.0)
            regime_consistency = metrics.get("regime_consistency", 0.0)
            regime_duration = metrics.get("regime_duration", 0)
            
            # Check price regime change
            if abs(price_regime) < self.regime_threshold:
                return False
            
            # Check volume confirmation
            if volume_regime < self.volume_threshold:
                return False
            
            # Check regime strength
            if regime_strength < 0.5:
                return False
            
            # Check regime consistency
            if regime_consistency < 0.3:
                return False
            
            # Check regime duration
            if regime_duration < self.confirmation_periods:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating regime shift signal: {e}")
            return False

    def _generate_regime_shift_signal(self, symbol: str, current_price: float, 
                                     metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate regime shift trading signal."""
        try:
            price_regime = metrics.get("price_regime", 0.0)
            volume_regime = metrics.get("volume_regime", 0.0)
            regime_strength = metrics.get("regime_strength", 0.0)
            regime_consistency = metrics.get("regime_consistency", 0.0)
            
            # Determine signal type
            if price_regime > 0:
                signal_type = "REGIME_SHIFT_BULLISH"
                confidence = min(abs(price_regime) / self.regime_threshold, 1.0)
            else:
                signal_type = "REGIME_SHIFT_BEARISH"
                confidence = min(abs(price_regime) / self.regime_threshold, 1.0)
            
            # Adjust confidence based on other factors
            volume_confidence = min(volume_regime / self.volume_threshold, 1.0)
            strength_confidence = min(regime_strength, 1.0)
            consistency_confidence = min(regime_consistency, 1.0)
            final_confidence = (confidence + volume_confidence + strength_confidence + consistency_confidence) / 4
            
            signal = {
                "signal_id": f"regime_shift_{int(time.time())}",
                "strategy_id": "regime_shift_detector",
                "strategy_type": "htf",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": final_confidence,
                "metadata": {
                    "price_regime": price_regime,
                    "volume_regime": volume_regime,
                    "regime_strength": regime_strength,
                    "regime_consistency": regime_consistency,
                    "regime_duration": metrics.get("regime_duration", 0)
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating regime shift signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")