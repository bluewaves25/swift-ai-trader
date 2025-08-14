#!/usr/bin/env python3
"""
Fed Policy Detector Strategy - News Driven
Focuses purely on strategy-specific tasks, delegating risk management to the risk management agent.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from datetime import datetime

# Import consolidated trading components
from ....trading.memory.trading_context import TradingContext
from ....trading.learning.trading_research_engine import TradingResearchEngine


class FedPolicyDetectorStrategy:
    """Fed policy detector strategy for news-driven trading."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.policy_impact_threshold = config.get("policy_impact_threshold", 0.03)  # 3% impact
        self.volatility_threshold = config.get("volatility_threshold", 0.02)  # 2% volatility
        self.volume_multiplier = config.get("volume_multiplier", 2.0)  # 2x average volume
        self.lookback_period = config.get("lookback_period", 100)  # 100 periods
        
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
                self.logger.error(f"Failed to initialize fed policy detector strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect fed policy opportunities."""
        if not market_data or len(market_data) < self.lookback_period:
            return []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').tail(self.lookback_period)
            
            opportunities = []
            
            for _, row in df.iterrows():
                symbol = row.get("symbol", "USDJPY")
                current_price = float(row.get("close", 0.0))
                current_volume = float(row.get("volume", 0.0))
                policy_impact = float(row.get("policy_impact", 0.0))
                volatility = float(row.get("volatility", 0.0))
                
                # Calculate policy metrics
                policy_metrics = await self._calculate_policy_metrics(
                    current_price, current_volume, policy_impact, volatility, market_data
                )
                
                # Check if policy signal meets criteria
                if self._is_valid_policy_signal(policy_metrics):
                    signal = self._generate_policy_signal(
                        symbol, current_price, policy_metrics
                    )
                    if signal:
                        self.trading_context.store_signal(signal)
                        opportunities.append(signal)
                        
                        # Update strategy performance
                        self.strategy_performance["total_signals"] += 1
                        self.strategy_performance["average_confidence"] = (
                            (self.strategy_performance["average_confidence"] * 
                             (self.strategy_performance["total_signals"] - 1) + signal["confidence"]) /
                            self.strategy_performance["total_signals"]
                        )
                        
                        self.last_signal_time = datetime.now()
                        
                        if self.logger:
                            self.logger.info(f"Fed policy signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting fed policy opportunities: {e}")
            return []

    async def _calculate_policy_metrics(self, current_price: float, current_volume: float, 
                                       policy_impact: float, volatility: float, 
                                       market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate policy metrics for analysis."""
        try:
            # Calculate volume metrics
            volumes = [float(d.get("volume", 0)) for d in market_data if d.get("volume")]
            avg_volume = np.mean(volumes) if volumes else current_volume
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Calculate policy impact strength
            policy_impact_strength = abs(policy_impact) / self.policy_impact_threshold if self.policy_impact_threshold > 0 else 0
            
            # Calculate volatility strength
            volatility_strength = volatility / self.volatility_threshold if self.volatility_threshold > 0 else 0
            
            # Calculate price momentum
            prices = [float(d.get("close", 0)) for d in market_data if d.get("close")]
            if len(prices) > 1:
                price_momentum = (current_price - prices[0]) / prices[0] if prices[0] > 0 else 0
            else:
                price_momentum = 0.0
            
            # Calculate policy consistency
            policy_impacts = [float(d.get("policy_impact", 0)) for d in market_data if d.get("policy_impact")]
            if len(policy_impacts) > 1:
                policy_consistency = 1.0 - np.std(policy_impacts)  # Higher consistency = lower std
            else:
                policy_consistency = 0.5
            
            return {
                "policy_impact": policy_impact,
                "policy_impact_strength": policy_impact_strength,
                "volatility": volatility,
                "volatility_strength": volatility_strength,
                "volume_ratio": volume_ratio,
                "price_momentum": price_momentum,
                "policy_consistency": policy_consistency,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating policy metrics: {e}")
            return {}

    def _is_valid_policy_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if policy signal meets criteria."""
        try:
            if not metrics:
                return False
            
            policy_impact_strength = metrics.get("policy_impact_strength", 0.0)
            volatility_strength = metrics.get("volatility_strength", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            policy_consistency = metrics.get("policy_consistency", 0.5)
            
            # Check policy impact
            if policy_impact_strength < 1.0:
                return False
            
            # Check volatility
            if volatility_strength < 1.0:
                return False
            
            # Check volume confirmation
            if volume_ratio < self.volume_multiplier:
                return False
            
            # Check policy consistency
            if policy_consistency < 0.3:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating policy signal: {e}")
            return False

    def _generate_policy_signal(self, symbol: str, current_price: float, 
                               metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate fed policy trading signal."""
        try:
            policy_impact = metrics.get("policy_impact", 0.0)
            policy_impact_strength = metrics.get("policy_impact_strength", 0.0)
            volatility_strength = metrics.get("volatility_strength", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            price_momentum = metrics.get("price_momentum", 0.0)
            
            # Determine signal type
            if policy_impact > 0:
                signal_type = "FED_POLICY_HAWKISH"
                confidence = min(policy_impact_strength, 1.0)
            else:
                signal_type = "FED_POLICY_DOVISH"
                confidence = min(policy_impact_strength, 1.0)
            
            # Adjust confidence based on other factors
            volatility_confidence = min(volatility_strength, 1.0)
            volume_confidence = min(volume_ratio / self.volume_multiplier, 1.0)
            momentum_confidence = min(abs(price_momentum) / self.policy_impact_threshold, 1.0)
            
            final_confidence = (confidence + volatility_confidence + volume_confidence + momentum_confidence) / 4
            
            signal = {
                "signal_id": f"fed_policy_{int(time.time())}",
                "strategy_id": "fed_policy_detector",
                "strategy_type": "news_driven",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": final_confidence,
                "metadata": {
                    "policy_impact": policy_impact,
                    "policy_impact_strength": policy_impact_strength,
                    "volatility": metrics.get("volatility", 0.0),
                    "volatility_strength": volatility_strength,
                    "volume_ratio": volume_ratio,
                    "price_momentum": price_momentum
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating fed policy signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")