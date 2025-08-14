#!/usr/bin/env python3
"""
Adaptive Quote Strategy - Market Making
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


class AdaptiveQuoteStrategy:
    """Adaptive quote strategy for market making."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.spread_multiplier = config.get("spread_multiplier", 1.5)  # 1.5x base spread
        self.volume_threshold = config.get("volume_threshold", 1000)  # Minimum volume
        self.volatility_threshold = config.get("volatility_threshold", 0.02)  # 2% volatility
        self.quote_refresh_rate = config.get("quote_refresh_rate", 1.0)  # 1 second refresh
        
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
                self.logger.error(f"Failed to initialize adaptive quote strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect adaptive quote opportunities."""
        if not market_data:
            return []
        
        try:
            opportunities = []
            
            for data in market_data:
                symbol = data.get("symbol", "BTCUSD")
                current_price = float(data.get("close", 0.0))
                current_volume = float(data.get("volume", 0.0))
                bid_price = float(data.get("bid", 0.0))
                ask_price = float(data.get("ask", 0.0))
                
                if current_volume < self.volume_threshold:
                    continue
                
                # Calculate spread metrics
                spread_metrics = await self._calculate_spread_metrics(
                    current_price, bid_price, ask_price, current_volume, market_data
                )
                
                # Check if adaptive quote signal meets criteria
                if self._is_valid_adaptive_quote_signal(spread_metrics):
                    signal = self._generate_adaptive_quote_signal(
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
                            self.logger.info(f"Adaptive quote signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting adaptive quote opportunities: {e}")
            return []

    async def _calculate_spread_metrics(self, current_price: float, bid_price: float, 
                                       ask_price: float, current_volume: float, 
                                       market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate spread metrics for adaptive quoting."""
        try:
            # Calculate current spread
            current_spread = ask_price - bid_price
            spread_percentage = current_spread / current_price if current_price > 0 else 0
            
            # Calculate volume-weighted average price (VWAP)
            total_volume = sum(float(d.get("volume", 0)) for d in market_data)
            vwap = sum(float(d.get("close", 0)) * float(d.get("volume", 0)) for d in market_data) / total_volume if total_volume > 0 else current_price
            
            # Calculate price deviation from VWAP
            price_deviation = abs(current_price - vwap) / vwap if vwap > 0 else 0
            
            # Calculate volatility
            prices = [float(d.get("close", 0)) for d in market_data if d.get("close")]
            if len(prices) > 1:
                volatility = np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0
            else:
                volatility = 0.0
            
            # Calculate optimal spread
            optimal_spread = max(
                spread_percentage * self.spread_multiplier,
                self.volatility_threshold
            )
            
            return {
                "current_spread": current_spread,
                "spread_percentage": spread_percentage,
                "optimal_spread": optimal_spread,
                "price_deviation": price_deviation,
                "volatility": volatility,
                "vwap": vwap,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating spread metrics: {e}")
            return {}

    def _is_valid_adaptive_quote_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if adaptive quote signal meets criteria."""
        try:
            if not metrics:
                return False
            
            spread_percentage = metrics.get("spread_percentage", 0.0)
            optimal_spread = metrics.get("optimal_spread", 0.0)
            price_deviation = metrics.get("price_deviation", 0.0)
            volatility = metrics.get("volatility", 0.0)
            
            # Check if current spread is too narrow
            if spread_percentage < optimal_spread * 0.8:
                return True
            
            # Check if price deviation is high
            if price_deviation > self.volatility_threshold:
                return True
            
            # Check if volatility is high
            if volatility > self.volatility_threshold:
                return True
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating adaptive quote signal: {e}")
            return False

    def _generate_adaptive_quote_signal(self, symbol: str, current_price: float, 
                                       metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate adaptive quote trading signal."""
        try:
            spread_percentage = metrics.get("spread_percentage", 0.0)
            optimal_spread = metrics.get("optimal_spread", 0.0)
            price_deviation = metrics.get("price_deviation", 0.0)
            volatility = metrics.get("volatility", 0.0)
            
            # Determine signal type
            if spread_percentage < optimal_spread * 0.8:
                signal_type = "WIDEN_SPREAD"
                confidence = min((optimal_spread - spread_percentage) / optimal_spread, 1.0)
            elif price_deviation > self.volatility_threshold:
                signal_type = "ADJUST_QUOTES"
                confidence = min(price_deviation / self.volatility_threshold, 1.0)
            elif volatility > self.volatility_threshold:
                signal_type = "VOLATILITY_ADJUSTMENT"
                confidence = min(volatility / self.volatility_threshold, 1.0)
            else:
                return None
            
            signal = {
                "signal_id": f"adaptive_quote_{int(time.time())}",
                "strategy_id": "adaptive_quote",
                "strategy_type": "market_making",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": confidence,
                "metadata": {
                    "spread_percentage": spread_percentage,
                    "optimal_spread": optimal_spread,
                    "price_deviation": price_deviation,
                    "volatility": volatility,
                    "vwap": metrics.get("vwap", 0.0)
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating adaptive quote signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")