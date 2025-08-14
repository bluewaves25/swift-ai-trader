#!/usr/bin/env python3
"""
Pairs Trading Strategy - Statistical Arbitrage
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


class PairsTradingStrategy:
    """Pairs trading strategy using statistical arbitrage principles."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.z_score_threshold = config.get("z_score_threshold", 2.0)  # Z-score threshold
        self.lookback_period = config.get("lookback_period", 60)  # 60 periods lookback
        self.min_correlation = config.get("min_correlation", 0.8)  # Minimum correlation
        self.position_threshold = config.get("position_threshold", 0.02)  # 2% position threshold
        self.stop_loss_threshold = config.get("stop_loss_threshold", 0.05)  # 5% stop loss
        
        # Strategy state
        self.last_signal_time = None
        self.current_positions = {}
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
                self.logger.info("Pairs trading strategy initialized successfully")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize pairs trading strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect pairs trading opportunities based on statistical analysis."""
        if not market_data or len(market_data) < self.lookback_period:
            return []
        
        try:
            opportunities = []
            
            # Extract unique symbols from market data
            symbols = list(set([data.get("symbol", "") for data in market_data if data.get("symbol")]))
            
            # Generate potential pairs
            trading_pairs = self._generate_trading_pairs(symbols)
            
            for pair in trading_pairs:
                if len(pair) == 2:
                    opportunity = await self._check_pair_opportunity(pair, market_data)
                    if opportunity:
                        opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting pairs trading opportunities: {e}")
            return []

    def _generate_trading_pairs(self, symbols: List[str]) -> List[List[str]]:
        """Generate potential trading pairs from available symbols."""
        try:
            pairs = []
            for i in range(len(symbols)):
                for j in range(i + 1, len(symbols)):
                    pairs.append([symbols[i], symbols[j]])
            
            return pairs[:20]  # Limit to 20 pairs for performance
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating trading pairs: {e}")
            return []

    async def _check_pair_opportunity(self, pair: List[str], market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check for trading opportunity in a specific pair."""
        try:
            symbol1, symbol2 = pair
            
            # Filter market data for both symbols
            data1 = [d for d in market_data if d.get("symbol") == symbol1]
            data2 = [d for d in market_data if d.get("symbol") == symbol2]
            
            if len(data1) < self.lookback_period or len(data2) < self.lookback_period:
                return None
            
            # Calculate pair statistics
            pair_stats = await self._calculate_pair_statistics(data1, data2)
            
            if not pair_stats['cointegrated']:
                return None
            
            # Check for trading signal
            current_z_score = pair_stats['current_z_score']
            
            if abs(current_z_score) > self.z_score_threshold:
                # Determine trade direction
                if current_z_score > self.z_score_threshold:
                    signal_type = "SHORT_LONG"  # Short symbol1, long symbol2
                    confidence = min(abs(current_z_score) / (self.z_score_threshold * 1.5), 1.0)
                else:
                    signal_type = "LONG_SHORT"  # Long symbol1, short symbol2
                    confidence = min(abs(current_z_score) / (self.z_score_threshold * 1.5), 1.0)
                
                # Create trading signal
                signal = {
                    "signal_id": f"pairs_trading_{int(time.time())}",
                    "strategy_id": "pairs_trading",
                    "strategy_type": "statistical_arbitrage",
                    "signal_type": signal_type,
                    "symbol": f"{symbol1}_{symbol2}",
                    "timestamp": datetime.now().isoformat(),
                    "price": pair_stats['spread'],
                    "confidence": confidence,
                    "metadata": {
                        "pair": pair,
                        "z_score": current_z_score,
                        "spread": pair_stats['spread'],
                        "correlation": pair_stats['correlation'],
                        "cointegration_score": pair_stats['cointegration_score'],
                        "lookback_period": self.lookback_period,
                        "z_score_threshold": self.z_score_threshold
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
                    self.logger.info(f"Pairs trading signal generated: {signal_type} for {pair} at {pair_stats['spread']:.4f}")
                
                return signal
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking pair opportunity: {e}")
            return None

    async def _calculate_pair_statistics(self, data1: List[Dict[str, Any]], data2: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate pair trading statistics."""
        try:
            # Convert to pandas DataFrames
            df1 = pd.DataFrame(data1)
            df2 = pd.DataFrame(data2)
            
            # Ensure same length
            min_length = min(len(df1), len(df2))
            df1 = df1.tail(min_length)
            df2 = df2.tail(min_length)
            
            # Get closing prices
            prices1 = df1['close'].values
            prices2 = df2['close'].values
            
            # Calculate correlation
            correlation = np.corrcoef(prices1, prices2)[0, 1]
            
            if abs(correlation) < self.min_correlation:
                return {
                    "cointegrated": False,
                    "correlation": correlation,
                    "spread": 0.0,
                    "current_z_score": 0.0,
                    "cointegration_score": 0.0
                }
            
            # Calculate spread
            spread = prices1 - prices2
            
            # Calculate z-score
            spread_mean = np.mean(spread)
            spread_std = np.std(spread)
            current_z_score = (spread[-1] - spread_mean) / spread_std if spread_std > 0 else 0
            
            # Simple cointegration test (ratio stability)
            ratio = prices1 / prices2
            ratio_std = np.std(ratio)
            cointegration_score = 1.0 / (1.0 + ratio_std)  # Higher score = more stable
            
            return {
                "cointegrated": cointegration_score > 0.7,  # Threshold for cointegration
                "correlation": correlation,
                "spread": spread[-1],
                "current_z_score": current_z_score,
                "cointegration_score": cointegration_score
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating pair statistics: {e}")
            return {
                "cointegrated": False,
                "correlation": 0.0,
                "spread": 0.0,
                "current_z_score": 0.0,
                "cointegration_score": 0.0
            }

    async def update_strategy_parameters(self, new_params: Dict[str, Any]) -> bool:
        """Update strategy parameters."""
        try:
            # Update configurable parameters
            if "z_score_threshold" in new_params:
                self.z_score_threshold = new_params["z_score_threshold"]
            if "lookback_period" in new_params:
                self.lookback_period = new_params["lookback_period"]
            if "min_correlation" in new_params:
                self.min_correlation = new_params["min_correlation"]
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
                "current_positions": self.current_positions,
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
                self.logger.info("Pairs trading strategy cleaned up successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")