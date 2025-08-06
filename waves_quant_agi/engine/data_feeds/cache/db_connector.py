import redis
from typing import Dict, Any, Optional

class DBConnector:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.key_prefix = "data_feed:"

    def store(self, data: Dict[str, Any]):
        """Store data in Redis with a unique key."""
        try:
            key = f"{self.key_prefix}{data['timestamp']}:{data.get('symbol', 'unknown')}:{data.get('type', 'generic')}"
            self.redis.hset(key, mapping=data)
            self.redis.expire(key, 86400)  # Expire after 24 hours
        except Exception as e:
            print(f"Error storing data in Redis: {e}")

    def retrieve(self, key_pattern: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from Redis by key pattern."""
        try:
            keys = self.redis.keys(f"{self.key_prefix}{key_pattern}")
            if not keys:
                return None
            data = self.redis.hgetall(keys[0])
            return {k: float(v) if k in {"price", "volume", "timestamp", "sentiment", "slippage", "spread", "liquidity", "strength"} else v for k, v in data.items()}
        except Exception as e:
            print(f"Error retrieving data from Redis: {e}")
            return None

    def backfill(self, key_pattern: str, limit: int = 100) -> list:
        """Backfill data from Redis for gaps."""
        try:
            keys = self.redis.keys(f"{self.key_prefix}{key_pattern}")[:limit]
            return [self.redis.hgetall(key) for key in keys]
        except Exception as e:
            print(f"Error backfilling data: {e}")
            return []