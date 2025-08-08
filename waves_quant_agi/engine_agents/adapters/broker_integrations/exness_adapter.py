from typing import Dict, Any, Optional
import requests
from .base_adapter import BaseAdapter

class ExnessAdapter(BaseAdapter):
    def __init__(self, api_key: str, api_secret: str):
        super().__init__("exness", api_key, api_secret)
        self.base_url = "https://api.exness.com/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}:{api_secret}',
            'Content-Type': 'application/json'
        })

    def format_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Format internal order to Exness-specific format."""
        formatted = {
            'instrument': f"{order['base']}{order['quote']}",
            'type': order['type'].lower(),
            'side': order['side'].lower(),
            'volume': order['amount'],
            'price': order.get('price') if order['type'] == 'limit' else None,
        }
        return self.handle_broker_quirks(formatted)

    async def send_order(self, formatted_order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send order to Exness and return response."""
        try:
            response = self.session.post(f"{self.base_url}/orders", json=formatted_order)
            response.raise_for_status()
            result = response.json()
            self.log_request(formatted_order, result)
            return result
        except Exception as e:
            self.log_request(formatted_order, {'error': str(e)})
            return None

    def confirm_order(self, order_id: str) -> bool:
        """Confirm if order was accepted by Exness."""
        try:
            response = self.session.get(f"{self.base_url}/orders/{order_id}")
            response.raise_for_status()
            order = response.json()
            return order['status'] in ['open', 'filled']
        except Exception as e:
            self.log_request({'order_id': order_id}, {'error': str(e)})
            return False

    def handle_broker_quirks(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Exness-specific quirks (e.g., volume precision)."""
        if 'volume' in order:
            order['volume'] = round(order['volume'], 4)  # Exness volume precision
        if 'price' in order and order['price']:
            order['price'] = round(order['price'], 5)
        return order