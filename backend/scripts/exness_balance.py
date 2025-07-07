import MetaTrader5 as mt5
import sys
import json

def get_balance(account: str, password: str, server: str):
    mt5.initialize()
    if not mt5.login(int(account), password, server):
        return {"error": "MT5 login failed"}
    return {"balance": mt5.account_info().balance}

if __name__ == "__main__":
    account, password, server = sys.argv[1], sys.argv[2], sys.argv[3]
    print(json.dumps(get_balance(account, password, server)))