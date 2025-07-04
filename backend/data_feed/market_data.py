import asyncio
import ccxt.async_support as ccxt
from dotenv import load_dotenv
import os
from datetime import datetime
from supabase_client import SupabaseClient

load_dotenv()

class MarketData:
    def __init__(self):
        self.exness = ccxt.exness({
            'apiKey': os.getenv("EXNESS_API_KEY"),
            'secret': os.getenv("EXNESS_API_SECRET"),
            'enableRateLimit': True,
        })
        self.db = SupabaseClient()

    async def fetch_candles(self, symbol: str, timeframe: str = '1s'):
        try:
            while True:
                candles = await self.exness.fetch_ohlcv(symbol, timeframe, limit=1)
                if candles:
                    candle = candles[-1]
                    data = {
                        'symbol': symbol,
                        'timestamp': datetime.utcfromtimestamp(candle[0] / 1000).isoformat(),
                        'open': candle[1],
                        'high': candle[2],
                        'low': candle[3],
                        'close': candle[4],
                        'volume': candle[5]
                    }
                    self.db.save_market_data(data)
                await asyncio.sleep(1)
        finally:
            await self.exness.close()

    async def close(self):
        await self.exness.close()