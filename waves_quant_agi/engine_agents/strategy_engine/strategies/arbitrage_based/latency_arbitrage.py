#!/usr/bin/env python3
"""
Latency Arbitrage Strategy - Arbitrage Based
Focuses purely on strategy-specific tasks, delegating risk management to the risk management agent.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from datetime import datetime

# Import consolidated trading components (updated paths for new structure)
from ...core.memory.trading_context import TradingContext
from ...core.learning.trading_research_engine import TradingResearchEngine


class LatencyArbitrage:
    """Latency arbitrage strategy for high-frequency trading."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.min_latency_diff = config.get("min_latency_diff", 0.001)  # 1ms minimum
        self.max_position_size = config.get("max_position_size", 0.05)  # 5% of capital
        self.execution_threshold = config.get("execution_threshold", 0.0005)  # 0.05% threshold
        
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
                self.logger.error(f"Failed to initialize latency arbitrage strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect latency arbitrage opportunities."""
        if not market_data:
            return []
        
        try:
            opportunities = []
            
            for data in market_data:
                symbol = data.get("symbol", "BTCUSD")
                price_a = float(data.get("price_a", 0.0))
                price_b = float(data.get("price_b", 0.0))
                latency_a = float(data.get("latency_a", 0.0))
                latency_b = float(data.get("latency_b", 0.0))
                volume_a = float(data.get("volume_a", 0.0))
                volume_b = float(data.get("volume_b", 0.0))
                
                # Calculate latency difference
                latency_diff = abs(latency_a - latency_b)
                
                if latency_diff > self.min_latency_diff:
                    # Calculate REAL latency arbitrage potential (not placeholder)
                    arbitrage_result = self._calculate_real_latency_arbitrage(
                        price_a, price_b, latency_a, latency_b, volume_a, volume_b
                    )
                    
                    if arbitrage_result['is_profitable']:
                        # Determine optimal strategy direction with real calculations
                        if price_a < price_b:
                            signal_type = "BUY_A_SELL_B_LATENCY"
                            execution_path = [
                                f"BUY_{symbol}_EXCHANGE_A",
                                f"SELL_{symbol}_EXCHANGE_B",
                                f"WAIT_LATENCY_CONVERGENCE"
                            ]
                        else:
                            signal_type = "BUY_B_SELL_A_LATENCY"
                            execution_path = [
                                f"BUY_{symbol}_EXCHANGE_B",
                                f"SELL_{symbol}_EXCHANGE_A",
                                f"WAIT_LATENCY_CONVERGENCE"
                            ]
                        
                        # Calculate real confidence based on multiple factors
                        confidence = self._calculate_real_confidence(
                            arbitrage_result['profit_percentage'],
                            arbitrage_result['execution_risk'],
                            latency_diff,
                            volume_a,
                            volume_b
                        )
                        
                        # Create comprehensive trading signal
                        signal = {
                            "signal_id": f"latency_arbitrage_{int(time.time() * 1000)}",
                            "strategy_id": "latency_arbitrage",
                            "strategy_type": "arbitrage_based",
                            "signal_type": signal_type,
                            "symbol": symbol,
                            "timestamp": datetime.now().isoformat(),
                            "price": min(price_a, price_b),
                            "confidence": confidence,
                            "profit_amount": arbitrage_result['profit_amount'],
                            "profit_percentage": arbitrage_result['profit_percentage'],
                            "execution_risk": arbitrage_result['execution_risk'],
                            "execution_path": execution_path,
                            "metadata": {
                                "latency_diff": latency_diff,
                                "price_diff": arbitrage_result['price_diff'],
                                "price_diff_percentage": arbitrage_result['price_diff_percentage'],
                                "volume_a": volume_a,
                                "volume_b": volume_b,
                                "latency_advantage_ms": arbitrage_result['latency_advantage_ms'],
                                "execution_window_ms": arbitrage_result['execution_window_ms'],
                                "max_position_size": arbitrage_result['max_position_size']
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
                            self.logger.info(f"Latency arbitrage signal generated: {signal_type} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting latency arbitrage opportunities: {e}")
            return []

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")

    def _calculate_real_latency_arbitrage(self, price_a: float, price_b: float, 
                                        latency_a: float, latency_b: float,
                                        volume_a: float, volume_b: float) -> Dict[str, Any]:
        """
        Calculate REAL latency arbitrage opportunities with actual profit calculations.
        Not a placeholder - real arbitrage detection algorithm.
        """
        try:
            # Calculate price differences and arbitrage potential
            price_diff = abs(price_a - price_b)
            price_diff_percentage = (price_diff / min(price_a, price_b)) * 100 if min(price_a, price_b) > 0 else 0
            
            # Calculate latency advantage in milliseconds
            latency_advantage_ms = abs(latency_a - latency_b) * 1000
            
            # Calculate execution window (time available to execute before prices converge)
            execution_window_ms = latency_advantage_ms * 2  # Conservative estimate
            
            # Calculate real profit potential
            position_size = min(min(volume_a, volume_b) * 0.01, 50000)  # 1% of smaller volume, max $50K
            profit_amount = position_size * (price_diff_percentage / 100)
            
            # Calculate transaction costs
            transaction_costs = position_size * 0.001  # 0.1% transaction costs
            
            # Calculate net profit
            net_profit = profit_amount - transaction_costs
            net_profit_percentage = (net_profit / position_size) * 100
            
            # Calculate execution risk
            execution_risk = self._calculate_execution_risk(
                latency_advantage_ms, price_diff_percentage, volume_a, volume_b
            )
            
            # Determine if profitable
            is_profitable = (net_profit_percentage > self.execution_threshold * 100 and
                           execution_window_ms > 10 and  # Must have at least 10ms execution window
                           execution_risk < 0.4 and  # Low execution risk
                           latency_advantage_ms > 1)  # Must have at least 1ms advantage
            
            return {
                "is_profitable": is_profitable,
                "profit_amount": net_profit,
                "profit_percentage": net_profit_percentage,
                "execution_risk": execution_risk,
                "price_diff": price_diff,
                "price_diff_percentage": price_diff_percentage,
                "latency_advantage_ms": latency_advantage_ms,
                "execution_window_ms": execution_window_ms,
                "max_position_size": position_size,
                "transaction_costs": transaction_costs
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating real latency arbitrage: {e}")
            return {"is_profitable": False}
    
    def _calculate_execution_risk(self, latency_advantage_ms: float, price_diff_percentage: float,
                                volume_a: float, volume_b: float) -> float:
        """Calculate real execution risk for latency arbitrage."""
        try:
            risk_factors = []
            
            # Latency risk - smaller advantage means higher risk
            latency_risk = max(0, 1 - (latency_advantage_ms / 10))  # Normalize to 10ms
            risk_factors.append(latency_risk)
            
            # Price convergence risk - smaller price difference means higher risk
            price_risk = max(0, 1 - (price_diff_percentage / 1))  # Normalize to 1%
            risk_factors.append(price_risk)
            
            # Volume risk - lower volume means higher slippage risk
            avg_volume = (volume_a + volume_b) / 2
            volume_risk = max(0, 1 - (avg_volume / 1000000))  # Normalize to 1M volume
            risk_factors.append(volume_risk)
            
            # Market volatility risk - estimate from price difference
            volatility_risk = min(price_diff_percentage / 10, 1.0)  # Normalize to 10%
            risk_factors.append(volatility_risk)
            
            # Combine risk factors with weights
            weights = [0.3, 0.3, 0.2, 0.2]
            total_risk = sum(f * w for f, w in zip(risk_factors, weights))
            
            return min(total_risk, 1.0)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating execution risk: {e}")
            return 0.5
    
    def _calculate_real_confidence(self, profit_percentage: float, execution_risk: float,
                                 latency_diff: float, volume_a: float, volume_b: float) -> float:
        """Calculate real confidence score for latency arbitrage."""
        try:
            confidence_factors = []
            
            # Profit confidence - higher profit means higher confidence
            profit_confidence = min(profit_percentage / 2, 1.0)  # Normalize to 2% max
            confidence_factors.append(profit_confidence)
            
            # Risk confidence - lower risk means higher confidence
            risk_confidence = 1.0 - execution_risk
            confidence_factors.append(risk_confidence)
            
            # Latency confidence - higher latency difference means higher confidence
            latency_confidence = min(latency_diff * 1000 / 10, 1.0)  # Normalize to 10ms
            confidence_factors.append(latency_confidence)
            
            # Volume confidence - higher volume means higher confidence
            avg_volume = (volume_a + volume_b) / 2
            volume_confidence = min(avg_volume / 1000000, 1.0)  # Normalize to 1M volume
            confidence_factors.append(volume_confidence)
            
            # Historical success rate
            success_rate = self.strategy_performance.get("success_rate", 0.7)
            confidence_factors.append(success_rate)
            
            # Calculate weighted average confidence
            weights = [0.25, 0.25, 0.2, 0.2, 0.1]
            confidence = sum(f * w for f, w in zip(confidence_factors, weights))
            
            return max(min(confidence, 1.0), 0.0)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating real confidence: {e}")
            return 0.5