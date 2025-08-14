#!/usr/bin/env python3
"""
Triangular Arbitrage Strategy - Arbitrage Based
Focuses purely on strategy-specific tasks, delegating risk management to the risk management agent.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from datetime import datetime

# Import consolidated trading components
from ....trading.memory.trading_context import TradingContext
from ....trading.learning.trading_research_engine import TradingResearchEngine


class TriangularArbitrage:
    """Triangular arbitrage strategy for cryptocurrency pairs."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.min_profit_threshold = config.get("min_profit_threshold", 0.001)  # 0.1% minimum
        self.max_trade_size = config.get("max_trade_size", 0.1)  # 10% of capital
        self.execution_timeout = config.get("execution_timeout", 0.1)  # 100ms timeout
        
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
                self.logger.error(f"Failed to initialize triangular arbitrage strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect triangular arbitrage opportunities."""
        if not market_data:
            return []
        
        try:
            opportunities = []
            
            for data in market_data:
                symbol_a = data.get("symbol_a", "BTC")
                symbol_b = data.get("symbol_b", "ETH")
                symbol_c = data.get("symbol_c", "USDT")
                
                price_ab = float(data.get("price_ab", 0.0))  # BTC/ETH
                price_bc = float(data.get("price_bc", 0.0))  # ETH/USDT
                price_ac = float(data.get("price_ac", 0.0))  # BTC/USDT
                
                volume_ab = float(data.get("volume_ab", 0.0))
                volume_bc = float(data.get("volume_bc", 0.0))
                volume_ac = float(data.get("volume_ac", 0.0))
                
                # Calculate triangular arbitrage
                calculated_ac = price_ab * price_bc
                price_diff = abs(calculated_ac - price_ac)
                price_diff_percentage = price_diff / price_ac if price_ac > 0 else 0
                
                if price_diff_percentage > self.min_profit_threshold:
                    # Determine strategy direction
                    if calculated_ac > price_ac:
                        signal_type = "BUY_TRIANGLE"
                    else:
                        signal_type = "SELL_TRIANGLE"
                    
                    confidence = min(price_diff_percentage / self.min_profit_threshold, 1.0)
                    
                    # Create trading signal
                    signal = {
                        "signal_id": f"triangular_arbitrage_{int(time.time())}",
                        "strategy_id": "triangular_arbitrage",
                        "strategy_type": "arbitrage_based",
                        "signal_type": signal_type,
                        "symbol": f"{symbol_a}_{symbol_b}_{symbol_c}",
                        "timestamp": datetime.now().isoformat(),
                        "price": price_ac,
                        "confidence": confidence,
                        "metadata": {
                            "price_ab": price_ab,
                            "price_bc": price_bc,
                            "price_ac": price_ac,
                            "calculated_ac": calculated_ac,
                            "price_diff": price_diff,
                            "price_diff_percentage": price_diff_percentage,
                            "volume_ab": volume_ab,
                            "volume_bc": volume_bc,
                            "volume_ac": volume_ac
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
                        self.logger.info(f"Triangular arbitrage signal generated: {signal_type} for {symbol_a}_{symbol_b}_{symbol_c}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting triangular arbitrage opportunities: {e}")
            return []

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")