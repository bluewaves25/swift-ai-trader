#!/usr/bin/env python3
"""
Macro Trend Tracker Strategy - Fixed and Enhanced
High time frame strategy for tracking macro economic trends.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from engine_agents.shared_utils import get_shared_redis

class MacroTrendTrackerStrategy:
    """Macro trend tracker strategy for high time frame trading."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.trend_strength_threshold = config.get("trend_strength_threshold", 0.8)  # Trend strength score
        self.lookback_period = config.get("lookback_period", 500)  # 500 periods lookback
        self.macro_signal_threshold = config.get("macro_signal_threshold", 0.6)  # Macro signal threshold
        self.correlation_threshold = config.get("correlation_threshold", 0.7)  # 70% correlation threshold
        self.min_trend_duration = config.get("min_trend_duration", 86400)  # 24 hour minimum

    async def detect_macro_trend(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect long-term macro trends for high time frame trading."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            # Get macro indicators from data feeds
            macro_indicators = await self._get_macro_indicators()
            
            # Get available asset classes from data feeds
            asset_classes = await self._get_asset_classes()
            
            # Check each asset class for macro trends
            for asset_class, symbols in asset_classes.items():
                if len(symbols) >= 2:  # Need at least 2 symbols for correlation
                    opportunity = await self._check_asset_class_macro_trend(asset_class, symbols, macro_indicators)
                    if opportunity:
                        opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting macro trend: {e}")
            return []

    async def _get_macro_indicators(self) -> List[Dict[str, Any]]:
        """Get macro indicators from data feeds."""
        try:
            if not self.redis_conn:
                return []
            
            # Get macro indicators from data feeds
            indicators_key = "data_feeds:macro_indicators"
            indicators_data = self.redis_conn.get(indicators_key)
            
            if indicators_data:
                import json
                return json.loads(indicators_data)
            
            return []
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting macro indicators: {e}")
            return []

    async def _get_asset_classes(self) -> Dict[str, List[str]]:
        """Get available asset classes from data feeds."""
        try:
            if not self.redis_conn:
                return {}
            
            # Get available symbols from data feeds
            symbols_key = "data_feeds:available_symbols"
            symbols_data = self.redis_conn.get(symbols_key)
            
            if symbols_data:
                import json
                symbols = json.loads(symbols_data)
                
                # Group symbols by asset class
                asset_class_data = {
                    "forex": [],
                    "crypto": [],
                    "stocks": [],
                    "indices": [],
                    "commodities": []
                }
                
                for symbol in symbols:
                    if any(forex_pair in symbol.upper() for forex_pair in ["EUR", "USD", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]):
                        asset_class_data["forex"].append(symbol)
                    elif any(crypto in symbol.upper() for crypto in ["BTC", "ETH", "USDT", "USDC", "BNB", "ADA", "SOL"]):
                        asset_class_data["crypto"].append(symbol)
                    elif any(stock_indicator in symbol.upper() for stock_indicator in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]):
                        asset_class_data["stocks"].append(symbol)
                    elif any(index in symbol.upper() for index in ["SPX", "NDX", "DJI", "VIX", "RUT"]):
                        asset_class_data["indices"].append(symbol)
                    elif any(commodity in symbol.upper() for commodity in ["GOLD", "SILVER", "OIL", "GAS", "COPPER"]):
                        asset_class_data["commodities"].append(symbol)
                
                # Remove empty asset classes
                asset_class_data = {k: v for k, v in asset_class_data.items() if v}
                
                return asset_class_data
            
            return {}
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error grouping by asset class: {e}")
            return {}

    async def _check_asset_class_macro_trend(self, asset_class: str, symbols: List[str], 
                                           macro_indicators: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check for macro trend in a specific asset class."""
        try:
            # Get historical data for all symbols in the asset class
            historical_data = {}
            for symbol in symbols[:5]:  # Limit to 5 symbols for performance
                hist_data = await self._get_historical_data(symbol)
                if hist_data is not None:
                    historical_data[symbol] = hist_data
            
            if len(historical_data) < 2:
                return None
            
            # Calculate macro trend metrics
            macro_metrics = await self._calculate_macro_metrics(historical_data, macro_indicators)
            
            if not macro_metrics['trend_detected']:
                return None
            
            # Determine optimal strategy
            optimal_strategy = await self._determine_optimal_strategy(macro_metrics)
            
            opportunity = {
                "type": "macro_trend_tracker",
                "strategy": "htf",
                "asset_class": asset_class,
                "action": optimal_strategy,
                "trend_score": macro_metrics['trend_score'],
                "macro_signal": macro_metrics['macro_signal'],
                "trend_direction": macro_metrics['trend_direction'],
                "trend_strength": macro_metrics['trend_strength'],
                "correlation_score": macro_metrics['correlation_score'],
                "confidence": macro_metrics['confidence'],
                "timestamp": int(time.time()),
                "description": f"Macro trend for {asset_class}: {macro_metrics['trend_direction']} trend, Score {macro_metrics['trend_score']:.2f}"
            }
            
            # Store macro trend in Redis with proper JSON serialization
            if self.redis_conn:
                try:
                    import json
                    self.redis_conn.set(
                        f"strategy_engine:macro_trend:{asset_class}:{int(time.time())}", 
                        json.dumps(opportunity), 
                        ex=3600
                    )
                except json.JSONEncodeError as e:
                    if self.logger:
                        self.logger.error(f"JSON encoding error storing macro trend: {e}")
                except ConnectionError as e:
                    if self.logger:
                        self.logger.error(f"Redis connection error storing macro trend: {e}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Unexpected error storing macro trend: {e}")
            
            if self.logger:
                self.logger.info(f"Macro trend opportunity: {opportunity['description']}")
            
            return opportunity
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking asset class macro trend: {e}")
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

    async def _calculate_macro_metrics(self, historical_data: Dict[str, pd.DataFrame], 
                                     macro_indicators: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate macro trend metrics."""
        try:
            # Calculate trend strength
            trend_strength = await self._calculate_trend_strength(historical_data)
            
            # Calculate macro signal
            macro_signal = await self._calculate_macro_signal(macro_indicators)
            
            # Calculate correlation with macro indicators
            correlation_score = await self._calculate_macro_correlation(historical_data, macro_indicators)
            
            # Determine trend direction
            trend_direction = await self._determine_trend_direction(trend_strength, macro_signal)
            
            # Calculate overall trend score
            trend_score = (trend_strength * 0.4 + macro_signal * 0.4 + correlation_score * 0.2)
            
            # Check if trend is detected
            trend_detected = (trend_score > self.trend_strength_threshold and 
                            abs(macro_signal) > self.macro_signal_threshold)
            
            # Calculate confidence
            confidence = min(trend_score, 0.9)
            
            return {
                "trend_strength": trend_strength,
                "macro_signal": macro_signal,
                "correlation_score": correlation_score,
                "trend_direction": trend_direction,
                "trend_score": trend_score,
                "trend_detected": trend_detected,
                "confidence": confidence
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating macro metrics: {e}")
            return {
                "trend_strength": 0.0,
                "macro_signal": 0.0,
                "correlation_score": 0.0,
                "trend_direction": "neutral",
                "trend_score": 0.0,
                "trend_detected": False,
                "confidence": 0.0
            }

    async def _calculate_trend_strength(self, historical_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate trend strength across assets."""
        try:
            trend_strengths = []
            
            for symbol, data in historical_data.items():
                if len(data) >= self.lookback_period:
                    # Calculate price trend
                    prices = data['close'].tail(self.lookback_period)
                    if len(prices) > 0:
                        # Linear regression slope
                        x = np.arange(len(prices))
                        y = prices.values
                        slope = np.polyfit(x, y, 1)[0]
                        
                        # Normalize slope by price
                        avg_price = np.mean(prices)
                        normalized_slope = slope / avg_price if avg_price > 0 else 0
                        trend_strengths.append(abs(normalized_slope))
            
            if not trend_strengths:
                return 0.0
            
            return np.mean(trend_strengths)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating trend strength: {e}")
            return 0.0

    async def _calculate_macro_signal(self, macro_indicators: List[Dict[str, Any]]) -> float:
        """Calculate macro signal from indicators."""
        try:
            if not macro_indicators:
                return 0.0
            
            signals = []
            
            for indicator in macro_indicators:
                indicator_type = indicator.get("type", "")
                value = float(indicator.get("value", 0.0))
                
                # Calculate signal based on indicator type
                if indicator_type == "vix":
                    # VIX > 30 = bearish, VIX < 15 = bullish
                    if value > 30:
                        signals.append(-0.8)  # Bearish
                    elif value < 15:
                        signals.append(0.8)   # Bullish
                    else:
                        signals.append(0.0)   # Neutral
                        
                elif indicator_type == "dollar_index":
                    # Strong dollar = bearish for commodities, weak dollar = bullish
                    if value > 105:
                        signals.append(-0.6)  # Bearish
                    elif value < 95:
                        signals.append(0.6)   # Bullish
                    else:
                        signals.append(0.0)   # Neutral
                        
                elif indicator_type == "treasury_yield":
                    # High yields = bearish for bonds, low yields = bullish
                    if value > 4.0:
                        signals.append(-0.7)  # Bearish
                    elif value < 2.0:
                        signals.append(0.7)   # Bullish
                    else:
                        signals.append(0.0)   # Neutral
            
            if not signals:
                return 0.0
            
            return np.mean(signals)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating macro signal: {e}")
            return 0.0

    async def _calculate_macro_correlation(self, historical_data: Dict[str, pd.DataFrame], 
                                         macro_indicators: List[Dict[str, Any]]) -> float:
        """Calculate correlation between asset prices and macro indicators."""
        try:
            if not macro_indicators or len(historical_data) < 2:
                return 0.0
            
            # Get recent price changes
            price_changes = []
            for symbol, data in historical_data.items():
                if len(data) >= 20:
                    returns = data['close'].pct_change().tail(20).dropna()
                    if len(returns) > 0:
                        price_changes.append(returns)
            
            if len(price_changes) < 2:
                return 0.0
            
            # Calculate average correlation between assets
            correlations = []
            for i in range(len(price_changes)):
                for j in range(i + 1, len(price_changes)):
                    if len(price_changes[i]) == len(price_changes[j]):
                        corr = np.corrcoef(price_changes[i], price_changes[j])[0, 1]
                        if not np.isnan(corr):
                            correlations.append(abs(corr))
            
            if not correlations:
                return 0.0
            
            return np.mean(correlations)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating macro correlation: {e}")
            return 0.0

    async def _determine_trend_direction(self, trend_strength: float, macro_signal: float) -> str:
        """Determine overall trend direction."""
        try:
            # Combine trend strength and macro signal
            combined_signal = (trend_strength * 0.6 + macro_signal * 0.4)
            
            if combined_signal > self.trend_strength_threshold:
                return "bullish"
            elif combined_signal < -self.trend_strength_threshold:
                return "bearish"
            else:
                return "neutral"
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error determining trend direction: {e}")
            return "neutral"

    async def _determine_optimal_strategy(self, macro_metrics: Dict[str, Any]) -> str:
        """Determine optimal strategy based on macro trends."""
        try:
            trend_direction = macro_metrics.get("trend_direction", "neutral")
            trend_strength = macro_metrics.get("trend_strength", 0.0)
            
            if trend_direction == "bullish" and trend_strength > self.trend_strength_threshold:
                return "trend_following"  # Follow the bullish trend
            elif trend_direction == "bearish" and trend_strength > self.trend_strength_threshold:
                return "short_selling"  # Short selling strategy
            elif trend_direction == "neutral":
                return "mean_reversion"  # Mean reversion in sideways market
            else:
                return "hold"  # Insufficient trend strength
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error determining optimal strategy: {e}")
            return "hold"

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Macro Trend Tracker Strategy",
            "type": "htf",
            "description": "High time frame strategy for tracking macro economic trends",
            "parameters": {
                "trend_strength_threshold": self.trend_strength_threshold,
                "lookback_period": self.lookback_period,
                "macro_signal_threshold": self.macro_signal_threshold,
                "correlation_threshold": self.correlation_threshold,
                "min_trend_duration": self.min_trend_duration
            },
            "timeframe": "strategic",  # 5min tier
            "asset_types": ["forex", "crypto", "stocks", "indices", "commodities"],
            "execution_speed": "slow"
        }