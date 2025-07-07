from data_feed.market_data import MarketData
import pandas as pd
from ta import add_all_ta_features

class MeanReversionStrategy:
    def __init__(self):
        self.market_data = MarketData()

    async def generate_signal(self, symbol: str, broker: str):
        data = await self.market_data.get_binance_data(symbol) if broker == "binance" else await self.market_data.get_exness_data(symbol)
        data = add_all_ta_features(data, open="open", high="high", low="low", close="close", volume="volume")
        if data["momentum_rsi"].iloc[-1] < 30:
            return {"side": "buy", "volume": 0.01, "price": data["close"].iloc[-1]}
        elif data["momentum_rsi"].iloc[-1] > 70:
            return {"side": "sell", "volume": 0.01, "price": data["close"].iloc[-1]}
        return None