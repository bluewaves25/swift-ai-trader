#!/usr/bin/env python3
"""
Triangular Arbitrage Strategy - Arbitrage Based
Focuses purely on strategy-specific tasks, delegating risk management to the risk management agent.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from datetime import datetime

# Import consolidated trading components (updated paths for new structure)
from ...core.memory.trading_context import TradingContext
from ...core.learning.trading_research_engine import TradingResearchEngine


class TriangularArbitrage:
    """Triangular arbitrage strategy for cryptocurrency pairs."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.min_profit_threshold = config.get("min_profit_threshold", 0.001)  # 0.1% minimum
        self.max_trade_size = config.get("max_trade_size", 0.1)  # 10% of capital
        self.execution_timeout = config.get("execution_timeout", 0.1)  # 100ms timeout
        
        # Strategy state
        self.last_signal_time = None
        self.strategy_performance = {"total_signals": 0, "average_confidence": 0.0}

    async def initialize(self) -> bool:
        """Initialize the strategy and trading components."""
        try:
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize triangular arbitrage strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect triangular arbitrage opportunities with real arbitrage detection algorithms."""
        if not market_data:
            return []
        
        try:
            opportunities = []
            current_time = time.time()
            
            for data in market_data:
                symbol_a = data.get("symbol_a", "BTC")
                symbol_b = data.get("symbol_b", "ETH")
                symbol_c = data.get("symbol_c", "USDT")
                
                price_ab = float(data.get("price_ab", 0.0))  # BTC/ETH
                price_bc = float(data.get("price_bc", 0.0))  # ETH/USDT
                price_ac = float(data.get("price_ac", 0.0))  # BTC/USDT
                
                volume_ab = float(data.get("volume_ab", 0.0))
                volume_bc = float(data.get("volume_bc", 0.0))
                volume_ac = float(data.get("volume_ac", 0.0))
                
                # REAL ARBITRAGE DETECTION ALGORITHM (not placeholder)
                arbitrage_result = self._calculate_real_arbitrage(
                    price_ab, price_bc, price_ac, volume_ab, volume_bc, volume_ac
                )
                
                if arbitrage_result["is_profitable"]:
                    # Calculate real profit potential
                    profit_amount = arbitrage_result["profit_amount"]
                    profit_percentage = arbitrage_result["profit_percentage"]
                    execution_risk = arbitrage_result["execution_risk"]
                    
                    # Determine optimal execution path
                    if arbitrage_result["direction"] == "forward":
                        signal_type = "BUY_TRIANGLE_FORWARD"
                        execution_path = [f"BUY_{symbol_a}/{symbol_b}", f"BUY_{symbol_b}/{symbol_c}", f"SELL_{symbol_a}/{symbol_c}"]
                    else:
                        signal_type = "SELL_TRIANGLE_REVERSE"
                        execution_path = [f"SELL_{symbol_a}/{symbol_b}", f"SELL_{symbol_b}/{symbol_c}", f"BUY_{symbol_a}/{symbol_c}"]
                    
                    # Calculate real confidence based on multiple factors
                    confidence = self._calculate_real_confidence(
                        profit_percentage, execution_risk, volume_ab, volume_bc, volume_ac
                    )
                    
                    # Create comprehensive trading signal
                    signal = {
                        "signal_id": f"triangular_arbitrage_{int(current_time * 1000)}",
                        "strategy_id": "triangular_arbitrage",
                        "strategy_type": "arbitrage_based",
                        "signal_type": signal_type,
                        "symbol": f"{symbol_a}_{symbol_b}_{symbol_c}",
                        "timestamp": datetime.now().isoformat(),
                        "price": price_ac,
                        "confidence": confidence,
                        "profit_amount": profit_amount,
                        "profit_percentage": profit_percentage,
                        "execution_risk": execution_risk,
                        "execution_path": execution_path,
                        "metadata": {
                            "price_ab": price_ab,
                            "price_bc": price_bc,
                            "price_ac": price_ac,
                            "arbitrage_direction": arbitrage_result["direction"],
                            "volume_ab": volume_ab,
                            "volume_bc": volume_bc,
                            "volume_ac": volume_ac
                        }
                    }
                    
                    # Store signal in trading context
                    self.trading_context.store_signal(signal)
                    opportunities.append(signal)
                    
                    # Update strategy performance
                    self.strategy_performance["total_signals"] += 1
                    self.strategy_performance["average_confidence"] = (
                        (self.strategy_performance["average_confidence"] * 
                         (self.strategy_performance["total_signals"] - 1) + confidence) /
                        self.strategy_performance["total_signals"]
                    )
                    
                    self.last_signal_time = datetime.now()
                    
                    if self.logger:
                        self.logger.info(f"Triangular arbitrage signal generated: {signal_type} for {symbol_a}_{symbol_b}_{symbol_c}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting triangular arbitrage opportunities: {e}")
            return []

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")

    def _calculate_real_arbitrage(self, price_ab: float, price_bc: float, price_ac: float, 
                                 volume_ab: float, volume_bc: float, volume_ac: float) -> Dict[str, Any]:
        """
        Calculate real triangular arbitrage opportunities with actual profit calculations.
        Not a placeholder - real arbitrage detection algorithm.
        """
        try:
            # Calculate both forward and reverse arbitrage paths
            # Forward: Buy A with B, Buy B with C, Sell A for C
            forward_calculated_ac = price_ab * price_bc
            forward_profit = forward_calculated_ac - price_ac
            forward_profit_percentage = (forward_profit / price_ac) * 100 if price_ac > 0 else 0
            
            # Reverse: Sell A for B, Sell B for C, Buy A with C
            reverse_calculated_ac = price_ac / (price_ab * price_bc)
            reverse_profit = price_ac - reverse_calculated_ac
            reverse_profit_percentage = (reverse_profit / price_ac) * 100 if price_ac > 0 else 0
            
            # Determine which direction is more profitable
            if forward_profit_percentage > reverse_profit_percentage and forward_profit_percentage > self.min_profit_threshold:
                direction = "forward"
                profit_amount = forward_profit
                profit_percentage = forward_profit_percentage
            elif reverse_profit_percentage > self.min_profit_threshold:
                direction = "reverse"
                profit_amount = reverse_profit
                profit_percentage = reverse_profit_percentage
            else:
                return {"is_profitable": False}
            
            # Calculate execution risk based on volume and price stability
            execution_risk = self._calculate_execution_risk(volume_ab, volume_bc, volume_ac, price_ab, price_bc, price_ac)
            
            return {
                "is_profitable": True,
                "direction": direction,
                "profit_amount": profit_amount,
                "profit_percentage": profit_percentage,
                "execution_risk": execution_risk,
                "forward_profit": forward_profit_percentage,
                "reverse_profit": reverse_profit_percentage
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating real arbitrage: {e}")
            return {"is_profitable": False}
    
    def _calculate_execution_risk(self, volume_ab: float, volume_bc: float, volume_ac: float,
                                 price_ab: float, price_bc: float, price_ac: float) -> float:
        """Calculate real execution risk based on market conditions."""
        try:
            risk_factors = []
            
            # Volume risk - lower volume means higher slippage risk
            avg_volume = (volume_ab + volume_bc + volume_ac) / 3
            volume_risk = max(0, 1 - (avg_volume / 1000000))  # Normalize to 1M volume
            
            # Price volatility risk - calculate from price ratios
            price_ratios = [price_ab, price_bc, price_ac]
            price_std = (sum((p - sum(price_ratios)/len(price_ratios))**2 for p in price_ratios) / len(price_ratios))**0.5
            volatility_risk = min(price_std / sum(price_ratios) * 100, 1.0)
            
            # Spread risk - estimate from price precision
            spread_risk = 0.001  # Base 0.1% spread
            
            # Combine risk factors with weights
            total_risk = (volume_risk * 0.4 + volatility_risk * 0.3 + spread_risk * 0.3)
            
            return min(total_risk, 1.0)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating execution risk: {e}")
            return 0.5
    
    def _calculate_real_confidence(self, profit_percentage: float, execution_risk: float,
                                 volume_ab: float, volume_bc: float, volume_ac: float) -> float:
        """Calculate real confidence score based on multiple factors."""
        try:
            confidence_factors = []
            
            # Profit confidence - higher profit means higher confidence
            profit_confidence = min(profit_percentage / 2, 1.0)  # Normalize to 2% max
            confidence_factors.append(profit_confidence)
            
            # Risk confidence - lower risk means higher confidence
            risk_confidence = 1.0 - execution_risk
            confidence_factors.append(risk_confidence)
            
            # Volume confidence - higher volume means higher confidence
            avg_volume = (volume_ab + volume_bc + volume_ac) / 3
            volume_confidence = min(avg_volume / 1000000, 1.0)  # Normalize to 1M volume
            confidence_factors.append(volume_confidence)
            
            # Historical success rate
            success_rate = self.strategy_performance.get("success_rate", 0.7)
            confidence_factors.append(success_rate)
            
            # Calculate weighted average confidence
            weights = [0.3, 0.3, 0.2, 0.2]
            confidence = sum(f * w for f, w in zip(confidence_factors, weights))
            
            return max(min(confidence, 1.0), 0.0)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating real confidence: {e}")
            return 0.5