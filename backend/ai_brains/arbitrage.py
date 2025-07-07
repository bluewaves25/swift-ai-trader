from data_feed.market_data import MarketData

class ArbitrageStrategy:
    def __init__(self):
        self.market_data = MarketData()

    async def generate_signal(self, symbol: str):
        binance_data = await self.market_data.get_binance_data(symbol)
        exness_data = await self.market_data.get_exness_data(symbol)
        if binance_data["close"].iloc[-1] > exness_data["close"].iloc[-1] * 1.01:
            return {"side": "sell", "volume": 0.01, "price": binance_data["close"].iloc[-1], "broker": "binance"}
        elif exness_data["close"].iloc[-1] > binance_data["close"].iloc[-1] * 1.01:
            return {"side": "buy", "volume": 0.01, "price": exness_data["close"].iloc[-1], "broker": "exness"}
        return None