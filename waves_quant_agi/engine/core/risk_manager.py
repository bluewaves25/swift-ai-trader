import logging
from typing import List
from waves_quant_agi.engine.core.signal import Signal
import numpy as np
from waves_quant_agi.engine.core.schema import MarketData

logger = logging.getLogger(__name__)

class RiskManager:
    """
    Dynamically manages risk based on real-time market volatility.
    - Calculates stop-loss and take-profit levels that adapt to market conditions.
    - Determines position size based on volatility and risk tolerance.
    - Provides a centralized approval check for all potential trades.
    """
    def __init__(self, risk_per_trade=0.01, atr_period=14, atr_multiplier=2.0):
        self.risk_per_trade = risk_per_trade
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.price_history = []
        self.atr = 0

    def update_market_data(self, market_data: MarketData):
        """Updates the manager with the latest market data to calculate volatility."""
        self.price_history.append({
            'high': market_data.high,
            'low': market_data.low,
            'close': market_data.close
        })
        if len(self.price_history) > self.atr_period:
            self.price_history.pop(0)
        
        if len(self.price_history) == self.atr_period:
            self._calculate_atr()

    def _calculate_atr(self):
        """Calculates the Average True Range (ATR) as a measure of volatility."""
        true_ranges = []
        for i in range(1, len(self.price_history)):
            high = self.price_history[i]['high']
            low = self.price_history[i]['low']
            prev_close = self.price_history[i-1]['close']
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            true_ranges.append(tr)
        
        if true_ranges:
            self.atr = np.mean(true_ranges)

    def get_risk_parameters(self, current_price: float, side: str) -> dict:
        """
        Calculates dynamic stop-loss, take-profit, and position size.
        """
        if self.atr == 0:
            return {
                "stop_loss": 0,
                "take_profit": 0,
                "position_size": 0.01 # Default small size if no volatility data
            }

        stop_loss_distance = self.atr * self.atr_multiplier
        
        if side == 'buy':
            stop_loss = current_price - stop_loss_distance
            take_profit = current_price + (stop_loss_distance * 1.5) # Example R:R of 1:1.5
        else: # sell
            stop_loss = current_price + stop_loss_distance
            take_profit = current_price - (stop_loss_distance * 1.5)

        # Simplified position size calculation (in a real system, this would involve account balance)
        position_size = 0.01 # Using a fixed size for now, can be made dynamic
        
        return {
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size": position_size
        }

    def approve_trade(self, signal) -> bool:
        """
        Centralized approval logic for trades.
        For now, approves all trades. Can be extended with more rules.
        """
        # Example rule: Don't trade if volatility is too low
        if self.atr < 0.0001: # Example threshold
             # print("Trade rejected: Low volatility")
             # return False
             pass
        
        return True
