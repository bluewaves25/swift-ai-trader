# engine/core/schema.py

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
from enum import Enum

class MarketRegime(Enum):
    TRENDING = "trending"
    RANGING = "ranging"
    VOLATILE = "volatile"
    CRASH = "crash"
    RECOVERY = "recovery"

@dataclass
class MarketData:
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
