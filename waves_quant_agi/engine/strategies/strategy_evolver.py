import random
from waves_quant_agi.engine.strategies.base_strategy import BaseStrategy

class StrategyEvolver(BaseStrategy):
    def __init__(self):
        super().__init__()

    def mutate(self, strategy_config):
        # Randomly change a parameter value slightly
        new_config = strategy_config.copy()
        for key in new_config:
            if isinstance(new_config[key], (int, float)):
                change = random.uniform(-0.1, 0.1)
                new_config[key] *= (1 + change)
        return new_config

    def crossover(self, parent_a, parent_b):
        child = {}
        for key in parent_a:
            child[key] = random.choice([parent_a[key], parent_b[key]])
        return child
