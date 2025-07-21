### engine/core/strategy_manager.py

from typing import Dict, List, Type
from waves_quant_agi.engine.strategies.base_strategy import BaseStrategy
from waves_quant_agi.engine.core.schema import MarketData
from waves_quant_agi.engine.core.signal import Signal
import logging
from waves_quant_agi.core.models.strategy import Strategy as StrategyModel
from waves_quant_agi.core.database import get_db
from sqlalchemy.future import select
import asyncio

logger = logging.getLogger(__name__)

class StrategyManager:
    """
    Manages the lifecycle and execution of a portfolio of trading strategies.
    - Holds all active strategies.
    - Assigns and dynamically updates weights based on performance.
    - Distributes market data to all strategies.
    - Collects and returns generated signals.
    """
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.strategy_weights: Dict[str, float] = {}

    def add_strategy(self, strategy: BaseStrategy, weight: float = 1.0):
        """Adds a strategy to the manager and sets its initial weight."""
        if strategy.strategy_id in self.strategies:
            print(f"Strategy {strategy.strategy_id} already exists.")
            return
        self.strategies[strategy.strategy_id] = strategy
        self.strategy_weights[strategy.strategy_id] = weight
        print(f"Strategy {strategy.strategy_id} added with weight {weight}")

    def remove_strategy(self, strategy_id: str):
        """Removes a strategy from the manager."""
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            del self.strategy_weights[strategy_id]
            print(f"Strategy {strategy_id} removed.")

    def update_strategy_weights(self, new_weights: Dict[str, float]):
        """Dynamically updates the weights of the strategies."""
        print(f"Updating strategy weights: {new_weights}")
        for strategy_id, weight in new_weights.items():
            if strategy_id in self.strategy_weights:
                self.strategy_weights[strategy_id] = weight

    def get_all_signals(self, market_data: MarketData) -> List[Signal]:
        """
        Distributes market data to all active strategies and collects signals.
        Enriches signals with the current strategy weight.
        """
        signals = []
        for strategy_id, strategy in self.strategies.items():
            signal = strategy.generate_signal(market_data)
            if signal:
                # Add the strategy's current weight to the signal metadata
                signal.metadata['strategy_weight'] = self.strategy_weights.get(strategy_id, 0)
                signals.append(signal)
        return signals
