# Trading Module - CONSOLIDATED FROM CORE AGENT
# All trading functionality moved from Core Agent to Strategy Engine Agent

from .signal_processor import TradingSignalProcessor
from .flow_manager import TradingFlowManager
from .logic_executor import TradingLogicExecutor

from .interfaces.trade_model import TradeCommand
from .interfaces.agent_io import TradingAgentIO

from .pipeline.execution_pipeline import TradingExecutionPipeline

from .memory.trading_context import TradingContext

__all__ = [
    'TradingSignalProcessor',
    'TradingFlowManager',
    'TradingLogicExecutor',
    'TradeCommand',
    'TradingAgentIO',
    'TradingExecutionPipeline',
    'TradingContext'
]
