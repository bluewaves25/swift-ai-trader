import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from ta import add_all_ta_features
from routes.signals import get_sentiment
from data_feed.market_data import MarketData
from db.supabase_client import get_supabase_client  # optional

class TradeValidationModel(nn.Module):
    def __init__(self):
        super(TradeValidationModel, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(3, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()  # Output between 0 and 1
        )

    def forward(self, x):
        return self.model(x)

class TradeValidator:
    def __init__(self):
        self.model = TradeValidationModel()
        self.model.load_state_dict(torch.load("trade_model.pt"))
        self.model.eval()
        self.market_data = MarketData()
        self.supabase = get_supabase_client()

    async def validate_trade(self, trade, broker: str):
        # 1. Get market data from Binance or Exness
        data = await self.market_data.get_binance_data(trade.symbol) if broker == "binance" else await self.market_data.get_exness_data(trade.symbol)

        # 2. Get sentiment score
        sentiment = await get_sentiment(trade.symbol)

        # 3. Prepare feature vector
        features = self.prepare_features(data, sentiment)
        input_tensor = torch.tensor(features, dtype=torch.float32)

        # 4. Predict score
        with torch.no_grad():
            score = self.model(input_tensor).item()

        # 5. (Optional) Save result to Supabase
        await self.log_prediction(trade.symbol, score, sentiment["combined_score"])

        # 6. Return score (percentage)
        return score * 100

    def prepare_features(self, market_data, sentiment):
        df = add_all_ta_features(market_data, open="open", high="high", low="low", close="close", volume="volume")
        features = np.array([
            df["trend_ema_fast"].iloc[-1],
            df["momentum_rsi"].iloc[-1],
            sentiment["combined_score"]
        ])
        return features.reshape(1, -1)

    async def log_prediction(self, symbol, score, sentiment_score):
        try:
            await self.supabase.table("trade_predictions").insert({
                "symbol": symbol,
                "score": score,
                "sentiment_score": sentiment_score,
            }).execute()
        except Exception as e:
            print(f"[Warning] Failed to log prediction: {e}")
