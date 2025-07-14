import logging
from typing import List
from engine.core.signal import Signal

logger = logging.getLogger(__name__)

class RiskManager:
    """
    🛡️ RiskManager: Applies risk constraints and portfolio rules to signals.
    """

    def __init__(self):
        self.max_risk_per_trade = 0.02
        self.max_position_size = 100000
        logger.info("Risk Manager initialized ✅")

    async def adjust_signals(self, signals: List[Signal], metrics: dict) -> List[Signal]:
        adjusted = []
        for signal in signals:
            original_size = signal.size

            max_allowed = self.max_risk_per_trade * 1_000_000
            signal.size = min(signal.size, max_allowed, self.max_position_size)

            logger.debug(f"Signal adjusted for {signal.symbol}: {original_size} ➞ {signal.size}")
            adjusted.append(signal)

        return adjusted
