#!/usr/bin/env python3
"""
Strategy Registry - Fixed and Enhanced
Manages registration and tracking of all active strategies.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from engine_agents.shared_utils import get_shared_redis, get_shared_logger

class StrategyRegistry:
    """Strategy registry for managing all active strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "registry")
        self.redis_conn = get_shared_redis()
        
        # Strategy categories based on types directory
        self.strategy_categories = {
            "trend_following": ["breakout_strategy", "momentum_rider", "moving_average_crossover"],
            "arbitrage_based": ["latency_arbitrage", "funding_rate_arbitrage", "triangular_arbitrage"],
            "statistical_arbitrage": ["pairs_trading", "mean_reversion", "cointegration_model"],
            "market_making": ["adaptive_quote", "spread_adjuster", "volatility_responsive_mm"],
            "news_driven": ["sentiment_analysis", "earnings_reaction", "fed_policy_detector"],
            "htf": ["regime_shift_detector", "global_liquidity_signal", "macro_trend_tracker"]
        }
        
        self.active_strategies: Dict[str, Dict[str, Any]] = {}
        self.strategy_performance: Dict[str, Dict[str, Any]] = {}
        
        self.stats = {
            "strategies_registered": 0,
            "strategies_updated": 0,
            "strategies_removed": 0,
            "errors": 0,
            "start_time": time.time()
        }

    async def register_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Register a new strategy in the system."""
        try:
            strategy_id = f"{strategy['type']}:{strategy.get('symbol', 'unknown')}:{strategy['timestamp']}"
            
            if strategy_id in self.active_strategies:
                self.logger.warning(f"Strategy {strategy_id} already registered")
                return False

            # Validate strategy structure
            if not self._validate_strategy(strategy):
                self.logger.error(f"Invalid strategy structure for {strategy_id}")
                return False

            self.active_strategies[strategy_id] = strategy
            self.strategy_performance[strategy_id] = {
                "signals_generated": 0,
                "successful_trades": 0,
                "failed_trades": 0,
                "total_pnl": 0.0,
                "last_activity": time.time()
            }
            
            # Store in Redis with proper JSON serialization
            try:
                import json
                self.redis_conn.set(
                    f"strategy_engine:registry:{strategy_id}", 
                    json.dumps(strategy), 
                    ex=604800
                )
                
                # Store performance tracking with proper JSON serialization
                self.redis_conn.set(
                    f"strategy_engine:performance:{strategy_id}", 
                    json.dumps(self.strategy_performance[strategy_id]), 
                    ex=604800
                )
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing strategy {strategy_id}: {e}")
                return False
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing strategy {strategy_id}: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Unexpected error storing strategy {strategy_id}: {e}")
                return False
            
            self.logger.info(f"Registered strategy {strategy_id}")
            self.stats["strategies_registered"] += 1
            
            # Notify core
            await self.notify_core({
                "type": "strategy_registered",
                "strategy_id": strategy_id,
                "strategy_type": strategy.get("type", "unknown"),
                "timestamp": int(time.time()),
                "description": f"Registered strategy {strategy_id}"
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering strategy: {e}")
            self.stats["errors"] += 1
            return False

    def _validate_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Validate strategy structure."""
        required_fields = ["type", "timestamp"]
        optional_fields = ["symbol", "action", "confidence", "description"]
        
        # Check required fields
        for field in required_fields:
            if field not in strategy:
                return False
        
        # Check if type is valid
        strategy_type = strategy.get("type", "")
        if strategy_type not in self.strategy_categories:
            # Allow custom strategy types
            pass
        
        return True

    async def get_active_strategies(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all active strategies, optionally filtered by category."""
        try:
            if category and category in self.strategy_categories:
                # Filter by category
                strategies = [
                    strategy for strategy_id, strategy in self.active_strategies.items()
                    if strategy.get("type") == category
                ]
            else:
                strategies = list(self.active_strategies.values())
            
            self.logger.info(f"Retrieved {len(strategies)} active strategies")
            return strategies
            
        except Exception as e:
            self.logger.error(f"Error retrieving active strategies: {e}")
            self.stats["errors"] += 1
            return []

    async def get_strategy_by_id(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific strategy by ID."""
        try:
            return self.active_strategies.get(strategy_id)
        except Exception as e:
            self.logger.error(f"Error getting strategy {strategy_id}: {e}")
            return None

    async def update_strategy(self, strategy_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing strategy."""
        try:
            if strategy_id not in self.active_strategies:
                self.logger.warning(f"Strategy {strategy_id} not found for update")
                return False
            
            # Update strategy
            self.active_strategies[strategy_id].update(updates)
            
            # Update in Redis with proper JSON serialization
            try:
                import json
                self.redis_conn.set(
                    f"strategy_engine:registry:{strategy_id}", 
                    json.dumps(self.active_strategies[strategy_id]), 
                    ex=604800
                )
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error updating strategy {strategy_id}: {e}")
                return False
            except ConnectionError as e:
                self.logger.error(f"Redis connection error updating strategy {strategy_id}: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Unexpected error updating strategy {strategy_id}: {e}")
                return False
            
            self.logger.info(f"Updated strategy {strategy_id}")
            self.stats["strategies_updated"] += 1
            
            await self.notify_core({
                "type": "strategy_updated",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Updated strategy {strategy_id}"
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating strategy: {e}")
            self.stats["errors"] += 1
            return False

    async def remove_strategy(self, strategy_id: str) -> bool:
        """Remove a strategy from the registry."""
        try:
            if strategy_id not in self.active_strategies:
                self.logger.warning(f"Strategy {strategy_id} not found for removal")
                return False
            
            # Remove from memory
            del self.active_strategies[strategy_id]
            if strategy_id in self.strategy_performance:
                del self.strategy_performance[strategy_id]
            
            # Remove from Redis
            self.redis_conn.delete(f"strategy_engine:registry:{strategy_id}")
            self.redis_conn.delete(f"strategy_engine:performance:{strategy_id}")
            
            self.logger.info(f"Removed strategy {strategy_id}")
            self.stats["strategies_removed"] += 1
            
            await self.notify_core({
                "type": "strategy_removed",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Removed strategy {strategy_id}"
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing strategy: {e}")
            self.stats["errors"] += 1
            return False

    async def update_strategy_performance(self, strategy_id: str, performance_data: Dict[str, Any]) -> bool:
        """Update strategy performance metrics."""
        try:
            if strategy_id not in self.strategy_performance:
                return False
            
            self.strategy_performance[strategy_id].update(performance_data)
            self.strategy_performance[strategy_id]["last_activity"] = time.time()
            
            # Update in Redis with proper JSON serialization
            try:
                import json
                self.redis_conn.set(
                    f"strategy_engine:performance:{strategy_id}", 
                    json.dumps(self.strategy_performance[strategy_id]), 
                    ex=604800
                )
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error updating performance for {strategy_id}: {e}")
                return False
            except ConnectionError as e:
                self.logger.error(f"Redis connection error updating performance for {strategy_id}: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Unexpected error updating performance for {strategy_id}: {e}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating strategy performance: {e}")
            return False

    async def get_strategy_performance(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific strategy."""
        try:
            return self.strategy_performance.get(strategy_id)
        except Exception as e:
            self.logger.error(f"Error getting strategy performance: {e}")
            return None

    async def get_all_strategy_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics for all strategies."""
        try:
            return self.strategy_performance.copy()
        except Exception as e:
            self.logger.error(f"Error getting all strategy performance: {e}")
            return {}

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            **self.stats,
            "active_strategies": len(self.active_strategies),
            "strategy_categories": {cat: len(strategies) for cat, strategies in self.strategy_categories.items()},
            "uptime": time.time() - self.stats["start_time"]
        }

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of registry updates."""
        try:
            if not isinstance(issue, dict):
                self.logger.error(f"Invalid issue type: {type(issue)}, expected dict")
                return
                
            self.logger.info(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
            
            # Publish with proper JSON serialization
            try:
                import json
                self.redis_conn.publish("strategy_engine_output", json.dumps(issue))
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error notifying core: {e}")
                self.stats["errors"] += 1
            except ConnectionError as e:
                self.logger.error(f"Redis connection error notifying core: {e}")
                self.stats["errors"] += 1
            except Exception as e:
                self.logger.error(f"Unexpected error notifying core: {e}")
                self.stats["errors"] += 1
                
        except Exception as e:
            self.logger.error(f"Unexpected error in notify_core: {e}")
            self.stats["errors"] += 1

    async def cleanup_expired_strategies(self, max_age: int = 86400) -> int:
        """Clean up strategies that haven't been active for a while."""
        try:
            current_time = time.time()
            expired_strategies = []
            
            for strategy_id, performance in self.strategy_performance.items():
                last_activity = performance.get("last_activity", 0)
                if current_time - last_activity > max_age:
                    expired_strategies.append(strategy_id)
            
            # Remove expired strategies
            for strategy_id in expired_strategies:
                await self.remove_strategy(strategy_id)
            
            self.logger.info(f"Cleaned up {len(expired_strategies)} expired strategies")
            return len(expired_strategies)
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired strategies: {e}")
            return 0