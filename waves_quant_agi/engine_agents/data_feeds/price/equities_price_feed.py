import asyncio
import ccxt.async_support as ccxt
from typing import Dict, Any, Optional
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class EquitiesPriceFeed:
    def __init__(self, exchanges: Dict[str, Dict[str, str]], symbols: list, interval: int = 1):
        self.exchanges = {name: getattr(ccxt, name)(config) for name, config in exchanges.items()}
        self.symbols = symbols  # e.g., ["AAPL", "TSLA"]
        self.interval = interval  # seconds
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.schema = {
            "exchange": str,
            "symbol": str,
            "price": float,
            "volume": float,
            "timestamp": float
        }

    async def fetch_price(self, exchange_name: str, exchange: ccxt.Exchange, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch price and volume for an equity symbol from an exchange."""
        try:
            ticker = await exchange.fetch_ticker(symbol)
            data = {
                "exchange": exchange_name,
                "symbol": symbol,
                "price": ticker["last"],
                "volume": ticker.get("baseVolume", 0.0),
                "timestamp": self.timestamp_utils.get_timestamp()
            }
            if self.validator.validate(data, self.schema):
                cleaned_data = self.cleaner.clean(data)
                return cleaned_data
            return None
        except Exception as e:
            print(f"Error fetching {symbol} from {exchange_name}: {e}")
            return None

    async def stream_prices(self):
        """Stream equity prices for all symbols and exchanges."""
        while True:
            tasks = []
            for exchange_name, exchange in self.exchanges.items():
                for symbol in self.symbols:
                    tasks.append(self.fetch_price(exchange_name, exchange, symbol))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for data in results:
                if data:
                    self.publisher.publish("equities_price", data)
                    self.db.store(data)
            
            await asyncio.sleep(self.interval)

    async def close(self):
        """Close all exchange connections."""
        for exchange in self.exchanges.values():
            await exchange.close()