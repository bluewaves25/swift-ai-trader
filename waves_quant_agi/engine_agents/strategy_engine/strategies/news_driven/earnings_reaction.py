#!/usr/bin/env python3
"""
Earnings Reaction Strategy - News Driven
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


class EarningsReactionStrategy:
    """Earnings reaction strategy for news-driven trading."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.earnings_impact_threshold = config.get("earnings_impact_threshold", 0.05)  # 5% impact
        self.volume_threshold = config.get("volume_threshold", 2.0)  # 2x average volume
        self.volatility_threshold = config.get("volatility_threshold", 0.03)  # 3% volatility
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
                self.logger.error(f"Failed to initialize earnings reaction strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect earnings reaction opportunities."""
        if not market_data or len(market_data) < self.lookback_period:
            return []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').tail(self.lookback_period)
            
            opportunities = []
            
            for _, row in df.iterrows():
                symbol = row.get("symbol", "AAPL")
                current_price = float(row.get("close", 0.0))
                current_volume = float(row.get("volume", 0.0))
                earnings_impact = float(row.get("earnings_impact", 0.0))
                volatility = float(row.get("volatility", 0.0))
                
                # Calculate earnings metrics
                earnings_metrics = await self._calculate_earnings_metrics(
                    current_price, current_volume, earnings_impact, volatility, market_data
                )
                
                # Check if earnings signal meets criteria
                if self._is_valid_earnings_signal(earnings_metrics):
                    signal = self._generate_earnings_signal(
                        symbol, current_price, earnings_metrics
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
                            self.logger.info(f"Earnings signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting earnings reaction opportunities: {e}")
            return []

    async def _calculate_earnings_metrics(self, current_price: float, current_volume: float, 
                                         earnings_impact: float, volatility: float, 
                                         market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate earnings metrics for analysis."""
        try:
            # Calculate volume metrics
            volumes = [float(d.get("volume", 0)) for d in market_data if d.get("volume")]
            avg_volume = np.mean(volumes) if volumes else current_volume
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Calculate earnings impact strength
            earnings_impact_strength = abs(earnings_impact) / self.earnings_impact_threshold if self.earnings_impact_threshold > 0 else 0
            
            # Calculate volatility strength
            volatility_strength = volatility / self.volatility_threshold if self.volatility_threshold > 0 else 0
            
            # Calculate price momentum
            prices = [float(d.get("close", 0)) for d in market_data if d.get("close")]
            if len(prices) > 1:
                price_momentum = (current_price - prices[0]) / prices[0] if prices[0] > 0 else 0
            else:
                price_momentum = 0.0
            
            # Calculate earnings consistency
            earnings_impacts = [float(d.get("earnings_impact", 0)) for d in market_data if d.get("earnings_impact")]
            if len(earnings_impacts) > 1:
                earnings_consistency = 1.0 - np.std(earnings_impacts)  # Higher consistency = lower std
            else:
                earnings_consistency = 0.5
            
            return {
                "earnings_impact": earnings_impact,
                "earnings_impact_strength": earnings_impact_strength,
                "volatility": volatility,
                "volatility_strength": volatility_strength,
                "volume_ratio": volume_ratio,
                "price_momentum": price_momentum,
                "earnings_consistency": earnings_consistency,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating earnings metrics: {e}")
            return {}

    def _is_valid_earnings_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if earnings signal meets criteria."""
        try:
            if not metrics:
                return False
            
            earnings_impact_strength = metrics.get("earnings_impact_strength", 0.0)
            volatility_strength = metrics.get("volatility_strength", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            earnings_consistency = metrics.get("earnings_consistency", 0.5)
            
            # Check earnings impact
            if earnings_impact_strength < 1.0:
                return False
            
            # Check volatility
            if volatility_strength < 1.0:
                return False
            
            # Check volume confirmation
            if volume_ratio < self.volume_threshold:
                return False
            
            # Check earnings consistency
            if earnings_consistency < 0.3:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating earnings signal: {e}")
            return False

    def _generate_earnings_signal(self, symbol: str, current_price: float, 
                                 metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate earnings reaction trading signal."""
        try:
            earnings_impact = metrics.get("earnings_impact", 0.0)
            earnings_impact_strength = metrics.get("earnings_impact_strength", 0.0)
            volatility_strength = metrics.get("volatility_strength", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            price_momentum = metrics.get("price_momentum", 0.0)
            
            # Determine signal type
            if earnings_impact > 0:
                signal_type = "EARNINGS_BEAT"
                confidence = min(earnings_impact_strength, 1.0)
            else:
                signal_type = "EARNINGS_MISS"
                confidence = min(earnings_impact_strength, 1.0)
            
            # Adjust confidence based on other factors
            volatility_confidence = min(volatility_strength, 1.0)
            volume_confidence = min(volume_ratio / self.volume_threshold, 1.0)
            momentum_confidence = min(abs(price_momentum) / self.earnings_impact_threshold, 1.0)
            
            final_confidence = (confidence + volatility_confidence + volume_confidence + momentum_confidence) / 4
            
            signal = {
                "signal_id": f"earnings_{int(time.time())}",
                "strategy_id": "earnings_reaction",
                "strategy_type": "news_driven",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": final_confidence,
                "metadata": {
                    "earnings_impact": earnings_impact,
                    "earnings_impact_strength": earnings_impact_strength,
                    "volatility": metrics.get("volatility", 0.0),
                    "volatility_strength": volatility_strength,
                    "volume_ratio": volume_ratio,
                    "price_momentum": price_momentum
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating earnings signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")