#!/usr/bin/env python3
"""
Volatility Responsive Market Making Strategy - Fixed and Enhanced
Market making strategy that responds to volatility changes.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
from engine_agents.shared_utils import get_shared_redis

class VolatilityResponsiveMM:
    """Volatility responsive market making strategy."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        self.volatility_threshold = config.get("volatility_threshold", 0.3)  # Volatility trigger

    async def generate_mm_signal(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate market-making signals based on volatility levels."""
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
                    
                volatility = float(data.get("volatility", 0.0))
                mid_price = float(data.get("mid_price", 0.0))
                
                if mid_price <= 0:
                    continue
                
                # Get fee information
                fee_score = await self._get_fee_score(symbol)
                
                # Calculate spread based on volatility
                spread_factor = 0.002 if volatility < self.volatility_threshold else 0.005
                bid_price = mid_price * (1 - spread_factor)
                ask_price = mid_price * (1 + spread_factor)

                if bid_price > 0 and ask_price > bid_price + fee_score:
                    opportunity = {
                        "type": "volatility_responsive_mm",
                        "symbol": symbol,
                        "bid_price": bid_price,
                        "ask_price": ask_price,
                        "volatility": volatility,
                        "timestamp": int(time.time()),
                        "description": f"Volatility-responsive MM for {symbol}: Bid {bid_price:.2f}, Ask {ask_price:.2f}"
                    }
                    opportunities.append(opportunity)
                    
                    # Store volatility quotes in Redis with proper JSON serialization
                    if self.redis_conn:
                        try:
                            import json
                            self.redis_conn.set(
                                f"strategy_engine:volatility_mm:{symbol}:{int(time.time())}", 
                                json.dumps(opportunity), 
                                ex=3600
                            )
                        except json.JSONEncodeError as e:
                            if self.logger:
                                self.logger.error(f"JSON encoding error storing volatility quotes: {e}")
                        except ConnectionError as e:
                            if self.logger:
                                self.logger.error(f"Redis connection error storing volatility quotes: {e}")
                        except Exception as e:
                            if self.logger:
                                self.logger.error(f"Unexpected error storing volatility quotes: {e}")
                    
                    if self.logger:
                        self.logger.info(f"Volatility MM opportunity: {opportunity['description']}")

            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating volatility MM signal: {e}")
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

    async def _get_fee_score(self, symbol: str) -> float:
        """Get fee score for a symbol."""
        try:
            if not self.redis_conn:
                return 0.001  # Default fee
            
            fee_key = f"fee_monitor:{symbol}:fee_score"
            fee_score = self.redis_conn.get(fee_key)
            
            if fee_score:
                return float(fee_score)
            
            return 0.001  # Default fee
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting fee score: {e}")
            return 0.001

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Volatility Responsive Market Making Strategy",
            "type": "market_making",
            "description": "Market making strategy that responds to volatility changes",
            "parameters": {
                "volatility_threshold": self.volatility_threshold
            },
            "timeframe": "fast",  # 100ms tier
            "asset_types": ["forex", "crypto", "stocks"],
            "execution_speed": "ultra_fast"
        }