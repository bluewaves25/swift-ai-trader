# engine/brokers/mt5_plugin.py

import MetaTrader5 as mt5
from engine.brokers.base_broker import BaseBroker
import time

class MT5Broker(BaseBroker):
    """
    MT5 (MetaTrader 5) plugin for broker interaction.
    Tested with Exness. Requires MT5 to be running with login session active.
    """

    def __init__(self, login: int, password: str, server: str):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False

    def connect(self) -> None:
        """
        Initialize connection with the MetaTrader 5 terminal.
        """
        if not mt5.initialize():
            raise ConnectionError(f"MT5 initialize failed: {mt5.last_error()}")

        authorized = mt5.login(self.login, password=self.password, server=self.server)
        if not authorized:
            raise PermissionError(f"MT5 login failed: {mt5.last_error()}")
        self.connected = True
        print(f"[MT5Broker] Connected to {self.server} as {self.login}")

    def get_balance(self) -> dict:
        """
        Returns account balance, equity, and margin data.
        """
        if not self.connected:
            self.connect()

        account_info = mt5.account_info()
        if account_info is None:
            raise RuntimeError(f"Failed to fetch account info: {mt5.last_error()}")

        return {
            "balance": account_info.balance,
            "equity": account_info.equity,
            "margin": account_info.margin,
            "margin_free": account_info.margin_free
        }

    def get_positions(self) -> list:
        """
        Return all currently open positions.
        """
        if not self.connected:
            self.connect()

        positions = mt5.positions_get()
        if positions is None:
            raise RuntimeError(f"Failed to get positions: {mt5.last_error()}")

        return [pos._asdict() for pos in positions]

    def place_order(self, symbol: str, side: str, volume: float, price: float = 0.0, order_type: str = "market") -> dict:
        """
        Place a new order (market or limit) with MT5.
        """
        if not self.connected:
            self.connect()

        order_type_map = {
            ("buy", "market"): mt5.ORDER_TYPE_BUY,
            ("sell", "market"): mt5.ORDER_TYPE_SELL,
            ("buy", "limit"): mt5.ORDER_TYPE_BUY_LIMIT,
            ("sell", "limit"): mt5.ORDER_TYPE_SELL_LIMIT,
        }

        order_type_code = order_type_map.get((side, order_type))
        if order_type_code is None:
            raise ValueError(f"Invalid order type: {side} {order_type}")

        request = {
            "action": mt5.TRADE_ACTION_DEAL if order_type == "market" else mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "type": order_type_code,
            "price": price if order_type == "limit" else mt5.symbol_info_tick(symbol).ask,
            "deviation": 10,
            "magic": 123456,
            "comment": "WAVES_QAGI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"Order failed: {result.retcode}, {result.comment}")

        return {"order_id": result.order, "status": "success"}

    def close_position(self, position_id: int) -> dict:
        """
        Close an open position by ID.
        """
        if not self.connected:
            self.connect()

        position = next((p for p in mt5.positions_get() if p.ticket == position_id), None)
        if position is None:
            raise ValueError(f"Position {position_id} not found.")

        side = "sell" if position.type == mt5.ORDER_TYPE_BUY else "buy"
        close_type = mt5.ORDER_TYPE_SELL if side == "sell" else mt5.ORDER_TYPE_BUY

        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": close_type,
            "position": position.ticket,
            "price": mt5.symbol_info_tick(position.symbol).bid if side == "sell" else mt5.symbol_info_tick(position.symbol).ask,
            "deviation": 10,
            "magic": 123456,
            "comment": "WAVES_QAGI_Close"
        }

        result = mt5.order_send(close_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"Close failed: {result.retcode}, {result.comment}")

        return {"status": "closed", "ticket": result.order}
