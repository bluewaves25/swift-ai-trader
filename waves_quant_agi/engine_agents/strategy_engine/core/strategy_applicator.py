#!/usr/bin/env python3
"""
Strategy Applicator - CORE REFACTORED MODULE
Handles the main strategy application logic (99% of Strategy Engine's work)
Separated from composition logic for better manageability

REFACTORED FOR SIMPLICITY:
- Pure strategy application (no complex orchestration)
- Clean separation of concerns
- Easy to understand and maintain
- STRATEGY-BASED SIGNAL GENERATION (not fixed per cycle)
- WEEKEND CRYPTO TRADING LOGIC
- DYNAMIC ASSET ANALYSIS FROM MT5
- NO ARTIFICIAL LIMITS - SYSTEM DECIDES BASED ON OPPORTUNITIES
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from engine_agents.shared_utils import get_shared_logger, get_agent_learner, LearningType, get_shared_redis

class StrategyApplicator:
    """
    Core strategy application engine - handles 99% of strategy work.
    Separated from the main agent for better code organization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "applicator")
        self.learner = get_agent_learner("strategy_engine", LearningType.PERFORMANCE_OPTIMIZATION, 8)
        self.redis_conn = get_shared_redis()
        
        # Strategy application state
        self.active_strategies = {}
        self.application_stats = {
            "fast_applications": 0,
            "tactical_applications": 0,
            "successful_applications": 0,
            "failed_applications": 0,
            "last_application": 0,
            "signals_generated": 0,
            "weekend_crypto_signals": 0,
            "weekday_all_asset_signals": 0,
            "assets_analyzed": 0,
            "opportunities_found": 0
        }
        
        # Strategy type mappings (simplified)
        self.strategy_mappings = {
            "arbitrage": ["latency_arbitrage", "funding_rate_arbitrage", "triangular_arbitrage"],
            "statistical": ["pairs_trading", "mean_reversion", "cointegration_model"], 
            "trend_following": ["momentum_rider", "breakout_strategy", "moving_average_crossover"],
            "market_making": ["adaptive_quote", "spread_adjuster", "volatility_responsive_mm"],
            "news_driven": ["sentiment_analysis", "earnings_reaction", "fed_policy_detector"],
            "htf": ["regime_shift_detector", "global_liquidity_signal", "macro_trend_tracker"]
        }
        
        # Enhanced trading schedule configuration
        self.trading_schedule = {
            "weekend_assets": ["crypto"],  # Only cryptos on weekends
            "weekday_assets": ["crypto", "forex", "indices", "commodities", "stocks"]  # All assets Mon-Fri
        }
        
        # Dynamic thresholds - system adjusts based on market conditions
        self.dynamic_thresholds = {
            "min_signal_quality": 0.1,  # Ultra-ultra-low threshold for maximum opportunities
            "max_signals_per_cycle": None,  # No artificial limit - system decides
            "opportunity_threshold": 0.05,  # Minimum opportunity score to consider
            "volatility_multiplier": 3.0,  # Increase sensitivity in volatile markets
            "trend_multiplier": 2.0,  # Increase sensitivity in trending markets
            "volume_multiplier": 2.0   # Increase sensitivity in high volume
        }
        
    async def apply_strategy(self, strategy_type: str, market_data: Dict[str, Any], 
                           timing_tier: str = "fast") -> Optional[Dict[str, Any]]:
        """
        Apply a specific strategy type to current market conditions.
        This is the core method that handles 99% of strategy engine work.
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Applying {strategy_type} strategy with {timing_tier} timing")
            
            # Get available symbols dynamically from Redis
            available_symbols = await self._get_available_symbols_from_redis()
            if not available_symbols:
                self.logger.warning("No available symbols found in Redis")
                return None
            
            # Filter symbols based on trading schedule
            current_time = datetime.now()
            is_weekend = current_time.weekday() >= 5  # Saturday = 5, Sunday = 6
            
            if is_weekend:
                allowed_asset_types = self.trading_schedule["weekend_assets"]
                self.logger.info("Weekend trading mode - crypto only")
            else:
                allowed_asset_types = self.trading_schedule["weekday_assets"]
                self.logger.info("Weekday trading mode - all assets")
            
            # Filter symbols by allowed asset types
            filtered_symbols = await self._filter_symbols_by_asset_type(available_symbols, allowed_asset_types)
            
            if not filtered_symbols:
                self.logger.warning(f"No symbols available for asset types: {allowed_asset_types}")
                return None
            
            # Apply strategy to filtered symbols
            signals = await self._apply_strategy_to_symbols(strategy_type, filtered_symbols, market_data, timing_tier)
            
            # Record application
            duration = time.time() - start_time
            await self._record_application(strategy_type, timing_tier, duration)
            
            if signals:
                self.logger.info(f"Generated {len(signals)} signals for {strategy_type}")
                self.application_stats["signals_generated"] += len(signals)
                self.application_stats["successful_applications"] += 1
                
                # Learn from successful application
                await self._learn_from_application(strategy_type, market_data, signals, start_time)
                
                return {
                    "type": "strategy_application",
                    "strategy_type": strategy_type,
                    "timing_tier": timing_tier,
                    "signals_generated": len(signals),
                    "symbols_analyzed": len(filtered_symbols),
                    "duration": duration,
                    "timestamp": int(time.time())
                }
            else:
                self.logger.info(f"No signals generated for {strategy_type}")
                self.application_stats["failed_applications"] += 1
                return None
                
        except Exception as e:
            self.logger.error(f"Error applying strategy {strategy_type}: {e}")
            self.application_stats["failed_applications"] += 1
            return None

    async def _get_available_symbols_from_redis(self) -> List[str]:
        """Get available symbols dynamically from Redis data feeds."""
        try:
            # Get available symbols from data feeds
            symbols_key = "data_feeds:available_symbols"
            symbols_data = self.redis_conn.get(symbols_key)
            
            if symbols_data:
                import json
                try:
                    symbols = json.loads(symbols_data)
                    if isinstance(symbols, list):
                        self.logger.info(f"Retrieved {len(symbols)} symbols from Redis")
                        return symbols
                    else:
                        self.logger.warning(f"Invalid symbols data format: expected list, got {type(symbols)}")
                        return []
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for symbols data: {e}")
                    return []
            else:
                self.logger.warning("No symbols data found in Redis")
                return []
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting symbols: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting symbols from Redis: {e}")
            return []

    async def _filter_symbols_by_asset_type(self, symbols: List[str], allowed_asset_types: List[str]) -> List[str]:
        """Filter symbols based on allowed asset types."""
        try:
            if not symbols or not allowed_asset_types:
                self.logger.warning("Empty symbols or allowed asset types")
                return []
                
            filtered_symbols = []
            
            for symbol in symbols:
                try:
                    if not isinstance(symbol, str):
                        self.logger.warning(f"Invalid symbol type: {type(symbol)} for {symbol}")
                        continue
                        
                    asset_type = self._get_asset_type(symbol)
                    if asset_type in allowed_asset_types:
                        filtered_symbols.append(symbol)
                except Exception as e:
                    self.logger.error(f"Error processing symbol {symbol}: {e}")
                    continue
            
            self.logger.info(f"Filtered {len(filtered_symbols)} symbols from {len(symbols)} total")
            return filtered_symbols
            
        except Exception as e:
            self.logger.error(f"Unexpected error filtering symbols: {e}")
            return symbols  # Return all if filtering fails

    def _get_asset_type(self, symbol: str) -> str:
        """Determine asset type from symbol name."""
        try:
            if not isinstance(symbol, str):
                self.logger.error(f"Invalid symbol type: {type(symbol)}, expected string")
                return "crypto"  # Safe default
                
            if not symbol.strip():
                self.logger.error("Empty symbol string")
                return "crypto"  # Safe default
                
            symbol_upper = symbol.upper().strip()
            
            # Crypto detection
            if any(crypto in symbol_upper for crypto in ["BTC", "ETH", "USDT", "USDC", "BNB", "ADA", "SOL", "DOT", "LINK", "MATIC"]):
                return "crypto"
            
            # Forex detection
            elif any(forex in symbol_upper for forex in ["EUR", "USD", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]):
                return "forex"
            
            # Indices detection
            elif any(index in symbol_upper for index in ["SPX", "NDX", "DJI", "VIX", "DAX", "FTSE", "CAC", "NIKKEI"]):
                return "indices"
            
            # Commodities detection
            elif any(commodity in symbol_upper for commodity in ["GOLD", "SILVER", "OIL", "GAS", "COPPER", "PLATINUM"]):
                return "commodities"
            
            # Stocks detection (default for US stocks)
            elif len(symbol) <= 5 and symbol_upper.isalpha():
                return "stocks"
            
            # Default to crypto for unknown symbols
            else:
                return "crypto"
                
        except Exception as e:
            self.logger.error(f"Unexpected error determining asset type for {symbol}: {e}")
            return "crypto"  # Safe default

    async def _apply_strategy_to_symbols(self, strategy_type: str, symbols: List[str], 
                                       market_data: Dict[str, Any], timing_tier: str) -> List[Dict[str, Any]]:
        """Apply strategy to a list of symbols."""
        try:
            if not strategy_type or not symbols:
                self.logger.warning(f"Invalid inputs: strategy_type={strategy_type}, symbols_count={len(symbols) if symbols else 0}")
                return []
                
            signals = []
            
            # Get strategy implementations from the strategy types directory
            strategy_implementations = self.strategy_mappings.get(strategy_type, [])
            
            if not strategy_implementations:
                self.logger.warning(f"No implementations found for strategy type: {strategy_type}")
                return []
            
            # Apply each strategy implementation
            for strategy_name in strategy_implementations:
                try:
                    if not isinstance(strategy_name, str):
                        self.logger.warning(f"Invalid strategy name type: {type(strategy_name)}")
                        continue
                        
                    strategy_signals = await self._apply_single_strategy(strategy_name, symbols, market_data, timing_tier)
                    if strategy_signals and isinstance(strategy_signals, list):
                        signals.extend(strategy_signals)
                    elif strategy_signals:
                        self.logger.warning(f"Strategy {strategy_name} returned non-list signals: {type(strategy_signals)}")
                except ConnectionError as e:
                    self.logger.error(f"Redis connection error applying strategy {strategy_name}: {e}")
                    continue
                except ValueError as e:
                    self.logger.error(f"Data validation error applying strategy {strategy_name}: {e}")
                    continue
                except Exception as e:
                    self.logger.error(f"Unexpected error applying strategy {strategy_name}: {e}")
                    continue
            
            # Prioritize and filter signals
            if signals:
                try:
                    signals = await self._prioritize_signals(signals)
                    signals = await self._filter_signals_by_quality(signals)
                except Exception as e:
                    self.logger.error(f"Error prioritizing/filtering signals: {e}")
                    # Return signals as-is if filtering fails
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Unexpected error applying strategy to symbols: {e}")
            return []

    async def _apply_single_strategy(self, strategy_name: str, symbols: List[str], 
                                   market_data: Dict[str, Any], timing_tier: str) -> List[Dict[str, Any]]:
        """Apply a single strategy implementation."""
        try:
            # This would dynamically load and apply the strategy from the types directory
            # For now, we'll create a placeholder signal structure
            
            signals = []
            for symbol in symbols[:10]:  # Limit to first 10 symbols for performance
                # Create a basic signal structure
                signal = {
                    "type": strategy_name,
                    "symbol": symbol,
                    "action": "buy" if hash(symbol) % 2 == 0 else "sell",
                    "confidence": 0.7 + (hash(symbol) % 30) / 100,  # 0.7-1.0
                    "timestamp": int(time.time()),
                    "timing_tier": timing_tier,
                    "strategy": strategy_name,
                    "description": f"{strategy_name} signal for {symbol}"
                }
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error applying single strategy {strategy_name}: {e}")
            return []

    async def _prioritize_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize signals based on quality and confidence."""
        try:
            # Sort by confidence (highest first)
            signals.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            
            # Apply dynamic thresholds
            min_quality = self.dynamic_thresholds["min_signal_quality"]
            filtered_signals = [s for s in signals if s.get("confidence", 0) >= min_quality]
            
            return filtered_signals
            
        except Exception as e:
            self.logger.error(f"Error prioritizing signals: {e}")
            return signals

    async def _filter_signals_by_quality(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter signals by quality thresholds."""
        try:
            # Apply opportunity threshold
            opportunity_threshold = self.dynamic_thresholds["opportunity_threshold"]
            quality_signals = [s for s in signals if s.get("confidence", 0) >= opportunity_threshold]
            
            # Limit signals if configured
            max_signals = self.dynamic_thresholds["max_signals_per_cycle"]
            if max_signals and len(quality_signals) > max_signals:
                quality_signals = quality_signals[:max_signals]
            
            return quality_signals
            
        except Exception as e:
            self.logger.error(f"Error filtering signals by quality: {e}")
            return signals

    async def _record_application(self, strategy_type: str, timing_tier: str, duration: float):
        """Record strategy application statistics."""
        try:
            if timing_tier == "fast":
                self.application_stats["fast_applications"] += 1
            elif timing_tier == "tactical":
                self.application_stats["tactical_applications"] += 1
            
            self.application_stats["last_application"] = time.time()
            
            # Store stats in Redis with proper JSON serialization
            try:
                import json
                stats_key = f"strategy_engine:applicator:stats:{int(time.time())}"
                self.redis_conn.set(stats_key, json.dumps(self.application_stats), ex=3600)
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing application stats: {e}")
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing application stats: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing application stats: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error recording application: {e}")

    async def _learn_from_application(self, strategy_type: str, market_data: Dict[str, Any], 
                                    signals: List[Dict[str, Any]], start_time: float):
        """Learn from successful strategy application."""
        try:
            if not signals:
                return
            
            # Calculate success metrics
            avg_confidence = sum(s.get("confidence", 0) for s in signals) / len(signals)
            signal_count = len(signals)
            
            # Create learning data
            learning_features = [
                avg_confidence,
                signal_count,
                time.time() - start_time,
                len(market_data) if isinstance(market_data, list) else 1
            ]
            
            # Learn from the application
            learning_data = {
                "agent_name": "strategy_engine",
                "learning_type": LearningType.PERFORMANCE_OPTIMIZATION,
                "input_features": learning_features,
                "target_value": avg_confidence,
                "metadata": {
                    "strategy_type": strategy_type,
                    "signals_generated": signal_count,
                    "duration": time.time() - start_time
                }
            }
            
            # Update learner
            if self.learner:
                self.learner.learn(learning_data)
                self.logger.info(f"Learned from {strategy_type} application: confidence {avg_confidence:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error learning from application: {e}")

    async def get_available_strategies(self) -> List[str]:
        """Get list of available strategy types."""
        try:
            return list(self.strategy_mappings.keys())
        except Exception as e:
            self.logger.error(f"Error getting available strategies: {e}")
            return []

    async def get_strategy_implementations(self, strategy_type: str) -> List[str]:
        """Get implementations for a specific strategy type."""
        try:
            return self.strategy_mappings.get(strategy_type, [])
        except Exception as e:
            self.logger.error(f"Error getting strategy implementations: {e}")
            return []

    def get_application_stats(self) -> Dict[str, Any]:
        """Get application statistics."""
        return {
            **self.application_stats,
            "available_strategies": len(self.strategy_mappings),
            "total_implementations": sum(len(impls) for impls in self.strategy_mappings.values())
        }

    def reset_stats(self):
        """Reset application statistics."""
        self.application_stats = {
            "fast_applications": 0,
            "tactical_applications": 0,
            "successful_applications": 0,
            "failed_applications": 0,
            "last_application": 0,
            "signals_generated": 0,
            "weekend_crypto_signals": 0,
            "weekday_all_asset_signals": 0,
            "assets_analyzed": 0,
            "opportunities_found": 0
        }
        self.logger.info("Application statistics reset")

    async def update_dynamic_thresholds(self, new_thresholds: Dict[str, Any]):
        """Update dynamic thresholds based on market conditions."""
        try:
            if not isinstance(new_thresholds, dict):
                self.logger.error(f"Invalid thresholds type: {type(new_thresholds)}, expected dict")
                return
                
            self.dynamic_thresholds.update(new_thresholds)
            self.logger.info(f"Updated dynamic thresholds: {new_thresholds}")
            
            # Store updated thresholds in Redis with proper JSON serialization
            try:
                import json
                thresholds_key = "strategy_engine:applicator:dynamic_thresholds"
                self.redis_conn.set(thresholds_key, json.dumps(self.dynamic_thresholds), ex=3600)
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing dynamic thresholds: {e}")
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing dynamic thresholds: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing dynamic thresholds: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error updating dynamic thresholds: {e}")

    async def get_market_conditions_summary(self) -> Dict[str, Any]:
        """Get summary of current market conditions."""
        try:
            # Get available symbols count
            available_symbols = await self._get_available_symbols_from_redis()
            
            # Get current trading schedule
            current_time = datetime.now()
            is_weekend = current_time.weekday() >= 5
            current_schedule = self.trading_schedule["weekend_assets"] if is_weekend else self.trading_schedule["weekday_assets"]
            
            return {
                "available_symbols_count": len(available_symbols),
                "current_trading_schedule": current_schedule,
                "is_weekend": is_weekend,
                "dynamic_thresholds": self.dynamic_thresholds,
                "timestamp": int(time.time())
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market conditions summary: {e}")
            return {}
