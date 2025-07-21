#!/usr/bin/env python
import sys
import os
import asyncio
import redis
import json
from datetime import datetime
from dotenv import load_dotenv

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

# Symbols to track (with 'm' suffix if available)
SYMBOLS = ["XAUUSDm", "EURUSDm", "GBPUSDm", "USDJPYm", "AUDUSDm", "USDCADm"]

async def fetch_and_publish():
    """Fetch MT5 data for specified symbols and publish to Redis."""
    print("🚀 Starting MT5 market data feeder...")
    while True:
        for symbol in SYMBOLS:
            if not mt5_broker.symbol_exists(symbol):
                print(f"⚠️ Symbol {symbol} not found in MT5, skipping.")
                continue

            rates = mt5_broker.get_market_data(symbol, count=1)
            if rates is not None and len(rates) > 0:
                rate = rates[0]
                market_data = {
                    "timestamp": datetime.fromtimestamp(rate['time']).isoformat(),
                    "symbol": symbol,
                    "open": rate['open'],
                    "high": rate['high'],
                    "low": rate['low'],
                    "close": rate['close'],
                    "volume": rate['tick_volume']
                }
                # Publish to Redis 'market-data' queue
                r.rpush("market-data", json.dumps([market_data]))
                print(f"📊 Published {symbol} data to Redis")
        
        await asyncio.sleep(0.5) # Fetch every 0.5 seconds for HFT

if __name__ == "__main__":
    try:
        asyncio.run(fetch_and_publish())
    except KeyboardInterrupt:
        print("🛑 Feeder stopped.") 