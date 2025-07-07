from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from strategy_core.validator import TradeValidator
from strategy_core.risk_manager import RiskManager
from supabase import Client
from db.supabase_client import get_supabase_client
from prometheus_client import Counter, Histogram
from datetime import datetime
from src.auth_middleware import get_current_user
import ccxt.async_support as ccxt
import MetaTrader5 as mt5
import os
from python_dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
trade_counter = Counter("trades_executed", "Number of trades executed", ["broker"])
trade_latency = Histogram("trade_execution_latency", "Trade execution latency", ["broker"])

class Trade(BaseModel):
    symbol: str
    side: str
    volume: float
    price: float
    stop_loss: float = 0.0
    take_profit: float = 0.0

class BinanceBroker:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv("BINANCE_API_KEY"),
            'secret': os.getenv("BINANCE_SECRET"),
            'enableRateLimit': True
        })

    async def execute_trade(self, trade: Trade):
        try:
            order_type = 'limit'
            params = {}
            if trade.stop_loss > 0:
                params['stopLossPrice'] = trade.stop_loss
            if trade.take_profit > 0:
                params['takeProfitPrice'] = trade.take_profit
            order = await self.exchange.create_order(
                symbol=trade.symbol,
                type=order_type,
                side=trade.side,
                amount=trade.volume,
                price=trade.price,
                params=params
            )
            logger.info(f"Binance trade executed: {order}")
            return {"order_id": order['id'], "status": order['status'], "filled": order['filled']}
        except Exception as e:
            logger.error(f"Binance trade failed: {str(e)}")
            raise
        finally:
            await self.exchange.close()

class ExnessBroker:
    def __init__(self):
        if not mt5.initialize(login=int(os.getenv("EXNESS_ACCOUNT")), password=os.getenv("EXNESS_PASSWORD"), server=os.getenv("EXNESS_SERVER")):
            raise Exception("MT5 initialization failed")

    async def execute_trade(self, trade: Trade, account: str):
        try:
            symbol_info = mt5.symbol_info(trade.symbol)
            if not symbol_info:
                raise Exception(f"Symbol {trade.symbol} not found")
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": trade.symbol,
                "volume": trade.volume,
                "type": mt5.ORDER_TYPE_BUY if trade.side == "buy" else mt5.ORDER_TYPE_SELL,
                "price": trade.price,
                "sl": trade.stop_loss,
                "tp": trade.take_profit,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
            }
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                raise Exception(f"Exness trade failed: {result.comment}")
            logger.info(f"Exness trade executed: {result}")
            return {"order_id": result.order, "status": "filled", "filled": trade.volume}
        except Exception as e:
            logger.error(f"Exness trade failed: {str(e)}")
            raise
        finally:
            mt5.shutdown()

@router.post("/{broker}/{account}")
async def execute_trade(
    broker: str,
    account: str,
    trade: Trade,
    supabase: Client = Depends(get_supabase_client),
    current_user: dict = Depends(get_current_user)
):
    validator = TradeValidator()
    risk_manager = RiskManager()
    async with trade_latency.labels(broker).time():
        score = await validator.validate_trade(trade, broker)
        min_score = 90 if broker == "binance" else 95
        if score < min_score:
            raise HTTPException(status_code=400, detail=f"Trade confidence too low: {score}")
        risk_check = await risk_manager.check_risk(trade, broker, account)
        if not risk_check["approved"]:
            raise HTTPException(status_code=400, detail=risk_check["reason"])
        try:
            pair = await supabase.table("trading_pairs").select("id").eq("symbol", trade.symbol).execute()
            if not pair.data:
                raise HTTPException(status_code=400, detail=f"Trading pair {trade.symbol} not found")
            pair_id = pair.data[0]["id"]
            
            if broker == "binance":
                result = await BinanceBroker().execute_trade(trade)
            elif broker == "exness":
                result = await ExnessBroker().execute_trade(trade, account)
            else:
                raise HTTPException(status_code=400, detail="Unsupported broker")
            trade_counter.labels(broker).inc()
            await supabase.table("trades").insert({
                "user_id": current_user["id"],
                "pair_id": pair_id,
                "broker": broker,
                "account_number": account,
                **trade.dict(),
                "timestamp": datetime.utcnow().isoformat(),
                "order_id": result["order_id"],
                "status": result["status"]
            }).execute()
            await risk_manager.update_post_trade(trade, result)
            return result
        except Exception as e:
            await risk_manager.handle_loss(trade, broker, str(e), current_user["id"])
            raise HTTPException(status_code=500, detail=str(e))