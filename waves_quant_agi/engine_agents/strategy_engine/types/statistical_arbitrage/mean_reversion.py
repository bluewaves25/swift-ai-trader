#!/usr/bin/env python3
"""
Mean Reversion Strategy - Fixed and Enhanced
Statistical arbitrage using mean reversion principles.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from engine_agents.shared_utils import get_shared_redis

class MeanReversionStrategy:
    """Mean reversion strategy using statistical arbitrage."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.std_multiplier = config.get("std_multiplier", 2.0)  # Standard deviation multiplier
        self.lookback_period = config.get("lookback_period", 50)  # 50 periods lookback
        self.mean_period = config.get("mean_period", 20)  # 20 periods for mean calculation
        self.min_deviation = config.get("min_deviation", 0.01)  # 1% minimum deviation
        self.position_threshold = config.get("position_threshold", 0.03)  # 3% position threshold
        self.stop_loss_threshold = config.get("stop_loss_threshold", 0.05)  # 5% stop loss

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect mean reversion opportunities."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            # Get available symbols from data feeds
            available_symbols = await self._get_available_symbols()
            
            for data in market_data:
                symbol = data.get("symbol", "")
                if not symbol or symbol not in available_symbols:
                    continue
                
                opportunity = await self._check_mean_reversion_opportunity(symbol, data)
                if opportunity:
                    opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting mean reversion opportunities: {e}")
            return []

    async def _get_available_symbols(self) -> List[str]:
        """Get available symbols from data feeds."""
        try:
            if not self.redis_conn:
                return []
            
            # Get available symbols from data feeds
            symbols_key = "data_feeds:available_symbols"
            symbols_data = self.redis_conn.get(symbols_key)
            
            if symbols_data:
                import json
                return json.loads(symbols_data)
            
            return []
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting available symbols: {e}")
            return []

    async def _check_mean_reversion_opportunity(self, symbol: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for mean reversion opportunity in a specific symbol."""
        try:
            close_price = float(data.get("close", 0.0))
            if close_price <= 0:
                return None
            
            # Get historical data
            historical_data = await self._get_historical_data(symbol)
            if historical_data is None or len(historical_data) < self.lookback_period:
                return None
            
            # Calculate mean reversion metrics
            mean_rev_stats = await self._calculate_mean_reversion_stats(historical_data, close_price)
            
            if not mean_rev_stats['opportunity_detected']:
                return None
            
            # Determine trade direction
            if mean_rev_stats['deviation'] > 0:
                action = "sell"  # Price above mean, expect reversion down
                entry_price = close_price
                stop_loss = close_price * (1 + self.stop_loss_threshold)
                take_profit = close_price * (1 - mean_rev_stats['expected_reversion'])
            else:
                action = "buy"  # Price below mean, expect reversion up
                entry_price = close_price
                stop_loss = close_price * (1 - self.stop_loss_threshold)
                take_profit = close_price * (1 + mean_rev_stats['expected_reversion'])
            
            opportunity = {
                "type": "mean_reversion",
                "strategy": "statistical_arbitrage",
                "symbol": symbol,
                "action": action,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "confidence": min(abs(mean_rev_stats['deviation']) / (self.std_multiplier * 0.5), 0.9),
                "deviation": mean_rev_stats['deviation'],
                "z_score": mean_rev_stats['z_score'],
                "expected_reversion": mean_rev_stats['expected_reversion'],
                "volatility": mean_rev_stats['volatility'],
                "timestamp": int(time.time()),
                "description": f"Mean reversion for {symbol}: Deviation {mean_rev_stats['deviation']:.4f}, Action {action}"
            }
            
            # Store in Redis for tracking with proper JSON serialization
            if self.redis_conn:
                try:
                    import json
                    self.redis_conn.set(
                        f"strategy_engine:mean_reversion:{symbol}:{int(time.time())}", 
                        json.dumps(opportunity), 
                        ex=3600
                    )
                except json.JSONEncodeError as e:
                    if self.logger:
                        self.logger.error(f"JSON encoding error storing mean reversion opportunity: {e}")
                except ConnectionError as e:
                    if self.logger:
                        self.logger.error(f"Redis connection error storing mean reversion opportunity: {e}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Unexpected error storing mean reversion opportunity: {e}")
            
            if self.logger:
                self.logger.info(f"Mean reversion opportunity: {opportunity['description']}")
            
            return opportunity
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking mean reversion opportunity: {e}")
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

    async def _calculate_mean_reversion_stats(self, historical_data: pd.DataFrame, current_price: float) -> Dict[str, Any]:
        """Calculate mean reversion statistics."""
        try:
            # Calculate rolling mean and standard deviation
            rolling_mean = historical_data['close'].rolling(window=self.mean_period).mean()
            rolling_std = historical_data['close'].rolling(window=self.mean_period).std()
            
            # Get current values
            current_mean = rolling_mean.iloc[-1]
            current_std = rolling_std.iloc[-1]
            
            if pd.isna(current_mean) or pd.isna(current_std) or current_std == 0:
                return {
                    "opportunity_detected": False,
                    "deviation": 0.0,
                    "z_score": 0.0,
                    "expected_reversion": 0.0,
                    "volatility": 0.0
                }
            
            # Calculate deviation and z-score
            deviation = (current_price - current_mean) / current_mean
            z_score = (current_price - current_mean) / current_std
            
            # Check if opportunity exists
            opportunity_detected = abs(z_score) > self.std_multiplier and abs(deviation) > self.min_deviation
            
            # Calculate expected reversion
            expected_reversion = min(abs(deviation) * 0.5, self.position_threshold)
            
            # Calculate volatility
            volatility = current_std / current_mean if current_mean > 0 else 0
            
            return {
                "opportunity_detected": opportunity_detected,
                "deviation": deviation,
                "z_score": z_score,
                "expected_reversion": expected_reversion,
                "volatility": volatility
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating mean reversion stats: {e}")
            return {
                "opportunity_detected": False,
                "deviation": 0.0,
                "z_score": 0.0,
                "expected_reversion": 0.0,
                "volatility": 0.0
            }

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Mean Reversion Strategy",
            "type": "statistical_arbitrage",
            "description": "Statistical arbitrage using mean reversion principles",
            "parameters": {
                "std_multiplier": self.std_multiplier,
                "lookback_period": self.lookback_period,
                "mean_period": self.mean_period,
                "min_deviation": self.min_deviation,
                "position_threshold": self.position_threshold,
                "stop_loss_threshold": self.stop_loss_threshold
            },
            "timeframe": "fast",  # 100ms tier
            "asset_types": ["crypto", "forex", "commodities"],
            "execution_speed": "fast"
        } 