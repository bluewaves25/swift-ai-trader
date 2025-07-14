def check_alpha_decay(signals: list[float], future_returns: list[list[float]], threshold: float = 0.5) -> tuple[bool, dict]:
    """
    Wrapper to use AlphaDecayMonitor directly for validation.

    Args:
        signals (list[float]): 1D signal array
        future_returns (list[list[float]]): 2D list of future returns
        threshold (float): Minimum acceptable decay score

    Returns:
        (bool, dict): pass/fail status and metrics
    """
    monitor = AlphaDecayMonitor()
    try:
        signals_np = np.array(signals)
        future_returns_np = np.array(future_returns)
        decay_score = monitor.compute_decay(signals_np, future_returns_np)
        passed = monitor.is_alpha_strong(decay_score, threshold)

        return passed, {
            "decay_score": round(float(decay_score), 4),
            "threshold": threshold,
            "passed": passed
        }

    except Exception as e:
        return False, {"error": str(e)}
