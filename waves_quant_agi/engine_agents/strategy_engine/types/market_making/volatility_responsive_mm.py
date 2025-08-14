#!/usr/bin/env python3
"""
Volatility Responsive Market Making Strategy
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


class VolatilityResponsiveMMStrategy:
    """Volatility responsive market making strategy."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.volatility_threshold = config.get("volatility_threshold", 0.02)  # 2% volatility
        self.spread_multiplier = config.get("spread_multiplier", 1.5)  # 1.5x base spread
        self.volume_threshold = config.get("volume_threshold", 500)  # Minimum volume
        self.lookback_period = config.get("lookback_period", 30)  # 30 periods
        
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
                self.logger.error(f"Failed to initialize volatility responsive MM strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect volatility responsive market making opportunities."""
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
                current_volatility = float(row.get("volatility", 0.0))
                
                if current_volume < self.volume_threshold:
                    continue
                
                # Calculate volatility metrics
                volatility_metrics = await self._calculate_volatility_metrics(
                    current_price, current_volume, current_volatility, market_data
                )
                
                # Check if volatility signal meets criteria
                if self._is_valid_volatility_signal(volatility_metrics):
                    signal = self._generate_volatility_signal(
                        symbol, current_price, volatility_metrics
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
                            self.logger.info(f"Volatility responsive MM signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting volatility responsive MM opportunities: {e}")
            return []

    async def _calculate_volatility_metrics(self, current_price: float, current_volume: float, 
                                           current_volatility: float, 
                                           market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate volatility metrics for market making."""
        try:
            # Calculate volume metrics
            volumes = [float(d.get("volume", 0)) for d in market_data if d.get("volume")]
            avg_volume = np.mean(volumes) if volumes else current_volume
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Calculate volatility strength
            volatility_strength = current_volatility / self.volatility_threshold if self.volatility_threshold > 0 else 0
            
            # Calculate price momentum
            prices = [float(d.get("close", 0)) for d in market_data if d.get("close")]
            if len(prices) > 1:
                price_momentum = (current_price - prices[0]) / prices[0] if prices[0] > 0 else 0
            else:
                price_momentum = 0.0
            
            # Calculate optimal spread based on volatility
            optimal_spread = max(
                0.001,  # 0.1% minimum
                min(0.01, current_volatility * self.spread_multiplier)  # 1% maximum
            )
            
            # Calculate volatility consistency
            volatilities = [float(d.get("volatility", 0)) for d in market_data if d.get("volatility")]
            if len(volatilities) > 1:
                volatility_consistency = 1.0 - np.std(volatilities)  # Higher consistency = lower std
            else:
                volatility_consistency = 0.5
            
            return {
                "current_volatility": current_volatility,
                "volatility_strength": volatility_strength,
                "optimal_spread": optimal_spread,
                "volume_ratio": volume_ratio,
                "price_momentum": price_momentum,
                "volatility_consistency": volatility_consistency,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating volatility metrics: {e}")
            return {}

    def _is_valid_volatility_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if volatility signal meets criteria."""
        try:
            if not metrics:
                return False
            
            volatility_strength = metrics.get("volatility_strength", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            volatility_consistency = metrics.get("volatility_consistency", 0.5)
            
            # Check volatility threshold
            if volatility_strength < 1.0:
                return False
            
            # Check volume confirmation
            if volume_ratio < 1.0:
                return False
            
            # Check volatility consistency
            if volatility_consistency < 0.3:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating volatility signal: {e}")
            return False

    def _generate_volatility_signal(self, symbol: str, current_price: float, 
                                   metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate volatility responsive market making signal."""
        try:
            volatility_strength = metrics.get("volatility_strength", 0.0)
            optimal_spread = metrics.get("optimal_spread", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            price_momentum = metrics.get("price_momentum", 0.0)
            
            # Determine signal type
            if volatility_strength > 1.5:
                signal_type = "HIGH_VOLATILITY_MM"
                confidence = min(volatility_strength / 2.0, 1.0)
            elif volatility_strength > 1.0:
                signal_type = "MEDIUM_VOLATILITY_MM"
                confidence = min(volatility_strength, 1.0)
            else:
                signal_type = "LOW_VOLATILITY_MM"
                confidence = volatility_strength
            
            # Adjust confidence based on other factors
            volume_confidence = min(volume_ratio / 2.0, 1.0)
            momentum_confidence = min(abs(price_momentum) / 0.05, 1.0)
            final_confidence = (confidence + volume_confidence + momentum_confidence) / 3
            
            signal = {
                "signal_id": f"volatility_mm_{int(time.time())}",
                "strategy_id": "volatility_responsive_mm",
                "strategy_type": "market_making",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": final_confidence,
                "metadata": {
                    "volatility_strength": volatility_strength,
                    "optimal_spread": optimal_spread,
                    "volume_ratio": volume_ratio,
                    "price_momentum": price_momentum
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating volatility responsive MM signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")