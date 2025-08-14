#!/usr/bin/env python3
"""
Strategy Learning Manager
Comprehensive learning system for strategy engine optimization.
"""

import asyncio
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from engine_agents.shared_utils import get_shared_logger, get_shared_redis

# Import consolidated trading functionality
from ..trading.memory.trading_context import TradingContext
from ..trading.learning.trading_research_engine import TradingResearchEngine
from ..trading.learning.trading_training_module import TradingTrainingModule
from ..trading.learning.trading_retraining_loop import TradingRetrainingLoop

class StrategyLearningManager:
    """Manages learning and optimization for all strategy components."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "learning_manager")
        self.redis_conn = get_shared_redis()

        # Initialize consolidated trading components
        self.trading_context = TradingContext(config)
        self.trading_research_engine = TradingResearchEngine(config)
        self.trading_training_module = TradingTrainingModule(config)
        self.trading_retraining_loop = TradingRetrainingLoop(config)

        # Learning configuration
        self.learning_rate = config.get("learning_rate", 0.01)
        self.batch_size = config.get("batch_size", 32)
        self.max_history = config.get("max_history", 1000)
        self.performance_threshold = config.get("performance_threshold", 0.6)
        
        # Learning state
        self.learning_history: List[Dict[str, Any]] = []
        self.performance_history: List[Dict[str, Any]] = []
        self.optimization_history: List[Dict[str, Any]] = []

        # Strategy performance tracking
        self.strategy_performance: Dict[str, Dict[str, Any]] = {}
        self.parameter_optimization: Dict[str, Dict[str, Any]] = {}

        # Learning statistics
        self.stats = {
            "learning_cycles": 0,
            "optimizations_performed": 0,
            "strategies_improved": 0,
            "learning_errors": 0,
            "start_time": time.time()
        }

    async def initialize(self) -> bool:
        """Initialize the learning manager."""
        try:
            self.logger.info("Initializing Strategy Learning Manager...")
            
            # Initialize trading components
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            await self.trading_training_module.initialize()
            await self.trading_retraining_loop.initialize()
            
            self.logger.info("Strategy Learning Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize learning manager: {e}")
            return False

    async def learn_from_strategy_execution(self, strategy_data: Dict[str, Any],
                                          execution_result: Dict[str, Any]) -> bool:
        """Learn from strategy execution results."""
        try:
            strategy_name = strategy_data.get("name", "unknown")
            strategy_type = strategy_data.get("type", "unknown")
            
            # Store execution result in trading context
            await self.trading_context.store_execution_result({
                "strategy_name": strategy_name,
                "strategy_type": strategy_type,
                "execution_data": execution_result,
                "timestamp": int(time.time())
            })
            
            # Analyze execution patterns using trading research engine
            execution_analysis = await self.trading_research_engine.analyze_trading_patterns([
                {"type": "execution", "data": execution_result}
            ])
            
            # Update strategy performance
            if strategy_name not in self.strategy_performance:
                self.strategy_performance[strategy_name] = {
                    "executions": 0,
                    "successful_executions": 0,
                    "total_pnl": 0.0,
                    "average_pnl": 0.0,
                    "last_execution": 0
                }
            
            performance = self.strategy_performance[strategy_name]
            performance["executions"] += 1
            performance["last_execution"] = int(time.time())
            
            # Calculate PnL if available
            pnl = execution_result.get("pnl", 0.0)
            if pnl > 0:
                performance["successful_executions"] += 1
            
            performance["total_pnl"] += pnl
            performance["average_pnl"] = performance["total_pnl"] / performance["executions"]
            
            # Store learning event
            learning_event = {
                "type": "strategy_execution",
                "strategy_name": strategy_name,
                "execution_result": execution_result,
                "analysis": execution_analysis,
                "timestamp": int(time.time())
            }
            
            self.learning_history.append(learning_event)
            self.stats["learning_cycles"] += 1
            
            # Trigger retraining if performance is poor
            if performance["average_pnl"] < -self.performance_threshold:
                await self.trading_retraining_loop.add_retraining_event({
                    "strategy_name": strategy_name,
                    "reason": "poor_performance",
                    "priority": "high",
                    "timestamp": int(time.time())
                })
            
            self.logger.info(f"Learned from {strategy_name} execution")
            return True
            
        except Exception as e:
            self.logger.error(f"Error learning from strategy execution: {e}")
            self.stats["learning_errors"] += 1
            return False

    async def optimize_strategy_parameters(self, strategy_name: str) -> Dict[str, Any]:
        """Optimize strategy parameters using machine learning."""
        try:
            # Get strategy performance data from trading context
            strategy_signals = await self.trading_context.get_recent_signals(strategy_name, limit=100)
            execution_results = await self.trading_context.get_recent_execution_results(strategy_name, limit=100)
            
            if not strategy_signals and not execution_results:
                return {"status": "no_data_for_optimization"}
            
            # Prepare training dataset
            training_data = await self.trading_training_module.prepare_trading_dataset(
                strategy_signals + execution_results
            )
            
            # Execute parameter optimization
            optimization_result = await self.trading_training_module.adapt_strategy(
                strategy_name, training_data
            )
            
            # Store optimization result
            self.parameter_optimization[strategy_name] = {
                "last_optimization": int(time.time()),
                "optimization_result": optimization_result,
                "performance_improvement": optimization_result.get("improvement", 0.0)
            }
            
            self.stats["optimizations_performed"] += 1
            
            if optimization_result.get("improvement", 0.0) > 0.1:
                self.stats["strategies_improved"] += 1
            
            return {
                "status": "optimization_completed",
                "strategy_name": strategy_name,
                "improvement": optimization_result.get("improvement", 0.0),
                "new_parameters": optimization_result.get("new_parameters", {})
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing strategy parameters: {e}")
            return {"status": "optimization_failed", "error": str(e)}

    async def get_learning_summary(self) -> Dict[str, Any]:
        """Get comprehensive learning summary."""
        return {
            "stats": self.stats,
            "strategy_performance": self.strategy_performance,
            "parameter_optimization": self.parameter_optimization,
            "learning_history_count": len(self.learning_history),
            "performance_history_count": len(self.performance_history),
            "optimization_history_count": len(self.optimization_history),
            "uptime": time.time() - self.stats["start_time"]
        }

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
            await self.trading_training_module.cleanup()
            await self.trading_retraining_loop.cleanup()
            self.logger.info("Strategy Learning Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
