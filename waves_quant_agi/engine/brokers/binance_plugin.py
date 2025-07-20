# engine/brokers/binance_plugin.py

import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode
from waves_quant_agi.engine.brokers.base_broker import BaseBroker

class BinanceBroker(BaseBroker):
    """
    Binance plugin for spot trading.
    Supports placing orders, checking balances, and getting price feeds.
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.binance.com"):
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: dict) -> dict:
        """
        Signs request with Binance API secret.
        """
        query_string = urlencode(params)
        signature = hmac.new(self.api_secret, query_string.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def _get(self, path: str, params: dict = {}) -> dict:
        """
        Performs signed GET request.
        """
        params["timestamp"] = int(time.time() * 1000)
        signed = self._sign(params)
        res = self.session.get(f"{self.base_url}{path}", params=signed)
        res.raise_for_status()
        return res.json()

    def _post(self, path: str, params: dict = {}) -> dict:
        """
        Performs signed POST request.
        """
        params["timestamp"] = int(time.time() * 1000)
        signed = self._sign(params)
        res = self.session.post(f"{self.base_url}{path}", params=signed)
        res.raise_for_status()
        return res.json()

    def get_balance(self, asset: str = "USDT") -> float:
        """
        Returns free balance of a given asset.
        """
        data = self._get("/api/v3/account")
        for item in data["balances"]:
            if item["asset"] == asset:
                return float(item["free"])
        return 0.0

    def get_price(self, symbol: str) -> float:
        """
        Get latest market price for a symbol (e.g., BTCUSDT)
        """
        res = self.session.get(f"{self.base_url}/api/v3/ticker/price", params={"symbol": symbol})
        res.raise_for_status()
        return float(res.json()["price"])

    def place_order(self, symbol: str, side: str, quantity: float, price: float = 0.0, order_type: str = "MARKET") -> dict:
        """
        Place market or limit order.
        """
        data = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity
        }

        if order_type.upper() == "LIMIT":
            data["price"] = f"{price:.2f}"
            data["timeInForce"] = "GTC"

        return self._post("/api/v3/order", data)

    def get_order_status(self, symbol: str, order_id: int) -> dict:
        """
        Fetch order status by ID.
        """
        return self._get("/api/v3/order", {"symbol": symbol, "orderId": order_id})
