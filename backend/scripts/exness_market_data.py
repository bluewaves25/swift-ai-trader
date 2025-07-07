import MetaTrader5 as mt5
import pandas as pd
import sys
import json

def get_market_data(symbol: str, timeframe: int):
    mt5.initialize()
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
    return pd.DataFrame(rates, columns=["time", "open", "high", "low", "close", "tick_volume"]).to_json()

if __name__ == "__main__":
    symbol, timeframe = sys.argv[1], sys.argv[2]
    print(get_market_data(symbol, int(timeframe)))