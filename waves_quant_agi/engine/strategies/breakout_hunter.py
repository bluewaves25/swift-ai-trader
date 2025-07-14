# engine/strategies/breakout_hunter.py

from .base_strategy import BaseStrategy
import numpy as np

class BreakoutHunter(BaseStrategy):
    """
    Detects breakouts using recent high/low + volume spike.
    """

    def generate_signal(self, data):
        highs = np.array(data["high"][-20:])
        lows = np.array(data["low"][-20:])
        volumes = np.array(data["volume"][-20:])
        price = data["close"][-1]

        breakout_high = max(highs)
        breakout_low = min(lows)
        avg_volume = np.mean(volumes)
        latest_volume = volumes[-1]

        if price > breakout_high and latest_volume > 1.5 * avg_volume:
            return "BUY"
        elif price < breakout_low and latest_volume > 1.5 * avg_volume:
            return "SELL"
        else:
            return "HOLD"
