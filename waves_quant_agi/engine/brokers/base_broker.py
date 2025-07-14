# engine/brokers/base_broker.py

from abc import ABC, abstractmethod

class BaseBroker(ABC):
    """
    Abstract base class for broker plugins.
    Enforces a consistent interface for all brokers (MT5, Binance, etc).
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection with broker API/server.
        """
        pass

    @abstractmethod
    def get_balance(self) -> dict:
        """
        Return available balance and equity.
        """
        pass

    @abstractmethod
    def get_positions(self) -> list:
        """
        Return list of all current open positions.
        """
        pass

    @abstractmethod
    def place_order(self, symbol: str, side: str, volume: float, price: float, order_type: str) -> dict:
        """
        Submit a trade order.
        Args:
            symbol (str): Trading pair like 'BTCUSD'
            side (str): 'buy' or 'sell'
            volume (float): Lot size
            price (float): Entry price
            order_type (str): 'market' or 'limit'
        Returns:
            dict: Confirmation or error from broker
        """
        pass

    @abstractmethod
    def close_position(self, position_id: str) -> dict:
        """
        Closes an open trade position.
        """
        pass
