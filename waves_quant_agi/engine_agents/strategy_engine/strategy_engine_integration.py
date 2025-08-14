#!/usr/bin/env python3
"""
Strategy Engine Integration Manager
Ensures all strategy engine components work together seamlessly.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from engine_agents.shared_utils import get_shared_redis, get_shared_logger

# Import all strategy engine components
from .manager.strategy_registry import StrategyRegistry
from .manager.performance_tracker import PerformanceTracker
from .manager.deployment_manager import DeploymentManager
from .core.strategy_composer import StrategyComposer
from .core.strategy_applicator import StrategyApplicator
from .composers.ml_composer import MLComposer
from .composers.online_generator import OnlineGenerator

# Import consolidated trading functionality
from .trading.signal_processor import TradingSignalProcessor
from .trading.flow_manager import TradingFlowManager
from .trading.logic_executor import TradingLogicExecutor
from .trading.interfaces.trade_model import TradeCommand
from .trading.interfaces.agent_io import TradingAgentIO
from .trading.pipeline.execution_pipeline import TradingExecutionPipeline
from .trading.memory.trading_context import TradingContext
from .trading.learning.trading_research_engine import TradingResearchEngine
from .trading.learning.trading_training_module import TradingTrainingModule
from .trading.learning.trading_retraining_loop import TradingRetrainingLoop

class StrategyEngineIntegration:
    """Integration manager for all strategy engine components."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "integration")
        self.redis_conn = get_shared_redis()
        
        # Initialize all components
        self.strategy_registry = StrategyRegistry(config)
        self.performance_tracker = PerformanceTracker(config)
        self.deployment_manager = DeploymentManager(config)
        self.strategy_composer = StrategyComposer(config)
        self.strategy_applicator = StrategyApplicator(config)
        self.ml_composer = MLComposer(config)
        self.online_generator = OnlineGenerator(config)

        # Initialize consolidated trading components
        self.trading_signal_processor = TradingSignalProcessor(config)
        self.trading_flow_manager = TradingFlowManager(config)
        self.trading_logic_executor = TradingLogicExecutor(config)
        self.trading_agent_io = TradingAgentIO(config)
        self.trading_execution_pipeline = TradingExecutionPipeline(config)
        self.trading_context = TradingContext(config)
        self.trading_research_engine = TradingResearchEngine(config)
        self.trading_training_module = TradingTrainingModule(config)
        self.trading_retraining_loop = TradingRetrainingLoop(config)

        # Integration state
        self.integration_stats = {
            "strategies_registered": 0,
            "strategies_deployed": 0,
            "performance_checks": 0,
            "ml_compositions": 0,
            "online_generations": 0,
            "trading_signals_processed": 0,
            "trading_flows_executed": 0,
            "trading_logic_executions": 0,
            "integration_errors": 0,
            "start_time": time.time()
        }
        
        # Component health status
        self.component_health = {
            "strategy_registry": "unknown",
            "performance_tracker": "unknown",
            "deployment_manager": "unknown",
            "strategy_composer": "unknown",
            "strategy_applicator": "unknown",
            "ml_composer": "unknown",
            "online_generator": "unknown",
            "trading_signal_processor": "unknown",
            "trading_flow_manager": "unknown",
            "trading_logic_executor": "unknown",
            "trading_agent_io": "unknown",
            "trading_execution_pipeline": "unknown",
            "trading_context": "unknown",
            "trading_research_engine": "unknown",
            "trading_training_module": "unknown",
            "trading_retraining_loop": "unknown"
        }

    async def initialize_all_components(self) -> bool:
        """Initialize all strategy engine components."""
        try:
            self.logger.info("Initializing all strategy engine components...")
            
            # Initialize core components
            await self.strategy_composer.initialize()
            await self.strategy_applicator.initialize()
            
            # Initialize trading components
            await self.trading_signal_processor.initialize()
            await self.trading_flow_manager.initialize()
            await self.trading_logic_executor.initialize()
            await self.trading_agent_io.initialize()
            await self.trading_execution_pipeline.initialize()
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            await self.trading_training_module.initialize()
            await self.trading_retraining_loop.initialize()
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            return False

    async def process_market_data(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process market data through the complete strategy engine pipeline."""
        try:
            if not market_data:
                return []
            
            self.logger.info(f"Processing {len(market_data)} market data points")
            
            # Step 1: Process through trading signal processor
            processed_signals = []
            for data in market_data:
                signal = await self.trading_signal_processor.process_trading_signal(data)
                if signal:
                    processed_signals.append(signal)
                    self.integration_stats["trading_signals_processed"] += 1
            
            # Step 2: Execute trading logic
            if processed_signals:
                logic_results = await self.trading_logic_executor.execute_trading_logic_tree(processed_signals)
                self.integration_stats["trading_logic_executions"] += 1
                
                # Step 3: Execute trading flow
                flow_results = await self.trading_flow_manager.process_trading_signal(logic_results)
                self.integration_stats["trading_flows_executed"] += 1
                
                return flow_results
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error processing market data: {e}")
            self.integration_stats["integration_errors"] += 1
            return []

    async def get_strategy_summary(self) -> Dict[str, Any]:
        """Get comprehensive strategy summary."""
        try:
            # Get stats from all components
            registry_stats = self.strategy_registry.get_registry_stats()
            performance_stats = self.performance_tracker.get_performance_stats()
            deployment_stats = self.deployment_manager.get_deployment_stats()
            composer_stats = self.strategy_composer.get_composition_stats()
            applicator_stats = self.strategy_applicator.get_application_stats()
            ml_stats = self.ml_composer.get_composer_stats()
            generator_stats = self.online_generator.get_generator_stats()
            
            # Get active strategies
            active_strategies = await self.strategy_registry.get_active_strategies()
            deployed_strategies = await self.deployment_manager.get_deployed_strategies()
            
            # Get performance alerts
            performance_alerts = await self.performance_tracker.get_performance_alerts()
            
            summary = {
                "integration_stats": self.integration_stats,
                "component_health": self.component_health,
                "registry_stats": registry_stats,
                "performance_stats": performance_stats,
                "deployment_stats": deployment_stats,
                "composer_stats": composer_stats,
                "applicator_stats": applicator_stats,
                "ml_stats": ml_stats,
                "generator_stats": generator_stats,
                "active_strategies_count": len(active_strategies),
                "deployed_strategies_count": len(deployed_strategies),
                "performance_alerts_count": len(performance_alerts),
                "timestamp": int(time.time())
            }
            
            return summary
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting strategy summary: {e}")
            return {
                "error": "connection_error",
                "message": "Unable to connect to data store",
                "timestamp": int(time.time())
            }
        except ValueError as e:
            self.logger.error(f"Data validation error getting strategy summary: {e}")
            return {
                "error": "validation_error", 
                "message": "Data validation failed",
                "timestamp": int(time.time())
            }
        except Exception as e:
            self.logger.error(f"Unexpected error getting strategy summary: {e}")
            return {
                "error": "unexpected_error",
                "message": "An unexpected error occurred",
                "timestamp": int(time.time())
            }

    async def cleanup_expired_strategies(self) -> int:
        """Clean up expired strategies across all components."""
        try:
            # Clean up expired strategies in registry
            expired_count = await self.strategy_registry.cleanup_expired_strategies()
            
            # Clean up old performance data
            # (This would be implemented in performance tracker if needed)
            
            self.logger.info(f"Cleaned up {expired_count} expired strategies")
            return expired_count
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error cleaning up expired strategies: {e}")
            return 0
        except ValueError as e:
            self.logger.error(f"Data validation error cleaning up expired strategies: {e}")
            return 0
        except Exception as e:
            self.logger.error(f"Unexpected error cleaning up expired strategies: {e}")
            return 0

    async def force_strategy_regeneration(self):
        """Force regeneration of strategies."""
        try:
            self.logger.info("Forcing strategy regeneration...")
            
            # Force ML model update
            try:
                await self.ml_composer.force_model_update()
            except Exception as e:
                self.logger.error(f"ML model update failed: {e}")
            
            # Force online adaptation
            try:
                await self.online_generator.force_adaptation()
            except Exception as e:
                self.logger.error(f"Online adaptation failed: {e}")
            
            # Force strategy composition
            try:
                self.strategy_composer.force_composition()
            except Exception as e:
                self.logger.error(f"Strategy composition failed: {e}")
            
            self.logger.info("Strategy regeneration completed")
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error forcing strategy regeneration: {e}")
        except ValueError as e:
            self.logger.error(f"Data validation error forcing strategy regeneration: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error forcing strategy regeneration: {e}")

    async def get_component_status(self) -> Dict[str, Any]:
        """Get detailed status of all components."""
        try:
            status = {}
            
            # Check each component
            for component_name, is_healthy in self.component_health.items():
                try:
                    if component_name == "strategy_registry":
                        status[component_name] = {
                            "healthy": is_healthy,
                            "active_strategies": len(await self.strategy_registry.get_active_strategies()),
                            "uptime": self.strategy_registry.get_registry_stats().get("uptime", 0)
                        }
                    elif component_name == "performance_tracker":
                        status[component_name] = {
                            "healthy": is_healthy,
                            "strategies_tracked": self.performance_tracker.get_performance_stats().get("strategies_tracked", 0),
                            "uptime": self.performance_tracker.get_performance_stats().get("uptime", 0)
                        }
                    elif component_name == "deployment_manager":
                        status[component_name] = {
                            "healthy": is_healthy,
                            "deployed_strategies": len(await self.deployment_manager.get_deployed_strategies()),
                            "uptime": self.deployment_manager.get_deployment_stats().get("uptime", 0)
                        }
                    else:
                        status[component_name] = {
                            "healthy": is_healthy,
                            "status": "operational"
                        }
                except Exception as e:
                    self.logger.error(f"Error getting status for component {component_name}: {e}")
                    status[component_name] = {
                        "healthy": False,
                        "status": "error",
                        "error": str(e)
                    }
            
            return status
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting component status: {e}")
            return {
                "error": "connection_error",
                "message": "Unable to connect to data store",
                "timestamp": int(time.time())
            }
        except ValueError as e:
            self.logger.error(f"Data validation error getting component status: {e}")
            return {
                "error": "validation_error",
                "message": "Data validation failed", 
                "timestamp": int(time.time())
            }
        except Exception as e:
            self.logger.error(f"Unexpected error getting component status: {e}")
            return {
                "error": "unexpected_error",
                "message": "An unexpected error occurred",
                "timestamp": int(time.time())
            }

    async def restart_component(self, component_name: str) -> bool:
        """Restart a specific component."""
        try:
            self.logger.info(f"Restarting component: {component_name}")
            
            if component_name == "ml_composer":
                try:
                    success = await self.ml_composer.initialize_model()
                    self.component_health["ml_composer"] = success
                except Exception as e:
                    self.logger.error(f"ML composer restart failed: {e}")
                    self.component_health["ml_composer"] = False
                    return False
            elif component_name == "online_generator":
                try:
                    await self.online_generator.force_adaptation()
                    self.component_health["online_generator"] = True
                except Exception as e:
                    self.logger.error(f"Online generator restart failed: {e}")
                    self.component_health["online_generator"] = False
                    return False
            else:
                self.logger.warning(f"Component {component_name} does not support restart")
                return False
            
            self.logger.info(f"Component {component_name} restarted successfully")
            return True
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error restarting component {component_name}: {e}")
            self.component_health[component_name] = False
            return False
        except ValueError as e:
            self.logger.error(f"Data validation error restarting component {component_name}: {e}")
            self.component_health[component_name] = False
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error restarting component {component_name}: {e}")
            self.component_health[component_name] = False
            return False

    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics."""
        return {
            **self.integration_stats,
            "uptime": time.time() - self.integration_stats["start_time"],
            "component_health": self.component_health
        }

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status."""
        return {
            "component_health": self.component_health,
            "integration_stats": self.integration_stats,
            "uptime": time.time() - self.integration_stats["start_time"],
            "status": "operational" if self.integration_stats["integration_errors"] < 10 else "degraded"
        }

    async def shutdown(self):
        """Gracefully shutdown the integration manager."""
        try:
            self.logger.info("Shutting down Strategy Engine Integration...")
            
            # Perform any necessary cleanup
            await self.cleanup_expired_strategies()
            
            # Store final stats with proper JSON serialization
            final_stats = self.get_integration_stats()
            import json
            self.redis_conn.set(
                "strategy_engine:integration:final_stats", 
                json.dumps(final_stats), 
                ex=604800
            )
            
            self.logger.info("Strategy Engine Integration shutdown completed")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON serialization error during shutdown: {e}")
        except ConnectionError as e:
            self.logger.error(f"Redis connection error during shutdown: {e}")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
