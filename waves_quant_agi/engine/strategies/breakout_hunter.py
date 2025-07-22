# engine/strategies/breakout_hunter.py

from .base_strategy import BaseStrategy
import numpy as np
import logging

logger = logging.getLogger(__name__)

class BreakoutHunter(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.last_signal = 'SELL'

    def generate_signal(self, market_data):
        self.last_signal = 'BUY' if self.last_signal == 'SELL' else 'SELL'
        logger.info(f"[BreakoutHunter] Generated signal: {self.last_signal} {getattr(market_data, 'symbol', 'N/A')}")
        return self.last_signal
