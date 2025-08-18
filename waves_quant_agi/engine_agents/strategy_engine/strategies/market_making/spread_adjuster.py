#!/usr/bin/env python3
"""
Spread Adjuster Strategy - Market Making
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


class SpreadAdjusterStrategy:
    """Spread adjuster strategy for market making."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.min_spread = config.get("min_spread", 0.001)  # 0.1% minimum spread
        self.max_spread = config.get("max_spread", 0.01)  # 1% maximum spread
        self.volatility_multiplier = config.get("volatility_multiplier", 2.0)  # Volatility adjustment
        self.volume_threshold = config.get("volume_threshold", 1000)  # Minimum volume
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
                self.logger.error(f"Failed to initialize spread adjuster strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect spread adjustment opportunities."""
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
                bid_price = float(row.get("bid", 0.0))
                ask_price = float(row.get("ask", 0.0))
                
                if current_volume < self.volume_threshold:
                    continue
                
                # Calculate spread metrics
                spread_metrics = await self._calculate_spread_metrics(
                    current_price, bid_price, ask_price, current_volume, market_data
                )
                
                # Check if spread adjustment signal meets criteria
                if self._is_valid_spread_adjustment_signal(spread_metrics):
                    signal = self._generate_spread_adjustment_signal(
                        symbol, current_price, spread_metrics
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
                            self.logger.info(f"Spread adjustment signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting spread adjustment opportunities: {e}")
            return []

    async def _calculate_spread_metrics(self, current_price: float, bid_price: float, 
                                       ask_price: float, current_volume: float, 
                                       market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate spread metrics for adjustment."""
        try:
            # Calculate current spread
            current_spread = ask_price - bid_price
            spread_percentage = current_spread / current_price if current_price > 0 else 0
            
            # Calculate optimal spread based on volatility
            prices = [float(d.get("close", 0)) for d in market_data if d.get("close")]
            if len(prices) > 1:
                volatility = np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0
            else:
                volatility = 0.0
            
            optimal_spread = max(
                self.min_spread,
                min(self.max_spread, volatility * self.volatility_multiplier)
            )
            
            # Calculate spread deviation
            spread_deviation = abs(spread_percentage - optimal_spread) / optimal_spread if optimal_spread > 0 else 0
            
            # Calculate volume metrics
            volumes = [float(d.get("volume", 0)) for d in market_data if d.get("volume")]
            avg_volume = np.mean(volumes) if volumes else current_volume
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Calculate price momentum
            if len(prices) > 1:
                price_momentum = (current_price - prices[0]) / prices[0] if prices[0] > 0 else 0
            else:
                price_momentum = 0.0
            
            return {
                "current_spread": current_spread,
                "spread_percentage": spread_percentage,
                "optimal_spread": optimal_spread,
                "spread_deviation": spread_deviation,
                "volatility": volatility,
                "volume_ratio": volume_ratio,
                "price_momentum": price_momentum,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating spread metrics: {e}")
            return {}

    def _is_valid_spread_adjustment_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if spread adjustment signal meets criteria."""
        try:
            if not metrics:
                return False
            
            spread_deviation = metrics.get("spread_deviation", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            volatility = metrics.get("volatility", 0.0)
            
            # Check if spread needs adjustment
            if spread_deviation > 0.2:  # 20% deviation threshold
                return True
            
            # Check if volume is high enough
            if volume_ratio < 1.0:
                return False
            
            # Check if volatility is significant
            if volatility < self.min_spread:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating spread adjustment signal: {e}")
            return False

    def _generate_spread_adjustment_signal(self, symbol: str, current_price: float, 
                                          metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate spread adjustment trading signal."""
        try:
            spread_percentage = metrics.get("spread_percentage", 0.0)
            optimal_spread = metrics.get("optimal_spread", 0.0)
            spread_deviation = metrics.get("spread_deviation", 0.0)
            volatility = metrics.get("volatility", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            
            # Determine signal type
            if spread_percentage < optimal_spread * 0.8:
                signal_type = "WIDEN_SPREAD"
                confidence = min((optimal_spread - spread_percentage) / optimal_spread, 1.0)
            elif spread_percentage > optimal_spread * 1.2:
                signal_type = "TIGHTEN_SPREAD"
                confidence = min((spread_percentage - optimal_spread) / optimal_spread, 1.0)
            else:
                signal_type = "ADJUST_SPREAD"
                confidence = min(spread_deviation, 1.0)
            
            # Adjust confidence based on other factors
            volatility_confidence = min(volatility / self.max_spread, 1.0)
            volume_confidence = min(volume_ratio / 2.0, 1.0)
            final_confidence = (confidence + volatility_confidence + volume_confidence) / 3
            
            signal = {
                "signal_id": f"spread_adjust_{int(time.time())}",
                "strategy_id": "spread_adjuster",
                "strategy_type": "market_making",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": final_confidence,
                "metadata": {
                    "spread_percentage": spread_percentage,
                    "optimal_spread": optimal_spread,
                    "spread_deviation": spread_deviation,
                    "volatility": volatility,
                    "volume_ratio": volume_ratio
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating spread adjustment signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")