import redis
from typing import Dict, Any
import json

class RealtimePublisher:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.pubsub = self.redis.pubsub()

    def publish(self, channel: str, data: Dict[str, Any]):
        """Publish data to a Redis channel."""
        try:
            self.redis.publish(channel, json.dumps(data))
        except Exception as e:
            print(f"Error publishing to {channel}: {e}")

    def close(self):
        """Close Redis connection."""
        try:
            self.redis.close()
        except Exception as e:
            print(f"Error closing Redis connection: {e}")