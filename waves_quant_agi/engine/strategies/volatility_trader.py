# engine/strategies/volatility_trader.py

from .base_strategy import BaseStrategy
import numpy as np

class VolatilityTrader(BaseStrategy):
    """
    Detects volatility expansion using rolling standard deviation.
    Enters long when vol breakout occurs.
    """

    def generate_signal(self, data):
        prices = np.array(data["close"])
        window = self.config.get("window", 20)
        threshold = self.config.get("vol_threshold", 1.5)

        if len(prices) < window:
            return "HOLD"

        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns[-window:])

        if volatility > threshold:
            return "BUY"
        elif volatility < threshold / 2:
            return "SELL"
        else:
            return "HOLD"
