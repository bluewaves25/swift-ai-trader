# engine/strategies/scalping_engine.py

from .base_strategy import BaseStrategy
import numpy as np

class ScalpingEngine(BaseStrategy):
    """
    Uses short-term momentum and micro pattern for quick trades.
    """

    def generate_signal(self, data):
        price = data["close"][-1]
        bid = data["bid"][-1]
        ask = data["ask"][-1]

        spread = ask - bid
        mid_price = (ask + bid) / 2

        if price < bid - spread:
            return "BUY"
        elif price > ask + spread:
            return "SELL"
        else:
            return "HOLD"
