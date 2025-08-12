#!/usr/bin/env python3
"""
Pairs Trading Strategy - Fixed and Enhanced
Statistical arbitrage using cointegrated pairs.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from engine_agents.shared_utils import get_shared_redis

class PairsTradingStrategy:
    """Pairs trading strategy using statistical arbitrage."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.z_score_threshold = config.get("z_score_threshold", 2.0)  # Z-score threshold
        self.lookback_period = config.get("lookback_period", 60)  # 60 periods lookback
        self.min_correlation = config.get("min_correlation", 0.8)  # Minimum correlation
        self.position_threshold = config.get("position_threshold", 0.02)  # 2% position threshold
        self.stop_loss_threshold = config.get("stop_loss_threshold", 0.05)  # 5% stop loss

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect pairs trading opportunities."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            # Get available trading pairs from data feeds
            trading_pairs = await self._get_trading_pairs()
            
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

    async def _get_trading_pairs(self) -> List[List[str]]:
        """Get available trading pairs from data feeds."""
        try:
            if not self.redis_conn:
                return []
            
            # Get available symbols from data feeds
            symbols_key = "data_feeds:available_symbols"
            symbols_data = self.redis_conn.get(symbols_key)
            
            if symbols_data:
                import json
                symbols = json.loads(symbols_data)
                
                # Generate pairs from available symbols
                pairs = []
                for i in range(len(symbols)):
                    for j in range(i + 1, len(symbols)):
                        pairs.append([symbols[i], symbols[j]])
                
                return pairs[:20]  # Limit to 20 pairs for performance
            
            return []
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting trading pairs: {e}")
            return []

    async def _check_pair_opportunity(self, pair: List[str], market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check for trading opportunity in a specific pair."""
        try:
            symbol1, symbol2 = pair
            
            # Get historical data for both symbols
            hist1 = await self._get_historical_data(symbol1)
            hist2 = await self._get_historical_data(symbol2)
            
            if hist1 is None or hist2 is None:
                return None
            
            # Check if we have enough data
            if len(hist1) < self.lookback_period or len(hist2) < self.lookback_period:
                return None
            
            # Calculate pair statistics
            pair_stats = await self._calculate_pair_statistics(hist1, hist2)
            
            if not pair_stats['cointegrated']:
                return None
            
            # Check for trading signal
            current_z_score = pair_stats['current_z_score']
            
            if abs(current_z_score) > self.z_score_threshold:
                # Determine trade direction
                if current_z_score > self.z_score_threshold:
                    action = "short_long"  # Short symbol1, long symbol2
                    entry_price = pair_stats['spread']
                    stop_loss = entry_price * (1 + self.stop_loss_threshold)
                    take_profit = entry_price * (1 - self.position_threshold)
                else:
                    action = "long_short"  # Long symbol1, short symbol2
                    entry_price = pair_stats['spread']
                    stop_loss = entry_price * (1 - self.stop_loss_threshold)
                    take_profit = entry_price * (1 + self.position_threshold)
                
                opportunity = {
                    "type": "pairs_trading",
                    "strategy": "statistical_arbitrage",
                    "pair": pair,
                    "action": action,
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "confidence": min(abs(current_z_score) / (self.z_score_threshold * 1.5), 0.9),
                    "z_score": current_z_score,
                    "spread": pair_stats['spread'],
                    "correlation": pair_stats['correlation'],
                    "cointegration": pair_stats['cointegration_score'],
                    "timestamp": int(time.time()),
                    "description": f"Pairs trading {pair}: Z-score {current_z_score:.2f}, Action {action}"
                }
                
                # Store in Redis for tracking with proper JSON serialization
                if self.redis_conn:
                    try:
                        import json
                        self.redis_conn.set(
                            f"strategy_engine:pairs_trading:{':'.join(pair)}:{int(time.time())}", 
                            json.dumps(opportunity), 
                            ex=3600
                        )
                    except json.JSONEncodeError as e:
                        if self.logger:
                            self.logger.error(f"JSON encoding error storing pairs trading opportunity: {e}")
                    except ConnectionError as e:
                        if self.logger:
                            self.logger.error(f"Redis connection error storing pairs trading opportunity: {e}")
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Unexpected error storing pairs trading opportunity: {e}")
                
                if self.logger:
                    self.logger.info(f"Pairs trading opportunity: {opportunity['description']}")
                
                return opportunity
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking pair opportunity: {e}")
            return None

    async def _get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get historical data for a symbol."""
        try:
            if not self.redis_conn:
                return None
            
            historical_key = f"market_data:{symbol}:history"
            historical_data = self.redis_conn.get(historical_key)
            
            if historical_data:
                import json
                return pd.DataFrame(json.loads(historical_data))
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting historical data for {symbol}: {e}")
            return None

    async def _calculate_pair_statistics(self, hist1: pd.DataFrame, hist2: pd.DataFrame) -> Dict[str, Any]:
        """Calculate pair trading statistics."""
        try:
            # Ensure same length
            min_length = min(len(hist1), len(hist2))
            hist1 = hist1.tail(min_length)
            hist2 = hist2.tail(min_length)
            
            # Get closing prices
            prices1 = hist1['close'].values
            prices2 = hist2['close'].values
            
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

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Pairs Trading Strategy",
            "type": "statistical_arbitrage",
            "description": "Statistical arbitrage using cointegrated pairs",
            "parameters": {
                "z_score_threshold": self.z_score_threshold,
                "lookback_period": self.lookback_period,
                "min_correlation": self.min_correlation,
                "position_threshold": self.position_threshold,
                "stop_loss_threshold": self.stop_loss_threshold
            },
            "timeframe": "fast",  # 100ms tier
            "asset_types": ["crypto", "forex", "stocks"],
            "execution_speed": "fast"
        }