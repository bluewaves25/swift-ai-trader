#!/usr/bin/env python3
"""
Cointegration Model Strategy - Fixed and Enhanced
Advanced statistical arbitrage using cointegration analysis.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from engine_agents.shared_utils import get_shared_redis

class CointegrationModelStrategy:
    """Cointegration model strategy for advanced statistical arbitrage."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.cointegration_threshold = config.get("cointegration_threshold", 0.05)  # 5% significance
        self.lookback_period = config.get("lookback_period", 100)  # 100 periods lookback
        self.min_correlation = config.get("min_correlation", 0.7)  # Minimum correlation
        self.z_score_threshold = config.get("z_score_threshold", 1.5)  # Z-score threshold
        self.position_threshold = config.get("position_threshold", 0.02)  # 2% position threshold
        self.stop_loss_threshold = config.get("stop_loss_threshold", 0.04)  # 4% stop loss

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect cointegration-based opportunities."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            # Get available asset pairs from data feeds
            asset_pairs = await self._get_available_asset_pairs()
            
            # Check each asset pair for cointegration opportunities
            for pair in asset_pairs:
                if len(pair) == 2:
                    opportunity = await self._check_pair_cointegration(pair, market_data)
                    if opportunity:
                        opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting cointegration opportunities: {e}")
            return []

    async def _get_available_asset_pairs(self) -> List[List[str]]:
        """Get available asset pairs from data feeds."""
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
                self.logger.error(f"Error getting available asset pairs: {e}")
            return []

    async def _check_pair_cointegration(self, pair: List[str], market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check for cointegration opportunity between two symbols."""
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
            
            # Calculate cointegration metrics
            coint_stats = await self._calculate_cointegration_stats(hist1, hist2)
            
            if not coint_stats['cointegrated']:
                return None
            
            # Check for trading signal
            current_z_score = coint_stats['current_z_score']
            
            if abs(current_z_score) > self.z_score_threshold:
                # Determine trade direction
                if current_z_score > self.z_score_threshold:
                    action = "short_long"  # Short symbol1, long symbol2
                    entry_price = coint_stats['spread']
                    stop_loss = entry_price * (1 + self.stop_loss_threshold)
                    take_profit = entry_price * (1 - self.position_threshold)
                else:
                    action = "long_short"  # Long symbol1, short symbol2
                    entry_price = coint_stats['spread']
                    stop_loss = entry_price * (1 - self.stop_loss_threshold)
                    take_profit = entry_price * (1 + self.position_threshold)
                
                opportunity = {
                    "type": "cointegration_model",
                    "strategy": "statistical_arbitrage",
                    "pair": pair,
                    "action": action,
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "confidence": min(abs(current_z_score) / (self.z_score_threshold * 1.5), 0.9),
                    "z_score": current_z_score,
                    "spread": coint_stats['spread'],
                    "correlation": coint_stats['correlation'],
                    "cointegration_score": coint_stats['cointegration_score'],
                    "half_life": coint_stats['half_life'],
                    "timestamp": int(time.time()),
                    "description": f"Cointegration {symbol1}-{symbol2}: Z-score {current_z_score:.2f}, Action {action}"
                }
                
                # Store in Redis for tracking with proper JSON serialization
                if self.redis_conn:
                    try:
                        import json
                        self.redis_conn.set(
                            f"strategy_engine:cointegration:{symbol1}_{symbol2}:{int(time.time())}", 
                            json.dumps(opportunity), 
                            ex=3600
                        )
                    except json.JSONEncodeError as e:
                        if self.logger:
                            self.logger.error(f"JSON encoding error storing cointegration opportunity: {e}")
                    except ConnectionError as e:
                        if self.logger:
                            self.logger.error(f"Redis connection error storing cointegration opportunity: {e}")
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Unexpected error storing cointegration opportunity: {e}")
                
                if self.logger:
                    self.logger.info(f"Cointegration opportunity: {opportunity['description']}")
                
                return opportunity
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking pair cointegration: {e}")
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

    async def _calculate_cointegration_stats(self, hist1: pd.DataFrame, hist2: pd.DataFrame) -> Dict[str, Any]:
        """Calculate cointegration statistics."""
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
                    "cointegration_score": 0.0,
                    "half_life": 0.0
                }
            
            # Calculate spread
            spread = prices1 - prices2
            
            # Calculate z-score
            spread_mean = np.mean(spread)
            spread_std = np.std(spread)
            current_z_score = (spread[-1] - spread_mean) / spread_std if spread_std > 0 else 0
            
            # Calculate cointegration score using ratio stability
            ratio = prices1 / prices2
            ratio_std = np.std(ratio)
            cointegration_score = 1.0 / (1.0 + ratio_std)  # Higher score = more stable
            
            # Calculate half-life (simplified)
            half_life = await self._calculate_half_life(spread)
            
            return {
                "cointegrated": cointegration_score > 0.8,  # Higher threshold for cointegration
                "correlation": correlation,
                "spread": spread[-1],
                "current_z_score": current_z_score,
                "cointegration_score": cointegration_score,
                "half_life": half_life
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating cointegration stats: {e}")
            return {
                "cointegrated": False,
                "correlation": 0.0,
                "spread": 0.0,
                "current_z_score": 0.0,
                "cointegration_score": 0.0,
                "half_life": 0.0
            }

    async def _calculate_half_life(self, spread: np.ndarray) -> float:
        """Calculate half-life of mean reversion."""
        try:
            if len(spread) < 2:
                return 0.0
            
            # Calculate spread changes
            spread_changes = np.diff(spread)
            spread_lagged = spread[:-1]
            
            # Simple regression to estimate half-life
            if len(spread_changes) > 0 and len(spread_lagged) > 0:
                # Avoid division by zero
                if np.std(spread_lagged) > 0:
                    beta = np.cov(spread_changes, spread_lagged)[0, 1] / np.var(spread_lagged)
                    if beta < 0:  # Mean reverting
                        half_life = -np.log(2) / beta
                        return min(half_life, 100.0)  # Cap at 100 periods
            
            return 0.0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating half-life: {e}")
            return 0.0

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Cointegration Model Strategy",
            "type": "statistical_arbitrage",
            "description": "Advanced statistical arbitrage using cointegration analysis",
            "parameters": {
                "cointegration_threshold": self.cointegration_threshold,
                "lookback_period": self.lookback_period,
                "min_correlation": self.min_correlation,
                "z_score_threshold": self.z_score_threshold,
                "position_threshold": self.position_threshold,
                "stop_loss_threshold": self.stop_loss_threshold
            },
            "timeframe": "fast",  # 100ms tier
            "asset_types": ["crypto", "forex", "stocks", "commodities"],
            "execution_speed": "fast"
        }