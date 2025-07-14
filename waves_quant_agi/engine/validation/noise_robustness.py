import numpy as np
from typing import Callable

class NoiseRobustnessTester:
    """
    Evaluates how resilient a trading strategy is to noisy data input.
    """

    def __init__(self, noise_level: float = 0.01, trials: int = 10):
        """
        Args:
            noise_level (float): Standard deviation of Gaussian noise to add.
            trials (int): Number of noise injection trials to perform.
        """
        self.noise_level = noise_level
        self.trials = trials

    def add_noise(self, data: np.ndarray) -> np.ndarray:
        """
        Adds Gaussian noise to a data array.

        Args:
            data (np.ndarray): Original time series data.

        Returns:
            np.ndarray: Noisy version of the data.
        """
        noise = np.random.normal(0, self.noise_level, size=data.shape)
        return data + noise

    def evaluate_strategy(self, strategy_fn: Callable, original_data: np.ndarray) -> float:
        """
        Applies noise repeatedly and evaluates how often the strategy's signal changes.

        Args:
            strategy_fn (Callable): A strategy function that returns a signal given data.
            original_data (np.ndarray): Clean data input.

        Returns:
            float: Percentage of times signal flipped due to noise (instability score).
        """
        base_signal = strategy_fn(original_data)
        flip_count = 0

        for _ in range(self.trials):
            noisy_data = self.add_noise(original_data)
            noisy_signal = strategy_fn(noisy_data)
            if noisy_signal != base_signal:
                flip_count += 1

        return flip_count / self.trials  # Instability ratio (0 = robust, 1 = unstable)

    def is_strategy_robust(self, instability_score: float, threshold: float = 0.3) -> bool:
        """
        Determines if the strategy is robust enough based on signal flip rate.

        Returns:
            bool: True if stable under noise, False if too sensitive.
        """
        return instability_score <= threshold
