import asyncio
import numpy as np
from typing import Dict, List, Any
import logging
import importlib
import pkgutil
import os

from waves_quant_agi.engine.strategies.base_strategy import BaseStrategy
from waves_quant_agi.engine.intelligence.attention_engine import AttentionEngine
from waves_quant_agi.engine.intelligence.chaos_amplifier import ChaosAmplifier
from waves_quant_agi.engine.intelligence.online_learner import OnlineLearner
from waves_quant_agi.engine.validation.strategy_validator import StrategyValidator
from waves_quant_agi.engine.core.risk_manager import RiskManager
from waves_quant_agi.engine.core.execution_engine import ExecutionEngine
from waves_quant_agi.engine.core.schema import MarketData, MarketRegime
from waves_quant_agi.engine.core.signal import Signal

logger = logging.getLogger(__name__)

class AGIEngine:
    def __init__(self, sandbox_mode=False):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.sandbox_strategies: Dict[str, BaseStrategy] = {}
        self.attention_engine = AttentionEngine()
        self.chaos_amplifier = ChaosAmplifier()
        self.online_learner = OnlineLearner()
        self.validator = StrategyValidator()
        self.risk_manager = RiskManager()
        self.execution_engine = ExecutionEngine()
        self.sandbox_mode = sandbox_mode

        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'current_regime': MarketRegime.RANGING,
            'strategy_performance': {},  # Track per-strategy performance
        }

        self.market_data: Dict[str, List[MarketData]] = {}
        self.current_regime = MarketRegime.RANGING
        self.volatility_level = 0.0
        self.explain_log: List[Dict[str, Any]] = []

        logger.info(f"AGI Engine initialized (sandbox_mode={sandbox_mode})")
        if os.getenv("DISCOVER_STRATEGIES", "false").lower() == "true":
            self._auto_discover_strategies()

    def _auto_discover_strategies(self):
        # Auto-discover and register all strategies in engine/strategies/
        import waves_quant_agi.engine.strategies
        strategy_path = os.path.dirname(waves_quant_agi.engine.strategies.__file__)
        for _, module_name, _ in pkgutil.iter_modules([strategy_path]):
            if module_name == "base_strategy":
                continue
            try:
                module = importlib.import_module(f"waves_quant_agi.engine.strategies.{module_name}")
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, type) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
                        instance = obj()
                        if getattr(instance, "sandbox", False):
                            self.sandbox_strategies[instance.name] = instance
                            logger.info(f"[SANDBOX] Registered strategy: {instance.name}")
                        else:
                            self.strategies[instance.name] = instance
                            logger.info(f"Registered strategy: {instance.name}")
            except Exception as e:
                logger.warning(f"Failed to load strategy {module_name}: {e}")

    def register_strategy(self, strategy: BaseStrategy, sandbox=False):
        if sandbox:
            self.sandbox_strategies[strategy.name] = strategy
            logger.info(f"[SANDBOX] Registered strategy: {strategy.name}")
        else:
            self.strategies[strategy.name] = strategy
            logger.info(f"Registered strategy: {strategy.name}")

    async def process_market_data(self, data: List[MarketData]):
        for tick in data:
            self.market_data.setdefault(tick.symbol, []).append(tick)
            if len(self.market_data[tick.symbol]) > 1000:
                self.market_data[tick.symbol] = self.market_data[tick.symbol][-1000:]

        await self._detect_regime()
        # Meta-controller: select/weight strategies based on performance and regime
        selected_strategies = self._select_strategies()
        signals = await self._generate_signals(data, selected_strategies)
        weighted = await self.attention_engine.apply_attention(signals, self.current_regime, self.volatility_level)
        amplified = await self.chaos_amplifier.amplify_signals(weighted, self.volatility_level)
        risk_adjusted = await self.risk_manager.adjust_signals(amplified, self.performance_metrics)
        executed = await self.execution_engine.execute_signals(risk_adjusted)
        await self._update_performance(executed, selected_strategies)
        await self.online_learner.learn_from_trades(executed)
        # Sandbox mode: run sandbox strategies in shadow mode
        if self.sandbox_mode and self.sandbox_strategies:
            await self._run_sandbox(data)
        return executed

    def _select_strategies(self):
        # Meta-controller: select/weight strategies based on regime and recent performance
        # For now, select all; can be improved to select top-N or weight by win rate
        regime = self.current_regime
        perf = self.performance_metrics.get('strategy_performance', {})
        # Example: select top 2 strategies for current regime
        sorted_strats = sorted(self.strategies.values(), key=lambda s: perf.get(s.name, {}).get('win_rate', 0), reverse=True)
        selected = sorted_strats[:2] if len(sorted_strats) > 2 else sorted_strats
        logger.info(f"[META] Selected strategies for regime {regime}: {[s.name for s in selected]}")
        self.explain_log.append({
            'event': 'strategy_selection',
            'regime': str(regime),
            'selected': [s.name for s in selected],
        })
        return selected

    async def _run_sandbox(self, data):
        for strategy in self.sandbox_strategies.values():
            try:
                result = await strategy.generate_signals(data)
                logger.info(f"[SANDBOX] {strategy.name} signals: {result}")
            except Exception as e:
                logger.warning(f"[SANDBOX] {strategy.name} failed: {e}")

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

    async def _generate_signals(self, data: List[MarketData], strategies: List[BaseStrategy]) -> List[Signal]:
        signals = []
        for strategy in strategies:
            result = await strategy.generate_signals(data)
            if result:
                signals.extend(result)
        return signals

    async def _update_performance(self, trades: List[Dict[str, Any]], strategies: List[BaseStrategy]):
        for trade in trades:
            self.performance_metrics['total_trades'] += 1
            self.performance_metrics['total_pnl'] += trade.get('pnl', 0.0)
            if trade.get('pnl', 0.0) > 0:
                self.performance_metrics['winning_trades'] += 1
            # Track per-strategy performance
            strat = trade.get('strategy')
            if strat:
                perf = self.performance_metrics['strategy_performance'].setdefault(strat, {'trades': 0, 'wins': 0, 'pnl': 0.0})
                perf['trades'] += 1
                perf['pnl'] += trade.get('pnl', 0.0)
                if trade.get('pnl', 0.0) > 0:
                    perf['wins'] += 1
                perf['win_rate'] = perf['wins'] / perf['trades'] if perf['trades'] else 0.0
        total = self.performance_metrics['total_trades']
        wins = self.performance_metrics['winning_trades']
        self.performance_metrics['win_rate'] = wins / total if total else 0.0
        self.explain_log.append({
            'event': 'performance_update',
            'metrics': self.performance_metrics.copy(),
        })

    def get_status(self):
        return {
            'performance_metrics': self.performance_metrics,
            'current_regime': str(self.current_regime),
            'volatility_level': self.volatility_level,
            'explain_log': self.explain_log[-10:],  # Last 10 events
            'strategies': list(self.strategies.keys()),
            'sandbox_strategies': list(self.sandbox_strategies.keys()),
        }
