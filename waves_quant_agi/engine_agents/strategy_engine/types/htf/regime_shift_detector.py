#!/usr/bin/env python3
"""
Regime Shift Detector Strategy - Fixed and Enhanced
High time frame strategy for detecting market regime shifts.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from engine_agents.shared_utils import get_shared_redis

class RegimeShiftDetectorStrategy:
    """Regime shift detector strategy for high time frame trading."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.regime_change_threshold = config.get("regime_change_threshold", 0.75)  # Regime shift confidence
        self.lookback_period = config.get("lookback_period", 200)  # 200 periods lookback
        self.volatility_threshold = config.get("volatility_threshold", 0.3)  # 30% volatility threshold
        self.correlation_threshold = config.get("correlation_threshold", 0.7)  # 70% correlation threshold
        self.min_regime_duration = config.get("min_regime_duration", 86400)  # 24 hour minimum

    async def detect_regime_shift(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect market regime shifts for high time frame trading."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            # Get available asset classes from data feeds
            asset_classes = await self._get_asset_classes()
            
            # Check each asset class for regime shifts
            for asset_class, symbols in asset_classes.items():
                if len(symbols) >= 2:  # Need at least 2 symbols for correlation
                    opportunity = await self._check_asset_class_regime(asset_class, symbols)
                    if opportunity:
                        opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting regime shift: {e}")
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

    async def _check_asset_class_regime(self, asset_class: str, symbols: List[str]) -> Optional[Dict[str, Any]]:
        """Check for regime shift in a specific asset class."""
        try:
            # Get historical data for all symbols in the asset class
            historical_data = {}
            for symbol in symbols[:5]:  # Limit to 5 symbols for performance
                hist_data = await self._get_historical_data(symbol)
                if hist_data is not None:
                    historical_data[symbol] = hist_data
            
            if len(historical_data) < 2:
                return None
            
            # Calculate regime metrics
            regime_metrics = await self._calculate_regime_metrics(historical_data)
            
            if not regime_metrics['regime_changed']:
                return None
            
            # Determine optimal strategy
            optimal_strategy = await self._determine_optimal_strategy(regime_metrics)
            
            opportunity = {
                "type": "regime_shift_detector",
                "strategy": "htf",
                "asset_class": asset_class,
                "action": optimal_strategy,
                "regime_score": regime_metrics['regime_confidence'],
                "current_regime": regime_metrics['current_regime'],
                "previous_regime": regime_metrics['previous_regime'],
                "volatility_regime": regime_metrics['volatility_regime'],
                "correlation_regime": regime_metrics['correlation_regime'],
                "regime_duration": regime_metrics['regime_duration'],
                "confidence": regime_metrics['regime_confidence'],
                "timestamp": int(time.time()),
                "description": f"Regime shift for {asset_class}: {regime_metrics['previous_regime']} to {regime_metrics['current_regime']}, Score {regime_metrics['regime_confidence']:.2f}"
            }
            
            # Store regime shift in Redis with proper JSON serialization
            if self.redis_conn:
                try:
                    import json
                    self.redis_conn.set(
                        f"strategy_engine:regime_shift:{asset_class}:{int(time.time())}", 
                        json.dumps(opportunity), 
                        ex=3600
                    )
                except json.JSONEncodeError as e:
                    if self.logger:
                        self.logger.error(f"JSON encoding error storing regime shift: {e}")
                except ConnectionError as e:
                    if self.logger:
                        self.logger.error(f"Redis connection error storing regime shift: {e}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Unexpected error storing regime shift: {e}")
            
            if self.logger:
                self.logger.info(f"Regime shift opportunity: {opportunity['description']}")
            
            return opportunity
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking asset class regime: {e}")
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

    async def _calculate_regime_metrics(self, historical_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate regime shift metrics."""
        try:
            # Calculate volatility regime
            volatility_regime = await self._calculate_volatility_regime(historical_data)
            
            # Calculate correlation regime
            correlation_regime = await self._calculate_correlation_regime(historical_data)
            
            # Determine current regime
            current_regime = await self._determine_current_regime(volatility_regime, correlation_regime)
            
            # Get previous regime
            previous_regime = await self._get_previous_regime()
            
            # Calculate regime confidence
            regime_confidence = await self._calculate_regime_confidence(
                volatility_regime, correlation_regime, historical_data
            )
            
            # Check if regime changed
            regime_changed = (current_regime != previous_regime and 
                            regime_confidence > self.regime_change_threshold)
            
            # Calculate regime duration
            regime_duration = await self._calculate_regime_duration(current_regime)
            
            return {
                "volatility_regime": volatility_regime,
                "correlation_regime": correlation_regime,
                "current_regime": current_regime,
                "previous_regime": previous_regime,
                "regime_confidence": regime_confidence,
                "regime_changed": regime_changed,
                "regime_duration": regime_duration
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating regime metrics: {e}")
            return {
                "volatility_regime": "unknown",
                "correlation_regime": "unknown",
                "current_regime": "unknown",
                "previous_regime": "unknown",
                "regime_confidence": 0.0,
                "regime_changed": False,
                "regime_duration": 0.0
            }

    async def _calculate_volatility_regime(self, historical_data: Dict[str, pd.DataFrame]) -> str:
        """Calculate volatility regime."""
        try:
            all_volatilities = []
            
            for symbol, data in historical_data.items():
                if len(data) >= self.lookback_period:
                    # Calculate rolling volatility
                    returns = data['close'].pct_change().dropna()
                    volatility = returns.rolling(window=20).std().iloc[-1]
                    all_volatilities.append(volatility)
            
            if not all_volatilities:
                return "unknown"
            
            avg_volatility = np.mean(all_volatilities)
            
            if avg_volatility > self.volatility_threshold:
                return "high_volatility"
            elif avg_volatility < self.volatility_threshold * 0.5:
                return "low_volatility"
            else:
                return "normal_volatility"
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating volatility regime: {e}")
            return "unknown"

    async def _calculate_correlation_regime(self, historical_data: Dict[str, pd.DataFrame]) -> str:
        """Calculate correlation regime."""
        try:
            if len(historical_data) < 2:
                return "unknown"
            
            # Calculate correlation matrix
            price_data = {}
            for symbol, data in historical_data.items():
                if len(data) >= self.lookback_period:
                    price_data[symbol] = data['close'].tail(self.lookback_period)
            
            if len(price_data) < 2:
                return "unknown"
            
            # Convert to DataFrame and calculate correlation
            price_df = pd.DataFrame(price_data)
            correlation_matrix = price_df.corr()
            
            # Calculate average correlation
            correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i + 1, len(correlation_matrix.columns)):
                    corr = correlation_matrix.iloc[i, j]
                    if not pd.isna(corr):
                        correlations.append(corr)
            
            if not correlations:
                return "unknown"
            
            avg_correlation = np.mean(correlations)
            
            if avg_correlation > self.correlation_threshold:
                return "high_correlation"
            elif avg_correlation < self.correlation_threshold * 0.5:
                return "low_correlation"
            else:
                return "normal_correlation"
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating correlation regime: {e}")
            return "unknown"

    async def _determine_current_regime(self, volatility_regime: str, correlation_regime: str) -> str:
        """Determine current market regime based on volatility and correlation."""
        try:
            # High volatility + high correlation = crisis regime
            if volatility_regime == "high_volatility" and correlation_regime == "high_correlation":
                return "crisis"
            
            # High volatility + low correlation = dispersion regime
            elif volatility_regime == "high_volatility" and correlation_regime == "low_correlation":
                return "dispersion"
            
            # Low volatility + high correlation = momentum regime
            elif volatility_regime == "low_volatility" and correlation_regime == "high_correlation":
                return "momentum"
            
            # Low volatility + low correlation = alpha regime
            elif volatility_regime == "low_volatility" and correlation_regime == "low_correlation":
                return "alpha"
            
            # Normal conditions
            else:
                return "normal"
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error determining current regime: {e}")
            return "unknown"

    async def _get_previous_regime(self) -> str:
        """Get previous regime from Redis."""
        try:
            if not self.redis_conn:
                return "unknown"
            
            previous_regime_key = "strategy_engine:previous_regime"
            previous_regime = self.redis_conn.get(previous_regime_key)
            
            return previous_regime if previous_regime else "unknown"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting previous regime: {e}")
            return "unknown"

    async def _calculate_regime_confidence(self, volatility_regime: str, correlation_regime: str, 
                                        historical_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate confidence in regime classification."""
        try:
            confidence = 0.5  # Base confidence
            
            # Volatility confidence
            if volatility_regime != "unknown":
                confidence += 0.2
            
            # Correlation confidence
            if correlation_regime != "unknown":
                confidence += 0.2
            
            # Data quality confidence
            data_quality = min(len(historical_data) / 5.0, 1.0)  # Normalize to 0-1
            confidence += data_quality * 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating regime confidence: {e}")
            return 0.0

    async def _calculate_regime_duration(self, current_regime: str) -> float:
        """Calculate duration of current regime."""
        try:
            if not self.redis_conn:
                return 0.0
            
            regime_start_key = f"strategy_engine:regime_start:{current_regime}"
            regime_start = self.redis_conn.get(regime_start_key)
            
            if regime_start:
                start_time = float(regime_start)
                duration = time.time() - start_time
                return duration
            
            return 0.0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating regime duration: {e}")
            return 0.0

    async def _determine_optimal_strategy(self, regime_metrics: Dict[str, Any]) -> str:
        """Determine optimal strategy based on regime."""
        try:
            current_regime = regime_metrics.get("current_regime", "unknown")
            
            if current_regime == "crisis":
                return "defensive"  # Reduce risk, increase cash
            elif current_regime == "dispersion":
                return "long_short"  # Long winners, short losers
            elif current_regime == "momentum":
                return "trend_following"  # Follow the trend
            elif current_regime == "alpha":
                return "fundamental"  # Stock picking
            elif current_regime == "normal":
                return "balanced"  # Balanced approach
            else:
                return "hold"  # Unknown regime, hold positions
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error determining optimal strategy: {e}")
            return "hold"

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Regime Shift Detector Strategy",
            "type": "htf",
            "description": "High time frame strategy for detecting market regime shifts",
            "parameters": {
                "regime_change_threshold": self.regime_change_threshold,
                "lookback_period": self.lookback_period,
                "volatility_threshold": self.volatility_threshold,
                "correlation_threshold": self.correlation_threshold,
                "min_regime_duration": self.min_regime_duration
            },
            "timeframe": "strategic",  # 5min tier
            "asset_types": ["forex", "crypto", "stocks", "indices", "commodities"],
            "execution_speed": "slow"
        }