#!/usr/bin/env python3
"""
Funding Rate Arbitrage Strategy - Arbitrage Based
Focuses purely on strategy-specific tasks, delegating risk management to the risk management agent.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from datetime import datetime

# Import consolidated trading components (updated paths for new structure)
from ...core.memory.trading_context import TradingContext
from ...core.learning.trading_research_engine import TradingResearchEngine


class FundingRateArbitrage:
    """Funding rate arbitrage strategy for perpetual futures."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.min_funding_rate = config.get("min_funding_rate", 0.0001)  # 0.01% minimum
        self.max_funding_rate = config.get("max_funding_rate", 0.01)  # 1% maximum
        self.funding_threshold = config.get("funding_threshold", 0.0005)  # 0.05% threshold
        self.position_size_limit = config.get("position_size_limit", 0.1)  # 10% of capital
        self.hedge_ratio = config.get("hedge_ratio", 0.95)  # 95% hedge ratio
        
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
                self.logger.error(f"Failed to initialize funding rate arbitrage strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect funding rate arbitrage opportunities."""
        if not market_data:
            return []
        
        try:
            opportunities = []
            
            for data in market_data:
                symbol = data.get("symbol", "BTCUSD")
                spot_price = float(data.get("spot_price", 0.0))
                futures_price = float(data.get("futures_price", 0.0))
                funding_rate = float(data.get("funding_rate", 0.0))
                next_funding_time = data.get("next_funding_time", 0)
                volume_24h = float(data.get("volume_24h", 0.0))
                
                # Check if funding rate is significant
                if abs(funding_rate) > self.funding_threshold:
                    # Calculate arbitrage potential
                    arbitrage_potential = await self._calculate_arbitrage_potential(
                        symbol, spot_price, futures_price, funding_rate, volume_24h
                    )
                    
                    if arbitrage_potential['profitable']:
                        # Determine strategy direction
                        if funding_rate > 0:  # Positive funding rate
                            signal_type = "LONG_SPOT_SHORT_FUTURES"
                        else:  # Negative funding rate
                            signal_type = "SHORT_SPOT_LONG_FUTURES"
                        
                        confidence = min(abs(funding_rate) / self.max_funding_rate, 1.0)
                        
                        # Create trading signal
                        signal = {
                            "signal_id": f"funding_arbitrage_{int(time.time())}",
                            "strategy_id": "funding_rate_arbitrage",
                            "strategy_type": "arbitrage_based",
                            "signal_type": signal_type,
                            "symbol": symbol,
                            "timestamp": datetime.now().isoformat(),
                            "price": spot_price,
                            "confidence": confidence,
                            "metadata": {
                                "funding_rate": funding_rate,
                                "funding_rate_annualized": funding_rate * 3 * 365,
                                "arbitrage_potential": arbitrage_potential['potential'],
                                "next_funding_time": next_funding_time,
                                "volume_24h": volume_24h,
                                "hedge_ratio": self.hedge_ratio
                            }
                        }
                        
                        # Store signal in trading context
                        self.trading_context.store_signal(signal)
                        opportunities.append(signal)
                        
                        # Update strategy performance
                        self.strategy_performance["total_signals"] += 1
                        self.strategy_performance["average_confidence"] = (
                            (self.strategy_performance["average_confidence"] * 
                             (self.strategy_performance["total_signals"] - 1) + confidence) /
                            self.strategy_performance["total_signals"]
                        )
                        
                        self.last_signal_time = datetime.now()
                        
                        if self.logger:
                            self.logger.info(f"Funding rate arbitrage signal generated: {signal_type} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting funding rate arbitrage opportunities: {e}")
            return []

    async def _calculate_arbitrage_potential(self, symbol: str, spot_price: float, 
                                           futures_price: float, funding_rate: float, 
                                           volume_24h: float) -> Dict[str, Any]:
        """Calculate arbitrage potential."""
        try:
            # Calculate basis
            basis = futures_price - spot_price
            basis_percentage = basis / spot_price if spot_price > 0 else 0
            
            # Calculate potential profit from funding rate
            funding_profit = abs(funding_rate) * 3 * 365  # Annualized
            
            # Check if profitable
            profitable = funding_profit > self.funding_threshold
            
            return {
                "profitable": profitable,
                "potential": funding_profit,
                "basis": basis,
                "basis_percentage": basis_percentage
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating arbitrage potential: {e}")
            return {"profitable": False, "potential": 0.0}

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")