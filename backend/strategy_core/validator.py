import tensorflow as tf
import numpy as np
import pandas as pd
from ta import add_all_ta_features
from routes.signal import get_sentiment
from data_feed.market_data import MarketData

class TradeValidator:
    def __init__(self):
        self.model = tf.keras.models.load_model("trade_model.h5")
        self.market_data = MarketData()

    async def validate_trade(self, trade, broker: str):
        data = await self.market_data.get_binance_data(trade.symbol) if broker == "binance" else await self.market_data.get_exness_data(trade.symbol)
        sentiment = await get_sentiment(trade.symbol)
        features = self.prepare_features(data, sentiment)
        score = self.model.predict(features)[0][0]
        return score * 100

    def prepare_features(self, market_data, sentiment):
        market_data = add_all_ta_features(market_data, open="open", high="high", low="low", close="close", volume="volume")
        features = np.array([market_data["trend_ema_fast"].iloc[-1], market_data["momentum_rsi"].iloc[-1], sentiment["combined_score"]])
        return features.reshape(1, -1)