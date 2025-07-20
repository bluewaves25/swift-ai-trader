import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from pykalman import KalmanFilter
from waves_quant_agi.engine.strategies.base_strategy import BaseStrategy

class StatisticalArbitrage(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.spread_threshold = 2.0  # Z-score trigger level
        self.history_window = 30     # Rolling window size for Z-score
        self.spread_history = []

    def calculate_kalman_spread(self, series_a, series_b):
        """
        Estimate spread dynamically using Kalman Filter
        """
        series_a = np.array(series_a)
        series_b = np.array(series_b)

        kf = KalmanFilter(
            transition_matrices=np.eye(2),
            observation_matrices=np.vstack([series_a, np.ones(len(series_a))]).T[:, np.newaxis, :],
            initial_state_mean=np.zeros(2),
            initial_state_covariance=np.eye(2),
            observation_covariance=1.0,
            transition_covariance=0.01 * np.eye(2)
        )

        state_means, _ = kf.filter(series_b)
        hedge_ratio = state_means[:, 0]
        spread = series_b - hedge_ratio * series_a
        return spread

    def is_cointegrated(self, spread):
        """
        Uses ADF test to check if spread is stationary (i.e., cointegrated)
        """
        result = adfuller(spread)
        return result[1] < 0.05  # p-value threshold

    def calculate_spread(self, series_a, series_b):
        """
        Wrapper to compute Z-score from Kalman-filtered spread
        """
        spread = self.calculate_kalman_spread(series_a, series_b)

        if not self.is_cointegrated(spread):
            return None  # Abort signal if no cointegration

        self.spread_history.extend(spread[-self.history_window:])
        if len(self.spread_history) < self.history_window:
            return None  # Not enough data

        mean = np.mean(self.spread_history)
        std = np.std(self.spread_history)
        zscore = (spread[-1] - mean) / std if std > 0 else 0
        return zscore

    def predict(self, series_a, series_b):
        """
        Decision logic based on Z-score threshold
        """
        z = self.calculate_spread(series_a, series_b)
        if z is None:
            return "hold"  # Not ready or not cointegrated

        if z > self.spread_threshold:
            return "sell_A_buy_B"
        elif z < -self.spread_threshold:
            return "buy_A_sell_B"
        return "hold"
