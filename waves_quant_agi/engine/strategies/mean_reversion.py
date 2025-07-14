# engine/strategies/mean_reversion.py

from .base_strategy import BaseStrategy
import numpy as np
from statsmodels.tsa.stattools import adfuller
from pykalman import KalmanFilter

class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion using ADF test + Kalman Filter for pair spread estimation.
    Assumes you're providing two price series: asset_x and asset_y.
    """

    def generate_signal(self, data):
        # Expect data to have 'asset_x' and 'asset_y' price series
        prices_x = np.array(data["asset_x"])
        prices_y = np.array(data["asset_y"])

        min_len = self.config.get("min_length", 50)
        adf_threshold = self.config.get("adf_pvalue", 0.05)
        z_threshold = self.config.get("z_threshold", 1.5)

        if len(prices_x) < min_len or len(prices_y) < min_len:
            return "HOLD"

        # Step 1: Estimate dynamic hedge ratio using Kalman Filter
        kf = KalmanFilter(transition_matrices=[1],
                          observation_matrices=np.expand_dims(prices_x, axis=1))

        state_means, _ = kf.filter(prices_y)
        hedge_ratio = state_means.flatten()

        # Step 2: Estimate spread
        spread = prices_y - hedge_ratio * prices_x

        # Step 3: Check if spread is stationary using ADF test
        adf_result = adfuller(spread)
        p_value = adf_result[1]

        if p_value > adf_threshold:
            return "HOLD"  # Spread is not stationary → unreliable mean reversion

        # Step 4: Calculate Z-score
        mean = np.mean(spread)
        std = np.std(spread)
        z = (spread[-1] - mean) / std if std > 0 else 0

        # Step 5: Generate trading signal based on Z-score
        if z < -z_threshold:
            return "BUY"   # Spread is too negative, expect it to revert up
        elif z > z_threshold:
            return "SELL"  # Spread is too positive, expect it to revert down
        else:
            return "HOLD"
