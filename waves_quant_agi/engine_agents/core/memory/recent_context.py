from typing import Dict, Any, List
from collections import deque
from ..logs.core_agent_logger import CoreAgentLogger
from ..interfaces.trade_model import TradeCommand

class RecentContext:
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.signals = deque(maxlen=max_history)
        self.rejections = deque(maxlen=max_history)
        self.pnl_snapshots = deque(maxlen=max_history)
        self.logger = CoreAgentLogger("recent_context")

    def store_signal(self, signal: Dict[str, Any]):
        """Store a trading signal."""
        self.signals.append(signal)
        self.logger.log_action("store_signal", {"signal_id": signal.get("signal_id")})

    def store_rejection(self, signal_id: str, reason: str):
        """Store a rejected signal with reason."""
        self.rejections.append({"signal_id": signal_id, "reason": reason})
        self.logger.log_action("store_rejection", {"signal_id": signal_id, "reason": reason})

    def store_pnl_snapshot(self, snapshot: Dict[str, Any]):
        """Store a PnL snapshot."""
        self.pnl_snapshots.append(snapshot)
        self.logger.log_action("store_pnl", {"snapshot": snapshot})

    def get_recent_signals(self) -> List[Dict[str, Any]]:
        """Get recent signals."""
        return list(self.signals)

    def get_recent_rejections(self) -> List[Dict[str, Any]]:
        """Get recent rejections."""
        return list(self.rejections)

    def get_recent_pnl(self) -> List[Dict[str, Any]]:
        """Get recent PnL snapshots."""
        return list(self.pnl_snapshots)

    def clear_context(self):
        """Clear all stored context."""
        self.signals.clear()
        self.rejections.clear()
        self.pnl_snapshots.clear()
        self.logger.log_action("clear_context", {})