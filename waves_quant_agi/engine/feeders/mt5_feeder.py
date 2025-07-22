#!/usr/bin/env python
import sys
import os
import asyncio
import redis
import json
from datetime import datetime
from dotenv import load_dotenv
import MetaTrader5 as mt5

# Add project root to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from waves_quant_agi.engine.brokers.mt5_plugin import MT5Broker

# Load env vars
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Redis connection
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# MT5 Connection
mt5_login = int(os.getenv("MT5_LOGIN"))
mt5_password = os.getenv("MT5_PASSWORD")
mt5_server = os.getenv("MT5_SERVER")
mt5_broker = MT5Broker(login=mt5_login, password=mt5_password, server=mt5_server)
mt5_broker.connect()

# Set the symbols to only XAUUSDm for testing
SYMBOLS = ["XAUUSDm"]

print(f"[MT5 FEEDER] Tracking symbols: {SYMBOLS}")
print("[MT5 FEEDER] Publishing to Redis queue: 'market-data'")
print("[MT5 FEEDER] Listing all available symbols in MT5 Market Watch:")
print(mt5_broker.get_all_symbols())

# Print all available symbols in Market Watch for debugging
if mt5.initialize():
    symbols = mt5.symbols_get()
    print("Available symbols in MT5 Market Watch:")
    for s in symbols:
        print(s.name)
    mt5.shutdown()
else:
    print("MT5 initialization failed")

async def fetch_and_publish():
    print("🚀 Starting MT5 market data feeder...")
    while True:
        for symbol in SYMBOLS:
            # Try to select the symbol
            selected = mt5.symbol_select(symbol, True)
            info = mt5.symbol_info(symbol)
            print(f"Debug: symbol={symbol}, selected={selected}, info={info}")

            if not selected or info is None:
                print(f"⚠️ Symbol {symbol} not found or not selectable in MT5, skipping.")
                continue

            try:
                if not mt5_broker.symbol_exists(symbol):
                    print(f"⚠️ Symbol {symbol} not found in MT5, skipping.")
                    continue
                rates = mt5_broker.get_market_data(symbol, count=1)
                if rates is not None and len(rates) > 0:
                    rate = rates[0]
                    market_data = {
                        "timestamp": datetime.fromtimestamp(float(rate['time'])).isoformat(),
                        "symbol": str(symbol),
                        "open": float(rate['open']),
                        "high": float(rate['high']),
                        "low": float(rate['low']),
                        "close": float(rate['close']),
                        "volume": float(rate['tick_volume'])
                    }
                    # Publish to Redis 'market-data' queue
                    try:
                        r.rpush("market-data", json.dumps([market_data]))
                        print(f"📊 Published {symbol} data to Redis")
                    except Exception as re:
                        print(f"[ERROR] Failed to publish {symbol} to Redis: {re}")
                else:
                    print(f"[WARN] No data for {symbol} (rates is None or empty)")
            except Exception as e:
                print(f"[ERROR] Exception for symbol {symbol}: {e}")
        await asyncio.sleep(0.5) # Fetch every 0.5 seconds for HFT

if __name__ == "__main__":
    try:
        asyncio.run(fetch_and_publish())
    except Exception as e:
        print(f"[FATAL] Feeder crashed: {e}") 