#!/usr/bin/env python3
"""
Online Generator - Fixed and Enhanced
Generates adaptive strategies based on real-time market conditions.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from engine_agents.shared_utils import get_shared_redis, get_shared_logger

class OnlineGenerator:
    """Online strategy generator for real-time market adaptation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "online_generator")
        self.redis_conn = get_shared_redis()
        
        # Generation thresholds
        self.strategy_threshold = config.get("strategy_threshold", 0.7)
        self.adaptation_frequency = config.get("adaptation_frequency", 300)  # 5 minutes
        self.max_strategies_per_cycle = config.get("max_strategies_per_cycle", 10)
        
        # Generation state
        self.generated_strategies: Dict[str, Dict[str, Any]] = {}
        self.adaptation_history: List[Dict[str, Any]] = []
        self.last_adaptation = 0
        
        self.stats = {
            "strategies_generated": 0,
            "adaptations_triggered": 0,
            "generation_errors": 0,
            "start_time": time.time()
        }

    async def generate_strategy(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate online strategies based on market conditions."""
        try:
            if not market_data:
                self.logger.warning("No market data provided for strategy generation")
                return []
            
            strategies = []
            
            # Analyze market conditions
            try:
                market_conditions = await self._analyze_market_conditions(market_data)
            except ConnectionError as e:
                self.logger.error(f"Redis connection error analyzing market conditions: {e}")
                return []
            except ValueError as e:
                self.logger.error(f"Data validation error analyzing market conditions: {e}")
                return []
            except Exception as e:
                self.logger.error(f"Unexpected error analyzing market conditions: {e}")
                return []
            
            if not market_conditions:
                self.logger.warning("No market conditions extracted")
                return []
            
            # Generate strategies for each market condition
            for condition in market_conditions:
                try:
                    strategy = await self._generate_single_strategy(condition)
                    if strategy:
                        strategies.append(strategy)
                        
                        # Store generated strategy
                        await self._store_generated_strategy(strategy)
                        
                        self.stats["strategies_generated"] += 1
                        
                except Exception as e:
                    self.logger.error(f"Error generating strategy for condition {condition}: {e}")
                    continue
            
            # Record adaptation
            if strategies:
                try:
                    await self._record_adaptation(market_conditions, len(strategies))
                except Exception as e:
                    self.logger.error(f"Error recording adaptation: {e}")
            
            self.logger.info(f"Generated {len(strategies)} online strategies")
            return strategies
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error in strategy generation: {e}")
            return []
        except ValueError as e:
            self.logger.error(f"Data validation error in strategy generation: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in strategy generation: {e}")
            return []

    async def _generate_single_strategy(self, market_condition: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a single strategy based on market condition."""
        try:
            if not isinstance(market_condition, dict):
                self.logger.error(f"Invalid market_condition type: {type(market_condition)}")
                return None
                
            # Extract market condition parameters
            market_regime = market_condition.get("market_regime", "unknown")
            volatility_level = market_condition.get("volatility_level", "unknown")
            trend_strength = market_condition.get("trend_strength", "unknown")
            
            # Determine strategy type based on market conditions
            strategy_type = self._determine_strategy_type_from_conditions(
                market_regime, volatility_level, trend_strength
            )
            
            if not strategy_type:
                return None
            
            # Create strategy
            strategy = {
                "type": "online_generated",
                "strategy_type": strategy_type,
                "market_conditions": market_condition,
                "confidence": 0.7,  # Base confidence for online strategies
                "timestamp": int(time.time()),
                "description": f"Online-generated {strategy_type} strategy for {market_regime} market"
            }
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Unexpected error generating single strategy: {e}")
            return None
    
    def _determine_strategy_type_from_conditions(self, market_regime: str, volatility_level: str, trend_strength: str) -> Optional[str]:
        """Determine strategy type based on market conditions."""
        try:
            if market_regime == "trending":
                if trend_strength in ["uptrend", "downtrend"]:
                    return "trend_following"
                else:
                    return "momentum_trading"
            elif market_regime == "volatile":
                if volatility_level == "high":
                    return "volatility_trading"
                else:
                    return "mean_reversion"
            elif market_regime == "stable":
                return "market_making"
            elif market_regime == "normal":
                return "statistical_arbitrage"
            else:
                return "adaptive"
                
        except Exception as e:
            self.logger.error(f"Unexpected error determining strategy type: {e}")
            return None

    async def _analyze_market_conditions(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market conditions for strategy generation."""
        try:
            if not market_data or not isinstance(market_data, list):
                self.logger.error(f"Invalid market_data: {type(market_data)}")
                return {}
            
            analysis = {
                "timestamp": int(time.time()),
                "data_points": len(market_data),
                "market_regime": "unknown",
                "volatility_level": "unknown",
                "trend_strength": "unknown",
                "volume_profile": "unknown"
            }
            
            # Extract market conditions from data
            try:
                # Simple market condition analysis
                if len(market_data) > 0:
                    # Analyze volatility
                    prices = [float(data.get("close", 0)) for data in market_data if data.get("close")]
                    if len(prices) > 1:
                        price_changes = [abs(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                        avg_change = sum(price_changes) / len(price_changes)
                        
                        if avg_change > 0.05:
                            analysis["volatility_level"] = "high"
                        elif avg_change > 0.02:
                            analysis["volatility_level"] = "medium"
                        else:
                            analysis["volatility_level"] = "low"
                    
                    # Analyze trend
                    if len(prices) > 5:
                        recent_prices = prices[-5:]
                        if recent_prices[0] < recent_prices[-1]:
                            analysis["trend_strength"] = "uptrend"
                        elif recent_prices[0] > recent_prices[-1]:
                            analysis["trend_strength"] = "downtrend"
                        else:
                            analysis["trend_strength"] = "sideways"
                    
                    # Determine market regime
                    if analysis["volatility_level"] == "high" and analysis["trend_strength"] != "sideways":
                        analysis["market_regime"] = "trending"
                    elif analysis["volatility_level"] == "high":
                        analysis["market_regime"] = "volatile"
                    elif analysis["volatility_level"] == "low":
                        analysis["market_regime"] = "stable"
                    else:
                        analysis["market_regime"] = "normal"
                        
            except Exception as e:
                self.logger.error(f"Error analyzing market data: {e}")
                # Keep default values
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Unexpected error in _analyze_market_conditions: {e}")
            return {}

    def _determine_market_regime(self, volatility: float, trend_strength: float, 
                                volume_ratio: float, rsi: float, macd: float) -> str:
        """Determine current market regime."""
        try:
            # High volatility + strong trend = trending regime
            if volatility > 0.4 and trend_strength > 0.6:
                return "trending"
            
            # High volatility + weak trend = volatile regime
            elif volatility > 0.4 and trend_strength < 0.3:
                return "volatile"
            
            # Low volatility + strong trend = momentum regime
            elif volatility < 0.2 and trend_strength > 0.7:
                return "momentum"
            
            # Low volatility + weak trend = sideways regime
            elif volatility < 0.2 and trend_strength < 0.3:
                return "sideways"
            
            # High volume + strong indicators = breakout regime
            elif volume_ratio > 1.5 and (abs(rsi - 50) > 20 or abs(macd) > 0.2):
                return "breakout"
            
            # Default to normal regime
            else:
                return "normal"
                
        except Exception as e:
            self.logger.error(f"Error determining market regime: {e}")
            return "normal"

    async def _calculate_condition_score(self, data: Dict[str, Any], 
                                       market_conditions: Dict[str, Any]) -> float:
        """Calculate condition score for strategy generation."""
        try:
            if not market_conditions:
                return 0.0
            
            score = 0.0
            
            # Volatility component
            volatility = float(data.get("volatility", 0.0))
            avg_volatility = market_conditions.get("avg_volatility", 0.0)
            
            if avg_volatility > 0:
                vol_ratio = volatility / avg_volatility
                if 0.8 <= vol_ratio <= 1.5:  # Optimal volatility range
                    score += 0.3
                elif vol_ratio > 1.5:  # High volatility opportunity
                    score += 0.2
            
            # Trend component
            trend_strength = float(data.get("trend_strength", 0.0))
            if abs(trend_strength) > 0.6:
                score += 0.3
            
            # Volume component
            volume = float(data.get("volume", 0.0))
            avg_volume = float(data.get("avg_volume", volume))
            if avg_volume > 0:
                volume_ratio = volume / avg_volume
                if volume_ratio > 1.3:  # Above average volume
                    score += 0.2
            
            # Technical indicators
            rsi = float(data.get("rsi", 50.0))
            if rsi < 30 or rsi > 70:  # Oversold/overbought
                score += 0.2
            
            macd = float(data.get("macd", 0.0))
            if abs(macd) > 0.1:  # Strong MACD signal
                score += 0.1
            
            # Market regime bonus
            market_regime = market_conditions.get("market_regime", "normal")
            regime_bonus = {
                "trending": 0.1,
                "volatile": 0.15,
                "momentum": 0.1,
                "breakout": 0.2,
                "sideways": 0.05,
                "normal": 0.0
            }.get(market_regime, 0.0)
            
            score += regime_bonus
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating condition score: {e}")
            return 0.0

    async def _determine_strategy_type(self, data: Dict[str, Any], 
                                     market_conditions: Dict[str, Any]) -> str:
        """Determine optimal strategy type based on market conditions."""
        try:
            market_regime = market_conditions.get("market_regime", "normal")
            volatility = float(data.get("volatility", 0.0))
            trend_strength = float(data.get("trend_strength", 0.0))
            rsi = float(data.get("rsi", 50.0))
            
            # Regime-based strategy selection
            if market_regime == "trending":
                if trend_strength > 0.7:
                    return "trend_following"
                else:
                    return "momentum_rider"
            
            elif market_regime == "volatile":
                if volatility > 0.6:
                    return "volatility_trading"
                else:
                    return "mean_reversion"
            
            elif market_regime == "momentum":
                return "momentum_rider"
            
            elif market_regime == "breakout":
                return "breakout_strategy"
            
            elif market_regime == "sideways":
                if abs(rsi - 50) > 20:
                    return "mean_reversion"
                else:
                    return "market_making"
            
            else:  # normal regime
                if abs(trend_strength) > 0.5:
                    return "trend_following"
                elif volatility > 0.3:
                    return "adaptive"
                else:
                    return "market_making"
                    
        except Exception as e:
            self.logger.error(f"Error determining strategy type: {e}")
            return "adaptive"

    async def _create_online_strategy(self, symbol: str, strategy_type: str, 
                                    condition_score: float, data: Dict[str, Any], 
                                    market_conditions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create online strategy from market analysis."""
        try:
            strategy = {
                "type": "online_generated",
                "symbol": symbol,
                "strategy_type": strategy_type,
                "condition_score": condition_score,
                "market_regime": market_conditions.get("market_regime", "normal"),
                "market_conditions": market_conditions,
                "asset_data": {
                    "volatility": float(data.get("volatility", 0.0)),
                    "trend_strength": float(data.get("trend_strength", 0.0)),
                    "volume_ratio": float(data.get("volume", 0.0)) / float(data.get("avg_volume", 1.0)) if data.get("avg_volume", 0) > 0 else 1.0,
                    "rsi": float(data.get("rsi", 50.0)),
                    "macd": float(data.get("macd", 0.0))
                },
                "confidence": min(condition_score * 0.8 + 0.2, 0.9),  # Base confidence of 20%
                "timestamp": int(time.time()),
                "description": f"Online {strategy_type} strategy for {symbol}: score {condition_score:.2f}, regime {market_conditions.get('market_regime', 'normal')}"
            }
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Error creating online strategy: {e}")
            return None

    async def _store_generated_strategy(self, strategy: Dict[str, Any]):
        """Store generated strategy in Redis."""
        try:
            if not isinstance(strategy, dict):
                self.logger.error(f"Invalid strategy type: {type(strategy)}, expected dict")
                return
                
            strategy_id = f"{strategy['type']}:{strategy.get('symbol', 'unknown')}:{strategy['timestamp']}"
            
            # Store in Redis with proper JSON serialization
            try:
                import json
                self.redis_conn.set(
                    f"strategy_engine:online_strategy:{strategy_id}", 
                    json.dumps(strategy), 
                    ex=604800
                )
                
                # Store in local cache
                self.generated_strategies[strategy_id] = strategy
                
                self.logger.info(f"Stored online-generated strategy: {strategy_id}")
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing online strategy: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing online strategy: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing online strategy: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error in _store_generated_strategy: {e}")

    async def _record_adaptation(self, market_conditions: Dict[str, Any], strategy_count: int):
        """Record adaptation event."""
        try:
            if not isinstance(market_conditions, dict):
                self.logger.error(f"Invalid market_conditions type: {type(market_conditions)}, expected dict")
                return
                
            adaptation_record = {
                "timestamp": int(time.time()),
                "market_conditions": market_conditions,
                "strategies_generated": strategy_count,
                "adaptation_type": "online_generation"
            }
            
            # Store adaptation record in Redis with proper JSON serialization
            try:
                import json
                record_key = f"strategy_engine:online_adaptation:{int(time.time())}"
                self.redis_conn.set(record_key, json.dumps(adaptation_record), ex=604800)
                
                # Add to local history
                self.adaptation_history.append(adaptation_record)
                
                # Keep only last 100 adaptations
                if len(self.adaptation_history) > 100:
                    self.adaptation_history = self.adaptation_history[-100:]
                    
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing adaptation record: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing adaptation record: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing adaptation record: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error in _record_adaptation: {e}")

    async def get_generated_strategies(self) -> List[Dict[str, Any]]:
        """Get all generated strategies."""
        try:
            return list(self.generated_strategies.values())
        except Exception as e:
            self.logger.error(f"Unexpected error getting generated strategies: {e}")
            return []

    async def get_adaptation_history(self) -> List[Dict[str, Any]]:
        """Get adaptation history."""
        try:
            return self.adaptation_history.copy()
        except Exception as e:
            self.logger.error(f"Unexpected error getting adaptation history: {e}")
            return []

    async def force_adaptation(self):
        """Force immediate strategy adaptation."""
        try:
            self.logger.info("Forcing online strategy adaptation...")
            
            # Reset adaptation timer
            self.last_adaptation = 0
            
            # Trigger immediate adaptation
            self.stats["adaptations_triggered"] += 1
            
            self.logger.info("Online strategy adaptation forced successfully")
            
        except Exception as e:
            self.logger.error(f"Unexpected error forcing adaptation: {e}")

    def get_generator_stats(self) -> Dict[str, Any]:
        """Get online generator statistics."""
        return {
            **self.stats,
            "generated_strategies": len(self.generated_strategies),
            "adaptations": len(self.adaptation_history),
            "uptime": time.time() - self.stats["start_time"]
        }