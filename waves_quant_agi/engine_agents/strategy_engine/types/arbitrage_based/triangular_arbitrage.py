#!/usr/bin/env python3
"""
Triangular Arbitrage Strategy - Fixed and Enhanced
Detects triangular arbitrage opportunities across currency pairs.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from engine_agents.shared_utils import get_shared_redis

class TriangularArbitrage:
    """Triangular arbitrage strategy for currency pairs."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.min_profit_threshold = config.get("min_profit_threshold", 0.0005)  # 0.05% minimum profit
        self.max_triangle_count = config.get("max_triangle_count", 10)  # Maximum triangles to check
        self.execution_timeout = config.get("execution_timeout", 100)  # 100ms timeout
        self.min_volume = config.get("min_volume", 1000)  # Minimum volume for arbitrage
        self.fee_buffer = config.get("fee_buffer", 0.0002)  # 0.02% fee buffer

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect triangular arbitrage opportunities."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            # Get available triangular pairs from data feeds
            triangular_pairs = await self._get_triangular_pairs()
            
            # Group market data by symbol
            symbol_data = {}
            for data in market_data:
                symbol = data.get("symbol", "")
                if symbol:
                    symbol_data[symbol] = data
            
            # Check triangular arbitrage for each triangle
            for triangle in triangular_pairs[:self.max_triangle_count]:
                if len(triangle) == 3:
                    opportunity = await self._check_triangle_arbitrage(triangle, symbol_data)
                    if opportunity:
                        opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting triangular arbitrage: {e}")
            return []

    async def _get_triangular_pairs(self) -> List[List[str]]:
        """Get available triangular pairs from data feeds."""
        try:
            if not self.redis_conn:
                return []
            
            # Get available symbols from data feeds
            symbols_key = "data_feeds:available_symbols"
            symbols_data = self.redis_conn.get(symbols_key)
            
            if symbols_data:
                import json
                symbols = json.loads(symbols_data)
                
                # Generate triangular pairs from available symbols
                triangular_pairs = []
                
                # Extract base currencies (first 3 characters of each symbol)
                base_currencies = set()
                for symbol in symbols:
                    if len(symbol) >= 6:  # Ensure symbol is long enough
                        base_currencies.add(symbol[:3])
                        base_currencies.add(symbol[3:6])
                
                # Generate triangles from base currencies
                base_list = list(base_currencies)
                for i in range(len(base_list)):
                    for j in range(i + 1, len(base_list)):
                        for k in range(j + 1, len(base_list)):
                            if i != j and j != k and i != k:
                                triangular_pairs.append([base_list[i], base_list[j], base_list[k]])
                
                return triangular_pairs[:20]  # Limit to 20 triangles for performance
            
            return []
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting triangular pairs: {e}")
            return []

    async def _check_triangle_arbitrage(self, triangle: List[str], symbol_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for arbitrage opportunity in a specific triangle."""
        try:
            # Extract the three currencies
            currency1, currency2, currency3 = triangle
            
            # Get exchange rates for the triangle
            rate1 = await self._get_exchange_rate(f"{currency1}{currency2}", symbol_data)
            rate2 = await self._get_exchange_rate(f"{currency2}{currency3}", symbol_data)
            rate3 = await self._get_exchange_rate(f"{currency1}{currency3}", symbol_data)
            
            if not all([rate1, rate2, rate3]):
                return None
            
            # Calculate triangular arbitrage
            # Path 1: currency1 -> currency2 -> currency3 -> currency1
            path1_result = (1 / rate1) * (1 / rate2) * rate3
            
            # Path 2: currency1 -> currency3 -> currency2 -> currency1  
            path2_result = (1 / rate3) * rate2 * rate1
            
            # Check for profitable arbitrage
            profit1 = path1_result - 1
            profit2 = path2_result - 1
            
            best_profit = max(profit1, profit2)
            best_path = "path1" if profit1 > profit2 else "path2"
            
            if best_profit > self.min_profit_threshold:
                # Calculate optimal trade sizes
                trade_sizes = await self._calculate_optimal_trade_sizes(
                    currency1, currency2, currency3, best_profit, symbol_data
                )
                
                opportunity = {
                    "type": "triangular_arbitrage",
                    "strategy": "arbitrage",
                    "triangle": triangle,
                    "action": "execute_triangle",
                    "entry_currency": currency1,
                    "path": best_path,
                    "profit_potential": best_profit,
                    "rate1": rate1,
                    "rate2": rate2,
                    "rate3": rate3,
                    "trade_sizes": trade_sizes,
                    "confidence": min(best_profit / (self.min_profit_threshold * 2), 0.9),
                    "execution_timeout": self.execution_timeout,
                    "timestamp": int(time.time()),
                    "description": f"Triangular arbitrage {triangle}: Profit {best_profit:.6f}, Path {best_path}"
                }
                
                # Store triangular arbitrage in Redis with proper JSON serialization
                if self.redis_conn:
                    try:
                        import json
                        self.redis_conn.set(
                            f"strategy_engine:triangular_arbitrage:{':'.join(triangle)}:{int(time.time())}", 
                            json.dumps(opportunity), 
                            ex=3600
                        )
                    except json.JSONEncodeError as e:
                        if self.logger:
                            self.logger.error(f"JSON encoding error storing triangular arbitrage: {e}")
                    except ConnectionError as e:
                        if self.logger:
                            self.logger.error(f"Redis connection error storing triangular arbitrage: {e}")
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Unexpected error storing triangular arbitrage: {e}")
                
                if self.logger:
                    self.logger.info(f"Triangular arbitrage opportunity: {opportunity['description']}")
                
                return opportunity
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking triangle arbitrage: {e}")
            return None

    async def _get_exchange_rate(self, pair: str, symbol_data: Dict[str, Any]) -> Optional[float]:
        """Get exchange rate for a currency pair."""
        try:
            # Try direct pair
            if pair in symbol_data:
                return float(symbol_data[pair].get("bid", 0.0))
            
            # Try reverse pair
            reverse_pair = pair[3:] + pair[:3] if len(pair) == 6 else None
            if reverse_pair and reverse_pair in symbol_data:
                return 1.0 / float(symbol_data[reverse_pair].get("ask", 0.0))
            
            # Try to construct from other pairs
            if len(pair) == 6:
                currency1, currency2 = pair[:3], pair[3:]
                # Look for intermediate pairs
                for symbol in symbol_data:
                    if symbol.startswith(currency1) and symbol.endswith(currency2):
                        return float(symbol_data[symbol].get("bid", 0.0))
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting exchange rate for {pair}: {e}")
            return None

    async def _calculate_optimal_trade_sizes(self, currency1: str, currency2: str, 
                                           currency3: str, profit: float, 
                                           symbol_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate optimal trade sizes for triangular arbitrage."""
        try:
            # Get available volumes for each currency
            volume1 = await self._get_currency_volume(currency1, symbol_data)
            volume2 = await self._get_currency_volume(currency2, symbol_data)
            volume3 = await self._get_currency_volume(currency3, symbol_data)
            
            # Calculate base trade size (conservative approach)
            base_size = min(volume1, volume2, volume3) * 0.1  # Use 10% of minimum volume
            
            # Adjust based on profit potential
            if profit > self.min_profit_threshold * 2:
                size_multiplier = 1.5
            elif profit > self.min_profit_threshold * 1.5:
                size_multiplier = 1.2
            else:
                size_multiplier = 1.0
            
            optimal_size = base_size * size_multiplier
            
            # Ensure minimum size
            optimal_size = max(optimal_size, self.min_volume)
            
            return {
                "currency1_size": optimal_size,
                "currency2_size": optimal_size,
                "currency3_size": optimal_size,
                "total_value": optimal_size * 3
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating optimal trade sizes: {e}")
            return {
                "currency1_size": self.min_volume,
                "currency2_size": self.min_volume,
                "currency3_size": self.min_volume,
                "total_value": self.min_volume * 3
            }

    async def _get_currency_volume(self, currency: str, symbol_data: Dict[str, Any]) -> float:
        """Get available volume for a currency."""
        try:
            total_volume = 0.0
            
            for symbol, data in symbol_data.items():
                if currency in symbol:
                    volume = float(data.get("volume_24h", 0.0))
                    total_volume += volume
            
            return total_volume
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting currency volume: {e}")
            return self.min_volume

    async def execute_triangular_arbitrage(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the triangular arbitrage opportunity."""
        try:
            start_time = time.time()
            
            # Simulate execution (in real implementation, this would place actual orders)
            execution_result = {
                "type": "triangular_arbitrage_execution",
                "opportunity_id": opportunity.get("triangle", []) + [str(opportunity.get("timestamp"))],
                "status": "executed",
                "execution_time_ms": (time.time() - start_time) * 1000,
                "profit_realized": opportunity.get("profit_potential", 0.0),
                "triangle": opportunity.get("triangle", []),
                "timestamp": int(time.time())
            }
            
            # Store execution result
            if self.redis_conn:
                self.redis_conn.set(
                    f"strategy_engine:triangular_execution:{execution_result['opportunity_id']}", 
                    str(execution_result), 
                    ex=7200
                )
            
            if self.logger:
                self.logger.info(f"Triangular arbitrage executed: {execution_result}")
            
            return execution_result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error executing triangular arbitrage: {e}")
            return {
                "type": "triangular_arbitrage_execution",
                "status": "failed",
                "error": str(e),
                "timestamp": int(time.time())
            }

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Triangular Arbitrage Strategy",
            "type": "arbitrage",
            "description": "Detects triangular arbitrage opportunities across currency pairs",
            "parameters": {
                "min_profit_threshold": self.min_profit_threshold,
                "max_triangle_count": self.max_triangle_count,
                "execution_timeout": self.execution_timeout,
                "min_volume": self.min_volume,
                "fee_buffer": self.fee_buffer
            },
            "timeframe": "ultra_hft",  # 1ms tier
            "asset_types": ["crypto", "forex"],
            "execution_speed": "ultra_fast"
        }