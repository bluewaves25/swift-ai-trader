from .base_strategy import BaseStrategy
from waves_quant_agi.engine.core.schema import MarketData
from waves_quant_agi.engine.core.signal import Signal
from datetime import datetime
import random

class AggressiveScalper(BaseStrategy):
    """
    A simple, highly aggressive scalping strategy for HFT simulation.
    Generates a buy or sell signal on nearly every new tick of data,
    simulating a high-frequency trading approach.
    """
    def __init__(self, strategy_id="aggressive_scalper_v1", symbol="XAUUSDm"):
        super().__init__(strategy_id)
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.last_price = None

    def generate_signal(self, market_data: MarketData) -> Signal | None:
        """
        Generates a signal on almost any price change.
        """
        if market_data.symbol != self.symbol:
            return None

        current_price = market_data.close
        
        # Don't trade if there's no price history yet
        if self.last_price is None:
            self.last_price = current_price
            return None

        signal = None
        # If price moved up, generate a BUY signal
        if current_price > self.last_price:
            signal = Signal(
                strategy_name=self.strategy_id,
                symbol=self.symbol,
                action="buy",
                size=0.01, # Standard lot size for scalping
                confidence=random.uniform(0.75, 0.95), # High confidence for HFT simulation
                timestamp=datetime.now(),
                metadata={"reason": "Aggressive scalping micro-trend up"}
            )
        # If price moved down, generate a SELL signal
        elif current_price < self.last_price:
            signal = Signal(
                strategy_name=self.strategy_id,
                symbol=self.symbol,
                action="sell",
                size=0.01,
                confidence=random.uniform(0.75, 0.95),
                timestamp=datetime.now(),
                metadata={"reason": "Aggressive scalping micro-trend down"}
            )
        
        self.last_price = current_price
        
        if signal:
            print(f"Generated signal: {signal.action} {signal.symbol} at {current_price}")
            
        return signal 