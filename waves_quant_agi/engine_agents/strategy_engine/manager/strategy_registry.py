#!/usr/bin/env python3
"""
Strategy Registry - Fixed and Enhanced
Manages registration and tracking of all active strategies.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from engine_agents.shared_utils import get_shared_redis, get_shared_logger

# Import consolidated trading functionality
from ..trading.memory.trading_context import TradingContext
from ..trading.interfaces.trade_model import TradeCommand

class StrategyRegistry:
    """Strategy registry for managing all active strategies."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "registry")
        self.redis_conn = get_shared_redis()

        # Initialize consolidated trading components
        self.trading_context = TradingContext(config)

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

    async def initialize(self) -> bool:
        """Initialize the strategy registry."""
        try:
            self.logger.info("Initializing Strategy Registry...")
            
            # Initialize trading components
            await self.trading_context.initialize()
            
            self.logger.info("Strategy Registry initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy registry: {e}")
            return False

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

            # Store strategy in trading context
            await self.trading_context.store_signal({
                "type": "strategy_registration",
                "strategy_id": strategy_id,
                "strategy_data": strategy,
                "timestamp": int(time.time())
            })

            # Add to active strategies
            self.active_strategies[strategy_id] = {
                **strategy,
                "registration_time": int(time.time()),
                "status": "active",
                "executions": 0,
                "last_execution": 0
            }

            # Initialize performance tracking
            self.strategy_performance[strategy_id] = {
                "total_pnl": 0.0,
                "successful_trades": 0,
                "total_trades": 0,
                "average_confidence": 0.0,
                "last_update": int(time.time())
            }

            self.stats["strategies_registered"] += 1
            self.logger.info(f"Strategy {strategy_id} registered successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error registering strategy: {e}")
            self.stats["errors"] += 1
            return False

    def _validate_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Validate strategy structure."""
        required_fields = ["type", "symbol", "timestamp"]
        return all(field in strategy for field in required_fields)

    async def update_strategy(self, strategy_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing strategy."""
        try:
            if strategy_id not in self.active_strategies:
                self.logger.warning(f"Strategy {strategy_id} not found for update")
                return False

            # Update strategy data
            self.active_strategies[strategy_id].update(updates)
            self.active_strategies[strategy_id]["last_update"] = int(time.time())

            # Store update in trading context
            await self.trading_context.store_signal({
                "type": "strategy_update",
                "strategy_id": strategy_id,
                "updates": updates,
                "timestamp": int(time.time())
            })

            self.stats["strategies_updated"] += 1
            self.logger.info(f"Strategy {strategy_id} updated successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error updating strategy {strategy_id}: {e}")
            self.stats["errors"] += 1
            return False

    async def remove_strategy(self, strategy_id: str) -> bool:
        """Remove a strategy from the registry."""
        try:
            if strategy_id not in self.active_strategies:
                self.logger.warning(f"Strategy {strategy_id} not found for removal")
                return False

            # Store removal in trading context
            await self.trading_context.store_signal({
                "type": "strategy_removal",
                "strategy_id": strategy_id,
                "removal_time": int(time.time())
            })

            # Remove from active strategies
            removed_strategy = self.active_strategies.pop(strategy_id)
            
            # Remove performance data
            self.strategy_performance.pop(strategy_id, None)

            self.stats["strategies_removed"] += 1
            self.logger.info(f"Strategy {strategy_id} removed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error removing strategy {strategy_id}: {e}")
            self.stats["errors"] += 1
            return False

    async def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific strategy by ID."""
        return self.active_strategies.get(strategy_id)

    async def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all active strategies."""
        return list(self.active_strategies.values())

    async def get_strategies_by_type(self, strategy_type: str) -> List[Dict[str, Any]]:
        """Get strategies by type."""
        return [s for s in self.active_strategies.values() if s.get("type") == strategy_type]

    async def get_strategies_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Get strategies by symbol."""
        return [s for s in self.active_strategies.values() if s.get("symbol") == symbol]

    async def update_strategy_performance(self, strategy_id: str, 
                                       performance_data: Dict[str, Any]) -> bool:
        """Update strategy performance metrics."""
        try:
            if strategy_id not in self.strategy_performance:
                self.logger.warning(f"Strategy {strategy_id} not found for performance update")
                return False

            performance = self.strategy_performance[strategy_id]
            
            # Update performance metrics
            if "pnl" in performance_data:
                performance["total_pnl"] += performance_data["pnl"]
            
            if "success" in performance_data:
                performance["total_trades"] += 1
                if performance_data["success"]:
                    performance["successful_trades"] += 1
            
            if "confidence" in performance_data:
                current_avg = performance["average_confidence"]
                total_trades = performance["total_trades"]
                if total_trades > 0:
                    performance["average_confidence"] = (
                        (current_avg * (total_trades - 1) + performance_data["confidence"]) / total_trades
                    )

            performance["last_update"] = int(time.time())

            # Store performance update in trading context
            await self.trading_context.store_pnl_snapshot({
                "strategy_id": strategy_id,
                "performance_data": performance,
                "timestamp": int(time.time())
            })

            self.logger.info(f"Performance updated for strategy {strategy_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating performance for strategy {strategy_id}: {e}")
            return False

    async def get_strategy_performance(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific strategy."""
        return self.strategy_performance.get(strategy_id)

    async def get_active_strategies(self) -> List[Dict[str, Any]]:
        """Get all active strategies."""
        try:
            return list(self.active_strategies.values())
        except Exception as e:
            self.logger.error(f"Error getting active strategies: {e}")
            return []

    async def get_registry_status(self) -> Dict[str, Any]:
        """Get comprehensive registry status."""
        return {
            "stats": self.stats,
            "active_strategies_count": len(self.active_strategies),
            "strategy_types": list(set(s.get("type") for s in self.active_strategies.values())),
            "symbols": list(set(s.get("symbol") for s in self.active_strategies.values())),
            "uptime": time.time() - self.stats["start_time"]
        }

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_context.cleanup()
            self.logger.info("Strategy Registry cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

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