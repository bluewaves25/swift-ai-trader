import asyncio
import ccxt.async_support as ccxt
from typing import Dict, Any, Optional
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class BinanceOrderBook:
    def __init__(self, api_key: str, api_secret: str, symbols: list, depth: int = 10, interval: int = 1):
        self.exchange = ccxt.binance({"apiKey": api_key, "secret": api_secret, "enableRateLimit": True})
        self.symbols = symbols  # e.g., ["BTC/USDT"]
        self.depth = depth  # Number of bid/ask levels
        self.interval = interval  # seconds
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.schema = {
            "exchange": str,
            "symbol": str,
            "bids": list,  # [[price, amount], ...]
            "asks": list,  # [[price, amount], ...]
            "timestamp": float
        }

    async def fetch_order_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch order book for a symbol from Binance."""
        try:
            order_book = await self.exchange.fetch_order_book(symbol, limit=self.depth)
            data = {
                "exchange": "binance",
                "symbol": symbol,
                "bids": order_book["bids"],
                "asks": order_book["asks"],
                "timestamp": self.timestamp_utils.get_timestamp()
            }
            if self.validator.validate(data, self.schema):
                cleaned_data = self.cleaner.clean(data)
                return cleaned_data
            return None
        except Exception as e:
            print(f"Error fetching order book for {symbol}: {e}")
            return None

    async def stream_order_book(self):
        """Stream order book data for all symbols."""
        while True:
            tasks = [self.fetch_order_book(symbol) for symbol in self.symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for data in results:
                if data:
                    self.publisher.publish("order_book", data)
                    self.db.store(data)
            await asyncio.sleep(self.interval)

    async def close(self):
        """Close exchange connection."""
        await self.exchange.close()