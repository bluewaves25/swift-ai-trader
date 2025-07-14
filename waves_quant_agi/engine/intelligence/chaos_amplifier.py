import numpy as np
import logging

logger = logging.getLogger(__name__)

class ChaosAmplifier:
    """
    ⚡ ChaosAmplifier enhances signals during high-volatility or anomaly events
    to exploit market instability.
    """

    def __init__(self, threshold=2.5):
        self.threshold = threshold

    def amplify(self, signal: float, volatility: float, news_sentiment: float = 0.0) -> float:
        chaos_score = volatility + abs(news_sentiment)
        if chaos_score > self.threshold:
            amplified = signal * 1.5
            logger.info(f"Chaos amplified signal: {amplified} (chaos_score={chaos_score})")
            return amplified
        return signal
