#!/usr/bin/env python3
"""
Latency Arbitrage Strategy - Fixed and Enhanced
Detects latency arbitrage opportunities across exchanges.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from engine_agents.shared_utils import get_shared_redis

class LatencyArbitrage:
    """Latency arbitrage strategy for cross-exchange opportunities."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.price_diff_threshold = config.get("price_diff_threshold", 0.005)  # 0.5% price difference
        self.min_spread = config.get("min_spread", 0.001)  # 0.1% minimum spread
        self.max_latency_ms = config.get("max_latency_ms", 50)  # 50ms max latency
        self.fee_buffer = config.get("fee_buffer", 0.0005)  # 0.05% fee buffer
        self.min_volume = config.get("min_volume", 1000)  # Minimum volume for arbitrage

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect latency arbitrage opportunities across exchanges."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            for data in market_data:
                symbol = data.get("symbol", "BTCUSD")
                exchange1_price = float(data.get("exchange1_price", 0.0))
                exchange2_price = float(data.get("exchange2_price", 0.0))
                exchange1_volume = float(data.get("exchange1_volume", 0.0))
                exchange2_volume = float(data.get("exchange2_volume", 0.0))
                latency_ms = float(data.get("latency_ms", 0.0))
                
                # Skip if latency is too high
                if latency_ms > self.max_latency_ms:
                    continue
                
                # Calculate price difference
                if exchange1_price > 0 and exchange2_price > 0:
                    price_diff = abs(exchange1_price - exchange2_price) / min(exchange1_price, exchange2_price)
                    
                    # Get fee information
                    fee_score = await self._get_fee_score(symbol)
                    
                    # Check if arbitrage is profitable
                    if (price_diff > self.price_diff_threshold and 
                        price_diff > (fee_score + self.fee_buffer) and
                        min(exchange1_volume, exchange2_volume) > self.min_volume):
                        
                        # Determine buy/sell direction
                        if exchange1_price < exchange2_price:
                            buy_exchange = "exchange1"
                            sell_exchange = "exchange2"
                            buy_price = exchange1_price
                            sell_price = exchange2_price
                            action = "buy"
                        else:
                            buy_exchange = "exchange2"
                            sell_exchange = "exchange1"
                            buy_price = exchange2_price
                            sell_price = exchange1_price
                            action = "sell"
                        
                        # Calculate profit potential
                        profit_potential = price_diff - fee_score - self.fee_buffer
                        
                        opportunity = {
                            "type": "latency_arbitrage",
                            "strategy": "arbitrage",
                            "symbol": symbol,
                            "action": action,
                            "buy_exchange": buy_exchange,
                            "sell_exchange": sell_exchange,
                            "buy_price": buy_price,
                            "sell_price": sell_price,
                            "entry_price": buy_price,
                            "stop_loss": buy_price * (0.999 if action == "buy" else 1.001),
                            "take_profit": sell_price * (0.999 if action == "sell" else 1.001),
                            "confidence": min(profit_potential / self.price_diff_threshold, 0.95),
                            "price_diff": price_diff,
                            "profit_potential": profit_potential,
                            "latency_ms": latency_ms,
                            "volume_available": min(exchange1_volume, exchange2_volume),
                            "timestamp": int(time.time()),
                            "description": f"Latency arbitrage for {symbol}: Diff {price_diff:.4f}, Profit {profit_potential:.4f}"
                        }
                        opportunities.append(opportunity)
                        
                        # Store latency arbitrage in Redis with proper JSON serialization
                        if self.redis_conn:
                            try:
                                import json
                                self.redis_conn.set(
                                    f"strategy_engine:latency_arbitrage:{symbol}:{int(time.time())}", 
                                    json.dumps(opportunity), 
                                    ex=3600
                                )
                            except json.JSONEncodeError as e:
                                if self.logger:
                                    self.logger.error(f"JSON encoding error storing latency arbitrage: {e}")
                            except ConnectionError as e:
                                if self.logger:
                                    self.logger.error(f"Redis connection error storing latency arbitrage: {e}")
                            except Exception as e:
                                if self.logger:
                                    self.logger.error(f"Unexpected error storing latency arbitrage: {e}")
                        
                        if self.logger:
                            self.logger.info(f"Latency arbitrage opportunity: {opportunity['description']}")

            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting latency arbitrage: {e}")
            return []

    async def _get_fee_score(self, symbol: str) -> float:
        """Get fee score for a symbol from fee monitor."""
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

    async def execute_arbitrage(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the arbitrage opportunity."""
        try:
            start_time = time.time()
            
            # Simulate execution (in real implementation, this would place actual orders)
            execution_result = {
                "type": "arbitrage_execution",
                "opportunity_id": opportunity.get("symbol") + str(opportunity.get("timestamp")),
                "status": "executed",
                "execution_time_ms": (time.time() - start_time) * 1000,
                "profit_realized": opportunity.get("profit_potential", 0.0),
                "timestamp": int(time.time())
            }
            
            # Store execution result
            if self.redis_conn:
                self.redis_conn.set(
                    f"strategy_engine:arbitrage_execution:{execution_result['opportunity_id']}", 
                    str(execution_result), 
                    ex=7200
                )
            
            if self.logger:
                self.logger.info(f"Arbitrage executed: {execution_result}")
            
            return execution_result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error executing arbitrage: {e}")
            return {
                "type": "arbitrage_execution",
                "status": "failed",
                "error": str(e),
                "timestamp": int(time.time())
            }

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Latency Arbitrage Strategy",
            "type": "arbitrage",
            "description": "Detects latency arbitrage opportunities across exchanges",
            "parameters": {
                "price_diff_threshold": self.price_diff_threshold,
                "min_spread": self.min_spread,
                "max_latency_ms": self.max_latency_ms,
                "fee_buffer": self.fee_buffer,
                "min_volume": self.min_volume
            },
            "timeframe": "ultra_hft",  # 1ms tier
            "asset_types": ["crypto", "forex"],
            "execution_speed": "ultra_fast"
        }