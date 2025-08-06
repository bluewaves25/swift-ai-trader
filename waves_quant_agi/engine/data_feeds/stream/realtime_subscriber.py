import redis
from typing import Dict, Any, Callable, Optional
import json
import asyncio

class RealtimeSubscriber:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.running = False

    async def subscribe(self, channels: list, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to Redis channels and process messages with callback."""
        try:
            self.pubsub.subscribe(*channels)
            self.running = True
            for message in self.pubsub.listen():
                if not self.running:
                    break
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        callback(data)
                    except Exception as e:
                        print(f"Error processing message: {e}")
                await asyncio.sleep(0.01)  # Prevent blocking
        except Exception as e:
            print(f"Error subscribing to channels {channels}: {e}")

    def stop(self):
        """Stop subscription."""
        self.running = False
        try:
            self.pubsub.unsubscribe()
        except Exception as e:
            print(f"Error unsubscribing: {e}")

    def close(self):
        """Close Redis connection."""
        try:
            self.redis.close()
        except Exception as e:
            print(f"Error closing Redis connection: {e}")