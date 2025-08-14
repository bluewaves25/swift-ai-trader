#!/usr/bin/env python3
"""
Enhanced Adapters Agent V2 - ROLE CONSOLIDATED: CONNECTION MANAGEMENT ONLY
Removed health monitoring functionality - now handled by Core Agent.
Focuses exclusively on broker connections, routing, and failover management.
"""

import asyncio
import time
import json
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedAdaptersAgentV2(BaseAgent):
    """Enhanced adapters agent - focused solely on connection management."""
    
    def _initialize_agent_components(self):
        """Initialize adapters specific components."""
        # Initialize adapters components
        self.connection_manager = None
        self.broker_router = None
        self.failover_manager = None
        
        # Connection management state
        self.connection_state = {
            "active_connections": {},
            "connection_pools": {},
            "routing_strategies": {},
            "failover_status": {},
            "last_connection_update": time.time()
        }
        
        # Connection management statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "orders_routed": 0,
            "successful_connections": 0,
            "connection_failures": 0,
            "total_orders_routed": 0,
            "failovers_executed": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Adapters specific startup logic."""
        try:
            # Initialize connection management components
            await self._initialize_connection_components()
            
            # Initialize broker routing systems
            await self._initialize_broker_routing()
            
            # Initialize failover management
            await self._initialize_failover_management()
            
            self.logger.info("✅ Adapters Agent: Connection management systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in adapters startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Adapters specific shutdown logic."""
        try:
            # Cleanup connection management resources
            await self._cleanup_connection_components()
            
            self.logger.info("✅ Adapters Agent: Connection management systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in adapters shutdown: {e}")
    
    # ============= BACKGROUND TASKS =============
    
    async def _broker_health_monitoring_loop(self):
        """Broker health monitoring loop."""
        while self.is_running:
            try:
                # Monitor broker health
                await self._monitor_broker_health()
                
                await asyncio.sleep(5.0)  # 5 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in broker health monitoring loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _adapter_health_monitoring_loop(self):
        """Adapter health monitoring loop."""
        while self.is_running:
            try:
                # Monitor adapter health
                await self._monitor_adapter_health()
                
                await asyncio.sleep(2.0)  # 2 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in adapter health monitoring loop: {e}")
                await asyncio.sleep(2.0)
    
    async def _connection_reporting_loop(self):
        """Connection reporting loop."""
        while self.is_running:
            try:
                # Report connection status
                await self._report_connection_status()
                
                await asyncio.sleep(30.0)  # 30 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in connection reporting loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _monitor_broker_health(self):
        """Monitor broker health."""
        try:
            # Placeholder for broker health monitoring
            pass
        except Exception as e:
            self.logger.error(f"Error monitoring broker health: {e}")
    
    async def _monitor_adapter_health(self):
        """Monitor adapter health."""
        try:
            # Placeholder for adapter health monitoring
            pass
        except Exception as e:
            self.logger.error(f"Error monitoring adapter health: {e}")
    
    async def _report_connection_status(self):
        """Report connection status."""
        try:
            # Placeholder for connection status reporting
            pass
        except Exception as e:
            self.logger.error(f"Error reporting connection status: {e}")

    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._connection_monitoring_loop, "Connection Monitoring", "fast"),
            (self._broker_health_monitoring_loop, "Broker Health Monitoring", "tactical"),
            (self._adapter_health_monitoring_loop, "Adapter Health Monitoring", "tactical"),
            (self._connection_reporting_loop, "Connection Reporting", "strategic")
        ]
    
    # ============= CONNECTION COMPONENT INITIALIZATION =============
    
    async def _initialize_connection_components(self):
        """Initialize connection management components."""
        try:
            # Initialize connection manager
            from .core.connection_manager import ConnectionManager
            self.connection_manager = ConnectionManager(self.config)
            
            # Initialize broker router
            from .core.broker_router import BrokerRouter
            self.broker_router = BrokerRouter(self.config)
            
            # Initialize failover manager
            from .core.failover_manager import FailoverManager
            self.failover_manager = FailoverManager(self.config)
            
            self.logger.info("✅ Connection management components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing connection components: {e}")
            raise
    
    async def _initialize_broker_routing(self):
        """Initialize broker routing systems."""
        try:
            # Set up broker connections
            await self.connection_manager.initialize_connections()
            
            # Set up routing strategies
            await self.broker_router.initialize_routing()
            
            # Set up connection pools
            await self._setup_connection_pools()
            
            self.logger.info("✅ Broker routing systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing broker routing: {e}")
            raise
    
    async def _initialize_failover_management(self):
        """Initialize failover management."""
        try:
            # Set up failover strategies
            await self.failover_manager.initialize_failover()
            
            # Set up failover monitoring
            await self._setup_failover_monitoring()
            
            self.logger.info("✅ Failover management initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing failover management: {e}")
            raise
    
    async def _setup_connection_pools(self):
        """Set up connection pools for different broker types."""
        try:
            # Set up connection pools for different strategies
            connection_pools = {
                "ultra_hft": {"max_connections": 10, "timeout": 0.001},
                "fast": {"max_connections": 20, "timeout": 0.1},
                "tactical": {"max_connections": 15, "timeout": 1.0},
                "strategic": {"max_connections": 5, "timeout": 5.0}
            }
            
            for pool_type, config in connection_pools.items():
                await self.connection_manager.create_connection_pool(pool_type, config)
                self.connection_state["connection_pools"][pool_type] = config
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up connection pools: {e}")
    
    async def _setup_failover_monitoring(self):
        """Set up failover monitoring."""
        try:
            # Set up failover thresholds
            failover_thresholds = {
                "connection_timeout": 5.0,  # 5 seconds
                "response_timeout": 2.0,    # 2 seconds
                "failure_threshold": 3,     # 3 consecutive failures
                "recovery_timeout": 30.0    # 30 seconds
            }
            
            await self.failover_manager.set_thresholds(failover_thresholds)
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up failover monitoring: {e}")
    
    # ============= CONNECTION MONITORING LOOP =============
    
    async def _connection_monitoring_loop(self):
        """Connection monitoring loop (100ms intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Monitor connection status
                connections_updated = await self._monitor_connection_status()
                
                # Update connection state
                if connections_updated > 0:
                    self._update_connection_state()
                
                # Record operation
                duration_ms = (time.time() - start_time) * 1000
                if hasattr(self, 'status_monitor') and self.status_monitor:
                    self.status_monitor.record_operation(duration_ms, connections_updated > 0)
                
                await asyncio.sleep(0.1)  # 100ms connection monitoring cycle
                
            except Exception as e:
                self.logger.error(f"Error in connection monitoring loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _monitor_connection_status(self) -> int:
        """Monitor connection status and return number of connections updated."""
        try:
            connections_updated = 0
            
            if not self.connection_manager:
                return 0
            
            # Check all connection pools
            for pool_type in self.connection_state["connection_pools"]:
                pool_status = await self.connection_manager.get_pool_status(pool_type)
                
                if pool_status:
                    # Update connection state
                    self.connection_state["active_connections"][pool_type] = pool_status
                    connections_updated += 1
                    
                    # Check for connection failures
                    await self._check_connection_failures(pool_type, pool_status)
            
            return connections_updated
            
        except Exception as e:
            self.logger.error(f"Error monitoring connection status: {e}")
            return 0
    
    async def _check_connection_failures(self, pool_type: str, pool_status: Dict[str, Any]):
        """Check for connection failures in a pool."""
        try:
            active_connections = pool_status.get("active_connections", 0)
            total_connections = pool_status.get("total_connections", 0)
            
            # Check if pool is below threshold
            if active_connections < total_connections * 0.5:  # 50% threshold
                self.logger.warning(f"Connection pool {pool_type} below threshold: {active_connections}/{total_connections}")
                
                # Trigger failover if needed
                await self._trigger_failover(pool_type)
                
        except Exception as e:
            self.logger.error(f"Error checking connection failures: {e}")
    
    # ============= ORDER ROUTING LOOP =============
    
    async def _order_routing_loop(self):
        """Order routing loop (1ms intervals for ultra-HFT)."""
        while self.is_running:
            try:
                # Process pending orders
                orders_routed = await self._process_pending_orders()
                
                # Update routing statistics
                if orders_routed > 0:
                    self.stats["orders_routed"] += orders_routed
                    self.stats["total_orders_routed"] += orders_routed
                
                await asyncio.sleep(0.001)  # 1ms for ultra-HFT routing
                
            except Exception as e:
                self.logger.error(f"Error in order routing loop: {e}")
                await asyncio.sleep(0.001)
    
    async def _process_pending_orders(self) -> int:
        """Process pending orders and return number of orders routed."""
        try:
            orders_routed = 0
            
            if not self.broker_router:
                return 0
            
            # Get pending orders from Redis
            pending_orders = await self._get_pending_orders()
            
            for order in pending_orders:
                if await self._route_order(order):
                    orders_routed += 1
                    
                    # Remove processed order
                    await self.redis_conn.lrem("orders:pending", 1, json.dumps(order))
            
            return orders_routed
            
        except Exception as e:
            self.logger.error(f"Error processing pending orders: {e}")
            return 0
    
    async def _get_pending_orders(self) -> List[Dict[str, Any]]:
        """Get pending orders from Redis."""
        try:
            # Get pending orders from Redis queue
            pending_orders = await self.redis_conn.lrange("orders:pending", 0, 9)
            
            orders = []
            for order in pending_orders:
                try:
                    orders.append(json.loads(order))
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid order format: {order}")
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Error getting pending orders: {e}")
            return []
    
    async def _route_order(self, order: Dict[str, Any]) -> bool:
        """Route a single order."""
        try:
            if not self.broker_router:
                return False
            
            # Get order details
            strategy_type = order.get("strategy_type", "general")
            symbol = order.get("symbol", "unknown")
            order_type = order.get("order_type", "market")
            
            # Route order to appropriate broker
            routing_result = await self.broker_router.route_order(order, strategy_type)
            
            # Update statistics
            if routing_result.get("success", False):
                self.stats["successful_connections"] += 1
            else:
                self.stats["connection_failures"] += 1
            
            # Publish routing result
            await self._publish_routing_result(order, routing_result)
            
            return routing_result.get("success", False)
            
        except Exception as e:
            self.logger.error(f"Error routing order: {e}")
            return False
    
    # ============= FAILOVER MANAGEMENT LOOP =============
    
    async def _failover_management_loop(self):
        """Failover management loop (30s intervals)."""
        while self.is_running:
            try:
                # Check failover status
                failover_events = await self._check_failover_status()
                
                # Update failover statistics
                if failover_events > 0:
                    self.stats["failovers_executed"] += failover_events
                
                # Publish failover status
                await self._publish_failover_status()
                
                await asyncio.sleep(30)  # 30s failover management cycle
                
            except Exception as e:
                self.logger.error(f"Error in failover management loop: {e}")
                await asyncio.sleep(30)
    
    async def _trigger_failover(self, pool_type: str):
        """Trigger failover for a connection pool."""
        try:
            if not self.failover_manager:
                return
            
            # Execute failover
            failover_result = await self.failover_manager.execute_failover(pool_type)
            
            if failover_result.get("success", False):
                self.logger.info(f"Failover executed successfully for {pool_type}")
                
                # Update failover status
                self.connection_state["failover_status"][pool_type] = {
                    "last_failover": time.time(),
                    "status": "completed",
                    "result": failover_result
                }
            else:
                self.logger.error(f"Failover failed for {pool_type}: {failover_result.get('error', 'unknown')}")
                
        except Exception as e:
            self.logger.error(f"Error triggering failover: {e}")
    
    async def _check_failover_status(self) -> int:
        """Check failover status and return number of failover events."""
        try:
            failover_events = 0
            
            if not self.failover_manager:
                return 0
            
            # Check failover status for all pools
            for pool_type in self.connection_state["connection_pools"]:
                failover_status = await self.failover_manager.get_failover_status(pool_type)
                
                if failover_status and failover_status.get("status") == "completed":
                    failover_events += 1
                    
                    # Update connection state
                    self.connection_state["failover_status"][pool_type] = failover_status
            
            return failover_events
            
        except Exception as e:
            self.logger.error(f"Error checking failover status: {e}")
            return 0
    
    # ============= UTILITY METHODS =============
    
    def _update_connection_state(self):
        """Update connection state with current information."""
        try:
            # Update last connection update timestamp
            self.connection_state["last_connection_update"] = time.time()
            
            # Update active connections count
            total_active = 0
            for pool_status in self.connection_state["active_connections"].values():
                total_active += pool_status.get("active_connections", 0)
            
            self.stats["active_connections"] = total_active
            
        except Exception as e:
            self.logger.error(f"Error updating connection state: {e}")
    
    async def _cleanup_connection_components(self):
        """Cleanup connection management components."""
        try:
            # Cleanup connection manager
            if self.connection_manager:
                await self.connection_manager.cleanup()
            
            # Cleanup broker router
            if self.broker_router:
                await self.broker_router.cleanup()
            
            # Cleanup failover manager
            if self.failover_manager:
                await self.failover_manager.cleanup()
            
            self.logger.info("✅ Connection management components cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up connection components: {e}")
    
    # ============= PUBLISHING METHODS =============
    
    async def _publish_routing_result(self, order: Dict[str, Any], result: Dict[str, Any]):
        """Publish order routing result."""
        try:
            routing_update = {
                "order": order,
                "result": result,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("adapters:routing_results", json.dumps(routing_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing routing result: {e}")
    
    async def _publish_failover_status(self):
        """Publish failover status."""
        try:
            failover_status = {
                "failover_status": self.connection_state["failover_status"],
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("adapters:failover_status", json.dumps(failover_status))
            
        except Exception as e:
            self.logger.error(f"Error publishing failover status: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status."""
        return {
            "connection_state": self.connection_state,
            "stats": self.stats,
            "last_update": time.time()
        }
    
    async def get_connection_pools(self) -> Dict[str, Any]:
        """Get connection pool information."""
        return {
            "connection_pools": self.connection_state["connection_pools"],
            "active_connections": self.connection_state["active_connections"],
            "last_update": time.time()
        }
    
    async def submit_order_routing_request(self, order: Dict[str, Any]) -> bool:
        """Submit an order routing request."""
        try:
            # Add order to pending queue
            await self.redis_conn.lpush("orders:pending", json.dumps(order))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting order routing request: {e}")
            return False
    
    async def get_failover_status(self) -> Dict[str, Any]:
        """Get failover status."""
        return {
            "failover_status": self.connection_state["failover_status"],
            "failovers_executed": self.stats["failovers_executed"],
            "last_update": time.time()
        }
