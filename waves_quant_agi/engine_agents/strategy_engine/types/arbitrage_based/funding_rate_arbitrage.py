#!/usr/bin/env python3
"""
Funding Rate Arbitrage Strategy - Fixed and Enhanced
Detects funding rate arbitrage opportunities in perpetual futures.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from engine_agents.shared_utils import get_shared_redis

class FundingRateArbitrage:
    """Funding rate arbitrage strategy for perpetual futures."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.min_funding_rate = config.get("min_funding_rate", 0.0001)  # 0.01% minimum
        self.max_funding_rate = config.get("max_funding_rate", 0.01)  # 1% maximum
        self.funding_threshold = config.get("funding_threshold", 0.0005)  # 0.05% threshold
        self.position_size_limit = config.get("position_size_limit", 0.1)  # 10% of capital
        self.hedge_ratio = config.get("hedge_ratio", 0.95)  # 95% hedge ratio

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect funding rate arbitrage opportunities."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            for data in market_data:
                symbol = data.get("symbol", "BTCUSD")
                spot_price = float(data.get("spot_price", 0.0))
                futures_price = float(data.get("futures_price", 0.0))
                funding_rate = float(data.get("funding_rate", 0.0))
                next_funding_time = data.get("next_funding_time", 0)
                volume_24h = float(data.get("volume_24h", 0.0))
                
                # Check if funding rate is significant
                if abs(funding_rate) > self.funding_threshold:
                    # Calculate arbitrage potential
                    arbitrage_potential = await self._calculate_arbitrage_potential(
                        symbol, spot_price, futures_price, funding_rate, volume_24h
                    )
                    
                    if arbitrage_potential['profitable']:
                        # Determine strategy direction
                        if funding_rate > 0:  # Positive funding rate
                            action = "long_spot_short_futures"
                            entry_price = spot_price
                            stop_loss = spot_price * 0.98
                            take_profit = spot_price * 1.02
                        else:  # Negative funding rate
                            action = "short_spot_long_futures"
                            entry_price = futures_price
                            stop_loss = futures_price * 1.02
                            take_profit = futures_price * 0.98
                        
                        opportunity = {
                            "type": "funding_rate_arbitrage",
                            "strategy": "arbitrage",
                            "symbol": symbol,
                            "action": action,
                            "entry_price": entry_price,
                            "stop_loss": stop_loss,
                            "take_profit": take_profit,
                            "confidence": min(abs(funding_rate) / self.max_funding_rate, 0.9),
                            "funding_rate": funding_rate,
                            "funding_rate_annualized": funding_rate * 3 * 365,  # 8-hour funding
                            "arbitrage_potential": arbitrage_potential['potential'],
                            "next_funding_time": next_funding_time,
                            "volume_24h": volume_24h,
                            "hedge_ratio": self.hedge_ratio,
                            "timestamp": int(time.time()),
                            "description": f"Funding arbitrage for {symbol}: Rate {funding_rate:.6f}, Potential {arbitrage_potential['potential']:.4f}"
                        }
                        opportunities.append(opportunity)
                        
                        # Store funding arbitrage in Redis with proper JSON serialization
                        if self.redis_conn:
                            try:
                                import json
                                self.redis_conn.set(
                                    f"strategy_engine:funding_arbitrage:{symbol}:{int(time.time())}", 
                                    json.dumps(opportunity), 
                                    ex=3600
                                )
                            except json.JSONEncodeError as e:
                                if self.logger:
                                    self.logger.error(f"JSON encoding error storing funding arbitrage: {e}")
                            except ConnectionError as e:
                                if self.logger:
                                    self.logger.error(f"Redis connection error storing funding arbitrage: {e}")
                            except Exception as e:
                                if self.logger:
                                    self.logger.error(f"Unexpected error storing funding arbitrage: {e}")
                        
                        if self.logger:
                            self.logger.info(f"Funding rate arbitrage opportunity: {opportunity['description']}")

            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting funding rate arbitrage: {e}")
            return []

    async def _calculate_arbitrage_potential(self, symbol: str, spot_price: float, 
                                           futures_price: float, funding_rate: float, 
                                           volume_24h: float) -> Dict[str, Any]:
        """Calculate arbitrage potential and profitability."""
        try:
            # Get market data for calculation
            market_info = await self._get_market_info(symbol)
            
            # Calculate basis (difference between spot and futures)
            basis = (futures_price - spot_price) / spot_price if spot_price > 0 else 0
            
            # Calculate funding rate impact
            funding_impact = abs(funding_rate) * 3 * 365  # Annualized
            
            # Calculate transaction costs
            transaction_costs = await self._estimate_transaction_costs(symbol, volume_24h)
            
            # Calculate arbitrage potential
            potential = funding_impact - transaction_costs - abs(basis)
            
            # Check profitability
            profitable = potential > self.funding_threshold
            
            # Calculate optimal position size
            optimal_size = await self._calculate_optimal_position_size(
                symbol, potential, volume_24h, market_info
            )
            
            return {
                "profitable": profitable,
                "potential": potential,
                "basis": basis,
                "funding_impact": funding_impact,
                "transaction_costs": transaction_costs,
                "optimal_position_size": optimal_size
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating arbitrage potential: {e}")
            return {
                "profitable": False,
                "potential": 0.0,
                "basis": 0.0,
                "funding_impact": 0.0,
                "transaction_costs": 0.0,
                "optimal_position_size": 0.0
            }

    async def _get_market_info(self, symbol: str) -> Dict[str, Any]:
        """Get market information for calculations."""
        try:
            if not self.redis_conn:
                return {}
            
            market_key = f"market_info:{symbol}"
            market_info = self.redis_conn.get(market_key)
            
            if market_info:
                import json
                return json.loads(market_info)
            
            return {}
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting market info: {e}")
            return {}

    async def _estimate_transaction_costs(self, symbol: str, volume_24h: float) -> float:
        """Estimate transaction costs for arbitrage."""
        try:
            # Base transaction costs
            base_cost = 0.0005  # 0.05% base cost
            
            # Volume-based adjustment
            if volume_24h > 1000000:  # High volume
                volume_adjustment = 0.8
            elif volume_24h > 100000:  # Medium volume
                volume_adjustment = 1.0
            else:  # Low volume
                volume_adjustment = 1.2
            
            # Market maker adjustment
            market_maker_adjustment = 0.9
            
            total_cost = base_cost * volume_adjustment * market_maker_adjustment
            
            return total_cost
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error estimating transaction costs: {e}")
            return 0.001  # Default cost

    async def _calculate_optimal_position_size(self, symbol: str, potential: float, 
                                             volume_24h: float, market_info: Dict[str, Any]) -> float:
        """Calculate optimal position size for arbitrage."""
        try:
            # Base position size
            base_size = self.position_size_limit
            
            # Adjust based on potential
            if potential > self.max_funding_rate:
                potential_adjustment = 1.2
            elif potential > self.funding_threshold * 2:
                potential_adjustment = 1.0
            else:
                potential_adjustment = 0.8
            
            # Adjust based on volume
            if volume_24h > 1000000:
                volume_adjustment = 1.0
            elif volume_24h > 100000:
                volume_adjustment = 0.8
            else:
                volume_adjustment = 0.6
            
            # Calculate optimal size
            optimal_size = base_size * potential_adjustment * volume_adjustment
            
            # Ensure within limits
            optimal_size = max(0.01, min(optimal_size, self.position_size_limit))
            
            return optimal_size
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating optimal position size: {e}")
            return 0.05  # Default size

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Funding Rate Arbitrage Strategy",
            "type": "arbitrage",
            "description": "Detects funding rate arbitrage opportunities in perpetual futures",
            "parameters": {
                "min_funding_rate": self.min_funding_rate,
                "max_funding_rate": self.max_funding_rate,
                "funding_threshold": self.funding_threshold,
                "position_size_limit": self.position_size_limit,
                "hedge_ratio": self.hedge_ratio
            },
            "timeframe": "fast",  # 100ms tier
            "asset_types": ["crypto"],
            "execution_speed": "fast"
        }