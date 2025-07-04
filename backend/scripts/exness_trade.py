import MetaTrader5 as mt5
import sys
import json

account = sys.argv[1]
password = sys.argv[2]
server = sys.argv[3]
trade = json.loads(sys.argv[4])

if not mt5.initialize(login=int(account), password=password, server=server):
    print(json.dumps({"error": "MT5 initialization failed"}))
    mt5.shutdown()
    sys.exit()

request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": trade["symbol"],
    "volume": float(trade["volume"]),
    "type": mt5.ORDER_TYPE_BUY if trade["side"] == "buy" else mt5.ORDER_TYPE_SELL,
    "price": float(trade["price"]),
    "sl": float(trade.get("stop_loss", 0)),
    "tp": float(trade.get("take_profit", 0)),
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

result = mt5.order_send(request)
print(json.dumps({"result": result.comment if result else "Failed"}))
mt5.shutdown()