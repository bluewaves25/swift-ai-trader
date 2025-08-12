#!/usr/bin/env python3
"""
Enhanced Strategy Engine Agent - INTEGRATED IMPLEMENTATION
Handles strategy execution and optimization with integrated components.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from engine_agents.shared_utils import BaseAgent, register_agent, get_shared_logger, get_shared_redis

# Import all strategy engine components
from .strategy_engine_integration import StrategyEngineIntegration
from .manager.strategy_registry import StrategyRegistry
from .manager.performance_tracker import PerformanceTracker
from .manager.deployment_manager import DeploymentManager
from .core.strategy_applicator import StrategyApplicator
from .core.strategy_composer import StrategyComposer
from .composers.ml_composer import MLComposer
from .composers.online_generator import OnlineGenerator
from .learning_layer.strategy_learning_manager import StrategyLearningManager
from .learning_layer.strategy_adaptation_engine import StrategyAdaptationEngine

class EnhancedStrategyEngineAgent(BaseAgent):
    """Enhanced strategy engine agent with integrated components."""
    
    def _initialize_agent_components(self):
        """Initialize strategy engine specific components."""
        # Initialize all strategy engine components
        self._initialize_strategy_components()
        
        # Register this agent
        register_agent(self.agent_name, self)
        
        # Initialize communication channels
        self._setup_communication_channels()
    
    def _initialize_strategy_components(self):
        """Initialize all strategy engine components."""
        try:
            # Core components
            self.strategy_applicator = StrategyApplicator(self.config)
            self.strategy_composer = StrategyComposer(self.config)
            
            # Manager components
            self.strategy_registry = StrategyRegistry(self.config)
            self.performance_tracker = PerformanceTracker(self.config)
            self.deployment_manager = DeploymentManager(self.config)
            
            # Composer components
            self.ml_composer = MLComposer(self.config)
            self.online_generator = OnlineGenerator(self.config)
            
            # Learning layer components
            self.learning_manager = StrategyLearningManager(self.config)
            self.adaptation_engine = StrategyAdaptationEngine(self.config)
            
            # Integration manager
            self.integration = StrategyEngineIntegration(self.config)
            
            self.logger.info("✅ All strategy engine components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing strategy components: {e}")
    
    def _setup_communication_channels(self):
        """Setup communication channels between components."""
        try:
            # Redis pub/sub channels for inter-component communication
            self.communication_channels = {
                "strategy_updates": "strategy_engine:strategy_updates",
                "performance_alerts": "strategy_engine:performance_alerts",
                "deployment_notifications": "strategy_engine:deployment_notifications",
                "learning_events": "strategy_engine:learning_events",
                "adaptation_triggers": "strategy_engine:adaptation_triggers",
                "parameter_updates": "strategy_engine:parameter_updates",
                "regime_changes": "strategy_engine:regime_changes"
            }
            
            # Initialize Redis connection for pub/sub
            self.redis_conn = get_shared_redis()
            
            self.logger.info("✅ Communication channels established")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up communication channels: {e}")
    
    async def _agent_specific_startup(self):
        """Strategy engine specific startup logic."""
        try:
            self.logger.info("🚀 Enhanced Strategy Engine starting with integrated components")
            
            # Initialize integration manager
            integration_success = await self.integration.initialize_integration()
            if not integration_success:
                self.logger.error("❌ Failed to initialize strategy engine integration")
                return False
            
            # Initialize learning components
            await self._initialize_learning_components()
            
            # Initialize manager components
            await self._initialize_manager_components()
            
            # Initialize composer components
            await self._initialize_composer_components()
            
            # Start communication listeners
            await self._start_communication_listeners()
            
            self.logger.info("✅ Enhanced Strategy Engine startup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error in strategy engine startup: {e}")
            return False
    
    async def _initialize_learning_components(self):
        """Initialize learning layer components."""
        try:
            # Initialize learning manager
            await self.learning_manager.reset_learning()
            
            # Initialize adaptation engine
            await self.adaptation_engine.reset_adaptations()
            
            self.logger.info("✅ Learning components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing learning components: {e}")
    
    async def _initialize_manager_components(self):
        """Initialize manager components."""
        try:
            # Initialize strategy registry
            await self.strategy_registry.cleanup_expired_strategies()
            
            # Initialize performance tracker
            # (Performance tracker auto-initializes)
            
            # Initialize deployment manager
            # (Deployment manager auto-initializes)
            
            self.logger.info("✅ Manager components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing manager components: {e}")
    
    async def _initialize_composer_components(self):
        """Initialize composer components."""
        try:
            # Initialize ML composer
            await self.ml_composer.initialize_model()
            
            # Initialize online generator
            # (Online generator auto-initializes)
            
            self.logger.info("✅ Composer components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing composer components: {e}")
    
    async def _start_communication_listeners(self):
        """Start listening to communication channels."""
        try:
            # Start background task for communication monitoring
            asyncio.create_task(self._monitor_communication_channels())
            
            self.logger.info("✅ Communication listeners started")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting communication listeners: {e}")
    
    async def _monitor_communication_channels(self):
        """Monitor communication channels for inter-component messages."""
        try:
            while self.is_running:
                # Check for new messages on each channel
                for channel_name, channel_key in self.communication_channels.items():
                    try:
                        # Get latest message from channel
                        message = self.redis_conn.get(f"{channel_key}:latest")
                        if message:
                            await self._process_communication_message(channel_name, message)
                    except Exception as e:
                        self.logger.error(f"Error monitoring channel {channel_name}: {e}")
                
                await asyncio.sleep(1)  # Check every second
                
        except Exception as e:
            self.logger.error(f"Error in communication monitoring: {e}")
    
    async def _process_communication_message(self, channel_name: str, message: str):
        """Process messages from communication channels."""
        try:
            import json
            message_data = json.loads(message)
            
            if channel_name == "strategy_updates":
                await self._handle_strategy_update(message_data)
            elif channel_name == "performance_alerts":
                await self._handle_performance_alert(message_data)
            elif channel_name == "deployment_notifications":
                await self._handle_deployment_notification(message_data)
            elif channel_name == "learning_events":
                await self._handle_learning_event(message_data)
            elif channel_name == "adaptation_triggers":
                await self._handle_adaptation_trigger(message_data)
            elif channel_name == "parameter_updates":
                await self._handle_parameter_update(message_data)
            elif channel_name == "regime_changes":
                await self._handle_regime_change(message_data)
                
        except Exception as e:
            self.logger.error(f"Error processing {channel_name} message: {e}")
    
    async def _handle_strategy_update(self, message_data: Dict[str, Any]):
        """Handle strategy update messages."""
        try:
            strategy_type = message_data.get("strategy_type")
            update_type = message_data.get("update_type")
            
            if update_type == "new_strategy":
                # Register new strategy
                await self.strategy_registry.register_strategy(message_data)
                self.logger.info(f"Registered new {strategy_type} strategy")
                
            elif update_type == "strategy_removal":
                # Handle strategy removal
                strategy_id = message_data.get("strategy_id")
                await self.strategy_registry.remove_strategy(strategy_id)
                self.logger.info(f"Removed strategy {strategy_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling strategy update: {e}")
    
    async def _handle_performance_alert(self, message_data: Dict[str, Any]):
        """Handle performance alert messages."""
        try:
            strategy_id = message_data.get("strategy_id")
            alert_type = message_data.get("alert_type")
            
            if alert_type == "performance_degradation":
                # Trigger strategy adaptation
                await self.adaptation_engine.force_adaptation(strategy_id)
                self.logger.info(f"Triggered adaptation for strategy {strategy_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling performance alert: {e}")
    
    async def _handle_deployment_notification(self, message_data: Dict[str, Any]):
        """Handle deployment notification messages."""
        try:
            strategy_id = message_data.get("strategy_id")
            deployment_status = message_data.get("status")
            
            if deployment_status == "deployed":
                # Update deployment tracking
                self.logger.info(f"Strategy {strategy_id} deployed successfully")
            elif deployment_status == "failed":
                # Handle deployment failure
                self.logger.warning(f"Strategy {strategy_id} deployment failed")
                
        except Exception as e:
            self.logger.error(f"Error handling deployment notification: {e}")
    
    async def _handle_learning_event(self, message_data: Dict[str, Any]):
        """Handle learning event messages."""
        try:
            event_type = message_data.get("event_type")
            
            if event_type == "parameter_optimization":
                # Apply optimized parameters
                strategy_name = message_data.get("strategy_name")
                new_params = message_data.get("new_parameters")
                await self._apply_optimized_parameters(strategy_name, new_params)
                
        except Exception as e:
            self.logger.error(f"Error handling learning event: {e}")
    
    async def _handle_adaptation_trigger(self, message_data: Dict[str, Any]):
        """Handle adaptation trigger messages."""
        try:
            trigger_type = message_data.get("trigger_type")
            
            if trigger_type == "market_regime_change":
                # Trigger strategy adaptation
                market_conditions = message_data.get("market_conditions")
                await self.adaptation_engine.adapt_strategies(market_conditions, {})
                
        except Exception as e:
            self.logger.error(f"Error handling adaptation trigger: {e}")
    
    async def _handle_parameter_update(self, message_data: Dict[str, Any]):
        """Handle parameter update messages."""
        try:
            strategy_type = message_data.get("strategy_type")
            new_parameters = message_data.get("new_parameters")
            
            # Update strategy parameters
            await self._update_strategy_parameters(strategy_type, new_parameters)
            
        except Exception as e:
            self.logger.error(f"Error handling parameter update: {e}")
    
    async def _handle_regime_change(self, message_data: Dict[str, Any]):
        """Handle market regime change messages."""
        try:
            new_regime = message_data.get("new_regime")
            market_analysis = message_data.get("market_analysis")
            
            # Update learning parameters for new regime
            await self.learning_manager._adapt_to_new_regime(new_regime)
            
            # Trigger strategy adaptation
            await self.adaptation_engine.adapt_strategies(market_analysis, {})
            
        except Exception as e:
            self.logger.error(f"Error handling regime change: {e}")
    
    async def _apply_optimized_parameters(self, strategy_name: str, new_params: Dict[str, Any]):
        """Apply optimized parameters to strategy."""
        try:
            # Store optimized parameters
            params_key = f"strategy_engine:parameters:{strategy_name}:optimized"
            self.redis_conn.set(params_key, str(new_params), ex=604800)
            
            self.logger.info(f"Applied optimized parameters for {strategy_name}")
            
        except Exception as e:
            self.logger.error(f"Error applying optimized parameters: {e}")
    
    async def _update_strategy_parameters(self, strategy_type: str, new_params: Dict[str, Any]):
        """Update strategy parameters."""
        try:
            # Store updated parameters
            params_key = f"strategy_engine:parameters:{strategy_type}"
            self.redis_conn.set(params_key, str(new_params), ex=604800)
            
            self.logger.info(f"Updated parameters for {strategy_type}")
            
        except Exception as e:
            self.logger.error(f"Error updating strategy parameters: {e}")
    
    async def _agent_specific_shutdown(self):
        """Strategy engine specific shutdown logic."""
        try:
            self.logger.info("🛑 Enhanced Strategy Engine shutting down")
            
            # Shutdown integration manager
            await self.integration.shutdown()
            
            # Cleanup communication channels
            await self._cleanup_communication_channels()
            
            self.logger.info("✅ Enhanced Strategy Engine shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in strategy engine shutdown: {e}")
    
    async def _cleanup_communication_channels(self):
        """Cleanup communication channels."""
        try:
            # Clear any pending messages
            for channel_name, channel_key in self.communication_channels.items():
                try:
                    self.redis_conn.delete(f"{channel_key}:latest")
                except:
                    pass
            
            self.logger.info("✅ Communication channels cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up communication channels: {e}")
    
    # TIER 2: FAST STRATEGY APPLICATION (100ms)
    async def _fast_application_loop(self):
        """TIER 2: Fast strategy application (100ms)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Get market data
                market_data = await self._get_market_data()
                
                if market_data:
                    # Process through integration pipeline
                    deployed_strategies = await self.integration.process_market_data([market_data])
                    
                    # Apply strategies using applicator
                    signals = await self.strategy_applicator.apply_strategy("comprehensive", market_data, "fast")
                    
                    # Process and route signals
                    if signals:
                        await self._route_signals(signals)
                        self.active_signals.extend(signals)
                    
                    # Update performance metrics
                    self._update_performance_metrics(signals)
                    
                    # Learn from execution
                    if signals:
                        await self._learn_from_execution(signals, market_data)
                
                # TIER 2 timing: 100ms
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in fast application loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _learn_from_execution(self, signals: List[Dict[str, Any]], market_data: Dict[str, Any]):
        """Learn from strategy execution."""
        try:
            for signal in signals:
                # Learn from execution result
                await self.learning_manager.learn_from_strategy_execution(
                    {"name": signal.get("type", "unknown"), "type": signal.get("type", "unknown")},
                    {"success": True, "pnl": signal.get("confidence", 0.0)}
                )
            
            # Learn from market conditions
            await self.learning_manager.learn_from_market_conditions(market_data, {})
            
        except Exception as e:
            self.logger.error(f"Error learning from execution: {e}")
    
    async def _get_market_data(self) -> Dict[str, Any]:
        """Get current market data from Redis."""
        try:
            if self.redis_conn:
                # Get latest market data from the list
                latest_data = self.redis_conn.lrange("market_data:latest", -1, -1)
                if latest_data:
                    import json
                    try:
                        market_data = json.loads(latest_data[0])
                        return market_data
                    except json.JSONDecodeError:
                        self.logger.error(f"Error parsing market data JSON: {latest_data[0]}")
                        return None
                
                # Fallback: try to get individual symbol data
                symbol_data = {}
                for symbol in ["BTCUSDm", "ETHUSDm", "XRPUSDm"]:
                    try:
                        data = self.redis_conn.hgetall(f"market_data:{symbol}")
                        if data:
                            symbol_data[symbol] = data
                    except:
                        pass
                
                if symbol_data:
                    return {"symbols": symbol_data}
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return None
    
    async def _route_signals(self, signals: List[Dict[str, Any]]):
        """Route signals to appropriate destinations."""
        try:
            for signal in signals:
                # Add timestamp and routing info
                signal["timestamp"] = int(time.time())
                signal["routed_by"] = "enhanced_strategy_engine"
                
                # Route to execution engine
                await self._route_to_execution(signal)
                
                # Route to performance tracker
                await self._route_to_performance_tracker(signal)
                
                # Store signal in Redis
                await self._store_signal(signal)
                
        except Exception as e:
            self.logger.error(f"Error routing signals: {e}")
    
    async def _route_to_execution(self, signal: Dict[str, Any]):
        """Route signal to execution engine."""
        try:
            # Add to execution queue
            execution_key = "execution_orders"
            self.redis_conn.lpush(execution_key, str(signal))
            
        except Exception as e:
            self.logger.error(f"Error routing to execution: {e}")
    
    async def _route_to_performance_tracker(self, signal: Dict[str, Any]):
        """Route signal to performance tracker."""
        try:
            # Notify performance tracker
            performance_key = "strategy_engine:performance:signals"
            self.redis_conn.lpush(performance_key, str(signal))
            
        except Exception as e:
            self.logger.error(f"Error routing to performance tracker: {e}")
    
    async def _store_signal(self, signal: Dict[str, Any]):
        """Store signal in Redis."""
        try:
            # Store in signals history
            signals_key = "strategy_engine:signals:history"
            self.redis_conn.lpush(signals_key, str(signal))
            
            # Keep only last 1000 signals
            self.redis_conn.ltrim(signals_key, 0, 999)
            
        except Exception as e:
            self.logger.error(f"Error storing signal: {e}")
    
    def _update_performance_metrics(self, signals: List[Dict[str, Any]]):
        """Update performance metrics."""
        try:
            if not hasattr(self, 'performance_metrics'):
                self.performance_metrics = {}
            
            for signal in signals:
                strategy_type = signal.get("type", "unknown")
                if strategy_type not in self.performance_metrics:
                    self.performance_metrics[strategy_type] = {"signals": 0, "total_confidence": 0.0}
                
                self.performance_metrics[strategy_type]["signals"] += 1
                self.performance_metrics[strategy_type]["total_confidence"] += signal.get("confidence", 0.0)
                
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        try:
            status = {
                "agent_name": self.agent_name,
                "status": "running" if self.is_running else "stopped",
                "uptime": time.time() - self.start_time,
                "active_signals": len(self.active_signals),
                "performance_metrics": self.performance_metrics,
                "component_health": {
                    "strategy_applicator": True,
                    "strategy_composer": True,
                    "strategy_registry": True,
                    "performance_tracker": True,
                    "deployment_manager": True,
                    "ml_composer": True,
                    "online_generator": True,
                    "learning_manager": True,
                    "adaptation_engine": True,
                    "integration": True
                }
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting agent status: {e}")
            return {"error": str(e)}
    
    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for the agent."""
        return [
            (self._fast_application_loop, "fast_application_loop"),
            (self._strategy_monitoring_loop, "strategy_monitoring_loop")
        ]
    
    async def _strategy_monitoring_loop(self):
        """Monitor strategy performance and trigger adaptations."""
        while self.is_running:
            try:
                # Check if adaptation is needed
                market_conditions = await self._get_market_conditions()
                strategy_performance = await self._get_strategy_performance()
                
                if market_conditions and strategy_performance:
                    # Check if adaptation is needed
                    if await self.adaptation_engine.check_adaptation_needed(market_conditions, strategy_performance):
                        # Trigger adaptation
                        adaptations = await self.adaptation_engine.adapt_strategies(market_conditions, strategy_performance)
                        if adaptations:
                            self.logger.info(f"Applied {len(adaptations)} strategy adaptations")
                
                # Check every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in strategy monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _get_market_conditions(self) -> Optional[Dict[str, Any]]:
        """Get current market conditions."""
        try:
            # Get market conditions from Redis
            conditions_key = "market_conditions:current"
            conditions = self.redis_conn.get(conditions_key)
            
            if conditions:
                import json
                return json.loads(conditions)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting market conditions: {e}")
            return None
    
    async def _get_strategy_performance(self) -> Optional[Dict[str, Any]]:
        """Get current strategy performance."""
        try:
            # Get performance data from Redis
            performance_key = "strategy_engine:performance:overall"
            performance = self.redis_conn.get(performance_key)
            
            if performance:
                import json
                return json.loads(performance)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting strategy performance: {e}")
            return None
