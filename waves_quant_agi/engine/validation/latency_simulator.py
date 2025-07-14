import numpy as np
import random

class LatencySimulator:
    """
    Simulates the impact of latency, slippage, and order execution delays
    on trading strategy signals and performance.
    """

    def __init__(self, max_latency_ms: int = 300, slippage_pct: float = 0.001):
        """
        Args:
            max_latency_ms (int): Maximum latency in milliseconds.
            slippage_pct (float): Slippage as percentage of price (e.g., 0.001 = 0.1%).
        """
        self.max_latency_ms = max_latency_ms
        self.slippage_pct = slippage_pct

    def simulate_latency(self, signal_time: float, execution_time: float) -> float:
        """
        Simulates random latency between signal and execution.

        Args:
            signal_time (float): Timestamp of when the trading signal was generated.
            execution_time (float): Timestamp of when execution was attempted.

        Returns:
            float: Simulated latency (in milliseconds).
        """
        simulated_latency = random.randint(1, self.max_latency_ms)
        actual_delay = execution_time - signal_time + (simulated_latency / 1000)
        return round(actual_delay * 1000, 2)

    def apply_slippage(self, execution_price: float) -> float:
        """
        Applies slippage to the execution price.

        Args:
            execution_price (float): Original price before slippage.

        Returns:
            float: Adjusted price after slippage.
        """
        slippage = execution_price * self.slippage_pct
        adjusted_price = execution_price + np.random.choice([-1, 1]) * slippage
        return round(adjusted_price, 5)

    def simulate_trade(self, signal_time: float, execution_time: float, price: float) -> dict:
        """
        Simulates the full latency and slippage effect on a trade.

        Args:
            signal_time (float): Time signal was generated.
            execution_time (float): Time trade was executed.
            price (float): Original execution price.

        Returns:
            dict: {
                "latency_ms": Simulated latency in milliseconds,
                "adjusted_price": Price after slippage adjustment
            }
        """
        latency = self.simulate_latency(signal_time, execution_time)
        adjusted_price = self.apply_slippage(price)
        return {
            "latency_ms": latency,
            "adjusted_price": adjusted_price
        }

# 👇 Optional shortcut export if needed elsewhere
def simulate_latency(signal_time: float, execution_time: float, max_latency_ms: int = 300) -> float:
    """
    Standalone function version for quick access if class is not needed.
    """
    sim = LatencySimulator(max_latency_ms=max_latency_ms)
    return sim.simulate_latency(signal_time, execution_time)
