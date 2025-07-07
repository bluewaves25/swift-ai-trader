from data_feed.market_data import MarketData
import pandas as pd

class BreakoutStrategy:
    def __init__(self):
        self.market_data = MarketData()

    async def generate_signal(self, symbol: str, broker: str):
        data = await self.market_data.get_binance_data(symbol) if broker == "binance" else await self.market_data.get_exness_data(symbol)
        data["high_20"] = data["high"].rolling(20).max()
        data["low_20"] = data["low"].rolling(20).min()
        if data["close"].iloc[-1] > data["high_20"].iloc[-1]:
            return {"side": "buy", "volume": 0.01, "price": data["close"].iloc[-1]}
        elif data["close"].iloc[-1] < data["low_20"].iloc[-1]:
            return {"side": "sell", "volume": 0.01, "price": data["close"].iloc[-1]}
        return None