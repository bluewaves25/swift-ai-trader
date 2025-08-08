from typing import Dict, Any, Optional
from ..broker_integrations.base_adapter import BaseAdapter

class RoutingStrategy:
    def select_broker(self, order: Dict[str, Any], adapters: Dict[str, BaseAdapter], metrics: Dict[str, Any]) -> Optional[str]:
        """Base method for broker selection."""
        raise NotImplementedError

class LowestFeeStrategy(RoutingStrategy):
    def select_broker(self, order: Dict[str, Any], adapters: Dict[str, BaseAdapter], metrics: Dict[str, Any]) -> Optional[str]:
        """Select broker with the lowest fees for the order."""
        min_fee = float('inf')
        selected_broker = None
        
        for broker_name, adapter in adapters.items():
            fee = metrics.get(broker_name, {}).get('fee', float('inf'))
            if fee < min_fee and self._is_broker_suitable(broker_name, order, metrics):
                min_fee = fee
                selected_broker = broker_name
                
        return selected_broker

    def _is_broker_suitable(self, broker_name: str, order: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """Check if broker is suitable based on order and metrics."""
        return metrics.get(broker_name, {}).get('status', 'down') == 'up'

class FastestRouteStrategy(RoutingStrategy):
    def select_broker(self, order: Dict[str, Any], adapters: Dict[str, BaseAdapter], metrics: Dict[str, Any]) -> Optional[str]:
        """Select broker with the fastest response time."""
        min_latency = float('inf')
        selected_broker = None
        
        for broker_name, adapter in adapters.items():
            latency = metrics.get(broker_name, {}).get('avg_latency', float('inf'))
            if latency < min_latency and self._is_broker_suitable(broker_name, order, metrics):
                min_latency = latency
                selected_broker = broker_name
                
        return selected_broker

    def _is_broker_suitable(self, broker_name: str, order: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """Check if broker is suitable based on order and metrics."""
        return metrics.get(broker_name, {}).get('status', 'down') == 'up'