import numpy as np

class DrawdownChecker:
    """
    Evaluates the maximum drawdown of a given equity curve or returns.
    Rejects strategies with drawdown above threshold (e.g. 5%).
    """
    def __init__(self, max_drawdown_threshold: float = 0.05):
        self.max_drawdown_threshold = max_drawdown_threshold  # e.g., 5% = 0.05

    def max_drawdown(self, equity_curve: list[float]) -> float:
        equity_curve = np.array(equity_curve)
        peak = np.maximum.accumulate(equity_curve)
        drawdowns = (peak - equity_curve) / peak
        return np.max(drawdowns)

    def validate(self, equity_curve: list[float]) -> tuple[bool, dict]:
        max_dd = self.max_drawdown(equity_curve)
        passed = max_dd <= self.max_drawdown_threshold

        return passed, {
            "max_drawdown": round(float(max_dd), 4),
            "threshold": self.max_drawdown_threshold,
            "passed": passed
        }

# ✅ Add this function so it can be imported directly
def check_drawdown(equity_curve: list[float], threshold: float = 0.05) -> tuple[bool, dict]:
    checker = DrawdownChecker(max_drawdown_threshold=threshold)
    return checker.validate(equity_curve)
