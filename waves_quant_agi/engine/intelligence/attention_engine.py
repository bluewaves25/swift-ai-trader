import logging

logger = logging.getLogger(__name__)

class AttentionEngine:
    """
    🎯 AttentionEngine dynamically selects and weights the most effective strategies
    based on current market regime and performance.
    """

    def __init__(self):
        self.weights = {}  # strategy_name: weight

    def update_weights(self, strategy_scores):
        """
        Update strategy weights based on external scoring logic.
        :param strategy_scores: Dict[str, float] - performance scores
        """
        total = sum(strategy_scores.values()) or 1.0
        self.weights = {k: v / total for k, v in strategy_scores.items()}
        logger.info(f"Updated attention weights: {self.weights}")

    def get_weight(self, strategy_name: str) -> float:
        return self.weights.get(strategy_name, 0.0)

    def fuse_signals(self, strategy_signals: dict):
        """
        Combines signals from multiple strategies based on learned weights.
        :param strategy_signals: Dict[str, float]
        :return: float - aggregated signal
        """
        return sum(strategy_signals.get(name, 0) * self.get_weight(name) for name in strategy_signals)
