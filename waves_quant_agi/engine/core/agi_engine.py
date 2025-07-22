import asyncio
import numpy as np
from typing import Dict, List, Any
import logging
import importlib
import pkgutil
import os
from datetime import datetime

from waves_quant_agi.engine.strategies.base_strategy import BaseStrategy
from waves_quant_agi.engine.intelligence.online_learner import OnlineLearner
from waves_quant_agi.engine.core.risk_manager import RiskManager
from waves_quant_agi.engine.core.execution_engine import ExecutionEngine
from waves_quant_agi.engine.core.schema import MarketData
from waves_quant_agi.engine.core.strategy_manager import StrategyManager
from waves_quant_agi.engine.strategies.aggressive_scalper import AggressiveScalper
from waves_quant_agi.core.models.transaction import Trade
from waves_quant_agi.core.database import SessionLocal
from waves_quant_agi.engine.feeders.mt5_feeder import SYMBOLS

logger = logging.getLogger(__name__)

class AGIEngine:
    """
    The central AGI engine of the platform.
    - Manages multiple strategies and integrates them with other core components.
    """
    def __init__(self, sandbox_mode=False):
        self.db_session = SessionLocal()
        self.strategy_manager = StrategyManager()
        self.risk_manager = RiskManager()
        # Correctly initialize ExecutionEngine with dependencies
        self.execution_engine = ExecutionEngine(self.db_session, self.risk_manager)
        self.online_learner = OnlineLearner()
        
        # Add an AggressiveScalper for every symbol
        for symbol in SYMBOLS:
            self.strategy_manager.add_strategy(AggressiveScalper(symbol=symbol, strategy_id=f"aggressive_scalper_{symbol}"))
        
        self.market_regime = "trending" 
        self.last_learning_update = datetime.now()

        logger.info(f"AGIEngine initialized (sandbox_mode={sandbox_mode})")

    def process_market_data(self, market_data: MarketData):
        """
        Main processing loop for the engine.
        - Updates risk manager with new data.
        - Gets signals from all strategies.
        - Executes the highest priority signal.
        - Periodically learns from past trades.
        """
        logger.info(f"[AGIEngine] Received market data: {market_data.symbol} {market_data.close}")
        # 1. Update risk manager with latest market data
        self.risk_manager.update_market_data(market_data)

        # 2. Get signals from all strategies
        signals = self.strategy_manager.get_all_signals(market_data)
        logger.info(f"[AGIEngine] Signals generated: {signals}")
        
        if not signals:
            logger.info(f"[AGIEngine] No signals generated for {market_data.symbol}")
            return

        # 3. Prioritize signals and execute the best one
        highest_priority_signal = max(signals, key=lambda s: s.confidence)
        logger.info(f"[AGIEngine] Executing signal: {highest_priority_signal.action} {highest_priority_signal.symbol}")
        try:
            asyncio.run(self.execution_engine.execute_signals([highest_priority_signal]))
        except Exception as e:
            logger.error(f"[AGIEngine] Error executing signal: {e}")

        # 4. Periodically update strategy weights from recent trades
        if (datetime.now() - self.last_learning_update).seconds > 60:
             # Fetch recent trades from Supabase
            recent_trades = self.db_session.query(Trade).order_by(Trade.timestamp.desc()).limit(100).all()
            if recent_trades:
                new_weights = self.online_learner.update_weights(recent_trades, self.strategy_manager.strategy_weights)
                self.strategy_manager.update_strategy_weights(new_weights)
            self.last_learning_update = datetime.now()
        
    def get_status(self):
        return {
            'performance_metrics': {},
            'current_regime': self.market_regime,
            'volatility_level': self.risk_manager.atr,
            'explain_log': [],
            'strategies': list(self.strategy_manager.strategies.keys()),
            'sandbox_strategies': [],
        }
