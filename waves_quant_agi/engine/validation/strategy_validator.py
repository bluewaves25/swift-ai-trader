from engine.validation.drawdown_checker import check_drawdown
from engine.validation.alpha_decay_monitor import check_alpha_decay
from engine.validation.walk_forward_validator import walk_forward_analysis
from engine.validation.latency_simulator import LatencySimulator  # ✅ Correct
from engine.validation.regime_stability_tester import test_regime_stability
from engine.validation.monte_carlo_simulator import MonteCarloValidator
from engine.validation.regime_stability_tester import test_regime_stability

class StrategyValidator:
    """
    Core validator that runs multiple tests to ensure the strategy is robust.
    """

    def __init__(self, min_win_rate=0.8, max_drawdown=0.05, min_sharpe=3.0, min_sortino=2.5):
        self.min_win_rate = min_win_rate
        self.max_drawdown = max_drawdown
        self.min_sharpe = min_sharpe
        self.min_sortino = min_sortino

    def validate(self, trades, equity_curve, signals, prices):
        """
        Run all strategy validation checks.

        :param trades: List of executed trades (PnL data)
        :param equity_curve: Time series of equity values
        :param signals: Strategy signals (entry/exit)
        :param prices: Raw price data used
        :return: (bool, dict of all validation results)
        """

        results = {}

        # 1. Monte Carlo stress testing
        results["monte_carlo_pass"], mc_details = monte_carlo_simulation(trades)
        results["monte_carlo_details"] = mc_details

        # 2. Drawdown analysis
        results["drawdown_pass"], dd_stats = check_drawdown(equity_curve, self.max_drawdown)
        results["drawdown_details"] = dd_stats

        # 3. Walk-forward generalization check
        results["walk_forward_pass"], wf_score = walk_forward_analysis(signals, prices)
        results["walk_forward_score"] = wf_score

        # 4. Regime stability (trending, ranging, crash, etc.)
        results["regime_stable"], regime_report = test_regime_stability(signals, prices)
        results["regime_report"] = regime_report

        # 5. Latency sensitivity (slippage, order delay modeling)
        results["latency_resistant"], latency_loss = simulate_latency(signals, prices)
        results["latency_loss"] = latency_loss

        # 6. Alpha Decay Monitor
        results["alpha_stable"], decay_stats = check_alpha_decay(trades)
        results["alpha_decay"] = decay_stats

        # Final Decision
        is_valid = all([
            results["monte_carlo_pass"],
            results["drawdown_pass"],
            results["walk_forward_pass"],
            results["regime_stable"],
            results["latency_resistant"],
            results["alpha_stable"]
        ])

        return is_valid, results
