#!/usr/bin/env python3
"""
Spread Adjuster Strategy - Fixed and Enhanced
Market making strategy that dynamically adjusts spreads.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
from engine_agents.shared_utils import get_shared_redis

class SpreadAdjusterStrategy:
    """Spread adjuster strategy for dynamic market making."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.base_spread = config.get("base_spread", 0.001)  # 0.1% base spread
        self.volatility_multiplier = config.get("volatility_multiplier", 2.0)
        self.volume_threshold = config.get("volume_threshold", 1000)
        self.max_spread = config.get("max_spread", 0.01)  # 1% maximum spread
        self.min_spread = config.get("min_spread", 0.0001)  # 0.01% minimum spread
        self.adjustment_frequency = config.get("adjustment_frequency", 60)  # 60 seconds

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect spread adjustment opportunities."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            # Get available trading pairs from data feeds
            trading_pairs = await self._get_trading_pairs()
            
            for pair in trading_pairs:
                opportunity = await self._check_spread_adjustment(pair, market_data)
                if opportunity:
                    opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting spread adjustment opportunities: {e}")
            return []

    async def _get_trading_pairs(self) -> List[str]:
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
                
                # Filter for suitable market making pairs
                suitable_pairs = []
                for symbol in symbols:
                    if any(asset_type in symbol.lower() for asset_type in ["usd", "eur", "btc", "eth"]):
                        suitable_pairs.append(symbol)
                
                return suitable_pairs[:10]  # Limit to 10 pairs for performance
            
            return []
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting trading pairs: {e}")
            return []

    async def _check_spread_adjustment(self, pair: str, market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check for spread adjustment opportunity."""
        try:
            # Get current market data for pair
            pair_data = await self._get_symbol_market_data(pair, market_data)
            if not pair_data:
                return None
            
            # Calculate current spread metrics
            spread_metrics = await self._calculate_spread_metrics(pair, pair_data)
            
            if not spread_metrics['adjustment_needed']:
                return None
            
            # Calculate optimal spread
            optimal_spread = await self._calculate_optimal_spread(spread_metrics)
            
            # Determine action
            current_spread = spread_metrics['current_spread']
            if optimal_spread > current_spread:
                action = "widen_spread"
            elif optimal_spread < current_spread:
                action = "tighten_spread"
            else:
                return None
            
            opportunity = {
                "type": "spread_adjuster",
                "strategy": "market_making",
                "symbol": pair,
                "action": action,
                "current_spread": current_spread,
                "optimal_spread": optimal_spread,
                "volatility": spread_metrics['volatility'],
                "volume": spread_metrics['volume'],
                "bid_price": spread_metrics['bid_price'],
                "ask_price": spread_metrics['ask_price'],
                "confidence": spread_metrics['confidence'],
                "timestamp": int(time.time()),
                "description": f"Spread adjustment for {pair}: {action} from {current_spread:.4f} to {optimal_spread:.4f}"
            }
            
            # Store in Redis with proper JSON serialization
            if self.redis_conn:
                try:
                    import json
                    self.redis_conn.set(
                        f"strategy_engine:spread_adjuster:{pair}:{int(time.time())}", 
                        json.dumps(opportunity), 
                        ex=3600
                    )
                except json.JSONEncodeError as e:
                    if self.logger:
                        self.logger.error(f"JSON encoding error storing spread adjustment: {e}")
                except ConnectionError as e:
                    if self.logger:
                        self.logger.error(f"Redis connection error storing spread adjustment: {e}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Unexpected error storing spread adjustment: {e}")
            
            if self.logger:
                self.logger.info(f"Spread adjustment opportunity: {opportunity['description']}")
            
            return opportunity
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking spread adjustment: {e}")
            return None

    async def _get_symbol_market_data(self, symbol: str, market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get market data for a specific symbol."""
        try:
            for data in market_data:
                if data.get("symbol") == symbol:
                    return data
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting symbol market data: {e}")
            return None

    async def _calculate_spread_metrics(self, pair: str, pair_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate spread adjustment metrics."""
        try:
            bid_price = float(pair_data.get("bid", 0.0))
            ask_price = float(pair_data.get("ask", 0.0))
            volume = float(pair_data.get("volume", 0.0))
            
            if bid_price <= 0 or ask_price <= 0:
                return {
                    "adjustment_needed": False,
                    "current_spread": 0.0,
                    "volatility": 0.0,
                    "volume": 0.0,
                    "bid_price": 0.0,
                    "ask_price": 0.0,
                    "confidence": 0.0
                }
            
            # Calculate current spread
            current_spread = (ask_price - bid_price) / bid_price
            
            # Get historical data for volatility calculation
            historical_data = await self._get_historical_data(pair)
            
            if historical_data is None:
                return {
                    "adjustment_needed": False,
                    "current_spread": current_spread,
                    "volatility": 0.0,
                    "volume": volume,
                    "bid_price": bid_price,
                    "ask_price": ask_price,
                    "confidence": 0.0
                }
            
            # Calculate volatility
            volatility = historical_data['close'].pct_change().std() if len(historical_data) > 1 else 0.0
            
            # Determine if adjustment is needed
            volume_threshold_met = volume > self.volume_threshold
            spread_deviation = abs(current_spread - self.base_spread) / self.base_spread if self.base_spread > 0 else 0
            
            adjustment_needed = volume_threshold_met and spread_deviation > 0.2  # 20% deviation
            
            # Calculate confidence
            confidence = min(
                (volume / self.volume_threshold) * (spread_deviation / 0.2), 
                0.9
            )
            
            return {
                "adjustment_needed": adjustment_needed,
                "current_spread": current_spread,
                "volatility": volatility,
                "volume": volume,
                "bid_price": bid_price,
                "ask_price": ask_price,
                "confidence": confidence
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating spread metrics: {e}")
            return {
                "adjustment_needed": False,
                "current_spread": 0.0,
                "volatility": 0.0,
                "volume": 0.0,
                "bid_price": 0.0,
                "ask_price": 0.0,
                "confidence": 0.0
            }

    async def _calculate_optimal_spread(self, spread_metrics: Dict[str, Any]) -> float:
        """Calculate optimal spread based on market conditions."""
        try:
            base_spread = self.base_spread
            volatility = spread_metrics['volatility']
            volume = spread_metrics['volume']
            
            # Adjust for volatility
            volatility_adjustment = min(volatility * self.volatility_multiplier, 0.005)
            
            # Adjust for volume (higher volume = tighter spread)
            volume_adjustment = -0.0001 * (volume / self.volume_threshold) if volume > self.volume_threshold else 0
            
            # Calculate optimal spread
            optimal_spread = base_spread + volatility_adjustment + volume_adjustment
            
            # Ensure within bounds
            optimal_spread = max(min(optimal_spread, self.max_spread), self.min_spread)
            
            return optimal_spread
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating optimal spread: {e}")
            return self.base_spread

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

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Spread Adjuster Strategy",
            "type": "market_making",
            "description": "Market making strategy that dynamically adjusts spreads",
            "parameters": {
                "base_spread": self.base_spread,
                "volatility_multiplier": self.volatility_multiplier,
                "volume_threshold": self.volume_threshold,
                "max_spread": self.max_spread,
                "min_spread": self.min_spread,
                "adjustment_frequency": self.adjustment_frequency
            },
            "timeframe": "fast",  # 100ms tier
            "asset_types": ["forex", "crypto"],
            "execution_speed": "ultra_fast"
        }