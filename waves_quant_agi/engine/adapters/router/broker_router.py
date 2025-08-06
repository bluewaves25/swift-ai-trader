from typing import Dict, Any, Optional
from ..broker_integrations.base_adapter import BaseAdapter
from .routing_strategies import LowestFeeStrategy, FastestRouteStrategy
from ..status_monitor.performance_tracker import PerformanceTracker

class BrokerRouter:
    def __init__(self, adapters: Dict[str, BaseAdapter], performance_tracker: PerformanceTracker):
        self.adapters = adapters
        self.performance_tracker = performance_tracker
        self.strategies = {
            'lowest_fee': LowestFeeStrategy(),
            'fastest_route': FastestRouteStrategy(),
        }
        self.current_strategy = 'fastest_route'

    def select_broker(self, order: Dict[str, Any]) -> Optional[BaseAdapter]:
        """Select the best broker for the order based on the current strategy."""
        strategy = self.strategies.get(self.current_strategy)
        if not strategy:
            return None
        
        broker_name = strategy.select_broker(
            order,
            self.adapters,
            self.performance_tracker.get_broker_metrics()
        )
        return self.adapters.get(broker_name)

    def set_strategy(self, strategy_name: str) -> bool:
        """Set the routing strategy."""
        if strategy_name in self.strategies:
            self.current_strategy = strategy_name
            return True
        return False

    async def route_order(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route and execute the order through the selected broker."""
        broker = self.select_broker(order)
        if not broker:
            return None
        
        formatted_order = broker.format_order(order)
        response = await broker.send_order(formatted_order)
        if response and broker.confirm_order(response.get('order_id', '')):
            return response
        return None