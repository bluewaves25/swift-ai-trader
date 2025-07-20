### engine/core/strategy_manager.py

from typing import Dict, List, Optional
from waves_quant_agi.engine.strategies.base_strategy import BaseStrategy
import logging
from waves_quant_agi.core.models.strategy import Strategy as StrategyModel
from waves_quant_agi.core.database import get_db
from sqlalchemy.future import select
import asyncio

logger = logging.getLogger(__name__)

class StrategyManager:
    """
    📈 StrategyManager: Handles registration, retrieval, update, and execution
    of all trading strategies within the AGI engine. Supports runtime management and DB persistence.
    """

    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        logger.info("Strategy Manager initialized ✅")

    async def register_strategy(self, strategy: BaseStrategy, db=None):
        if strategy.name in self.strategies:
            logger.warning(f"Strategy '{strategy.name}' already registered, skipping")
            return
        self.strategies[strategy.name] = strategy
        logger.info(f"Registered strategy: {strategy.name}")
        # Persist to DB if db session provided
        if db:
            await self._persist_strategy(strategy, db)

    async def remove_strategy(self, strategy_name: str, db=None):
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
            logger.info(f"Removed strategy: {strategy_name}")
            if db:
                await self._remove_strategy_db(strategy_name, db)
        else:
            logger.warning(f"Strategy '{strategy_name}' not found")

    def get_strategy(self, strategy_name: str) -> Optional[BaseStrategy]:
        return self.strategies.get(strategy_name)

    def list_strategies(self) -> List[str]:
        return list(self.strategies.keys())

    async def update_strategy(self, strategy_name: str, config: dict, db=None):
        strat = self.strategies.get(strategy_name)
        if strat:
            strat.config.update(config)
            logger.info(f"Updated config for strategy: {strategy_name}")
            if db:
                await self._update_strategy_db(strategy_name, config, db)
        else:
            logger.warning(f"Strategy '{strategy_name}' not found for update")

    async def run_all(self, market_data):
        results = []
        for name, strategy in self.strategies.items():
            logger.info(f"Running strategy: {name}")
            signal = await strategy.generate_signal(market_data)
            results.append(signal)
        return results

    async def _persist_strategy(self, strategy: BaseStrategy, db):
        # Save strategy config to DB
        db_strategy = StrategyModel(
            id=strategy.name,
            name=strategy.name,
            win_rate=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            max_drawdown=0.0,
            validated=False,
            status="active",
            performance=0.0,
            description=strategy.__doc__ or ""
        )
        db.add(db_strategy)
        await db.commit()

    async def _remove_strategy_db(self, strategy_name: str, db):
        result = await db.execute(select(StrategyModel).where(StrategyModel.name == strategy_name))
        db_strategy = result.scalar_one_or_none()
        if db_strategy:
            await db.delete(db_strategy)
            await db.commit()

    async def _update_strategy_db(self, strategy_name: str, config: dict, db):
        result = await db.execute(select(StrategyModel).where(StrategyModel.name == strategy_name))
        db_strategy = result.scalar_one_or_none()
        if db_strategy:
            db_strategy.status = config.get("status", db_strategy.status)
            db_strategy.description = config.get("description", db_strategy.description)
            await db.commit()
