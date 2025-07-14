import asyncio
import numpy as np
from typing import Dict, List, Any
import logging

from engine.strategies.base_strategy import BaseStrategy
from engine.intelligence.attention_engine import AttentionEngine
from engine.intelligence.chaos_amplifier import ChaosAmplifier
from engine.intelligence.online_learner import OnlineLearner
from engine.validation.strategy_validator import StrategyValidator
from engine.core.risk_manager import RiskManager
from engine.core.execution_engine import ExecutionEngine
from engine.core.schema import MarketData, MarketRegime
from engine.core.signal import Signal

logger = logging.getLogger(__name__)

class AGIEngine:
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.attention_engine = AttentionEngine()
        self.chaos_amplifier = ChaosAmplifier()
        self.online_learner = OnlineLearner()
        self.validator = StrategyValidator()
        self.risk_manager = RiskManager()
        self.execution_engine = ExecutionEngine()

        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'current_regime': MarketRegime.RANGING
        }

        self.market_data: Dict[str, List[MarketData]] = {}
        self.current_regime = MarketRegime.RANGING
        self.volatility_level = 0.0

        logger.info("AGI Engine initialized")

    def register_strategy(self, strategy: BaseStrategy):
        self.strategies[strategy.name] = strategy
        logger.info(f"Registered strategy: {strategy.name}")

    async def process_market_data(self, data: List[MarketData]):
        for tick in data:
            self.market_data.setdefault(tick.symbol, []).append(tick)
            if len(self.market_data[tick.symbol]) > 1000:
                self.market_data[tick.symbol] = self.market_data[tick.symbol][-1000:]

        await self._detect_regime()
        signals = await self._generate_signals(data)
        weighted = await self.attention_engine.apply_attention(signals, self.current_regime, self.volatility_level)
        amplified = await self.chaos_amplifier.amplify_signals(weighted, self.volatility_level)
        risk_adjusted = await self.risk_manager.adjust_signals(amplified, self.performance_metrics)
        executed = await self.execution_engine.execute_signals(risk_adjusted)
        await self._update_performance(executed)
        await self.online_learner.learn_from_trades(executed)
        return executed

    async def _detect_regime(self):
        recent_data = [tick for data in self.market_data.values() if len(data) >= 20 for tick in data[-20:]]
        if not recent_data:
            return
        prices = [tick.close for tick in recent_data]
        returns = np.diff(np.log(prices))
        volatility = np.std(returns) * np.sqrt(252)
        self.volatility_level = volatility

        if volatility > 0.4:
            self.current_regime = MarketRegime.CRASH
        elif volatility > 0.25:
            self.current_regime = MarketRegime.VOLATILE
        elif volatility > 0.15:
            self.current_regime = MarketRegime.TRENDING
        elif volatility < 0.05:
            self.current_regime = MarketRegime.RANGING
        else:
            self.current_regime = MarketRegime.RECOVERY

    async def _generate_signals(self, data: List[MarketData]) -> List[Signal]:
        signals = []
        for strategy in self.strategies.values():
            result = await strategy.generate_signals(data)
            if result:
                signals.extend(result)
        return signals

    async def _update_performance(self, trades: List[Dict[str, Any]]):
        for trade in trades:
            self.performance_metrics['total_trades'] += 1
            self.performance_metrics['total_pnl'] += trade.get('pnl', 0.0)
            if trade.get('pnl', 0.0) > 0:
                self.performance_metrics['winning_trades'] += 1
        total = self.performance_metrics['total_trades']
        wins = self.performance_metrics['winning_trades']
        self.performance_metrics['win_rate'] = wins / total if total else 0.0
