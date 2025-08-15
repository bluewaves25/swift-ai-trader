try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None
    print("Warning: MetaTrader5 module not available (likely running on non-Windows system)")

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

class MT5Broker:
    """MetaTrader 5 broker implementation for Exness integration."""
    
    def __init__(self, login: int, password: str, server: str):
        if not MT5_AVAILABLE:
            raise ImportError("MetaTrader5 module is not available on this system")
        
        self.login = login
        self.password = password
        self.server = server
        self.is_connected = False
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Connect to MT5 terminal with Exness credentials."""
        try:
            self.logger.info(f"🔄 Attempting to connect to MT5 with login: {self.login}, server: {self.server}")
            
            # Initialize MT5 connection
            if not mt5.initialize():
                error_code = mt5.last_error()
                self.logger.error(f"MT5 initialize() failed with error: {error_code}")
                return False
            
            self.logger.info("✅ MT5 initialized successfully")
            
            # Attempt to login
            authorized = mt5.login(login=self.login, password=self.password, server=self.server)
            if not authorized:
                error_code = mt5.last_error()
                self.logger.error(f"MT5 login failed: {error_code}")
                mt5.shutdown()
                return False
            
            self.is_connected = True
            account_info = mt5.account_info()
            if account_info:
                self.logger.info(f"✅ Connected to MT5 - Account: {account_info.login}, Server: {account_info.server}")
            return True
            
        except Exception as e:
            self.logger.error(f"MT5 connection error: {e}")
            if 'mt5' in globals():
                mt5.shutdown()
            return False
    
    def disconnect(self):
        """Disconnect from MT5 terminal."""
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            self.logger.info("Disconnected from MT5")
    
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance information."""
        if not self.is_connected:
            return {"error": "Not connected to MT5"}
        
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return {"error": "Failed to get account info"}
            
            return {
                "balance": account_info.balance,
                "equity": account_info.equity,
                "margin": account_info.margin,
                "free_margin": account_info.margin_free,
                "margin_level": account_info.margin_level,
                "profit": account_info.profit,
                "currency": account_info.currency,
                "leverage": account_info.leverage
            }
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            return {"error": str(e)}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions."""
        if not self.is_connected:
            return []
        
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            positions_list = []
            for pos in positions:
                positions_list.append({
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": pos.type,  # 0 = buy, 1 = sell
                    "volume": pos.volume,
                    "price_open": pos.price_open,
                    "price_current": pos.price_current,
                    "swap": pos.swap,
                    "profit": pos.profit,
                    "comment": pos.comment,
                    "time": pos.time,
                    "magic": pos.magic
                })
            return positions_list
            
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []
    
    def get_closed_trades(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get closed trades from the last N days."""
        if not self.is_connected:
            return []
        
        try:
            # Get deals for the last N days
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            deals = mt5.history_deals_get(start_date, end_date)
            if deals is None:
                return []
            
            trades_list = []
            for deal in deals:
                if deal.type in [0, 1]:  # Only buy/sell deals
                    trades_list.append({
                        "ticket": deal.ticket,
                        "order": deal.order,
                        "symbol": deal.symbol,
                        "type": deal.type,
                        "volume": deal.volume,
                        "price": deal.price,
                        "commission": deal.commission,
                        "swap": deal.swap,
                        "profit": deal.profit,
                        "fee": deal.fee,
                        "comment": deal.comment,
                        "time": deal.time,
                        "magic": deal.magic
                    })
            return trades_list
            
        except Exception as e:
            self.logger.error(f"Error getting closed trades: {e}")
            return []
    
    def get_all_symbols(self) -> List[str]:
        """Get all available trading symbols with weekend awareness."""
        if not self.is_connected:
            return []
        
        try:
            symbols = mt5.symbols_get()
            if symbols is None:
                return []
            
            all_symbols = [symbol.name for symbol in symbols if symbol.visible]
            
            # Weekend detection - only cryptos available on weekends
            import datetime
            now = datetime.datetime.now()
            is_weekend = now.weekday() >= 5  # Saturday = 5, Sunday = 6
            
            if is_weekend:
                # Weekend: Only crypto pairs (typically end with 'm' on Exness)
                crypto_symbols = [s for s in all_symbols if any(crypto in s.upper() for crypto in ['BTC', 'ETH', 'LTC', 'XRP', 'ADA', 'DOT', 'LINK', 'BCH', 'XLM', 'EOS', 'ATOM', 'SOL', 'MATIC', 'AVAX', 'UNI', 'AAVE', 'COMP', 'MKR', 'SNX', 'SUSHI'])]
                self.logger.info(f"🌅 Weekend detected - Trading {len(crypto_symbols)} crypto pairs")
                return crypto_symbols
            else:
                # Weekday: All assets available
                self.logger.info(f"🏢 Weekday - Trading {len(all_symbols)} total assets")
                return all_symbols
            
        except Exception as e:
            self.logger.error(f"Error getting symbols: {e}")
            return []
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get information about a specific symbol."""
        if not self.is_connected:
            return {}
        
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {}
            
            return {
                "name": symbol_info.name,
                "description": symbol_info.description,
                "path": symbol_info.path,
                "currency_base": symbol_info.currency_base,
                "currency_profit": symbol_info.currency_profit,
                "currency_margin": symbol_info.currency_margin,
                "digits": symbol_info.digits,
                "point": symbol_info.point,
                "spread": symbol_info.spread,
                "volume_min": symbol_info.volume_min,
                "volume_max": symbol_info.volume_max,
                "volume_step": symbol_info.volume_step,
                "trade_mode": symbol_info.trade_mode,
                "visible": symbol_info.visible
            }
            
        except Exception as e:
            self.logger.error(f"Error getting symbol info for {symbol}: {e}")
            return {}
    
    def get_symbol_tick(self, symbol: str) -> Dict[str, Any]:
        """Get current tick data for a symbol."""
        if not self.is_connected:
            return {}
        
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return {}
            
            return {
                "symbol": symbol,
                "time": tick.time,
                "bid": tick.bid,
                "ask": tick.ask,
                "last": tick.last,
                "volume": tick.volume,
                "spread": tick.ask - tick.bid if tick.ask and tick.bid else 0,
                "timestamp": tick.time_msc / 1000.0  # Convert to seconds
            }
            
        except Exception as e:
            self.logger.error(f"Error getting tick for {symbol}: {e}")
            return {}
    
    def get_crypto_symbols(self) -> List[str]:
        """Get all available crypto symbols with comprehensive detection."""
        if not self.is_connected:
            return []
        
        try:
            all_symbols = self.get_all_symbols()
            # Comprehensive crypto detection for Exness MT5
            crypto_keywords = [
                'BTC', 'ETH', 'LTC', 'XRP', 'ADA', 'DOT', 'LINK', 'BCH', 'XLM', 'EOS',
                'ATOM', 'SOL', 'MATIC', 'AVAX', 'UNI', 'AAVE', 'COMP', 'MKR', 'SNX', 'SUSHI',
                'FTM', 'NEAR', 'ALGO', 'VET', 'THETA', 'FIL', 'ICP', 'APT', 'ARB', 'OP',
                'INJ', 'TIA', 'SEI', 'SUI', 'APT', 'STRK', 'ZKSYNC', 'BASE', 'ARBITRUM'
            ]
            
            crypto_symbols = [s for s in all_symbols if any(crypto in s.upper() for crypto in crypto_keywords)]
            
            # Log what we found
            if crypto_symbols:
                self.logger.info(f"🔍 Found {len(crypto_symbols)} crypto symbols: {', '.join(crypto_symbols[:5])}{'...' if len(crypto_symbols) > 5 else ''}")
            else:
                self.logger.warning("⚠️ No crypto symbols found - check symbol naming convention")
                
            return crypto_symbols
            
        except Exception as e:
            self.logger.error(f"Error getting crypto symbols: {e}")
            return []
    
    def get_tick_data(self, symbol: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get latest tick data for a symbol."""
        if not self.is_connected:
            return []
        
        try:
            ticks = mt5.copy_ticks_from(symbol, datetime.now(), count, mt5.COPY_TICKS_ALL)
            if ticks is None:
                return []
            
            tick_list = []
            for tick in ticks:
                tick_list.append({
                    "time": tick.time,
                    "bid": tick.bid,
                    "ask": tick.ask,
                    "last": tick.last,
                    "volume": tick.volume,
                    "flags": tick.flags
                })
            return tick_list
            
        except Exception as e:
            self.logger.error(f"Error getting tick data for {symbol}: {e}")
            return []
    
    def place_order(self, symbol: str, order_type: str, volume: float, price: float = None, 
                   sl: float = None, tp: float = None, comment: str = "") -> Dict[str, Any]:
        """Place a trading order."""
        if not self.is_connected:
            return {"error": "Not connected to MT5"}
        
        try:
            # Prepare the request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if order_type.lower() == "buy" else mt5.ORDER_TYPE_SELL,
                "deviation": 20,
                "magic": 234000,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Add price for limit orders
            if price is not None:
                request["price"] = price
                request["type"] = mt5.ORDER_TYPE_BUY_LIMIT if order_type.lower() == "buy" else mt5.ORDER_TYPE_SELL_LIMIT
            
            # Add stop loss and take profit
            if sl is not None:
                request["sl"] = sl
            if tp is not None:
                request["tp"] = tp
            
            # Send the order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    "error": f"Order failed: {result.retcode}",
                    "comment": result.comment
                }
            
            return {
                "success": True,
                "order": result.order,
                "deal": result.deal,
                "volume": result.volume,
                "price": result.price,
                "comment": result.comment
            }
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return {"error": str(e)}
    
    def close_position(self, ticket: int) -> Dict[str, Any]:
        """Close a specific position."""
        if not self.is_connected:
            return {"error": "Not connected to MT5"}
        
        try:
            # Get position info
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return {"error": "Position not found"}
            
            pos = position[0]
            
            # Prepare close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
                "position": ticket,
                "deviation": 20,
                "magic": 234000,
                "comment": "Close position",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send close order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    "error": f"Close failed: {result.retcode}",
                    "comment": result.comment
                }
            
            return {
                "success": True,
                "deal": result.deal,
                "volume": result.volume,
                "price": result.price
            }
            
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
            return {"error": str(e)}
    
    def close_all_positions(self) -> Dict[str, Any]:
        """Close all open positions."""
        if not self.is_connected:
            return {"error": "Not connected to MT5"}
        
        try:
            positions = self.get_positions()
            closed_count = 0
            errors = []
            
            for pos in positions:
                result = self.close_position(pos["ticket"])
                if result.get("success"):
                    closed_count += 1
                else:
                    errors.append(f"Failed to close {pos['ticket']}: {result.get('error')}")
            
            return {
                "success": True,
                "closed_positions": closed_count,
                "total_positions": len(positions),
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"Error closing all positions: {e}")
            return {"error": str(e)}
    
    def get_forex_symbols(self) -> List[str]:
        """Get list of available forex symbols."""
        if not self.is_connected:
            return []
        
        try:
            symbols = mt5.symbols_get()
            if symbols is None:
                return []
            
            # Filter for forex symbols (typically contain currency pairs)
            forex_symbols = []
            for symbol in symbols:
                symbol_name = symbol.name
                # Check if it's a forex symbol (contains currency pairs)
                if any(currency in symbol_name for currency in ['EUR', 'USD', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']):
                    forex_symbols.append(symbol_name)
            
            return forex_symbols
            
        except Exception as e:
            self.logger.error(f"Error getting forex symbols: {e}")
            return []
