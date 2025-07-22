import numpy as np
from waves_quant_agi.engine.strategies.base_strategy import BaseStrategy
import random
import logging

logger = logging.getLogger(__name__)

class CrisisAlphaBot(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.last_signal = 'sell'

    def generate_signal(self, market_data):
        # Alternate between buy and sell for HFT simulation
        self.last_signal = 'buy' if self.last_signal == 'sell' else 'sell'
        logger.info(f"[CrisisAlphaBot] Generated signal: {self.last_signal} {getattr(market_data, 'symbol', 'N/A')}")
        return self.last_signal
