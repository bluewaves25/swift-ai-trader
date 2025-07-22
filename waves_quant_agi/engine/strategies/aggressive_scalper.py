from .base_strategy import BaseStrategy
from waves_quant_agi.engine.core.schema import MarketData
from waves_quant_agi.engine.core.signal import Signal
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class AggressiveScalper(BaseStrategy):
    """
    Aggressive HFT scalper: generates a buy or sell signal on every tick, alternating for HFT simulation.
    """
    def __init__(self, strategy_id="aggressive_scalper_v1", symbol="GBPUSDm"):
        super().__init__(strategy_id)
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.last_signal = "sell"

    def generate_signal(self, market_data: MarketData) -> Signal | None:
        if market_data.symbol != self.symbol:
            return None
        # Alternate between buy and sell
        self.last_signal = "buy" if self.last_signal == "sell" else "sell"
        signal = Signal(
            symbol=market_data.symbol,
            action=self.last_signal,
            size=0.01,
            confidence=1.0,
            strategy_name=self.strategy_id,
            timestamp=datetime.now(),
            metadata={}
        )
        logger.info(f"[AggressiveScalper] Generated signal: {signal.action} {signal.symbol} at {market_data.close}")
        return signal 