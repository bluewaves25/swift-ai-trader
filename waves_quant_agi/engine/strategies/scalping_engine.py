# engine/strategies/scalping_engine.py

from .base_strategy import BaseStrategy
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ScalpingEngine(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.last_signal = 'SELL'

    def generate_signal(self, market_data):
        self.last_signal = 'BUY' if self.last_signal == 'SELL' else 'SELL'
        logger.info(f"[ScalpingEngine] Generated signal: {self.last_signal} {getattr(market_data, 'symbol', 'N/A')}")
        return self.last_signal
