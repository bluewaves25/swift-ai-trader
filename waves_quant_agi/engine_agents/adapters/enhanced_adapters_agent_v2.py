#!/usr/bin/env python3
"""
Enhanced Adapters Agent V2 - REFACTORED TO USE BASE AGENT
Eliminates duplicate start/stop methods and Redis connection logic.
"""

import asyncio
import time
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedAdaptersAgentV2(BaseAgent):
    """Enhanced adapters agent using base class."""
    
    def _initialize_agent_components(self):
        """Initialize adapters specific components."""
        # Initialize adapters components with mock implementations
        self.connection_manager = MockConnectionManager()
        self.broker_router = MockBrokerRouter()
        self.comm_hub = None
        self.connection_state = {}
        
        # Adapters statistics
        self.stats = {
            "start_time": time.time(),
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "orders_routed": 0,
            "optimizations_applied": 0,
            "successful_connections": 0,
            "connection_failures": 0,
            "total_orders_routed": 0,
            "failovers_executed": 0
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Adapters specific startup logic."""
        # Initialize broker connections and routing systems
        self.logger.info("Adapters components initialized")
    
    async def _agent_specific_shutdown(self):
        """Adapters specific shutdown logic."""
        # Close all broker connections
        self.logger.info("Adapters components cleaned up")
    
    # ============= 4-TIER CONNECTION LOOPS =============
    
    async def _ultra_hft_connection_loop(self):
        """TIER 1: Ultra-HFT connections (1ms) for arbitrage strategies."""
        while self.is_running:
            try:
                # Monitor ultra-fast connections
                await self.connection_manager.monitor_ultra_hft_connections()
                
                await asyncio.sleep(0.001)  # 1ms
                
            except Exception as e:
                self.logger.warning(f"Error in ultra-HFT connection loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _fast_connection_loop(self):
        """TIER 2: Fast connections (100ms) for market making strategies."""
        while self.is_running:
            try:
                # Monitor fast connections
                await self.connection_manager.monitor_fast_connections()
                
                # Route strategy-specific orders
                await self.broker_router.route_pending_orders()
                
                await asyncio.sleep(0.1)  # 100ms
                
            except Exception as e:
                self.logger.warning(f"Error in fast connection loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _tactical_health_monitoring(self):
        """TIER 3: Tactical health monitoring (30s)."""
        while self.is_running:
            try:
                # Comprehensive connection health check
                health_results = await self.connection_manager.perform_health_check()
                
                # Update connection state
                self._update_connection_state(health_results)
                
                # Handle connection failures
                await self._handle_connection_failures(health_results)
                
                await asyncio.sleep(30)  # 30s
                
            except Exception as e:
                self.logger.warning(f"Error in tactical health monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _strategic_optimization_loop(self):
        """TIER 4: Strategic optimization (300s)."""
        while self.is_running:
            try:
                # Optimize connection performance
                optimization_results = await self.broker_router.optimize_connections()
                
                # Update routing strategies
                await self._update_routing_strategies(optimization_results)
                
                # Publish connection report
                await self._publish_connection_report(optimization_results)
                
                await asyncio.sleep(300)  # 300s (5 minutes)
                
            except Exception as e:
                self.logger.warning(f"Error in strategic optimization: {e}")
                await asyncio.sleep(300)
    
    # ============= MESSAGE HANDLERS =============
    
    async def _handle_order_request(self, message):
        """Handle order routing requests."""
        try:
            order_data = message.payload
            strategy_type = order_data.get("strategy_type", "statistical")
            
            # Route order to appropriate broker
            routing_result = await self.broker_router.route_order(order_data, strategy_type)
            
            # Update statistics
            if routing_result.get("success", False):
                self.stats["successful_connections"] += 1
            else:
                self.stats["connection_failures"] += 1
            
            # Learn from routing performance
            await self._learn_from_routing(order_data, routing_result)
            
        except Exception as e:
            self.logger.warning(f"Error handling order request: {e}")
    
    async def _handle_strategy_signal(self, message):
        """Handle strategy signals for connection optimization."""
        try:
            signal_data = message.payload
            strategy_type = signal_data.get("strategy_id", "statistical")
            
            # Optimize connections for strategy
            await self.broker_router.optimize_for_strategy(strategy_type)
            
        except Exception as e:
            self.logger.warning(f"Error handling strategy signal: {e}")
    
    async def _handle_system_alert(self, message):
        """Handle system alerts for failover management."""
        try:
            alert_data = message.payload
            alert_type = alert_data.get("alert_type", "")
            
            if "connection" in alert_type.lower() or "broker" in alert_type.lower():
                # Execute failover if needed
                await self.connection_manager.execute_failover()
                self.stats["failovers_executed"] += 1
            
        except Exception as e:
            self.logger.warning(f"Error handling system alert: {e}")
    
    # ============= CONNECTION MANAGEMENT =============
    
    def _update_connection_state(self, health_results: Dict[str, Any]):
        """Update connection state from health check results."""
        try:
            self.connection_state.update({
                "active_connections": health_results.get("active_connections", 0),
                "failed_connections": health_results.get("failed_connections", 0),
                "average_latency_ms": health_results.get("average_latency_ms", 0.0),
                "connection_health_score": health_results.get("health_score", 1.0),
                "last_health_check": time.time()
            })
            
        except Exception as e:
            self.logger.warning(f"Error updating connection state: {e}")
    
    async def _handle_connection_failures(self, health_results: Dict[str, Any]):
        """Handle connection failures and execute failover if needed."""
        try:
            failed_connections = health_results.get("failed_connections", 0)
            
            if failed_connections > 0:
                # Execute failover
                await self.connection_manager.execute_failover()
                self.stats["failovers_executed"] += 1
                
                # Send alert
                if self.comm_hub:
                    from ..communication.message_formats import create_system_alert
                    alert = create_system_alert(
                        "adapters",
                        "CONNECTION_FAILURE",
                        {"failed_connections": failed_connections}
                    )
                    await self.comm_hub.publish_message(alert)
            
        except Exception as e:
            self.logger.warning(f"Error handling connection failures: {e}")
    
    async def _update_routing_strategies(self, optimization_results: Dict[str, Any]):
        """Update routing strategies based on optimization results."""
        try:
            # Update broker router with optimization results
            await self.broker_router.update_routing_strategies(optimization_results)
            
        except Exception as e:
            self.logger.warning(f"Error updating routing strategies: {e}")
    
    async def _learn_from_routing(self, order_data: Dict[str, Any], routing_result: Dict[str, Any]):
        """Learn from routing performance for future optimization."""
        try:
            # Simple learning features
            features = [
                order_data.get("quantity", 0.0) / 1000.0,  # Normalize
                routing_result.get("latency_ms", 0.0) / 1000.0,  # Normalize
                1.0 if routing_result.get("success", False) else 0.0,
                len(order_data.get("symbol", "")) / 10.0,  # Symbol complexity
                time.time() % 86400 / 86400  # Time of day (normalized)
            ]
            
            # Target is routing success
            target = 1.0 if routing_result.get("success", False) else 0.0
            
            # Learn for future optimization
            from engine_agents.shared_utils import LearningData
            learning_data = LearningData(
                agent_name="adapters",
                learning_type=LearningType.CONNECTIVITY_OPTIMIZATION,
                input_features=features,
                target_value=target
            )
            
            self.learner.learn(learning_data)
            
        except Exception as e:
            self.logger.warning(f"Learning error: {e}")
    
    # ============= COMMUNICATION & REPORTING =============
    
    async def _publish_connection_report(self, optimization_results: Dict[str, Any]):
        """Publish comprehensive connection report."""
        try:
            if self.comm_hub:
                report_data = {
                    "type": "COMPREHENSIVE_CONNECTION_REPORT",
                    "connection_state": self.connection_state,
                    "optimization_results": optimization_results,
                    "statistics": self.stats,
                    "timestamp": time.time()
                }
                
                from ..communication.message_formats import BaseMessage, MessageType
                message = BaseMessage(
                    sender="adapters",
                    message_type=MessageType.LOG_MESSAGE,
                    payload=report_data
                )
                
                await self.comm_hub.publish_message(message)
            
        except Exception as e:
            self.logger.warning(f"Error publishing connection report: {e}")
    
    # ============= UTILITY METHODS =============
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        return {
            "is_running": self.is_running,
            "connection_state": self.connection_state,
            "stats": self.stats,
            "uptime_seconds": int(time.time() - self.stats["start_time"])
        }

# Mock classes for components that don't exist yet
class MockConnectionManager:
    async def initialize_connections(self):
        pass
    
    async def close_all_connections(self):
        pass
    
    async def monitor_ultra_hft_connections(self):
        pass
    
    async def monitor_fast_connections(self):
        pass
    
    async def perform_health_check(self):
        return {"status": "healthy", "connections": 0}

class MockBrokerRouter:
    async def route_pending_orders(self):
        pass
    
    async def optimize_connections(self):
        return {"optimizations": []}
