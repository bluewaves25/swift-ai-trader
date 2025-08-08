import time
from typing import Dict, Any, Optional, List
from ..broker_integrations.base_adapter import BaseAdapter
from .routing_strategies import LowestFeeStrategy, FastestRouteStrategy
from ..status_monitor.performance_tracker import PerformanceTracker
from ..logs.broker_logger import BrokerLogger

class BrokerRouter:
    """Intelligent broker router with performance tracking and strategy selection."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.adapters = {}
        self.performance_tracker = PerformanceTracker()
        self.logger = BrokerLogger("broker_router")
        
        # Initialize routing strategies
        self.strategies = {
            'lowest_fee': LowestFeeStrategy(),
            'fastest_route': FastestRouteStrategy(),
        }
        self.current_strategy = config.get('default_strategy', 'fastest_route')
        
        # Performance tracking
        self.stats = {
            "total_orders_routed": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "total_volume_routed": 0.0,
            "last_route_time": 0,
            "start_time": time.time()
        }

    def add_adapter(self, broker_name: str, adapter: BaseAdapter):
        """Add a broker adapter to the router."""
        try:
            self.adapters[broker_name] = adapter
            self.logger.log(f"Added adapter for {broker_name}")
        except Exception as e:
            self.logger.log_error(f"Error adding adapter for {broker_name}: {e}")

    def remove_adapter(self, broker_name: str):
        """Remove a broker adapter from the router."""
        try:
            if broker_name in self.adapters:
                del self.adapters[broker_name]
                self.logger.log(f"Removed adapter for {broker_name}")
        except Exception as e:
            self.logger.log_error(f"Error removing adapter for {broker_name}: {e}")

    def get_available_brokers(self) -> List[str]:
        """Get list of available brokers."""
        return list(self.adapters.keys())

    def select_broker(self, order: Dict[str, Any]) -> Optional[BaseAdapter]:
        """Select the best broker for the order based on the current strategy."""
        try:
            if not self.adapters:
                self.logger.log_error("No adapters available")
                return None
            
            # Get current strategy
            strategy = self.strategies.get(self.current_strategy)
            if not strategy:
                self.logger.log_error(f"Strategy {self.current_strategy} not found")
                return None
            
            # Get broker metrics
            broker_metrics = self.performance_tracker.get_broker_metrics()
            
            # Select broker using strategy
            broker_name = strategy.select_broker(
                order,
                self.adapters,
                broker_metrics
            )
            
            if broker_name and broker_name in self.adapters:
                self.logger.log(f"Selected {broker_name} for order using {self.current_strategy} strategy")
                return self.adapters[broker_name]
            else:
                self.logger.log_error(f"Strategy {self.current_strategy} returned invalid broker: {broker_name}")
                return None
                
        except Exception as e:
            self.logger.log_error(f"Error selecting broker: {e}")
            return None

    def set_strategy(self, strategy_name: str) -> bool:
        """Set the routing strategy."""
        try:
            if strategy_name in self.strategies:
                self.current_strategy = strategy_name
                self.logger.log(f"Switched to {strategy_name} strategy")
                return True
            else:
                self.logger.log_error(f"Strategy {strategy_name} not found")
                return False
        except Exception as e:
            self.logger.log_error(f"Error setting strategy: {e}")
            return False

    def get_available_strategies(self) -> List[str]:
        """Get list of available routing strategies."""
        return list(self.strategies.keys())

    async def route_order(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route and execute the order through the selected broker."""
        try:
            start_time = time.time()
            
            # Select broker
            broker = self.select_broker(order)
            if not broker:
                self.stats["failed_routes"] += 1
                return None
            
            # Check broker connection
            if not await broker.check_connection():
                self.logger.log_error(f"Broker {broker.broker_name} not connected")
                self.stats["failed_routes"] += 1
                return None
            
            # Execute order
            response = await broker.execute_order(order)
            
            # Update stats
            self.stats["total_orders_routed"] += 1
            self.stats["last_route_time"] = time.time()
            
            if response:
                self.stats["successful_routes"] += 1
                volume = float(order.get("amount", 0)) * float(order.get("price", 0))
                self.stats["total_volume_routed"] += volume
                
                # Update performance tracker
                execution_time = time.time() - start_time
                self.performance_tracker.record_execution(
                    broker.broker_name,
                    execution_time,
                    volume,
                    True
                )
                
                self.logger.log_order(
                    broker.broker_name,
                    order,
                    "routed_successfully",
                    response.get("id")
                )
                
                return response
            else:
                self.stats["failed_routes"] += 1
                
                # Update performance tracker
                execution_time = time.time() - start_time
                self.performance_tracker.record_execution(
                    broker.broker_name,
                    execution_time,
                    0,
                    False
                )
                
                self.logger.log_order(broker.broker_name, order, "routing_failed")
                return None
                
        except Exception as e:
            self.stats["failed_routes"] += 1
            self.logger.log_error(f"Error routing order: {e}", {"order": order})
            return None

    async def route_order_with_fallback(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route order with fallback to other brokers if primary fails."""
        try:
            # Try primary broker
            response = await self.route_order(order)
            if response:
                return response
            
            # If primary fails, try other brokers
            available_brokers = list(self.adapters.keys())
            primary_broker = self.select_broker(order)
            
            if primary_broker:
                primary_name = primary_broker.broker_name
                # Remove primary from fallback list
                fallback_brokers = [b for b in available_brokers if b != primary_name]
            else:
                fallback_brokers = available_brokers
            
            # Try fallback brokers
            for broker_name in fallback_brokers:
                self.logger.log(f"Trying fallback broker: {broker_name}")
                
                broker = self.adapters.get(broker_name)
                if broker and await broker.check_connection():
                    response = await broker.execute_order(order)
                    if response:
                        self.logger.log_order(broker_name, order, "fallback_success", response.get("id"))
                        return response
            
            self.logger.log_error("All brokers failed for order", {"order": order})
            return None
            
        except Exception as e:
            self.logger.log_error(f"Error in fallback routing: {e}", {"order": order})
            return None

    async def check_all_connections(self) -> Dict[str, bool]:
        """Check connection status of all brokers."""
        connection_status = {}
        
        for broker_name, adapter in self.adapters.items():
            try:
                is_connected = await adapter.check_connection()
                connection_status[broker_name] = is_connected
                
                if is_connected:
                    self.logger.log_connection_status(broker_name, "connected")
                else:
                    self.logger.log_connection_status(broker_name, "disconnected")
                    
            except Exception as e:
                connection_status[broker_name] = False
                self.logger.log_connection_status(broker_name, "error", str(e))
        
        return connection_status

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        uptime = time.time() - self.stats["start_time"]
        total_routes = self.stats["successful_routes"] + self.stats["failed_routes"]
        
        return {
            "uptime_seconds": uptime,
            "total_orders_routed": total_routes,
            "successful_routes": self.stats["successful_routes"],
            "failed_routes": self.stats["failed_routes"],
            "success_rate": (self.stats["successful_routes"] / max(total_routes, 1)) * 100,
            "total_volume_routed": self.stats["total_volume_routed"],
            "routes_per_second": total_routes / max(uptime, 1),
            "last_route_time": self.stats["last_route_time"],
            "current_strategy": self.current_strategy,
            "available_brokers": list(self.adapters.keys()),
            "available_strategies": list(self.strategies.keys())
        }

    def get_broker_stats(self) -> Dict[str, Any]:
        """Get statistics for all brokers."""
        broker_stats = {}
        
        for broker_name, adapter in self.adapters.items():
            try:
                broker_stats[broker_name] = adapter.get_stats()
            except Exception as e:
                self.logger.log_error(f"Error getting stats for {broker_name}: {e}")
                broker_stats[broker_name] = {"error": str(e)}
        
        return broker_stats