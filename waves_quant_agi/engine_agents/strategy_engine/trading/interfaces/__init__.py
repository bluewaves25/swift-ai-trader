# Trading Interfaces - CONSOLIDATED FROM CORE AGENT
# All trading interfaces moved from Core Agent to Strategy Engine Agent

from .trade_model import TradeCommand
from .agent_io import TradingAgentIO

__all__ = [
    'TradeCommand',
    'TradingAgentIO'
]
