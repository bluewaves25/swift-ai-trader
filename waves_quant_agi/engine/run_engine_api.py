# engine/run_engine_api.py

import time
import redis
import json
from engine.core.agi_engine import AGIEngine
from engine.core.schema import MarketData
from datetime import datetime

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
engine = AGIEngine()

print("🚀 AGI Engine is live (via Redis queue)")

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

while True:
    task = r.blpop("market-data", timeout=0)
    if task:
        _, payload = task
        try:
            raw_data = json.loads(payload)
            data = parse_market_data(raw_data)
            trades = asyncio.run(engine.process_market_data(data))
            r.set("market-result", json.dumps(trades))
        except Exception as e:
            r.set("market-result", json.dumps({"error": str(e)}))
