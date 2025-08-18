#!/usr/bin/env python3
"""
Mean Reversion Strategy - Statistical Arbitrage
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


class MeanReversionStrategy:
    """Mean reversion strategy using statistical arbitrage principles."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.std_multiplier = config.get("std_multiplier", 2.0)  # Standard deviation multiplier
        self.lookback_period = config.get("lookback_period", 50)  # 50 periods lookback
        self.mean_period = config.get("mean_period", 20)  # 20 periods for mean calculation
        self.min_deviation = config.get("min_deviation", 0.01)  # 1% minimum deviation
        self.position_threshold = config.get("position_threshold", 0.03)  # 3% position threshold
        self.stop_loss_threshold = config.get("stop_loss_threshold", 0.05)  # 5% stop loss
        
        # Strategy state
        self.last_signal_time = None
        self.current_position = 0
        self.entry_price = None
        self.strategy_performance = {
            "total_signals": 0,
            "successful_trades": 0,
            "total_pnl": 0.0,
            "average_confidence": 0.0
        }

    async def initialize(self) -> bool:
        """Initialize the strategy and trading components."""
        try:
            # Initialize trading components
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            
            if self.logger:
                self.logger.info("Mean reversion strategy initialized successfully")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize mean reversion strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect mean reversion opportunities based on statistical analysis."""
        if not market_data or len(market_data) < self.lookback_period:
            return []
        
        try:
            # Convert to pandas DataFrame for analysis
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').tail(self.lookback_period)
            
            # Calculate statistical measures
            current_price = df['close'].iloc[-1]
            rolling_mean = df['close'].rolling(window=self.mean_period).mean().iloc[-1]
            rolling_std = df['close'].rolling(window=self.mean_period).std().iloc[-1]
            
            # Calculate deviation from mean
            deviation = abs(current_price - rolling_mean) / rolling_mean
            
            # Check if deviation exceeds threshold
            if deviation > self.min_deviation:
                # Determine signal direction
                if current_price < rolling_mean - (rolling_std * self.std_multiplier):
                    signal_type = "BUY"  # Price below mean, expect reversion up
                    confidence = min(deviation / self.min_deviation, 1.0)
                elif current_price > rolling_mean + (rolling_std * self.std_multiplier):
                    signal_type = "SELL"  # Price above mean, expect reversion down
                    confidence = min(deviation / self.min_deviation, 1.0)
                else:
                    return []
                
                # Create trading signal
                signal = {
                    "signal_id": f"mean_rev_{int(time.time())}",
                    "strategy_id": "mean_reversion",
                    "strategy_type": "statistical_arbitrage",
                    "signal_type": signal_type,
                    "symbol": market_data[0].get("symbol", "UNKNOWN"),
                    "timestamp": datetime.now().isoformat(),
                    "price": current_price,
                    "confidence": confidence,
                    "metadata": {
                        "deviation": deviation,
                        "rolling_mean": rolling_mean,
                        "rolling_std": rolling_std,
                        "lookback_period": self.lookback_period,
                        "mean_period": self.mean_period
                    }
                }
                
                # Store signal in trading context
                self.trading_context.store_signal(signal)
                
                # Update strategy performance
                self.strategy_performance["total_signals"] += 1
                self.strategy_performance["average_confidence"] = (
                    (self.strategy_performance["average_confidence"] * 
                     (self.strategy_performance["total_signals"] - 1) + confidence) /
                    self.strategy_performance["total_signals"]
                )
                
                self.last_signal_time = datetime.now()
                
                if self.logger:
                    self.logger.info(f"Mean reversion signal generated: {signal_type} at {current_price:.4f}")
                
                return [signal]
            
            return []
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting mean reversion opportunity: {e}")
            return []

    async def update_strategy_parameters(self, new_params: Dict[str, Any]) -> bool:
        """Update strategy parameters."""
        try:
            # Update configurable parameters
            if "std_multiplier" in new_params:
                self.std_multiplier = new_params["std_multiplier"]
            if "lookback_period" in new_params:
                self.lookback_period = new_params["lookback_period"]
            if "mean_period" in new_params:
                self.mean_period = new_params["mean_period"]
            if "min_deviation" in new_params:
                self.min_deviation = new_params["min_deviation"]
            if "position_threshold" in new_params:
                self.position_threshold = new_params["position_threshold"]
            if "stop_loss_threshold" in new_params:
                self.stop_loss_threshold = new_params["stop_loss_threshold"]
            
            if self.logger:
                self.logger.info(f"Strategy parameters updated: {new_params}")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to update strategy parameters: {e}")
            return False

    async def get_strategy_performance(self) -> Dict[str, Any]:
        """Get current strategy performance metrics."""
        try:
            # Get recent signals from trading context
            recent_signals = self.trading_context.get_recent_signals(limit=100)
            
            # Calculate additional metrics
            performance = self.strategy_performance.copy()
            performance.update({
                "last_signal_time": self.last_signal_time.isoformat() if self.last_signal_time else None,
                "current_position": self.current_position,
                "entry_price": self.entry_price,
                "recent_signals_count": len(recent_signals),
                "timestamp": datetime.now().isoformat()
            })
            
            return performance
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get strategy performance: {e}")
            return {}

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
            
            if self.logger:
                self.logger.info("Mean reversion strategy cleaned up successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}") 