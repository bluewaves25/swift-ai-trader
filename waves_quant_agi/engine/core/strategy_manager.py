### engine/core/strategy_manager.py

from typing import Dict, List
from engine.strategies.base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class StrategyManager:
    """
    📈 StrategyManager: Handles registration, retrieval, and execution
    of all trading strategies within the AGI engine.
    """

    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        logger.info("Strategy Manager initialized ✅")

    def register_strategy(self, strategy: BaseStrategy):
        if strategy.name in self.strategies:
            logger.warning(f"Strategy '{strategy.name}' already registered, skipping")
            return
        self.strategies[strategy.name] = strategy
        logger.info(f"Registered strategy: {strategy.name}")

    def remove_strategy(self, strategy_name: str):
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
            logger.info(f"Removed strategy: {strategy_name}")
        else:
            logger.warning(f"Strategy '{strategy_name}' not found")

    def get_strategy(self, strategy_name: str) -> BaseStrategy:
        return self.strategies.get(strategy_name)

    def list_strategies(self) -> List[str]:
        return list(self.strategies.keys())

    async def run_all(self, market_data):
        results = []
        for name, strategy in self.strategies.items():
            logger.info(f"Running strategy: {name}")
            signal = await strategy.generate_signal(market_data)
            results.append(signal)
        return results
