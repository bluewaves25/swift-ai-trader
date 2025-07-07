import ccxt.async_support as ccxt
import MetaTrader5 as mt5
from python_dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

class MarketData:
    def __init__(self):
        self.binance = ccxt.binance({"apiKey": os.getenv("BINANCE_API_KEY"), "secret": os.getenv("BINANCE_SECRET")})
        self.exness = mt5

    async def get_binance_data(self, symbol: str, timeframe: str = "1m"):
        ohlcv = await self.binance.fetch_ohlcv(symbol, timeframe)
        return pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

    async def get_exness_data(self, symbol: str, timeframe: int = mt5.TIMEFRAME_M1):
        mt5.initialize()
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
        return pd.DataFrame(rates, columns=["time", "open", "high", "low", "close", "tick_volume"])