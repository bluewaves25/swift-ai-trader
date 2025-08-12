#!/usr/bin/env python3
"""
Breakout Strategy - Fixed and Enhanced
Detects breakout opportunities after volatility contraction.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
from engine_agents.shared_utils import get_shared_redis

class BreakoutStrategy:
    """Breakout strategy for detecting price breakouts after volatility contraction."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection instead of creating new one
        self.redis_conn = get_shared_redis()
        self.breakout_threshold = config.get("breakout_threshold", 0.02)  # 2% breakout level
        
        # Strategy parameters
        self.min_volume_threshold = config.get("min_volume_threshold", 1.5)
        self.confirmation_periods = config.get("confirmation_periods", 3)
        self.volatility_lookback = config.get("volatility_lookback", 20)

    async def detect_breakout(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect breakout opportunities after volatility contraction."""
        try:
            opportunities = []
            
            if market_data.empty:
                return opportunities
                
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTCUSD")
                high = float(row.get("high", 0.0))
                low = float(row.get("low", 0.0))
                close = float(row.get("close", 0.0))
                volume = float(row.get("volume", 0.0))
                
                # Get historical data for confirmation
                historical_data = await self._get_historical_data(symbol)
                if not historical_data:
                    continue
                
                # Calculate breakout metrics
                breakout_score = await self._calculate_breakout_score(
                    high, low, close, volume, historical_data
                )
                
                if breakout_score > self.breakout_threshold:
                    opportunity = {
                        "type": "breakout_strategy",
                        "strategy": "breakout",
                        "symbol": symbol,
                        "action": "buy" if close > high else "sell",
                        "entry_price": close,
                        "stop_loss": low * 0.995 if close > high else high * 1.005,
                        "take_profit": close * 1.02 if close > high else close * 0.98,
                        "confidence": min(breakout_score / self.breakout_threshold, 0.95),
                        "breakout_level": high if close > high else low,
                        "volume_confirmation": volume > self.min_volume_threshold,
                        "timestamp": int(time.time()),
                        "description": f"Breakout detected for {symbol}: Score {breakout_score:.4f}"
                    }
                    opportunities.append(opportunity)
                    
                    # Store in Redis for tracking with proper JSON serialization
                    if self.redis_conn:
                        try:
                            import json
                            self.redis_conn.set(
                                f"strategy_engine:breakout:{symbol}:{int(time.time())}", 
                                json.dumps(opportunity), 
                                ex=3600
                            )
                        except json.JSONEncodeError as e:
                            if self.logger:
                                self.logger.error(f"JSON encoding error storing breakout opportunity: {e}")
                        except ConnectionError as e:
                            if self.logger:
                                self.logger.error(f"Redis connection error storing breakout opportunity: {e}")
                        except Exception as e:
                            if self.logger:
                                self.logger.error(f"Unexpected error storing breakout opportunity: {e}")
                    
                    # Log if logger available
                    if self.logger:
                        self.logger.info(f"Breakout opportunity: {opportunity['description']}")

            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting breakout: {e}")
            return []

    async def _get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get historical data for breakout confirmation."""
        try:
            if not self.redis_conn:
                return None
                
            # Get recent market data from Redis
            historical_key = f"market_data:{symbol}:history"
            historical_data = self.redis_conn.get(historical_key)
            
            if historical_data:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(historical_data, bytes):
                        historical_data = historical_data.decode('utf-8')
                    elif not isinstance(historical_data, str):
                        return None
                        
                    parsed_data = json.loads(historical_data)
                    if isinstance(parsed_data, list):
                        return pd.DataFrame(parsed_data)
                    else:
                        return None
                        
                except json.JSONDecodeError as e:
                    if self.logger:
                        self.logger.error(f"JSON decode error for historical data: {e}")
                    return None
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Unexpected error parsing historical data: {e}")
                    return None
            
            return None
            
        except ConnectionError as e:
            if self.logger:
                self.logger.error(f"Redis connection error getting historical data: {e}")
            return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Unexpected error getting historical data: {e}")
            return None

    async def _calculate_breakout_score(self, high: float, low: float, close: float, 
                                      volume: float, historical_data: pd.DataFrame) -> float:
        """Calculate breakout score based on multiple factors."""
        try:
            if historical_data.empty:
                return 0.0
            
            # Price breakout factor
            prev_high = historical_data['high'].max()
            prev_low = historical_data['low'].min()
            prev_close = historical_data['close'].iloc[-1]
            
            # Volume confirmation
            avg_volume = historical_data['volume'].mean()
            volume_factor = volume / avg_volume if avg_volume > 0 else 1.0
            
            # Volatility contraction
            volatility = historical_data['close'].pct_change().std()
            current_range = (high - low) / prev_close if prev_close > 0 else 0
            
            # Breakout score calculation
            price_breakout = 1.0 if close > prev_high or close < prev_low else 0.5
            volume_confirmation = min(volume_factor / self.min_volume_threshold, 1.0)
            volatility_factor = 1.0 if current_range > volatility else 0.5
            
            # Weighted score
            breakout_score = (
                price_breakout * 0.4 +
                volume_confirmation * 0.3 +
                volatility_factor * 0.3
            )
            
            return breakout_score
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating breakout score: {e}")
            return 0.0

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Breakout Strategy",
            "type": "trend_following",
            "description": "Detects breakout opportunities after volatility contraction",
            "parameters": {
                "breakout_threshold": self.breakout_threshold,
                "min_volume_threshold": self.min_volume_threshold,
                "confirmation_periods": self.confirmation_periods,
                "volatility_lookback": self.volatility_lookback
            },
            "timeframe": "fast",  # 100ms tier
            "asset_types": ["crypto", "forex", "indices", "stocks"]
        }