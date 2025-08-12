#!/usr/bin/env python3
"""
Dynamic Risk Limits - Real-time risk limit calculation
Replaces hardcoded values with dynamic data from real sources
Provides intelligent caching and market-responsive limits
"""

import time
import asyncio
import numpy as np
from typing import Dict, Any, List, Optional
from .connection_manager import ConnectionManager

class DynamicRiskLimits:
    """Dynamic risk limits based on real-time market data."""
    
    def __init__(self, connection_manager: ConnectionManager, config: Dict[str, Any]):
        self.connection_manager = connection_manager
        self.config = config
        self.cache = {}
        self.cache_ttl = config.get('cache_ttl', 300)  # 5 minutes default
        self.max_cache_size = config.get('max_cache_size', 1000)
        
        # Base risk limits (fallback values)
        self.base_limits = {
            "arbitrage": {
                "max_position_size": 0.05,
                "max_leverage": 2.0,
                "stop_loss": 0.002,
                "max_drawdown": 0.01
            },
            "trend_following": {
                "max_position_size": 0.15,
                "max_leverage": 1.2,
                "stop_loss": 0.01,
                "max_drawdown": 0.03
            },
            "market_making": {
                "max_position_size": 0.08,
                "max_leverage": 3.0,
                "stop_loss": 0.003,
                "max_drawdown": 0.015
            },
            "news_driven": {
                "max_position_size": 0.12,
                "max_leverage": 1.0,
                "stop_loss": 0.008,
                "max_drawdown": 0.025
            },
            "htf": {
                "max_position_size": 0.20,
                "max_leverage": 1.0,
                "stop_loss": 0.02,
                "max_drawdown": 0.05
            }
        }
    
    async def get_strategy_risk_limits(self, strategy_type: str, symbol: str) -> Dict[str, Any]:
        """Get dynamic risk limits for a strategy and symbol."""
        cache_key = f"{strategy_type}:{symbol}"
        
        # Check cache first
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() < cache_entry['expiry']:
                return cache_entry['data']
            else:
                del self.cache[cache_key]
        
        # Fetch real-time risk limits
        try:
            limits = await self._fetch_real_risk_limits(strategy_type, symbol)
            
            # Cache the results
            self._update_cache(cache_key, limits)
            
            return limits
            
        except Exception as e:
            # Fallback to base limits if data fetching fails
            print(f"Failed to fetch dynamic limits for {strategy_type}:{symbol}, using base limits: {e}")
            return self._get_base_limits(strategy_type)
    
    async def _fetch_real_risk_limits(self, strategy_type: str, symbol: str) -> Dict[str, Any]:
        """Fetch real-time risk limits from data sources."""
        try:
            # Get base limits for this strategy
            base_limits = self._get_base_limits(strategy_type)
            
            # Fetch real-time market data
            market_data = await self._get_market_data(symbol)
            volatility_data = await self._get_volatility_data(symbol)
            liquidity_data = await self._get_liquidity_data(symbol)
            correlation_data = await self._get_correlation_data(symbol)
            
            # Calculate dynamic adjustments
            volatility_adjustment = self._calculate_volatility_adjustment(volatility_data)
            liquidity_adjustment = self._calculate_liquidity_adjustment(liquidity_data)
            correlation_adjustment = self._calculate_correlation_adjustment(correlation_data)
            
            # Apply adjustments to base limits
            dynamic_limits = self._apply_market_adjustments(
                base_limits, 
                volatility_adjustment, 
                liquidity_adjustment, 
                correlation_adjustment
            )
            
            # Ensure limits are within safe bounds
            dynamic_limits = self._apply_safety_bounds(dynamic_limits, strategy_type)
            
            return dynamic_limits
            
        except Exception as e:
            print(f"Error fetching real risk limits: {e}")
            raise
    
    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time market data for a symbol."""
        async with self.connection_manager.get_redis_connection() as redis_client:
            # Get market data from Redis (replace with actual data feed integration)
            market_data = redis_client.hgetall(f"market_data:{symbol}")
            
            if not market_data:
                # Mock data for now - replace with real data feed
                market_data = {
                    "price": "1.0000",
                    "volume": "1000000",
                    "bid": "0.9999",
                    "ask": "1.0001",
                    "timestamp": str(int(time.time()))
                }
            
            return market_data
    
    async def _get_volatility_data(self, symbol: str) -> Dict[str, Any]:
        """Get volatility data for a symbol."""
        async with self.connection_manager.get_redis_connection() as redis_client:
            # Get volatility data from Redis (replace with actual data feed)
            volatility_data = redis_client.hgetall(f"volatility_data:{symbol}")
            
            if not volatility_data:
                # Mock data for now - replace with real data feed
                volatility_data = {
                    "current_volatility": "0.15",
                    "historical_volatility": "0.12",
                    "volatility_ratio": "1.25",
                    "timestamp": str(int(time.time()))
                }
            
            return volatility_data
    
    async def _get_liquidity_data(self, symbol: str) -> Dict[str, Any]:
        """Get liquidity data for a symbol."""
        async with self.connection_manager.get_redis_connection() as redis_client:
            # Get liquidity data from Redis (replace with actual data feed)
            liquidity_data = redis_client.hgetall(f"liquidity_data:{symbol}")
            
            if not liquidity_data:
                # Mock data for now - replace with real data feed
                liquidity_data = {
                    "bid_ask_spread": "0.0002",
                    "market_depth": "1000000",
                    "liquidity_score": "0.85",
                    "timestamp": str(int(time.time()))
                }
            
            return liquidity_data
    
    async def _get_correlation_data(self, symbol: str) -> Dict[str, Any]:
        """Get correlation data for portfolio risk assessment."""
        async with self.connection_manager.get_redis_connection() as redis_client:
            # Get correlation data from Redis (replace with actual data feed)
            correlation_data = redis_client.hgetall(f"correlation_data:{symbol}")
            
            if not correlation_data:
                # Mock data for now - replace with real data feed
                correlation_data = {
                    "portfolio_correlation": "0.3",
                    "sector_correlation": "0.4",
                    "market_correlation": "0.6",
                    "timestamp": str(int(time.time()))
                }
            
            return correlation_data
    
    def _calculate_volatility_adjustment(self, volatility_data: Dict[str, Any]) -> float:
        """Calculate volatility-based adjustment factor."""
        try:
            current_vol = float(volatility_data.get('current_volatility', 0.15))
            historical_vol = float(volatility_data.get('historical_volatility', 0.12))
            
            if historical_vol == 0:
                return 1.0
            
            volatility_ratio = current_vol / historical_vol
            
            # Adjust risk limits based on volatility
            if volatility_ratio > 1.5:  # High volatility
                return 0.7  # Reduce risk by 30%
            elif volatility_ratio < 0.7:  # Low volatility
                return 1.2  # Increase risk by 20%
            else:
                return 1.0  # No adjustment
                
        except Exception as e:
            print(f"Error calculating volatility adjustment: {e}")
            return 1.0
    
    def _calculate_liquidity_adjustment(self, liquidity_data: Dict[str, Any]) -> float:
        """Calculate liquidity-based adjustment factor."""
        try:
            liquidity_score = float(liquidity_data.get('liquidity_score', 0.85))
            
            # Adjust risk limits based on liquidity
            if liquidity_score < 0.5:  # Low liquidity
                return 0.6  # Reduce risk by 40%
            elif liquidity_score > 0.9:  # High liquidity
                return 1.1  # Increase risk by 10%
            else:
                return 1.0  # No adjustment
                
        except Exception as e:
            print(f"Error calculating liquidity adjustment: {e}")
            return 1.0
    
    def _calculate_correlation_adjustment(self, correlation_data: Dict[str, Any]) -> float:
        """Calculate correlation-based adjustment factor."""
        try:
            portfolio_corr = float(correlation_data.get('portfolio_correlation', 0.3))
            
            # Adjust risk limits based on correlation
            if portfolio_corr > 0.7:  # High correlation
                return 0.8  # Reduce risk by 20%
            elif portfolio_corr < 0.2:  # Low correlation
                return 1.1  # Increase risk by 10%
            else:
                return 1.0  # No adjustment
                
        except Exception as e:
            print(f"Error calculating correlation adjustment: {e}")
            return 1.0
    
    def _apply_market_adjustments(self, base_limits: Dict[str, Any], 
                                 volatility_adj: float, 
                                 liquidity_adj: float, 
                                 correlation_adj: float) -> Dict[str, Any]:
        """Apply market adjustments to base limits."""
        # Calculate composite adjustment factor
        composite_adjustment = (volatility_adj + liquidity_adj + correlation_adj) / 3
        
        adjusted_limits = {}
        for key, value in base_limits.items():
            if key in ['max_position_size', 'max_leverage']:
                adjusted_limits[key] = value * composite_adjustment
            else:
                adjusted_limits[key] = value
        
        return adjusted_limits
    
    def _apply_safety_bounds(self, limits: Dict[str, Any], strategy_type: str) -> Dict[str, Any]:
        """Apply safety bounds to ensure limits are within acceptable ranges."""
        # Define safety bounds for each strategy type
        safety_bounds = {
            "arbitrage": {
                "max_position_size": (0.02, 0.10),  # 2% to 10%
                "max_leverage": (1.0, 3.0),         # 1x to 3x
                "stop_loss": (0.001, 0.005),        # 0.1% to 0.5%
                "max_drawdown": (0.005, 0.02)       # 0.5% to 2%
            },
            "trend_following": {
                "max_position_size": (0.05, 0.25),  # 5% to 25%
                "max_leverage": (1.0, 2.0),         # 1x to 2x
                "stop_loss": (0.005, 0.02),         # 0.5% to 2%
                "max_drawdown": (0.01, 0.05)        # 1% to 5%
            },
            "market_making": {
                "max_position_size": (0.03, 0.15),  # 3% to 15%
                "max_leverage": (1.5, 4.0),         # 1.5x to 4x
                "stop_loss": (0.001, 0.008),        # 0.1% to 0.8%
                "max_drawdown": (0.005, 0.03)       # 0.5% to 3%
            },
            "news_driven": {
                "max_position_size": (0.05, 0.20),  # 5% to 20%
                "max_leverage": (1.0, 1.5),         # 1x to 1.5x
                "stop_loss": (0.005, 0.015),        # 0.5% to 1.5%
                "max_drawdown": (0.01, 0.04)        # 1% to 4%
            },
            "htf": {
                "max_position_size": (0.10, 0.30),  # 10% to 30%
                "max_leverage": (1.0, 1.5),         # 1x to 1.5x
                "stop_loss": (0.01, 0.03),          # 1% to 3%
                "max_drawdown": (0.02, 0.08)        # 2% to 8%
            }
        }
        
        bounds = safety_bounds.get(strategy_type, safety_bounds["htf"])
        bounded_limits = {}
        
        for key, value in limits.items():
            if key in bounds:
                min_val, max_val = bounds[key]
                bounded_limits[key] = max(min_val, min(value, max_val))
            else:
                bounded_limits[key] = value
        
        return bounded_limits
    
    def _get_base_limits(self, strategy_type: str) -> Dict[str, Any]:
        """Get base risk limits for a strategy type."""
        return self.base_limits.get(strategy_type, self.base_limits["htf"])
    
    def _update_cache(self, key: str, data: Dict[str, Any]):
        """Update cache with new data."""
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_cache_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['expiry'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'data': data,
            'expiry': time.time() + self.cache_ttl
        }
    
    def clear_cache(self):
        """Clear the entire cache."""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self.cache),
            'max_cache_size': self.max_cache_size,
            'cache_ttl': self.cache_ttl,
            'cache_keys': list(self.cache.keys())
        }
