#!/usr/bin/env python3
"""
Global Liquidity Signal Strategy - HTF
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


class GlobalLiquiditySignalStrategy:
    """Global liquidity signal strategy for high time frame analysis."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.liquidity_threshold = config.get("liquidity_threshold", 1000000)  # $1M minimum
        self.liquidity_ratio_threshold = config.get("liquidity_ratio_threshold", 0.1)  # 10% ratio
        self.execution_threshold = config.get("execution_threshold", 0.005)  # 0.5% threshold
        self.lookback_period = config.get("lookback_period", 100)  # 100 periods
        
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
                self.logger.error(f"Failed to initialize global liquidity signal strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect global liquidity opportunities."""
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
                spot_liquidity = float(row.get("spot_liquidity", 0.0))
                futures_liquidity = float(row.get("futures_liquidity", 0.0))
                options_liquidity = float(row.get("options_liquidity", 0.0))
                total_liquidity = spot_liquidity + futures_liquidity + options_liquidity
                
                if total_liquidity < self.liquidity_threshold:
                    continue
                
                # Calculate liquidity ratios
                spot_ratio = spot_liquidity / total_liquidity if total_liquidity > 0 else 0
                futures_ratio = futures_liquidity / total_liquidity if total_liquidity > 0 else 0
                options_ratio = options_liquidity / total_liquidity if total_liquidity > 0 else 0
                
                # Check for liquidity imbalances
                max_ratio = max(spot_ratio, futures_ratio, options_ratio)
                if max_ratio > self.liquidity_ratio_threshold:
                    # Determine strategy direction
                    if spot_ratio > futures_ratio and spot_ratio > options_ratio:
                        signal_type = "LIQUIDITY_TO_FUTURES"
                    elif futures_ratio > spot_ratio and futures_ratio > options_ratio:
                        signal_type = "LIQUIDITY_TO_SPOT"
                    else:
                        signal_type = "LIQUIDITY_TO_OPTIONS"
                    
                    confidence = min(max_ratio / self.liquidity_ratio_threshold, 1.0)
                    
                    # Create trading signal
                    signal = {
                        "signal_id": f"global_liquidity_{int(time.time())}",
                        "strategy_id": "global_liquidity_signal",
                        "strategy_type": "htf",
                        "signal_type": signal_type,
                        "symbol": symbol,
                        "timestamp": datetime.now().isoformat(),
                        "price": 0.0,  # No specific price for liquidity signals
                        "confidence": confidence,
                        "metadata": {
                            "spot_liquidity": spot_liquidity,
                            "futures_liquidity": futures_liquidity,
                            "options_liquidity": options_liquidity,
                            "total_liquidity": total_liquidity,
                            "spot_ratio": spot_ratio,
                            "futures_ratio": futures_ratio,
                            "options_ratio": options_ratio,
                            "max_ratio": max_ratio
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
                        self.logger.info(f"Global liquidity signal generated: {signal_type} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting global liquidity opportunities: {e}")
            return []

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")