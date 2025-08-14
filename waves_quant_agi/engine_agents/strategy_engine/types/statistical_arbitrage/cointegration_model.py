#!/usr/bin/env python3
"""
Cointegration Model Strategy - Statistical Arbitrage
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


class CointegrationModelStrategy:
    """Cointegration-based statistical arbitrage strategy."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.lookback_period = config.get("lookback_period", 100)
        self.cointegration_threshold = config.get("cointegration_threshold", 0.05)
        self.z_score_threshold = config.get("z_score_threshold", 2.0)
        self.min_correlation = config.get("min_correlation", 0.7)
        
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
                self.logger.error(f"Failed to initialize cointegration strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect cointegration-based opportunities."""
        if not market_data or len(market_data) < self.lookback_period:
            return []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').tail(self.lookback_period)
            
            # Get unique symbols
            symbols = df['symbol'].unique()
            if len(symbols) < 2:
                return []
            
            opportunities = []
            
            # Check pairs for cointegration
            for i in range(len(symbols)):
                for j in range(i + 1, len(symbols)):
                    symbol1, symbol2 = symbols[i], symbols[j]
                    
                    # Get data for both symbols
                    data1 = df[df['symbol'] == symbol1]['close'].values
                    data2 = df[df['symbol'] == symbol2]['close'].values
                    
                    if len(data1) < self.lookback_period or len(data2) < self.lookback_period:
                        continue
                    
                    # Calculate cointegration
                    cointegration_result = self._calculate_cointegration(data1, data2)
                    
                    if cointegration_result['is_cointegrated']:
                        # Check for trading signal
                        z_score = cointegration_result['z_score']
                        if abs(z_score) > self.z_score_threshold:
                            signal = self._generate_signal(symbol1, symbol2, z_score, cointegration_result)
                            if signal:
                                self.trading_context.store_signal(signal)
                                opportunities.append(signal)
                                self.strategy_performance["total_signals"] += 1
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting cointegration opportunities: {e}")
            return []

    def _calculate_cointegration(self, prices1: np.ndarray, prices2: np.ndarray) -> Dict[str, Any]:
        """Calculate cointegration between two price series."""
        try:
            # Calculate correlation
            correlation = np.corrcoef(prices1, prices2)[0, 1]
            
            if abs(correlation) < self.min_correlation:
                return {"is_cointegrated": False}
            
            # Calculate spread
            spread = prices1 - prices2
            
            # Calculate z-score
            spread_mean = np.mean(spread)
            spread_std = np.std(spread)
            z_score = (spread[-1] - spread_mean) / spread_std if spread_std > 0 else 0
            
            # Simple cointegration test
            ratio = prices1 / prices2
            ratio_std = np.std(ratio)
            cointegration_score = 1.0 / (1.0 + ratio_std)
            
            return {
                "is_cointegrated": cointegration_score > 0.8,
                "z_score": z_score,
                "correlation": correlation,
                "cointegration_score": cointegration_score,
                "spread": spread[-1]
            }
            
        except Exception as e:
            return {"is_cointegrated": False}

    def _generate_signal(self, symbol1: str, symbol2: str, z_score: float, cointegration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signal."""
        try:
            signal_type = "SHORT_LONG" if z_score > 0 else "LONG_SHORT"
            confidence = min(abs(z_score) / (self.z_score_threshold * 1.5), 1.0)
            
            signal = {
                "signal_id": f"cointegration_{int(time.time())}",
                "strategy_id": "cointegration_model",
                "strategy_type": "statistical_arbitrage",
                "signal_type": signal_type,
                "symbol": f"{symbol1}_{symbol2}",
                "timestamp": datetime.now().isoformat(),
                "price": cointegration_result.get("spread", 0.0),
                "confidence": confidence,
                "metadata": {
                    "z_score": z_score,
                    "correlation": cointegration_result.get("correlation", 0.0),
                    "cointegration_score": cointegration_result.get("cointegration_score", 0.0)
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")