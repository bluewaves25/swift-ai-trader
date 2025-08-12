import os
from typing import Dict, Any, Optional, List
from .base_adapter import BaseAdapter
from ..brokers.mt5_plugin import MT5Broker

class ExnessMT5Adapter(BaseAdapter):
    """Exness adapter using MT5 connection instead of API."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Get MT5 credentials from environment or config
        mt5_login = int(os.getenv("MT5_LOGIN", config.get("mt5_login", 0) if config else 0))
        mt5_password = os.getenv("MT5_PASSWORD", config.get("mt5_password", "") if config else "")
        mt5_server = os.getenv("MT5_SERVER", config.get("mt5_server", "Exness-MT5Trial") if config else "Exness-MT5Trial")
        
        # Initialize base adapter with MT5 credentials as api_key/secret for compatibility
        super().__init__("exness_mt5", str(mt5_login), mt5_password, config)
        
        # Initialize MT5 broker
        self.mt5_broker = MT5Broker(mt5_login, mt5_password, mt5_server)
        self.mt5_connected = False
        
        # Connect to MT5
        self._connect_mt5()
    
    def _connect_mt5(self) -> bool:
        """Connect to MT5 broker."""
        try:
            self.mt5_connected = self.mt5_broker.connect()
            if self.mt5_connected:
                self.logger.log("Successfully connected to Exness MT5")
                self.is_connected = True
                balance_info = self.mt5_broker.get_balance()
                self.logger.log(f"Account balance: {balance_info.get('balance', 0)} {balance_info.get('currency', 'USD')}")
            else:
                self.logger.log_error("Failed to connect to Exness MT5")
                self.is_connected = False
            return self.mt5_connected
        except Exception as e:
            self.logger.log_error(f"MT5 connection error: {e}")
            self.is_connected = False
            return False
    
    def format_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Format internal order to MT5-compatible format."""
        try:
            # Convert internal order format to MT5 format
            formatted = {
                'symbol': self._format_symbol(order.get('base', ''), order.get('quote', '')),
                'order_type': order.get('side', 'buy').lower(),  # buy/sell
                'volume': float(order.get('amount', 0)),
                'price': float(order.get('price', 0)) if order.get('price') else None,
                'sl': float(order.get('stop_loss', 0)) if order.get('stop_loss') else None,
                'tp': float(order.get('take_profit', 0)) if order.get('take_profit') else None,
                'comment': order.get('comment', 'Engine order'),
                'type': order.get('type', 'market').lower()  # market/limit
            }
            
            # Apply broker-specific quirks
            return self.handle_broker_quirks(formatted)
            
        except Exception as e:
            self.logger.log_error(f"Error formatting order: {e}")
            return {}
    
    def _format_symbol(self, base: str, quote: str) -> str:
        """Format symbol for Exness MT5 (e.g., EURUSD, XAUUSD)."""
        if not base or not quote:
            return ""
        
        # Common forex pairs
        symbol = f"{base}{quote}".upper()
        
        # Check if we need the 'm' suffix (common for Exness)
        available_symbols = self.mt5_broker.get_all_symbols()
        
        # First try with 'm' suffix
        if f"{symbol}m" in available_symbols:
            return f"{symbol}m"
        
        # Then try without suffix
        if symbol in available_symbols:
            return symbol
        
        # Default to the symbol as is
        return symbol
    
    async def send_order(self, formatted_order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send order to MT5 and return response."""
        if not self.mt5_connected:
            self.logger.log_error("MT5 not connected, attempting reconnection...")
            if not self._connect_mt5():
                return None
        
        try:
            symbol = formatted_order.get('symbol')
            order_type = formatted_order.get('order_type', 'buy')
            volume = formatted_order.get('volume', 0)
            price = formatted_order.get('price')
            sl = formatted_order.get('sl')
            tp = formatted_order.get('tp')
            comment = formatted_order.get('comment', '')
            
            # Place the order
            result = self.mt5_broker.place_order(
                symbol=symbol,
                order_type=order_type,
                volume=volume,
                price=price,
                sl=sl,
                tp=tp,
                comment=comment
            )
            
            # Log the request and response
            self.log_request(formatted_order, result)
            
            # Update stats
            self.stats["total_orders"] += 1
            if result.get("success"):
                self.stats["successful_orders"] += 1
                self.stats["total_volume"] += volume
            else:
                self.stats["failed_orders"] += 1
            
            return result
            
        except Exception as e:
            error_result = {'error': str(e)}
            self.log_request(formatted_order, error_result)
            self.stats["failed_orders"] += 1
            self.logger.log_error(f"Error sending order: {e}")
            return None
    
    def confirm_order(self, order_id: str) -> bool:
        """Confirm if order was accepted by MT5."""
        if not self.mt5_connected:
            return False
        
        try:
            # Check if order exists in positions (for market orders)
            positions = self.mt5_broker.get_positions()
            for pos in positions:
                if str(pos.get('ticket')) == str(order_id) or str(pos.get('order')) == str(order_id):
                    return True
            
            # Check recent closed trades
            closed_trades = self.mt5_broker.get_closed_trades(days=1)
            for trade in closed_trades:
                if str(trade.get('ticket')) == str(order_id) or str(trade.get('order')) == str(order_id):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.log_error(f"Error confirming order {order_id}: {e}")
            return False
    
    def handle_broker_quirks(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Exness MT5-specific quirks."""
        try:
            # Volume precision (Exness typically uses 2 decimal places)
            if 'volume' in order and order['volume']:
                order['volume'] = round(float(order['volume']), 2)
                
                # Minimum volume check
                if order['volume'] < 0.01:
                    order['volume'] = 0.01
            
            # Price precision (5 decimal places for most forex pairs)
            if 'price' in order and order['price']:
                order['price'] = round(float(order['price']), 5)
            
            # Stop loss and take profit precision
            if 'sl' in order and order['sl']:
                order['sl'] = round(float(order['sl']), 5)
            
            if 'tp' in order and order['tp']:
                order['tp'] = round(float(order['tp']), 5)
            
            return order
            
        except Exception as e:
            self.logger.log_error(f"Error handling broker quirks: {e}")
            return order
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information from MT5."""
        if not self.mt5_connected:
            return {"error": "MT5 not connected"}
        
        return self.mt5_broker.get_balance()
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions."""
        if not self.mt5_connected:
            return []
        
        return self.mt5_broker.get_positions()
    
    def get_available_symbols(self) -> List[str]:
        """Get available symbols based on current trading schedule and weekend logic."""
        try:
            from datetime import datetime
            
            current_time = datetime.now()
            is_weekend = current_time.weekday() >= 5  # Saturday = 5, Sunday = 6
            
            # Get all symbols from MT5
            all_symbols = self.mt5_broker.get_all_symbols()
            
            if is_weekend:
                # Weekend: filter to crypto symbols only
                crypto_symbols = [s for s in all_symbols if self._is_crypto_symbol(s)]
                self.logger.log(f"Weekend mode: {len(crypto_symbols)} crypto symbols available")
                return crypto_symbols
            else:
                # Weekday: return all available symbols
                self.logger.log(f"Weekday mode: {len(all_symbols)} symbols available")
                return all_symbols
                
        except Exception as e:
            self.logger.log_error(f"Error getting available symbols: {e}")
            return []
    
    def _is_crypto_symbol(self, symbol: str) -> bool:
        """Check if a symbol is a cryptocurrency."""
        crypto_indicators = ["BTC", "ETH", "LTC", "XRP", "ADA", "DOT", "LINK", "BCH", "XLM", "EOS"]
        return any(indicator in symbol.upper() for indicator in crypto_indicators)
    
    def get_crypto_symbols(self) -> List[str]:
        """Get only cryptocurrency symbols."""
        try:
            all_symbols = self.mt5_broker.get_all_symbols()
            crypto_symbols = [s for s in all_symbols if self._is_crypto_symbol(s)]
            return crypto_symbols
        except Exception as e:
            self.logger.log_error(f"Error getting crypto symbols: {e}")
            return []
    
    def get_forex_symbols(self) -> List[str]:
        """Get only forex symbols."""
        try:
            all_symbols = self.mt5_broker.get_all_symbols()
            forex_symbols = [s for s in all_symbols if not self._is_crypto_symbol(s)]
            return forex_symbols
        except Exception as e:
            self.logger.log_error(f"Error getting forex symbols: {e}")
            return []
    
    def get_trading_schedule_info(self) -> Dict[str, Any]:
        """Get current trading schedule information."""
        try:
            from datetime import datetime
            
            current_time = datetime.now()
            is_weekend = current_time.weekday() >= 5
            
            return {
                "current_time": current_time.isoformat(),
                "is_weekend": is_weekend,
                "trading_mode": "weekend_crypto" if is_weekend else "weekday_all_assets",
                "available_asset_types": ["crypto"] if is_weekend else ["crypto", "forex", "indices", "commodities", "stocks"],
                "crypto_symbols_count": len(self.get_crypto_symbols()),
                "forex_symbols_count": len(self.get_forex_symbols()) if not is_weekend else 0,
                "total_symbols_count": len(self.get_available_symbols())
            }
            
        except Exception as e:
            self.logger.log_error(f"Error getting trading schedule info: {e}")
            return {"error": str(e)}
    
    def close_position(self, ticket: int) -> Dict[str, Any]:
        """Close a specific position."""
        if not self.mt5_connected:
            return {"error": "MT5 not connected"}
        
        return self.mt5_broker.close_position(ticket)
    
    def close_all_positions(self) -> Dict[str, Any]:
        """Close all open positions."""
        if not self.mt5_connected:
            return {"error": "MT5 not connected"}
        
        return self.mt5_broker.close_all_positions()
    
    def disconnect(self):
        """Disconnect from MT5."""
        if self.mt5_broker:
            self.mt5_broker.disconnect()
            self.mt5_connected = False
            self.is_connected = False
            self.logger.log("Disconnected from Exness MT5")
    
    def get_symbol_tick(self, symbol: str) -> Dict[str, Any]:
        """Get current tick data for a symbol."""
        if not self.mt5_connected:
            return {}
        return self.mt5_broker.get_symbol_tick(symbol)
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get symbol information."""
        if not self.mt5_connected:
            return {}
        return self.mt5_broker.get_symbol_info(symbol)
    
    def get_price_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get current price data for multiple symbols."""
        if not self.mt5_connected:
            return {}
        
        price_data = {}
        for symbol in symbols:
            tick_data = self.get_symbol_tick(symbol)
            if tick_data:
                price_data[symbol] = {
                    "exchange": "exness_mt5",
                    "symbol": symbol,
                    "price": tick_data.get("last", tick_data.get("bid", 0)),
                    "bid": tick_data.get("bid", 0),
                    "ask": tick_data.get("ask", 0),
                    "volume": tick_data.get("volume", 0),
                    "spread": tick_data.get("spread", 0),
                    "timestamp": tick_data.get("timestamp", 0)
                }
        
        return price_data
    
    def __del__(self):
        """Cleanup when adapter is destroyed."""
        self.disconnect()
