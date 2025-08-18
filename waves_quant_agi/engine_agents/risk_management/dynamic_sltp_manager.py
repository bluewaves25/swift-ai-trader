#!/usr/bin/env python3
"""
Dynamic SL/TP Adjustment Manager - Advanced Risk Management for AI Trading Engine
"""

import asyncio
import time
import json
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class VolatilityConfig:
    """Configuration for volatility-based SL/TP adjustments."""
    strategy_type: str
    volatility_multiplier: float  # Multiplier for volatility-based adjustments
    min_adjustment_threshold: float  # Minimum change required for adjustment
    max_adjustment_frequency: int  # Maximum adjustments per hour

@dataclass
class MarketConditionConfig:
    """Configuration for market condition-based adjustments."""
    strategy_type: str
    trend_strength_multiplier: float  # Multiplier for trend strength
    volume_impact_multiplier: float   # Multiplier for volume impact
    news_impact_multiplier: float     # Multiplier for news impact

class DynamicSLTPManager:
    """Manages dynamic SL/TP adjustments based on market conditions."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        self.active_dynamic_adjustments = {}
        self.volatility_configs = self._initialize_volatility_configs()
        self.market_condition_configs = self._initialize_market_condition_configs()
        self.adjustment_history = {}
        
    def _initialize_volatility_configs(self) -> Dict[str, VolatilityConfig]:
        """Initialize volatility-based adjustment configurations."""
        configs = {
            "arbitrage": VolatilityConfig(
                strategy_type="arbitrage",
                volatility_multiplier=0.5,  # Conservative for HFT
                min_adjustment_threshold=0.001,  # 0.1% minimum change
                max_adjustment_frequency=10  # Max 10 adjustments per hour
            ),
            "trend_following": VolatilityConfig(
                strategy_type="trend_following",
                volatility_multiplier=1.2,  # More aggressive for trends
                min_adjustment_threshold=0.005,  # 0.5% minimum change
                max_adjustment_frequency=6   # Max 6 adjustments per hour
            ),
            "market_making": VolatilityConfig(
                strategy_type="market_making",
                volatility_multiplier=0.8,  # Moderate for market making
                min_adjustment_threshold=0.003,  # 0.3% minimum change
                max_adjustment_frequency=8   # Max 8 adjustments per hour
            ),
            "htf": VolatilityConfig(
                strategy_type="htf",
                volatility_multiplier=1.5,  # Most aggressive for HTF
                min_adjustment_threshold=0.008,  # 0.8% minimum change
                max_adjustment_frequency=4   # Max 4 adjustments per hour
            ),
            "news_driven": VolatilityConfig(
                strategy_type="news_driven",
                volatility_multiplier=1.0,  # Standard for news strategies
                min_adjustment_threshold=0.004,  # 0.4% minimum change
                max_adjustment_frequency=7   # Max 7 adjustments per hour
            ),
            "statistical_arbitrage": VolatilityConfig(
                strategy_type="statistical_arbitrage",
                volatility_multiplier=0.9,  # Moderate for stat arb
                min_adjustment_threshold=0.003,  # 0.3% minimum change
                max_adjustment_frequency=8   # Max 8 adjustments per hour
            )
        }
        return configs
    
    def _initialize_market_condition_configs(self) -> Dict[str, MarketConditionConfig]:
        """Initialize market condition-based adjustment configurations."""
        configs = {
            "arbitrage": MarketConditionConfig(
                strategy_type="arbitrage",
                trend_strength_multiplier=0.3,  # Low trend impact for HFT
                volume_impact_multiplier=0.8,   # High volume impact for HFT
                news_impact_multiplier=0.2      # Low news impact for HFT
            ),
            "trend_following": MarketConditionConfig(
                strategy_type="trend_following",
                trend_strength_multiplier=1.5,  # High trend impact
                volume_impact_multiplier=0.6,   # Moderate volume impact
                news_impact_multiplier=0.4      # Moderate news impact
            ),
            "market_making": MarketConditionConfig(
                strategy_type="market_making",
                trend_strength_multiplier=0.8,  # Moderate trend impact
                volume_impact_multiplier=1.2,   # High volume impact
                news_impact_multiplier=0.3      # Low news impact
            ),
            "htf": MarketConditionConfig(
                strategy_type="htf",
                trend_strength_multiplier=2.0,  # Highest trend impact
                volume_impact_multiplier=0.4,   # Low volume impact
                news_impact_multiplier=0.8      # High news impact
            ),
            "news_driven": MarketConditionConfig(
                strategy_type="news_driven",
                trend_strength_multiplier=0.6,  # Low trend impact
                volume_impact_multiplier=0.5,   # Moderate volume impact
                news_impact_multiplier=1.5      # Highest news impact
            ),
            "statistical_arbitrage": MarketConditionConfig(
                strategy_type="statistical_arbitrage",
                trend_strength_multiplier=0.7,  # Moderate trend impact
                volume_impact_multiplier=0.7,   # Moderate volume impact
                news_impact_multiplier=0.3      # Low news impact
            )
        }
        return configs
    
    async def add_dynamic_adjustment_tracking(self, position_data: Dict[str, Any]) -> bool:
        """Add a new position to dynamic SL/TP adjustment tracking."""
        try:
            position_id = position_data.get("position_id")
            symbol = position_data.get("symbol")
            strategy_type = position_data.get("strategy_type", "unknown")
            entry_price = position_data.get("entry_price", 0)
            stop_loss = position_data.get("stop_loss", 0)
            take_profit = position_data.get("take_profit", 0)
            
            if not all([position_id, symbol, entry_price, stop_loss, take_profit]):
                if self.logger:
                    self.logger.warning(f"⚠️ Incomplete position data for dynamic adjustment: {position_data}")
                return False
            
            # Get configuration for strategy type
            volatility_config = self.volatility_configs.get(strategy_type)
            market_config = self.market_condition_configs.get(strategy_type)
            
            if not volatility_config or not market_config:
                if self.logger:
                    self.logger.warning(f"⚠️ No dynamic adjustment config for {strategy_type} strategy")
                return False
            
            # Initialize dynamic adjustment tracking
            dynamic_data = {
                "position_id": position_id,
                "symbol": symbol,
                "strategy_type": strategy_type,
                "entry_price": entry_price,
                "current_stop_loss": stop_loss,
                "current_take_profit": take_profit,
                "original_stop_loss": stop_loss,
                "original_take_profit": take_profit,
                "volatility_config": volatility_config,
                "market_config": market_config,
                "adjustments_made": [],
                "last_adjustment_time": None,
                "adjustments_this_hour": 0,
                "last_hour_reset": time.time(),
                "created_at": time.time()
            }
            
            self.active_dynamic_adjustments[position_id] = dynamic_data
            
            if self.logger:
                self.logger.info(f"🎯 Dynamic SL/TP tracking added for {symbol} ({strategy_type}): "
                               f"Volatility multiplier: {volatility_config.volatility_multiplier}, "
                               f"Max adjustments/hour: {volatility_config.max_adjustment_frequency}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error adding dynamic adjustment tracking: {e}")
            return False
    
    async def check_dynamic_adjustments(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if any dynamic SL/TP adjustments should be made."""
        try:
            adjustments_made = []
            
            for position_id, dynamic_data in self.active_dynamic_adjustments.items():
                symbol = dynamic_data["symbol"]
                symbol_market_data = market_data.get(symbol, {})
                
                if not symbol_market_data:
                    continue
                
                # Check if we should make an adjustment
                adjustment = await self._should_make_dynamic_adjustment(dynamic_data, symbol_market_data)
                if adjustment:
                    adjustments_made.append(adjustment)
            
            return adjustments_made
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error checking dynamic adjustments: {e}")
            return []
    
    async def _should_make_dynamic_adjustment(self, dynamic_data: Dict[str, Any], market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if a dynamic adjustment should be made."""
        try:
            current_time = time.time()
            volatility_config = dynamic_data["volatility_config"]
            market_config = dynamic_data["market_config"]
            
            # Check adjustment frequency limit
            if current_time - dynamic_data["last_hour_reset"] > 3600:  # 1 hour
                dynamic_data["adjustments_this_hour"] = 0
                dynamic_data["last_hour_reset"] = current_time
            
            if dynamic_data["adjustments_this_hour"] >= volatility_config.max_adjustment_frequency:
                return None
            
            # Get market condition data
            volatility = market_data.get("volatility", 0.02)  # Default 2%
            trend_strength = market_data.get("trend_strength", 0.5)  # Default 0.5
            volume_change = market_data.get("volume_change", 0.0)  # Default 0%
            news_impact = market_data.get("news_impact", 0.0)  # Default 0%
            
            # Calculate adjustment factors
            volatility_factor = volatility * volatility_config.volatility_multiplier
            trend_factor = trend_strength * market_config.trend_strength_multiplier
            volume_factor = abs(volume_change) * market_config.volume_impact_multiplier
            news_factor = abs(news_impact) * market_config.news_impact_multiplier
            
            # Combined adjustment factor
            total_adjustment_factor = volatility_factor + trend_factor + volume_factor + news_factor
            
            # Check if adjustment threshold met
            if total_adjustment_factor < volatility_config.min_adjustment_threshold:
                return None
            
            # Calculate new SL/TP values
            entry_price = dynamic_data["entry_price"]
            current_stop_loss = dynamic_data["current_stop_loss"]
            current_take_profit = dynamic_data["current_take_profit"]
            
            # Adjust based on market conditions
            new_stop_loss = await self._calculate_adjusted_stop_loss(
                current_stop_loss, entry_price, total_adjustment_factor, market_data
            )
            
            new_take_profit = await self._calculate_adjusted_take_profit(
                current_take_profit, entry_price, total_adjustment_factor, market_data
            )
            
            # Check if adjustment is significant enough
            stop_loss_change = abs(new_stop_loss - current_stop_loss) / entry_price
            take_profit_change = abs(new_take_profit - current_take_profit) / entry_price
            
            if (stop_loss_change < volatility_config.min_adjustment_threshold and 
                take_profit_change < volatility_config.min_adjustment_threshold):
                return None
            
            # Create adjustment
            adjustment = {
                "position_id": dynamic_data["position_id"],
                "symbol": dynamic_data["symbol"],
                "strategy_type": dynamic_data["strategy_type"],
                "old_stop_loss": current_stop_loss,
                "new_stop_loss": new_stop_loss,
                "old_take_profit": current_take_profit,
                "new_take_profit": new_take_profit,
                "adjustment_factor": total_adjustment_factor,
                "volatility_factor": volatility_factor,
                "trend_factor": trend_factor,
                "volume_factor": volume_factor,
                "news_factor": news_factor,
                "timestamp": current_time
            }
            
            # Update dynamic data
            dynamic_data["current_stop_loss"] = new_stop_loss
            dynamic_data["current_take_profit"] = new_take_profit
            dynamic_data["adjustments_made"].append(adjustment)
            dynamic_data["last_adjustment_time"] = current_time
            dynamic_data["adjustments_this_hour"] += 1
            
            if self.logger:
                self.logger.info(f"🎯 Dynamic SL/TP adjustment for {dynamic_data['symbol']}: "
                               f"SL: {current_stop_loss:.5f} → {new_stop_loss:.5f}, "
                               f"TP: {current_take_profit:.5f} → {new_take_profit:.5f}, "
                               f"Factor: {total_adjustment_factor:.4f}")
            
            return adjustment
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error checking dynamic adjustment: {e}")
            return None
    
    async def _calculate_adjusted_stop_loss(self, current_stop_loss: float, entry_price: float, 
                                          adjustment_factor: float, market_data: Dict[str, Any]) -> float:
        """Calculate adjusted stop loss based on market conditions."""
        try:
            # Base adjustment
            base_adjustment = entry_price * adjustment_factor
            
            # Directional adjustment based on trend
            trend_direction = market_data.get("trend_direction", 0)  # -1 for bearish, 1 for bullish
            
            if trend_direction > 0:  # Bullish trend
                # Move stop loss up (more protective)
                adjusted_stop_loss = current_stop_loss + base_adjustment
            elif trend_direction < 0:  # Bearish trend
                # Move stop loss down (more protective)
                adjusted_stop_loss = current_stop_loss - base_adjustment
            else:
                # No trend, minimal adjustment
                adjusted_stop_loss = current_stop_loss + (base_adjustment * 0.1)
            
            return adjusted_stop_loss
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error calculating adjusted stop loss: {e}")
            return current_stop_loss
    
    async def _calculate_adjusted_take_profit(self, current_take_profit: float, entry_price: float, 
                                            adjustment_factor: float, market_data: Dict[str, Any]) -> float:
        """Calculate adjusted take profit based on market conditions."""
        try:
            # Base adjustment
            base_adjustment = entry_price * adjustment_factor
            
            # Directional adjustment based on trend
            trend_direction = market_data.get("trend_direction", 0)  # -1 for bearish, 1 for bullish
            
            if trend_direction > 0:  # Bullish trend
                # Move take profit up (more aggressive)
                adjusted_take_profit = current_take_profit + base_adjustment
            elif trend_direction < 0:  # Bearish trend
                # Move take profit down (more aggressive)
                adjusted_take_profit = current_take_profit - base_adjustment
            else:
                # No trend, minimal adjustment
                adjusted_take_profit = current_take_profit + (base_adjustment * 0.1)
            
            return adjusted_take_profit
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error calculating adjusted take profit: {e}")
            return current_take_profit
    
    async def remove_dynamic_adjustment_tracking(self, position_id: str) -> bool:
        """Remove a position from dynamic adjustment tracking."""
        try:
            if position_id in self.active_dynamic_adjustments:
                dynamic_data = self.active_dynamic_adjustments[position_id]
                symbol = dynamic_data["symbol"]
                strategy_type = dynamic_data["strategy_type"]
                adjustments = len(dynamic_data["adjustments_made"])
                
                del self.active_dynamic_adjustments[position_id]
                
                if self.logger:
                    self.logger.info(f"🎯 Dynamic SL/TP tracking removed for {symbol} ({strategy_type}): "
                                   f"{adjustments} adjustments made")
                
                return True
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error removing dynamic adjustment tracking: {e}")
            return False
    
    async def get_dynamic_adjustment_status(self, position_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of dynamic adjustment tracking."""
        try:
            return self.active_dynamic_adjustments.get(position_id)
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting dynamic adjustment status: {e}")
            return None
    
    async def get_all_dynamic_adjustments(self) -> Dict[str, Any]:
        """Get all active dynamic adjustments."""
        try:
            return {
                "active_count": len(self.active_dynamic_adjustments),
                "dynamic_adjustments": self.active_dynamic_adjustments,
                "timestamp": time.time()
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting all dynamic adjustments: {e}")
            return {"active_count": 0, "dynamic_adjustments": {}, "timestamp": time.time()}
    
    async def cleanup(self):
        """Cleanup dynamic SL/TP manager resources."""
        try:
            self.active_dynamic_adjustments.clear()
            if self.logger:
                self.logger.info("✅ Dynamic SL/TP manager cleaned up")
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error cleaning up dynamic SL/TP manager: {e}")
