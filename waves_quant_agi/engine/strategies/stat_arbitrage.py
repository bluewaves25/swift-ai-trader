import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from pykalman import KalmanFilter
from waves_quant_agi.engine.strategies.base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class StatisticalArbitrage(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.last_signal = 'sell'

    def generate_signal(self, market_data):
        self.last_signal = 'buy' if self.last_signal == 'sell' else 'sell'
        logger.info(f"[StatArb] Generated signal: {self.last_signal} {getattr(market_data, 'symbol', 'N/A')}")
        return self.last_signal
