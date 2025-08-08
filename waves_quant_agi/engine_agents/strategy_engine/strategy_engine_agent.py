#!/usr/bin/env python3
"""
Strategy Engine Agent
Main orchestrator for strategy composition, registration, and performance tracking
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
import redis
from .logs.strategy_engine_logger import StrategyEngineLogger
from .manager.strategy_registry import StrategyRegistry
from .manager.performance_tracker import PerformanceTracker
from .manager.deployment_manager import DeploymentManager
from .composers.ml_composer import MLComposer
from .composers.online_generator import OnlineGenerator

class StrategyEngineAgent:
    """Main orchestrator for the strategy engine system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        self.redis_client = self._init_redis()
        self.logger = StrategyEngineLogger("strategy_engine_agent", self.redis_client)
        
        # Initialize components
        self.registry = StrategyRegistry(config.get("registry", {}))
        self.performance_tracker = PerformanceTracker(config.get("performance", {}))
        self.deployment_manager = DeploymentManager(config.get("deployment", {}))
        self.ml_composer = MLComposer(config.get("ml_composer", {}))
        self.online_generator = OnlineGenerator(config.get("online_generator", {}))
        
        # Initialize learning components
        self._init_learning_components()
        
        self.stats = {
            "strategies_composed": 0,
            "strategies_deployed": 0,
            "performance_checks": 0,
            "learning_updates": 0,
            "errors": 0,
            "start_time": time.time()
        }

    def _init_redis(self) -> redis.Redis:
        """Initialize Redis connection."""
        try:
            redis_url = self.config.get("redis_url", "redis://localhost:6379")
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            self.logger.log("Redis connection established", "info")
            return client
        except Exception as e:
            self.logger.log_error(f"Failed to connect to Redis: {e}")
            raise

    def _init_learning_components(self):
        """Initialize learning layer components."""
        try:
            # Import learning components
            from .learning_layer.internal.training_module import TrainingModule
            from .learning_layer.internal.research_engine import ResearchEngine
            from .learning_layer.internal.retraining_loop import RetrainingLoop
            
            # Initialize learning components
            self.training_module = TrainingModule(self.config.get("training", {}))
            self.research_engine = ResearchEngine(self.config.get("research", {}))
            self.retraining_loop = RetrainingLoop(self.config.get("retraining", {}))
            
            self.logger.log("Learning components initialized", "info")
        except Exception as e:
            self.logger.log_error(f"Error initializing learning components: {e}")

    async def start(self):
        """Start the strategy engine agent."""
        self.is_running = True
        self.logger.log("Strategy engine agent started", "info")
        
        # Start background tasks
        asyncio.create_task(self._strategy_composition_loop())
        asyncio.create_task(self._performance_monitoring_loop())
        asyncio.create_task(self._deployment_management_loop())
        asyncio.create_task(self._learning_update_loop())
        asyncio.create_task(self._research_loop())
        asyncio.create_task(self._stats_reporting_loop())

    async def stop(self):
        """Stop the strategy engine agent."""
        self.is_running = False
        self.logger.log("Strategy engine agent stopped", "info")

    async def _strategy_composition_loop(self):
        """Main loop for strategy composition."""
        while self.is_running:
            try:
                # Get market data for composition
                market_data = await self._get_market_data()
                
                if market_data:
                    # Compose ML-based strategies
                    ml_strategies = await self.ml_composer.compose_strategy(market_data)
                    
                    # Compose online strategies
                    online_strategies = await self.online_generator.generate_strategies(market_data)
                    
                    # Combine strategies
                    all_strategies = ml_strategies + online_strategies
                    
                    # Register strategies
                    for strategy in all_strategies:
                        success = await self.registry.register_strategy(strategy)
                        if success:
                            self.stats["strategies_composed"] += 1
                    
                    self.logger.log_strategy_composition(
                        "composition_loop",
                        {
                            "ml_strategies": len(ml_strategies),
                            "online_strategies": len(online_strategies),
                            "total_strategies": len(all_strategies)
                        }
                    )
                
                await asyncio.sleep(5)  # 5 second intervals
                
            except Exception as e:
                self.logger.log_error(f"Error in strategy composition loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(5)

    async def _performance_monitoring_loop(self):
        """Main loop for performance monitoring."""
        while self.is_running:
            try:
                # Get active strategies
                active_strategies = await self.registry.get_active_strategies()
                
                if active_strategies:
                    # Track performance
                    performance_results = await self.performance_tracker.track_performance(active_strategies)
                    
                    # Update strategy performance in registry
                    for result in performance_results:
                        strategy_id = result.get("strategy_id")
                        if strategy_id:
                            await self.registry.update_strategy(strategy_id, {"performance": result})
                    
                    self.stats["performance_checks"] += 1
                
                await asyncio.sleep(10)  # 10 second intervals
                
            except Exception as e:
                self.logger.log_error(f"Error in performance monitoring loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(10)

    async def _deployment_management_loop(self):
        """Main loop for deployment management."""
        while self.is_running:
            try:
                # Get strategies ready for deployment
                deployable_strategies = await self._get_deployable_strategies()
                
                for strategy in deployable_strategies:
                    # Deploy strategy
                    deployment_result = await self.deployment_manager.deploy_strategy(strategy)
                    
                    if deployment_result.get("success"):
                        self.stats["strategies_deployed"] += 1
                        self.logger.log_strategy_deployment(
                            strategy.get("strategy_id"),
                            deployment_result
                        )
                
                await asyncio.sleep(15)  # 15 second intervals
                
            except Exception as e:
                self.logger.log_error(f"Error in deployment management loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(15)

    async def _learning_update_loop(self):
        """Main loop for learning updates."""
        while self.is_running:
            try:
                # Update training models
                await self.training_module.update_models()
                
                # Update retraining loop
                await self.retraining_loop.run_retraining_cycle()
                
                self.stats["learning_updates"] += 1
                
                await asyncio.sleep(30)  # 30 second intervals
                
            except Exception as e:
                self.logger.log_error(f"Error in learning update loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(30)

    async def _research_loop(self):
        """Main loop for research activities."""
        while self.is_running:
            try:
                # Run research engine
                research_results = await self.research_engine.run_research_cycle()
                
                if research_results:
                    self.logger.log_strategy_research(
                        "research_cycle",
                        {
                            "insights_count": len(research_results),
                            "timestamp": time.time()
                        }
                    )
                
                await asyncio.sleep(60)  # 1 minute intervals
                
            except Exception as e:
                self.logger.log_error(f"Error in research loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(60)

    async def _stats_reporting_loop(self):
        """Main loop for statistics reporting."""
        while self.is_running:
            try:
                await self._report_stats()
                await asyncio.sleep(60)  # Report every minute
            except Exception as e:
                self.logger.log_error(f"Error in stats reporting loop: {e}")
                await asyncio.sleep(60)

    async def _get_market_data(self) -> List[Dict[str, Any]]:
        """Get market data for strategy composition."""
        try:
            # Get market data from Redis
            market_data = []
            raw_data = self.redis_client.lrange("market_data:latest", 0, 99)  # Get last 100 entries
            
            for raw_entry in raw_data:
                try:
                    import json
                    entry = json.loads(raw_entry)
                    market_data.append(entry)
                except json.JSONDecodeError:
                    continue
            
            return market_data
        except Exception as e:
            self.logger.log_error(f"Error getting market data: {e}")
            return []

    async def _get_deployable_strategies(self) -> List[Dict[str, Any]]:
        """Get strategies ready for deployment."""
        try:
            # Get strategies with high confidence scores
            deployable = []
            active_strategies = await self.registry.get_active_strategies()
            
            for strategy in active_strategies:
                confidence = strategy.get("confidence", 0.0)
                if confidence > 0.8:  # High confidence threshold
                    deployable.append(strategy)
            
            return deployable
        except Exception as e:
            self.logger.log_error(f"Error getting deployable strategies: {e}")
            return []

    async def _report_stats(self):
        """Report agent statistics to Redis."""
        try:
            stats = {
                **self.stats,
                "uptime": time.time() - self.stats["start_time"],
                "registry_stats": self.registry.get_registry_stats(),
                "performance_stats": self.performance_tracker.get_performance_stats(),
                "composer_stats": self.ml_composer.get_composer_stats(),
                "timestamp": time.time()
            }
            
            # Store stats in Redis
            self.redis_client.hset("strategy_engine:agent:stats", mapping=stats)
            
            # Log stats
            self.logger.log_strategy_metric("agent_stats", len(stats), {"component": "strategy_engine_agent"})
            
        except Exception as e:
            self.logger.log_error(f"Error reporting stats: {e}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "is_running": self.is_running,
            "stats": self.stats,
            "redis_connected": self.redis_client.ping(),
            "uptime": time.time() - self.stats["start_time"]
        }

    async def compose_strategy_manual(self, strategy_data: Dict[str, Any]) -> bool:
        """Manually compose a strategy."""
        try:
            # Register strategy
            success = await self.registry.register_strategy(strategy_data)
            
            if success:
                self.stats["strategies_composed"] += 1
                self.logger.log_strategy_composition(
                    "manual_composition",
                    {
                        "strategy_id": strategy_data.get("strategy_id"),
                        "type": strategy_data.get("type"),
                        "symbol": strategy_data.get("symbol")
                    }
                )
            
            return success
        except Exception as e:
            self.logger.log_error(f"Error in manual strategy composition: {e}")
            self.stats["errors"] += 1
            return False

    async def deploy_strategy_manual(self, strategy_id: str) -> bool:
        """Manually deploy a strategy."""
        try:
            # Get strategy from registry
            active_strategies = await self.registry.get_active_strategies()
            strategy = next((s for s in active_strategies if s.get("strategy_id") == strategy_id), None)
            
            if not strategy:
                self.logger.log(f"Strategy {strategy_id} not found for deployment", "warning")
                return False
            
            # Deploy strategy
            deployment_result = await self.deployment_manager.deploy_strategy(strategy)
            
            if deployment_result.get("success"):
                self.stats["strategies_deployed"] += 1
                self.logger.log_strategy_deployment(strategy_id, deployment_result)
                return True
            else:
                self.logger.log_strategy_error("deployment_failed", {"strategy_id": strategy_id})
                return False
                
        except Exception as e:
            self.logger.log_error(f"Error in manual strategy deployment: {e}")
            self.stats["errors"] += 1
            return False

if __name__ == "__main__":
    # Test the strategy engine agent
    config = {
        "redis_url": "redis://localhost:6379",
        "registry": {
            "redis_url": "redis://localhost:6379"
        },
        "performance": {
            "redis_url": "redis://localhost:6379",
            "sharpe_threshold": 1.0,
            "drawdown_threshold": 0.1
        },
        "deployment": {
            "redis_url": "redis://localhost:6379"
        },
        "ml_composer": {
            "redis_url": "redis://localhost:6379",
            "n_estimators": 100,
            "confidence_threshold": 0.7
        },
        "online_generator": {
            "redis_url": "redis://localhost:6379"
        },
        "training": {},
        "research": {},
        "retraining": {}
    }
    
    async def test_agent():
        agent = StrategyEngineAgent(config)
        await agent.start()
        
        # Test for 10 seconds
        await asyncio.sleep(10)
        
        status = agent.get_agent_status()
        print(f"Agent status: {status}")
        
        await agent.stop()
    
    asyncio.run(test_agent())
