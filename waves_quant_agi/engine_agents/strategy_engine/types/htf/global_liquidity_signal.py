#!/usr/bin/env python3
"""
Global Liquidity Signal Strategy - Fixed and Enhanced
High-timeframe strategy for detecting global liquidity changes.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
from engine_agents.shared_utils import get_shared_redis

class GlobalLiquiditySignalStrategy:
    """Global liquidity signal strategy for high-timeframe analysis."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.liquidity_threshold = config.get("liquidity_threshold", 0.7)  # 70% confidence threshold
        self.lookback_period = config.get("lookback_period", 500)  # 500 periods lookback
        self.correlation_window = config.get("correlation_window", 100)  # 100 periods for correlation
        self.volume_threshold = config.get("volume_threshold", 2.0)  # 2x volume increase
        self.volatility_threshold = config.get("volatility_threshold", 1.5)  # 1.5x volatility increase

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect global liquidity signal opportunities."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            # Get global market indicators from data feeds
            global_indicators = await self._get_global_indicators()
            
            # Check for liquidity signals
            liquidity_signals = await self._check_liquidity_signals(global_indicators, market_data)
            
            for signal in liquidity_signals:
                opportunity = await self._create_liquidity_opportunity(signal, market_data)
                if opportunity:
                    opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting global liquidity opportunities: {e}")
            return []

    async def _get_global_indicators(self) -> List[Dict[str, Any]]:
        """Get global market indicators from data feeds."""
        try:
            if not self.redis_conn:
                return []
            
            # Get global indicators from data feeds
            indicators_key = "data_feeds:global_indicators"
            indicators_data = self.redis_conn.get(indicators_key)
            
            if indicators_data:
                import json
                return json.loads(indicators_data)
            
            # Fallback to basic indicators
            return [
                {"type": "vix", "value": 20.0, "timestamp": int(time.time())},
                {"type": "dollar_index", "value": 100.0, "timestamp": int(time.time())},
                {"type": "treasury_yield", "value": 2.5, "timestamp": int(time.time())}
            ]
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting global indicators: {e}")
            return []

    async def _check_liquidity_signals(self, global_indicators: List[Dict[str, Any]], 
                                     market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for global liquidity signals."""
        try:
            signals = []
            
            for indicator in global_indicators:
                signal = await self._analyze_indicator_liquidity(indicator, market_data)
                if signal:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking liquidity signals: {e}")
            return []

    async def _analyze_indicator_liquidity(self, indicator: Dict[str, Any], 
                                         market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze liquidity impact of a global indicator."""
        try:
            indicator_type = indicator.get("type", "")
            indicator_value = float(indicator.get("value", 0.0))
            timestamp = indicator.get("timestamp", 0)
            
            # Check if indicator is recent
            current_time = time.time()
            if current_time - timestamp > 3600:  # 1 hour old
                return None
            
            # Analyze based on indicator type
            if indicator_type == "vix":
                return await self._analyze_vix_liquidity(indicator_value, market_data)
            elif indicator_type == "dollar_index":
                return await self._analyze_dollar_liquidity(indicator_value, market_data)
            elif indicator_type == "treasury_yield":
                return await self._analyze_yield_liquidity(indicator_value, market_data)
            else:
                return None
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error analyzing indicator liquidity: {e}")
            return None

    async def _analyze_vix_liquidity(self, vix_value: float, market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze VIX-based liquidity signals."""
        try:
            # VIX > 30 indicates high volatility, potential liquidity issues
            if vix_value > 30:
                return {
                    "type": "vix_liquidity",
                    "signal": "liquidity_risk",
                    "confidence": min((vix_value - 30) / 20, 0.9),
                    "description": f"High VIX ({vix_value:.1f}) indicates liquidity risk"
                }
            # VIX < 15 indicates low volatility, potential liquidity abundance
            elif vix_value < 15:
                return {
                    "type": "vix_liquidity",
                    "signal": "liquidity_abundance",
                    "confidence": min((15 - vix_value) / 10, 0.9),
                    "description": f"Low VIX ({vix_value:.1f}) indicates liquidity abundance"
                }
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error analyzing VIX liquidity: {e}")
            return None

    async def _analyze_dollar_liquidity(self, dollar_value: float, market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze dollar index-based liquidity signals."""
        try:
            # Strong dollar (>105) can indicate liquidity tightening
            if dollar_value > 105:
                return {
                    "type": "dollar_liquidity",
                    "signal": "liquidity_tightening",
                    "confidence": min((dollar_value - 105) / 10, 0.9),
                    "description": f"Strong dollar ({dollar_value:.1f}) indicates liquidity tightening"
                }
            # Weak dollar (<95) can indicate liquidity easing
            elif dollar_value < 95:
                return {
                    "type": "dollar_liquidity",
                    "signal": "liquidity_easing",
                    "confidence": min((95 - dollar_value) / 10, 0.9),
                    "description": f"Weak dollar ({dollar_value:.1f}) indicates liquidity easing"
                }
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error analyzing dollar liquidity: {e}")
            return None

    async def _analyze_yield_liquidity(self, yield_value: float, market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze treasury yield-based liquidity signals."""
        try:
            # High yields (>4%) can indicate liquidity tightening
            if yield_value > 4.0:
                return {
                    "type": "yield_liquidity",
                    "signal": "liquidity_tightening",
                    "confidence": min((yield_value - 4.0) / 2.0, 0.9),
                    "description": f"High yields ({yield_value:.2f}%) indicate liquidity tightening"
                }
            # Low yields (<2%) can indicate liquidity easing
            elif yield_value < 2.0:
                return {
                    "type": "yield_liquidity",
                    "signal": "liquidity_easing",
                    "confidence": min((2.0 - yield_value) / 1.0, 0.9),
                    "description": f"Low yields ({yield_value:.2f}%) indicate liquidity easing"
                }
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error analyzing yield liquidity: {e}")
            return None

    async def _create_liquidity_opportunity(self, signal: Dict[str, Any], 
                                          market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Create liquidity trading opportunity."""
        try:
            signal_type = signal.get("type", "")
            signal_signal = signal.get("signal", "")
            confidence = signal.get("confidence", 0.0)
            description = signal.get("description", "")
            
            if confidence < self.liquidity_threshold:
                return None
            
            # Get affected assets
            affected_assets = await self._get_affected_assets(signal)
            
            if not affected_assets:
                return None
            
            # Create opportunity for each affected asset
            opportunities = []
            for asset in affected_assets:
                opportunity = {
                    "type": "global_liquidity_signal",
                    "strategy": "htf",
                    "symbol": asset,
                    "action": "buy" if "easing" in signal_signal else "sell" if "tightening" in signal_signal else "hold",
                    "liquidity_signal": signal_signal,
                    "signal_type": signal_type,
                    "confidence": confidence,
                    "description": f"{description} - {asset}",
                    "timestamp": int(time.time())
                }
                
                # Store liquidity signal in Redis with proper JSON serialization
                if self.redis_conn:
                    try:
                        import json
                        self.redis_conn.set(
                            f"strategy_engine:global_liquidity:{asset}:{int(time.time())}", 
                            json.dumps(opportunity), 
                            ex=3600
                        )
                    except json.JSONEncodeError as e:
                        if self.logger:
                            self.logger.error(f"JSON encoding error storing liquidity signal: {e}")
                    except ConnectionError as e:
                        if self.logger:
                            self.logger.error(f"Redis connection error storing liquidity signal: {e}")
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Unexpected error storing liquidity signal: {e}")
                
                opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error creating liquidity opportunity: {e}")
            return None

    async def _get_affected_assets(self, signal: Dict[str, Any]) -> List[str]:
        """Get assets affected by the liquidity signal."""
        try:
            signal_type = signal.get("type", "")
            signal_signal = signal.get("signal", "")
            
            # Get available assets from data feeds
            available_assets = await self._get_available_assets()
            
            # Filter assets based on signal type
            if "vix" in signal_type:
                # VIX affects all risk assets
                return available_assets[:10]  # Top 10 assets
            elif "dollar" in signal_type:
                # Dollar affects forex and commodities
                return [asset for asset in available_assets if any(currency in asset for currency in ["USD", "EUR", "GBP", "JPY", "XAU", "XAG"])]
            elif "yield" in signal_type:
                # Yields affect bonds and growth stocks
                return [asset for asset in available_assets if any(asset_type in asset for asset_type in ["BOND", "SPY", "QQQ", "IWM"])]
            else:
                return available_assets[:5]  # Default to top 5 assets
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting affected assets: {e}")
            return []

    async def _get_available_assets(self) -> List[str]:
        """Get available assets from data feeds."""
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
                self.logger.error(f"Error getting available assets: {e}")
            return []

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Global Liquidity Signal Strategy",
            "type": "htf",
            "description": "High-timeframe strategy for detecting global liquidity changes",
            "parameters": {
                "liquidity_threshold": self.liquidity_threshold,
                "lookback_period": self.lookback_period,
                "correlation_window": self.correlation_window,
                "volume_threshold": self.volume_threshold,
                "volatility_threshold": self.volatility_threshold
            },
            "timeframe": "strategic",  # 5min tier
            "asset_types": ["forex", "indices", "bonds", "commodities"],
            "execution_speed": "slow"
        }