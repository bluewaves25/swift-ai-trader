#!/usr/bin/env python3
"""
Adaptive Quote Strategy - Fixed and Enhanced
Market making with adaptive quote adjustment.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from engine_agents.shared_utils import get_shared_redis

class AdaptiveQuoteStrategy:
    """Adaptive quote strategy for market making."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.base_spread = config.get("base_spread", 0.001)  # 0.1% base spread
        self.volatility_multiplier = config.get("volatility_multiplier", 2.0)  # Volatility adjustment
        self.volume_multiplier = config.get("volume_multiplier", 1.5)  # Volume adjustment
        self.min_quote_size = config.get("min_quote_size", 100)  # Minimum quote size
        self.max_quote_size = config.get("max_quote_size", 10000)  # Maximum quote size
        self.quote_refresh_ms = config.get("quote_refresh_ms", 100)  # 100ms refresh rate
        
        # Market making state
        self.active_quotes = {}
        self.quote_history = []

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect market making opportunities."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            for data in market_data:
                symbol = data.get("symbol", "")
                if not symbol:
                    continue
                
                opportunity = await self._check_market_making_opportunity(symbol, data)
                if opportunity:
                    opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting market making opportunities: {e}")
            return []

    async def _check_market_making_opportunity(self, symbol: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for market making opportunity in a specific symbol."""
        try:
            bid = float(data.get("bid", 0.0))
            ask = float(data.get("ask", 0.0))
            volume = float(data.get("volume", 0.0))
            
            if bid <= 0 or ask <= 0:
                return None
            
            # Get historical data for volatility calculation
            historical_data = await self._get_historical_data(symbol)
            if historical_data is None:
                return None
            
            # Calculate market making metrics
            mm_metrics = await self._calculate_market_making_metrics(
                bid, ask, volume, historical_data
            )
            
            if not mm_metrics['profitable']:
                return None
            
            # Generate adaptive quotes
            quotes = await self._generate_adaptive_quotes(symbol, mm_metrics)
            
            opportunity = {
                "type": "adaptive_quote",
                "strategy": "market_making",
                "symbol": symbol,
                "action": "provide_liquidity",
                "bid_quote": quotes['bid_quote'],
                "ask_quote": quotes['ask_quote'],
                "quote_size": quotes['quote_size'],
                "confidence": mm_metrics['confidence'],
                "spread": mm_metrics['spread'],
                "volatility": mm_metrics['volatility'],
                "volume_profile": mm_metrics['volume_profile'],
                "refresh_rate_ms": self.quote_refresh_ms,
                "timestamp": int(time.time()),
                "description": f"Adaptive quotes for {symbol}: Bid {quotes['bid_quote']:.6f}, Ask {quotes['ask_quote']:.6f}"
            }
            
            # Store in Redis
            if self.redis_conn:
                self.redis_conn.set(
                    f"strategy_engine:adaptive_quote:{symbol}:{int(time.time())}", 
                    str(opportunity), 
                    ex=3600
                )
            
            if self.logger:
                self.logger.info(f"Adaptive quote opportunity: {opportunity['description']}")
            
            return opportunity
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking market making opportunity: {e}")
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

    async def _calculate_market_making_metrics(self, bid: float, ask: float, volume: float, 
                                             historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate market making metrics."""
        try:
            # Calculate current spread
            mid_price = (bid + ask) / 2
            spread = (ask - bid) / mid_price if mid_price > 0 else 0
            
            # Calculate volatility
            if len(historical_data) > 1:
                returns = historical_data['close'].pct_change().dropna()
                volatility = returns.std() if len(returns) > 0 else 0
            else:
                volatility = 0
            
            # Calculate volume profile
            if len(historical_data) > 0:
                avg_volume = historical_data['volume'].mean()
                volume_profile = volume / avg_volume if avg_volume > 0 else 1.0
            else:
                volume_profile = 1.0
            
            # Determine if market making is profitable
            min_spread = self.base_spread * (1 + volatility * self.volatility_multiplier)
            profitable = spread > min_spread
            
            # Calculate confidence
            confidence = min(spread / (min_spread * 1.5), 0.9) if profitable else 0.0
            
            return {
                "profitable": profitable,
                "confidence": confidence,
                "spread": spread,
                "volatility": volatility,
                "volume_profile": volume_profile,
                "min_spread": min_spread
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating market making metrics: {e}")
            return {
                "profitable": False,
                "confidence": 0.0,
                "spread": 0.0,
                "volatility": 0.0,
                "volume_profile": 1.0,
                "min_spread": self.base_spread
            }

    async def _generate_adaptive_quotes(self, symbol: str, mm_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate adaptive bid and ask quotes."""
        try:
            # Get current market data
            current_data = await self._get_current_market_data(symbol)
            if not current_data:
                return {
                    "bid_quote": 0.0,
                    "ask_quote": 0.0,
                    "quote_size": self.min_quote_size
                }
            
            mid_price = (current_data['bid'] + current_data['ask']) / 2
            
            # Calculate adaptive spread
            adaptive_spread = self.base_spread * (1 + mm_metrics['volatility'] * self.volatility_multiplier)
            
            # Adjust for volume
            if mm_metrics['volume_profile'] > 1.5:
                adaptive_spread *= 0.8  # Tighter spread for high volume
            elif mm_metrics['volume_profile'] < 0.5:
                adaptive_spread *= 1.2  # Wider spread for low volume
            
            # Generate quotes
            bid_quote = mid_price * (1 - adaptive_spread / 2)
            ask_quote = mid_price * (1 + adaptive_spread / 2)
            
            # Calculate quote size
            quote_size = self.min_quote_size
            if mm_metrics['volume_profile'] > 1.0:
                quote_size = min(self.max_quote_size, quote_size * mm_metrics['volume_profile'])
            
            quote_data = {
                "bid_quote": bid_quote,
                "ask_quote": ask_quote,
                "quote_size": quote_size
            }
            
            # Store quotes in Redis with proper JSON serialization
            if self.redis_conn:
                try:
                    import json
                    self.redis_conn.set(
                        f"strategy_engine:adaptive_quote:{symbol}:{int(time.time())}", 
                        json.dumps(quote_data), 
                        ex=3600
                    )
                except json.JSONEncodeError as e:
                    if self.logger:
                        self.logger.error(f"JSON encoding error storing adaptive quote: {e}")
                except ConnectionError as e:
                    if self.logger:
                        self.logger.error(f"Redis connection error storing adaptive quote: {e}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Unexpected error storing adaptive quote: {e}")
            
            return quote_data
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating adaptive quotes: {e}")
            return {
                "bid_quote": 0.0,
                "ask_quote": 0.0,
                "quote_size": self.min_quote_size
            }

    async def _get_current_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current market data for a symbol."""
        try:
            if not self.redis_conn:
                return None
            
            current_key = f"market_data:{symbol}"
            current_data = self.redis_conn.hgetall(current_key)
            
            if current_data:
                return {
                    "bid": float(current_data.get("bid", 0)),
                    "ask": float(current_data.get("ask", 0)),
                    "volume": float(current_data.get("volume", 0))
                }
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting current market data: {e}")
            return None

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Adaptive Quote Strategy",
            "type": "market_making",
            "description": "Market making with adaptive quote adjustment",
            "parameters": {
                "base_spread": self.base_spread,
                "volatility_multiplier": self.volatility_multiplier,
                "volume_multiplier": self.volume_multiplier,
                "min_quote_size": self.min_quote_size,
                "max_quote_size": self.max_quote_size,
                "quote_refresh_ms": self.quote_refresh_ms
            },
            "timeframe": "ultra_hft",  # 1ms tier
            "asset_types": ["crypto", "forex", "stocks"],
            "execution_speed": "ultra_fast"
        }