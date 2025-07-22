#!/usr/bin/env python

import sys
import os
import asyncio
import time
import redis
import json
from datetime import datetime

# ✅ Add root project directory to sys.path once (auto-detects root of project)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ✅ Now all internal modules will load properly
from waves_quant_agi.engine.core.agi_engine import AGIEngine
from waves_quant_agi.engine.core.schema import MarketData

# 🔌 Redis connection
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# 🚀 Start the engine
engine = AGIEngine()
print("🚀 AGI Engine is live (via Redis queue)")
print("[TRADING ENGINE WORKER] Listening for trading jobs on 'market-data' queue.")

def parse_market_data(raw: list) -> list:
    return [
        MarketData(
            timestamp=datetime.fromisoformat(item["timestamp"]),
            symbol=item["symbol"],
            open=item["open"],
            high=item["high"],
            low=item["low"],
            close=item["close"],
            volume=item["volume"]
        ) for item in raw
    ]

# 🔁 Main event loop
last_data_time = time.time()
while True:
    try:
        # Set engine heartbeat
        r.set("engine-heartbeat", datetime.now().isoformat())
        task = r.blpop("market-data", timeout=10)
        if not task:
            if time.time() - last_data_time > 10:
                print("[WARN] No market data received in the last 10 seconds. Check your feeder and Redis.")
            continue

        _, payload = task
        last_data_time = time.time()
        raw_data = json.loads(payload)

        # 📊 Parse + process
        market_data_list = parse_market_data(raw_data)
        for market_data in market_data_list:
            print(f"[ENGINE] Processing market data: {market_data.symbol}")
            trades = engine.process_market_data(market_data)
            r.set("market-result", json.dumps(trades))

    except Exception as e:
        print(f"[ERROR] {e}")
        r.set("market-result", json.dumps({"error": str(e)}))
        continue
