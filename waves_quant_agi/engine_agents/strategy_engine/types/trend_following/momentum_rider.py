#!/usr/bin/env python3
"""
Momentum Rider Strategy - Fixed and Enhanced
Rides strong momentum trends with dynamic position sizing.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
from engine_agents.shared_utils import get_shared_redis

class MomentumRiderStrategy:
    """Momentum strategy for riding strong trends with dynamic sizing."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.momentum_threshold = config.get("momentum_threshold", 0.015)  # 1.5% momentum
        self.momentum_lookback = config.get("momentum_lookback", 10)
        self.volume_multiplier = config.get("volume_multiplier", 2.0)
        self.trend_confirmation = config.get("trend_confirmation", 3)
        self.max_position_size = config.get("max_position_size", 0.1)

    async def detect_momentum(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect momentum opportunities across assets."""
        try:
            opportunities = []
            
            if market_data.empty:
                return opportunities
                
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTCUSD")
                close = float(row.get("close", 0.0))
                volume = float(row.get("volume", 0.0))
                
                # Get historical data for momentum calculation
                historical_data = await self._get_historical_data(symbol)
                if not historical_data:
                    continue
                
                # Calculate momentum metrics
                momentum_score = await self._calculate_momentum_score(
                    close, volume, historical_data
                )
                
                if momentum_score > self.momentum_threshold:
                    # Determine trend direction
                    trend_direction = await self._determine_trend_direction(historical_data)
                    
                    opportunity = {
                        "type": "momentum_rider",
                        "strategy": "momentum",
                        "symbol": symbol,
                        "action": "buy" if trend_direction > 0 else "sell",
                        "entry_price": close,
                        "stop_loss": close * (0.98 if trend_direction > 0 else 1.02),
                        "take_profit": close * (1.03 if trend_direction > 0 else 0.97),
                        "confidence": min(momentum_score / self.momentum_threshold, 0.9),
                        "momentum_strength": momentum_score,
                        "trend_direction": trend_direction,
                        "volume_confirmation": volume > self.volume_multiplier,
                        "timestamp": int(time.time()),
                        "description": f"Momentum opportunity for {symbol}: Score {momentum_score:.4f}"
                    }
                    opportunities.append(opportunity)
                    
                    # Store in Redis for tracking with proper JSON serialization
                    if self.redis_conn:
                        try:
                            import json
                            self.redis_conn.set(
                                f"strategy_engine:momentum:{symbol}:{int(time.time())}", 
                                json.dumps(opportunity), 
                                ex=3600
                            )
                        except json.JSONEncodeError as e:
                            if self.logger:
                                self.logger.error(f"JSON encoding error storing momentum opportunity: {e}")
                        except ConnectionError as e:
                            if self.logger:
                                self.logger.error(f"Redis connection error storing momentum opportunity: {e}")
                        except Exception as e:
                            if self.logger:
                                self.logger.error(f"Unexpected error storing momentum opportunity: {e}")
                    
                    if self.logger:
                        self.logger.info(f"Momentum opportunity: {opportunity['description']}")

            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting momentum: {e}")
            return []

    async def _get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get historical data for momentum calculation."""
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
                self.logger.error(f"Error getting historical data: {e}")
            return None

    async def _calculate_momentum_score(self, close: float, volume: float, 
                                      historical_data: pd.DataFrame) -> float:
        """Calculate momentum score based on price and volume."""
        try:
            if historical_data.empty or len(historical_data) < self.momentum_lookback:
                return 0.0
            
            # Price momentum
            recent_prices = historical_data['close'].tail(self.momentum_lookback)
            price_momentum = (close - recent_prices.iloc[0]) / recent_prices.iloc[0]
            
            # Volume momentum
            recent_volumes = historical_data['volume'].tail(self.momentum_lookback)
            avg_volume = recent_volumes.mean()
            volume_momentum = volume / avg_volume if avg_volume > 0 else 1.0
            
            # Volatility adjustment
            volatility = recent_prices.pct_change().std()
            volatility_factor = 1.0 / (1.0 + volatility) if volatility > 0 else 1.0
            
            # Combined momentum score
            momentum_score = (
                abs(price_momentum) * 0.5 +
                min(volume_momentum / self.volume_multiplier, 1.0) * 0.3 +
                volatility_factor * 0.2
            )
            
            return momentum_score
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating momentum score: {e}")
            return 0.0

    async def _determine_trend_direction(self, historical_data: pd.DataFrame) -> float:
        """Determine trend direction using multiple timeframes."""
        try:
            if historical_data.empty:
                return 0.0
            
            # Short-term trend (last 5 periods)
            short_trend = historical_data['close'].tail(5).pct_change().mean()
            
            # Medium-term trend (last 10 periods)
            medium_trend = historical_data['close'].tail(10).pct_change().mean()
            
            # Long-term trend (last 20 periods)
            long_trend = historical_data['close'].tail(20).pct_change().mean()
            
            # Weighted trend direction
            trend_direction = (
                short_trend * 0.5 +
                medium_trend * 0.3 +
                long_trend * 0.2
            )
            
            return trend_direction
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error determining trend direction: {e}")
            return 0.0

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Momentum Rider Strategy",
            "type": "trend_following",
            "description": "Rides strong momentum trends with dynamic position sizing",
            "parameters": {
                "momentum_threshold": self.momentum_threshold,
                "momentum_lookback": self.momentum_lookback,
                "volume_multiplier": self.volume_multiplier,
                "trend_confirmation": self.trend_confirmation,
                "max_position_size": self.max_position_size
            },
            "timeframe": "fast",  # 100ms tier
            "asset_types": ["crypto", "forex", "indices", "stocks"]
        }