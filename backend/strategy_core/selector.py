
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from supabase_client import SupabaseClient
from datetime import datetime, timedelta
import numpy as np

class StrategySelector:
    def __init__(self):
        self.db = SupabaseClient()
        self.model = RandomForestClassifier(n_estimators=100)

    def train_model(self, symbol: str):
        end_time = datetime.utcnow().isoformat()
        start_time = (datetime.utcnow() - timedelta(days=30)).isoformat()
        data = self.db.get_historical_data(symbol, start_time, end_time).data
        df = pd.DataFrame(data)

        # Feature engineering
        df['rsi'] = self.calculate_rsi(df['close'])
        df['volatility'] = df['high'] - df['low']
        df['market_condition'] = df.apply(self.detect_condition, axis=1)

        # Train model
        X = df[['rsi', 'volatility']].fillna(0)
        y = df['market_condition']
        self.model.fit(X, y)

    def calculate_rsi(self, prices, period=14):
        deltas = prices.diff()
        gain = (deltas.where(deltas > 0, 0)).rolling(window=period).mean()
        loss = (-deltas.where(deltas < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def detect_condition(self, row):
        if row['volatility'] > row['volatility'].mean() * 1.5:
            return 'volatile'
        elif row['close'] > row['close'].shift(1):
            return 'trending_up'
        elif row['close'] < row['close'].shift(1):
            return 'trending_down'
        else:
            return 'ranging'

    def select_strategy(self, symbol: str, latest_data: dict):
        self.train_model(symbol)
        features = pd.DataFrame([{
            'rsi': self.calculate_rsi(pd.Series([latest_data['close']])),
            'volatility': latest_data['high'] - latest_data['low']
        }]).fillna(0)
        condition = self.model.predict(features)[0]
        return {
            'trending_up': 'breakout',
            'trending_down': 'breakout',
            'volatile': 'scalping',
            'ranging': 'mean_reversion'
        }.get(condition, 'scalping')
