import ccxt.async_support as ccxt
import MetaTrader5 as mt5
import os
from python_dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceBroker:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv("BINANCE_API_KEY"),
            'secret': os.getenv("BINANCE_SECRET"),
            'enableRateLimit': True
        })

    async def execute_trade(self, trade):
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

    async def withdraw(self, currency: str, amount: float, address: str):
        try:
            withdrawal = await self.exchange.withdraw(
                code=currency,
                amount=amount,
                address=address
            )
            logger.info(f"Binance withdrawal: {withdrawal}")
            return withdrawal
        except Exception as e:
            logger.error(f"Binance withdrawal failed: {str(e)}")
            raise
        finally:
            await self.exchange.close()

class ExnessBroker:
    def __init__(self):
        if not mt5.initialize(login=int(os.getenv("EXNESS_ACCOUNT")), password=os.getenv("EXNESS_PASSWORD"), server=os.getenv("EXNESS_SERVER")):
            raise Exception("MT5 initialization failed")

    async def execute_trade(self, trade, account: str):
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

    async def request_withdrawal(self, amount: float, address: str):
        try:
            # Note: Exness MT5 does not support programmatic withdrawals; manual process required
            logger.warning(f"Exness withdrawal request for {amount} to {address} must be processed manually via Exness portal")
            return {"status": "pending", "message": "Manual withdrawal required"}
        except Exception as e:
            logger.error(f"Exness withdrawal failed: {str(e)}")
            raise