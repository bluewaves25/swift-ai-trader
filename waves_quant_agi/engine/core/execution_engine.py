# engine/core/execution_engine.py

import logging
import os
from typing import List
from waves_quant_agi.engine.core.signal import Signal
from waves_quant_agi.engine.core.schema import MarketData  
from waves_quant_agi.engine.brokers.mt5_plugin import MT5Broker
from waves_quant_agi.engine.brokers.binance_plugin import BinanceBroker
from waves_quant_agi.engine.brokers.base_broker import BaseBroker
from dotenv import load_dotenv
import MetaTrader5 as mt5
from waves_quant_agi.core.models.transaction import Trade, TradeStatus
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

logger = logging.getLogger(__name__)
load_dotenv()

class ExecutionEngine:
    """
    ⚙️ Multi-Broker Execution Engine with Smart Routing.
    - MT5 handles: forex, metals, indices.
    - Binance handles: spot crypto.
    """

    def __init__(self):
        self.executed_orders = []

        self.mt5_broker = None
        self.binance_broker = None

        if os.getenv("USE_MT5", "false").lower() == "true":
            try:
                self.mt5_broker = MT5Broker(
                    login=int(os.getenv("MT5_LOGIN")),
                    password=os.getenv("MT5_PASSWORD"),
                    server=os.getenv("MT5_SERVER")
                )
                self.mt5_broker.connect()
                logger.info("✅ MT5 broker connected")
            except Exception as e:
                logger.warning(f"⚠️ Failed to connect MT5 broker: {e}")

        if os.getenv("USE_BINANCE", "false").lower() == "true":
            try:
                self.binance_broker = BinanceBroker(
                    api_key=os.getenv("BINANCE_API_KEY"),
                    api_secret=os.getenv("BINANCE_API_SECRET")
                )
                logger.info("✅ Binance broker activated")
            except Exception as e:
                logger.warning(f"⚠️ Failed to init Binance broker: {e}")

    async def execute_signals(self, signals: List[Signal]) -> List[dict]:
        executed_trades = []

        for signal in signals:
            broker = self._select_broker(signal.symbol)

            if broker is None:
                logger.warning(f"⚠️ No broker assigned for {signal.symbol}")
                continue

            try:
                trade = await self._execute_order_with_broker(signal, broker, db, user_id)
                if trade:
                    executed_trades.append(trade)
            except Exception as e:
                logger.error(f"❌ Execution failed for {signal.symbol} via {type(broker).__name__}: {e}")

        return executed_trades

    def _select_broker(self, symbol: str) -> BaseBroker | None:
        """
        Select broker based on asset class inferred from symbol.
        """
        symbol = symbol.upper()

        if symbol.endswith("USD") or symbol in ["XAUUSD", "XAGUSD", "WTI", "BRENT", "US500", "NAS100", "GER30"]:
            return self.mt5_broker if self.mt5_broker else None
        elif symbol.endswith("USDT") or symbol.endswith("BTC") or symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
            return self.binance_broker if self.binance_broker else None
        else:
            return None

    async def _execute_order_with_broker(self, signal: Signal, broker: BaseBroker, db: AsyncSession, user_id: str) -> dict:
        logger.info(f"🚀 Executing {signal.action.upper()} {signal.symbol} x{signal.size} via {type(broker).__name__}")

        result = broker.place_order(
            symbol=signal.symbol,
            side=signal.action.lower(),
            volume=signal.size,
            price=0.0,
            order_type="market"
        )

        executed_price = await self._get_live_price(signal.symbol, broker)
        execution_result = {
            "broker": type(broker).__name__,
            "strategy": signal.strategy_name,
            "symbol": signal.symbol,
            "action": signal.action,
            "size": signal.size,
            "confidence": signal.confidence,
            "executed_price": executed_price,
            "timestamp": signal.timestamp.isoformat(),
            "metadata": signal.metadata,
            "order_id": result.get("order_id") if isinstance(result, dict) else None
        }

        # Persist trade to DB
        await self._save_trade_to_db(signal, executed_price, user_id, db)

        self.executed_orders.append(execution_result)
        return execution_result

    async def _save_trade_to_db(self, signal: Signal, executed_price: float, user_id: str, db: AsyncSession):
        trade = Trade(
            id=str(uuid.uuid4()),
            user_id=user_id,
            symbol=signal.symbol,
            side=signal.action.lower(),
            volume=signal.size,
            price=executed_price,
            pnl=0.0,  # Update with actual PnL if available
            strategy=signal.strategy_name,
            status=TradeStatus.CLOSED,
        )
        db.add(trade)
        await db.commit()
        await db.refresh(trade)

    async def _get_live_price(self, symbol: str, broker: BaseBroker) -> float:
        if isinstance(broker, MT5Broker):
            tick = mt5.symbol_info_tick(symbol)
            return round(tick.ask if tick else 0.0, 5)
        elif isinstance(broker, BinanceBroker):
            return round(broker.get_price(symbol), 5)
        return 0.0

    def get_executed_orders(self) -> List[dict]:
        return self.executed_orders
