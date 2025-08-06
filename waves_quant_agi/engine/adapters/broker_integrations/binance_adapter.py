from typing import Dict, Any, Optional
import ccxt.async_support as ccxt
from .base_adapter import BaseAdapter

class BinanceAdapter(BaseAdapter):
    def __init__(self, api_key: str, api_secret: str):
        super().__init__("binance", api_key, api_secret)
        self.client = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })

    def format_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Format internal order to Binance-specific format."""
        formatted = {
            'symbol': f"{order['base']}{order['quote']}",
            'side': order['side'].upper(),
            'type': order['type'].upper(),
            'quantity': order['amount'],
            'price': order.get('price') if order['type'] == 'LIMIT' else None,
        }
        return self.handle_broker_quirks(formatted)

    async def send_order(self, formatted_order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send order to Binance and return response."""
        try:
            response = await self.client.create_order(**formatted_order)
            self.log_request(formatted_order, response)
            return response
        except Exception as e:
            self.log_request(formatted_order, {'error': str(e)})
            return None

    def confirm_order(self, order_id: str) -> bool:
        """Confirm if order was accepted by Binance."""
        try:
            order = self.client.fetch_order(order_id)
            return order['status'] == 'open' or order['status'] == 'filled'
        except Exception as e:
            self.log_request({'order_id': order_id}, {'error': str(e)})
            return False

    def handle_broker_quirks(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Binance-specific quirks (e.g., decimal limits)."""
        if 'quantity' in order:
            order['quantity'] = round(order['quantity'], 8)  # Binance decimal limit
        if 'price' in order and order['price']:
            order['price'] = round(order['price'], 8)
        return order