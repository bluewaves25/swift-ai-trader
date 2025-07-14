# engine/strategies/base_strategy.py

from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np

class BaseStrategy(ABC):
    """
    Abstract base class for all strategies.
    Ensures consistency and standard interface across strategies.
    """

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.latest_signal = None
        self.position = None  # LONG, SHORT, or NONE
        self.performance = []

    @abstractmethod
    def generate_signal(self, data: Dict[str, Any]) -> str:
        """
        Must be implemented by subclasses.
        Should return 'BUY', 'SELL', or 'HOLD'.
        """
        pass

    def update_position(self, signal: str):
        """
        Updates internal state of the strategy based on new signal.
        """
        self.latest_signal = signal
        if signal == "BUY":
            self.position = "LONG"
        elif signal == "SELL":
            self.position = "SHORT"
        else:
            self.position = "NONE"

    def record_performance(self, pnl: float):
        """
        Record PnL (profit and loss) for later evaluation.
        """
        self.performance.append(pnl)

    def get_name(self):
        return self.name

    def get_config(self):
        return self.config

    def get_position(self):
        return self.position
