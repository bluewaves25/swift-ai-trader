import redis
import json
import time
from datetime import datetime
import os

# --- MT5 (Exness) ---
import MetaTrader5 as mt5

# --- Binance ---
import requests

# --- Redis ---
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# --- MT5 Login ---
MT5_LOGIN = int(os.getenv('MT5_LOGIN', ''))
MT5_PASSWORD = os.getenv('MT5_PASSWORD', '')
MT5_SERVER = os.getenv('MT5_SERVER', '')

# --- Binance API ---
BINANCE_SYMBOLS = ['BTCUSDT', 'ETHUSDT']  # Add more as needed
BINANCE_URL = 'https://api.binance.com/api/v3/ticker/price?symbol={}'

# --- Forex/Commodities/Indices symbols ---
MT5_SYMBOLS = ['EURUSDm', 'XAUUSDm', 'US500m', 'GBPUSDm']  # Add more as needed

# --- Connect to MT5 ---
if not mt5.initialize():
    print(f"[ERROR] MT5 initialize failed: {mt5.last_error()}")
    exit(1)
if not mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
    print(f"[ERROR] MT5 login failed: {mt5.last_error()}")
    exit(1)
print("[INFO] Connected to MT5 (Exness)")

def fetch_mt5(symbol):
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        return None
    return {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "open": tick.ask,  # MT5 doesn't provide open/high/low/close in tick, so use ask as proxy
        "high": tick.ask,
        "low": tick.bid,
        "close": tick.last,
        "volume": tick.volume
    }

def fetch_binance(symbol):
    try:
        res = requests.get(BINANCE_URL.format(symbol))
        res.raise_for_status()
        price = float(res.json()['price'])
        return {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": 0  # Binance ticker/price endpoint does not provide volume
        }
    except Exception as e:
        print(f"[ERROR] Binance fetch failed for {symbol}: {e}")
        return None

while True:
    data = []
    # MT5 symbols
    for symbol in MT5_SYMBOLS:
        d = fetch_mt5(symbol)
        if d:
            data.append(d)
    # Binance symbols
    for symbol in BINANCE_SYMBOLS:
        d = fetch_binance(symbol)
        if d:
            data.append(d)
    if data:
        r.lpush('market-data', json.dumps(data))
        print(f"[INFO] Pushed {len(data)} market data points to Redis queue.")
    time.sleep(5) 