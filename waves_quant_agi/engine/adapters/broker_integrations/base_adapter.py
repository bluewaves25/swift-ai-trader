from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..logs.broker_logger import BrokerLogger

class BaseAdapter(ABC):
    def __init__(self, broker_name: str, api_key: str, api_secret: str):
        self.broker_name = broker_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = BrokerLogger(broker_name)

    @abstractmethod
    def format_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Format internal order to broker-specific format."""
        pass

    @abstractmethod
    async def send_order(self, formatted_order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send order to broker and return response."""
        pass

    @abstractmethod
    def confirm_order(self, order_id: str) -> bool:
        """Confirm if order was accepted by broker."""
        pass

    @abstractmethod
    def handle_broker_quirks(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Handle broker-specific quirks (e.g., decimal limits, KYC)."""
        pass

    def log_request(self, request: Dict[str, Any], response: Optional[Dict[str, Any]] = None):
        """Log request and response details."""
        self.logger.log_request(self.broker_name, request, response)