# engine/core/signal.py

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class Signal:
    strategy_name: str
    symbol: str
    action: str  # "BUY", "SELL", "HOLD"
    confidence: float
    size: float
    timestamp: datetime
    metadata: Dict[str, Any]
