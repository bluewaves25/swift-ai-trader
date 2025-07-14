import numpy as np
from engine.strategies.base_strategy import BaseStrategy

class CrisisAlphaBot(BaseStrategy):
    def __init__(self):
        super().__init__()

    def detect_volatility_spike(self, price_series):
        returns = np.diff(price_series) / price_series[:-1]
        volatility = np.std(returns[-10:])
        return volatility > 0.05  # Arbitrary crisis threshold

    def predict(self, price_series):
        if self.detect_volatility_spike(price_series):
            return "safe_mode_on"
        return "normal"
