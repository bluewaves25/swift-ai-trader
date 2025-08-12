import asyncio
import ccxt.async_support as ccxt
from typing import Dict, Any, Optional
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class TradeCollector:
    def __init__(self, exchanges: Dict[str, Dict[str, str]] = None, symbols: list = None, interval: int = 1):
        self.symbols = symbols or ["BTC/USDT", "ETH/USDT"]
        self.interval = interval  # seconds
        
        # Only initialize exchanges if provided
        if exchanges:
            self.exchanges = {name: getattr(ccxt, name)(config) for name, config in exchanges.items()}
            self.enabled = True
        else:
            self.exchanges = {}
            self.enabled = False
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.schema = {
            "exchange": str,
            "symbol": str,
            "price": float,
            "amount": float,
            "side": str,  # "buy" or "sell"
            "timestamp": float
        }

    async def fetch_trades(self, exchange_name: str, exchange: ccxt.Exchange, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch recent trades for a symbol from an exchange."""
        try:
            trades = await exchange.fetch_trades(symbol, limit=10)
            if not trades:
                return None
            # Process most recent trade
            trade = trades[0]
            data = {
                "exchange": exchange_name,
                "symbol": symbol,
                "price": float(trade["price"]),
                "amount": float(trade["amount"]),
                "side": trade["side"],
                "timestamp": self.timestamp_utils.get_timestamp()
            }
            if self.validator.validate(data, self.schema):
                cleaned_data = self.cleaner.clean(data)
                return cleaned_data
            return None
        except Exception as e:
            print(f"Error fetching trades for {symbol} from {exchange_name}: {e}")
            return None

    async def stream_trades(self):
        """Stream trade tape data for all symbols and exchanges."""
        while True:
            tasks = [self.fetch_trades(name, exchange, symbol) for name, exchange in self.exchanges.items() for symbol in self.symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for data in results:
                if data:
                    self.publisher.publish("trade_tape", data)
                    self.db.store(data)
            await asyncio.sleep(self.interval)

    async def close(self):
        """Close all exchange connections."""
        for exchange in self.exchanges.values():
            await exchange.close()