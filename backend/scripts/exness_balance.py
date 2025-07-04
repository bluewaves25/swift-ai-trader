import MetaTrader5 as mt5
import sys
import json

account = sys.argv[1]
password = sys.argv[2]
server = sys.argv[3]

if not mt5.initialize(login=int(account), password=password, server=server):
    print(json.dumps({"error": "MT5 initialization failed"}))
    mt5.shutdown()
    sys.exit()

account_info = mt5.account_info()
if account_info:
    print(json.dumps({"balance": account_info.balance, "currency": account_info.currency}))
else:
    print(json.dumps({"error": "Failed to fetch account info"}))

mt5.shutdown()