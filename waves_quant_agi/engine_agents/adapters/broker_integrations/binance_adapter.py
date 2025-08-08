from typing import Dict, Any, Optional
import ccxt.async_support as ccxt
import time
from .base_adapter import BaseAdapter

class BinanceAdapter(BaseAdapter):
    """Binance exchange adapter with comprehensive error handling and monitoring."""
    
    def __init__(self, api_key: str, api_secret: str, config: Optional[Dict[str, Any]] = None):
        super().__init__("binance", api_key, api_secret, config)
        
        # Initialize CCXT client
        self.client = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'sandbox': config.get('sandbox', False) if config else False,
            'options': {
                'defaultType': 'spot',  # or 'future'
                'adjustForTimeDifference': True,
            }
        })
        
        # Binance-specific settings
        self.min_order_size = config.get('min_order_size', 0.001) if config else 0.001
        self.max_order_size = config.get('max_order_size', 1000000.0) if config else 1000000.0
        self.price_precision = config.get('price_precision', 8) if config else 8
        self.quantity_precision = config.get('quantity_precision', 8) if config else 8

    async def connect(self) -> bool:
        """Establish connection to Binance."""
        try:
            # Test connection by fetching account info
            await self.client.load_markets()
            account_info = await self.client.fetch_balance()
            
            self.is_connected = True
            self.last_heartbeat = time.time()
            self.connection_errors = 0
            
            self.logger.log_connection_status(self.broker_name, "connected", f"Account: {account_info.get('info', {}).get('accountType', 'unknown')}")
            return True
            
        except Exception as e:
            self.is_connected = False
            self.connection_errors += 1
            self.logger.log_connection_status(self.broker_name, "failed", str(e))
            return False

    async def check_connection(self) -> bool:
        """Check if connection to Binance is healthy."""
        try:
            # Simple ping test
            await self.client.fetch_ticker('BTC/USDT')
            self.last_heartbeat = time.time()
            return True
        except Exception as e:
            self.is_connected = False
            self.connection_errors += 1
            self.logger.log_error(f"Connection check failed for {self.broker_name}: {e}")
            return False

    def format_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Format internal order to Binance-specific format."""
        try:
            # Extract order components
            symbol = order.get('symbol', '')
            side = order.get('side', 'buy').upper()
            order_type = order.get('type', 'market').upper()
            quantity = float(order.get('amount', 0))
            price = order.get('price')
            
            # Validate symbol format
            if '/' in symbol:
                base, quote = symbol.split('/')
                formatted_symbol = f"{base}{quote}"
            else:
                formatted_symbol = symbol
            
            formatted = {
                'symbol': formatted_symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
            }
            
            # Add price for limit orders
            if order_type == 'LIMIT' and price:
                formatted['price'] = price
            
            # Add time in force for limit orders
            if order_type == 'LIMIT':
                formatted['timeInForce'] = 'GTC'  # Good Till Canceled
            
            return self.handle_broker_quirks(formatted)
            
        except Exception as e:
            self.logger.log_error(f"Error formatting order: {e}", {"order": order})
            return order

    async def send_order(self, formatted_order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send order to Binance and return response."""
        try:
            # Validate order before sending
            if not self._validate_order(formatted_order):
                self.logger.log_error("Order validation failed", {"order": formatted_order})
                return None
            
            # Send order
            response = await self.client.create_order(**formatted_order)
            
            # Log the request and response
            self.log_request(formatted_order, response)
            
            return response
            
        except ccxt.InsufficientFunds as e:
            self.logger.log_error(f"Insufficient funds: {e}", {"order": formatted_order})
            return None
            
        except ccxt.InvalidOrder as e:
            self.logger.log_error(f"Invalid order: {e}", {"order": formatted_order})
            return None
            
        except ccxt.NetworkError as e:
            self.logger.log_error(f"Network error: {e}", {"order": formatted_order})
            return None
            
        except Exception as e:
            self.logger.log_error(f"Unexpected error sending order: {e}", {"order": formatted_order})
            return None

    def confirm_order(self, order_id: str) -> bool:
        """Confirm if order was accepted by Binance."""
        try:
            order = self.client.fetch_order(order_id)
            status = order.get('status', 'unknown')
            
            is_confirmed = status in ['open', 'filled', 'partially_filled']
            
            self.logger.log_order(
                self.broker_name,
                {"order_id": order_id},
                "confirmed" if is_confirmed else "rejected",
                order_id
            )
            
            return is_confirmed
            
        except Exception as e:
            self.logger.log_error(f"Error confirming order {order_id}: {e}")
            return False

    def handle_broker_quirks(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Binance-specific quirks (e.g., decimal limits, minimums)."""
        try:
            # Round quantity to precision
            if 'quantity' in order:
                order['quantity'] = round(float(order['quantity']), self.quantity_precision)
                
                # Check minimum order size
                if order['quantity'] < self.min_order_size:
                    self.logger.log_error(f"Order quantity {order['quantity']} below minimum {self.min_order_size}")
                    return order
            
            # Round price to precision
            if 'price' in order and order['price']:
                order['price'] = round(float(order['price']), self.price_precision)
            
            # Check maximum order size
            if 'quantity' in order and order['quantity'] > self.max_order_size:
                self.logger.log_error(f"Order quantity {order['quantity']} above maximum {self.max_order_size}")
                return order
            
            return order
            
        except Exception as e:
            self.logger.log_error(f"Error handling broker quirks: {e}", {"order": order})
            return order

    def _validate_order(self, order: Dict[str, Any]) -> bool:
        """Validate order before sending."""
        try:
            required_fields = ['symbol', 'side', 'type', 'quantity']
            
            # Check required fields
            for field in required_fields:
                if field not in order:
                    self.logger.log_error(f"Missing required field: {field}", {"order": order})
                    return False
            
            # Validate side
            if order['side'] not in ['BUY', 'SELL']:
                self.logger.log_error(f"Invalid side: {order['side']}", {"order": order})
                return False
            
            # Validate type
            if order['type'] not in ['MARKET', 'LIMIT']:
                self.logger.log_error(f"Invalid type: {order['type']}", {"order": order})
                return False
            
            # Validate quantity
            quantity = float(order['quantity'])
            if quantity <= 0:
                self.logger.log_error(f"Invalid quantity: {quantity}", {"order": order})
                return False
            
            # Validate price for limit orders
            if order['type'] == 'LIMIT':
                if 'price' not in order or not order['price']:
                    self.logger.log_error("Price required for limit orders", {"order": order})
                    return False
                
                price = float(order['price'])
                if price <= 0:
                    self.logger.log_error(f"Invalid price: {price}", {"order": order})
                    return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error validating order: {e}", {"order": order})
            return False

    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account information from Binance."""
        try:
            balance = await self.client.fetch_balance()
            return {
                "balances": balance.get("info", {}).get("balances", []),
                "account_type": balance.get("info", {}).get("accountType", "unknown"),
                "permissions": balance.get("info", {}).get("permissions", [])
            }
        except Exception as e:
            self.logger.log_error(f"Error getting account info: {e}")
            return None

    async def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific order."""
        try:
            order = await self.client.fetch_order(order_id)
            return {
                "id": order.get("id"),
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "type": order.get("type"),
                "status": order.get("status"),
                "quantity": order.get("amount"),
                "filled": order.get("filled"),
                "price": order.get("price"),
                "cost": order.get("cost"),
                "timestamp": order.get("timestamp")
            }
        except Exception as e:
            self.logger.log_error(f"Error getting order status: {e}")
            return None

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a specific order."""
        try:
            result = await self.client.cancel_order(order_id)
            self.logger.log_order(self.broker_name, {"order_id": order_id}, "cancelled", order_id)
            return True
        except Exception as e:
            self.logger.log_error(f"Error canceling order {order_id}: {e}")
            return False

    async def get_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current ticker for a symbol."""
        try:
            ticker = await self.client.fetch_ticker(symbol)
            return {
                "symbol": ticker.get("symbol"),
                "last": ticker.get("last"),
                "bid": ticker.get("bid"),
                "ask": ticker.get("ask"),
                "high": ticker.get("high"),
                "low": ticker.get("low"),
                "volume": ticker.get("baseVolume"),
                "timestamp": ticker.get("timestamp")
            }
        except Exception as e:
            self.logger.log_error(f"Error getting ticker for {symbol}: {e}")
            return None

    async def close(self):
        """Close the adapter and disconnect from Binance."""
        try:
            await self.disconnect()
            if hasattr(self.client, 'close'):
                await self.client.close()
            self.logger.log("Binance adapter closed")
        except Exception as e:
            self.logger.log_error(f"Error closing Binance adapter: {e}")