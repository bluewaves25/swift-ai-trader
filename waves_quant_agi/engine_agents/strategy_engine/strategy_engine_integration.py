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
        
        # Integration state
        self.integration_stats = {
            "strategies_registered": 0,
            "strategies_deployed": 0,
            "performance_checks": 0,
            "ml_compositions": 0,
            "online_generations": 0,
            "integration_errors": 0,
            "start_time": time.time()
        }
        
        # Component health status
        self.component_health = {
            "strategy_registry": False,
            "performance_tracker": False,
            "deployment_manager": False,
            "strategy_composer": False,
            "strategy_applicator": False,
            "ml_composer": False,
            "online_generator": False
        }

    async def initialize_integration(self) -> bool:
        """Initialize all strategy engine components."""
        try:
            self.logger.info("Initializing Strategy Engine Integration...")
            
            # Initialize ML composer
            ml_ready = await self.ml_composer.initialize_model()
            self.component_health["ml_composer"] = ml_ready
            
            # Check Redis connectivity for all components
            redis_healthy = await self._check_redis_connectivity()
            if not redis_healthy:
                self.logger.error("Redis connectivity check failed")
                return False
            
            # Initialize component health
            self.component_health["strategy_registry"] = True
            self.component_health["performance_tracker"] = True
            self.component_health["deployment_manager"] = True
            self.component_health["strategy_composer"] = True
            self.component_health["strategy_applicator"] = True
            self.component_health["online_generator"] = True
            
            self.logger.info("Strategy Engine Integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing integration: {e}")
            return False

    async def _check_redis_connectivity(self) -> bool:
        """Check Redis connectivity for all components."""
        try:
            # Test basic Redis operations
            test_key = "strategy_engine:integration_test"
            test_value = {"test": True, "timestamp": time.time()}
            
            # Set test value with proper JSON serialization
            import json
            self.redis_conn.set(test_key, json.dumps(test_value), ex=60)
            
            # Get test value
            retrieved_value = self.redis_conn.get(test_key)
            
            # Clean up
            self.redis_conn.delete(test_key)
            
            if retrieved_value:
                # Parse the JSON back
                parsed_value = json.loads(retrieved_value)
                if parsed_value.get("test") and parsed_value.get("timestamp"):
                    self.logger.info("Redis connectivity check passed")
                    return True
                else:
                    self.logger.error("Redis connectivity check failed - data corruption detected")
                    return False
            else:
                self.logger.error("Redis connectivity check failed - no data retrieved")
                return False
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Redis JSON serialization error: {e}")
            return False
        except ConnectionError as e:
            self.logger.error(f"Redis connection error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Redis connectivity check error: {e}")
            return False

    async def process_market_data(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process market data through the complete strategy engine pipeline."""
        try:
            if not market_data:
                return []
            
            self.logger.info(f"Processing {len(market_data)} market data points")
            
            # Step 1: Apply existing strategies
            try:
                applied_signals = await self.strategy_applicator.apply_strategy("comprehensive", market_data)
            except ConnectionError as e:
                self.logger.error(f"Redis connection error in strategy application: {e}")
                self.integration_stats["integration_errors"] += 1
                return []
            except ValueError as e:
                self.logger.error(f"Invalid market data format: {e}")
                self.integration_stats["integration_errors"] += 1
                return []
            except Exception as e:
                self.logger.error(f"Unexpected error in strategy application: {e}")
                self.integration_stats["integration_errors"] += 1
                return []
            
            # Step 2: Generate new strategies if needed
            ml_strategies = []
            online_strategies = []
            
            try:
                ml_strategies = await self.ml_composer.compose_strategy(market_data)
            except Exception as e:
                self.logger.error(f"ML composer error: {e}")
                # Continue with other strategies
                
            try:
                online_strategies = await self.online_generator.generate_strategy(market_data)
            except Exception as e:
                self.logger.error(f"Online generator error: {e}")
                # Continue with other strategies
            
            # Step 3: Register new strategies
            all_strategies = applied_signals + ml_strategies + online_strategies
            
            registered_strategies = []
            for strategy in all_strategies:
                try:
                    if await self.strategy_registry.register_strategy(strategy):
                        registered_strategies.append(strategy)
                        self.integration_stats["strategies_registered"] += 1
                except Exception as e:
                    self.logger.error(f"Failed to register strategy {strategy.get('name', 'unknown')}: {e}")
                    continue
            
            # Step 4: Track performance for existing strategies
            if registered_strategies:
                try:
                    performance_metrics = await self.performance_tracker.track_performance(registered_strategies)
                    self.integration_stats["performance_checks"] += 1
                except Exception as e:
                    self.logger.error(f"Performance tracking error: {e}")
                    # Continue without performance tracking
            
            # Step 5: Deploy strategies
            deployed_strategies = []
            for strategy in registered_strategies:
                try:
                    if await self.deployment_manager.deploy_strategy(strategy):
                        deployed_strategies.append(strategy)
                        self.integration_stats["strategies_deployed"] += 1
                except Exception as e:
                    self.logger.error(f"Failed to deploy strategy {strategy.get('name', 'unknown')}: {e}")
                    continue
            
            # Update stats
            self.integration_stats["ml_compositions"] += len(ml_strategies)
            self.integration_stats["online_generations"] += len(online_strategies)
            
            self.logger.info(f"Pipeline processed: {len(applied_signals)} applied, {len(ml_strategies)} ML, {len(online_strategies)} online, {len(deployed_strategies)} deployed")
            
            return deployed_strategies
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error in market data processing: {e}")
            self.integration_stats["integration_errors"] += 1
            return []
        except ValueError as e:
            self.logger.error(f"Data validation error in market data processing: {e}")
            self.integration_stats["integration_errors"] += 1
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in market data processing: {e}")
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
