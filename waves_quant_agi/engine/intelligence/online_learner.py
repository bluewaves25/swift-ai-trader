import logging
import random
import numpy as np
from typing import List, Dict
from waves_quant_agi.core.models.transaction import Trade

logger = logging.getLogger(__name__)

class OnlineLearner:
    """
    The brain of the AGI engine. Learns from past trades to dynamically
    adjust strategy weights, creating a powerful feedback loop.
    - Analyzes trade outcomes (profit/loss).
    - Uses a simple reinforcement learning model to reward profitable strategies
      and penalize unprofitable ones.
    - Normalizes weights to ensure the portfolio remains balanced.
    """
    def __init__(self, learning_rate=0.01, decay_factor=0.995):
        self.learning_rate = learning_rate
        self.decay_factor = decay_factor

    def update_weights(self, trades: List[Trade], current_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Adjusts strategy weights based on the PnL of recent trades.
        """
        if not trades:
            # Apply a slight decay to all weights if no recent trades
            for strategy_id in current_weights:
                current_weights[strategy_id] *= self.decay_factor
            return self._normalize_weights(current_weights)

        for trade in trades:
            strategy_id = trade.strategy
            if strategy_id not in current_weights:
                continue

            # Reward or penalize based on trade profit
            if trade.pnl > 0:
                reward = self.learning_rate * np.log1p(trade.pnl) # Log scale for big wins
                current_weights[strategy_id] += reward
            elif trade.pnl < 0:
                penalty = self.learning_rate * np.log1p(abs(trade.pnl))
                current_weights[strategy_id] -= penalty

        return self._normalize_weights(current_weights)

    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Normalizes weights so they sum to 1, ensuring a balanced portfolio.
        """
        total_weight = sum(weights.values())
        if total_weight <= 0:
            # Reset to equal weights if all become zero or negative
            return {strategy_id: 1.0 / len(weights) for strategy_id in weights}
            
        normalized_weights = {s_id: w / total_weight for s_id, w in weights.items()}
        return normalized_weights
