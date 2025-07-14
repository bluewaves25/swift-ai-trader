import numpy as np

class MonteCarloValidator:
    """
    Runs Monte Carlo simulations on strategy PnLs to test robustness.
    """

    def __init__(self, simulations: int = 1000, initial_equity: float = 10000.0, pass_threshold_ratio: float = 1.15):
        self.simulations = simulations
        self.initial_equity = initial_equity
        self.pass_threshold = initial_equity * pass_threshold_ratio

    def simulate(self, trade_returns: list[float]) -> tuple[bool, dict]:
        trade_returns = np.array(trade_returns)
        equity_paths = []

        for _ in range(self.simulations):
            shuffled = np.random.permutation(trade_returns)
            equity = np.cumsum(np.insert(shuffled, 0, self.initial_equity))
            equity_paths.append(equity)

        equity_paths = np.array(equity_paths)
        final_equities = equity_paths[:, -1]
        median_equity = np.median(final_equities)
        best_case = np.max(final_equities)
        worst_case = np.min(final_equities)

        passed = median_equity >= self.pass_threshold

        return passed, {
            "simulations": self.simulations,
            "median_final_equity": float(median_equity),
            "best_case": float(best_case),
            "worst_case": float(worst_case),
            "initial_equity": self.initial_equity,
            "pass_threshold": float(self.pass_threshold),
            "passed": passed
        }
