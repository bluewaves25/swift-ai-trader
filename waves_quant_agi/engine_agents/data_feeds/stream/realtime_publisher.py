import redis
import json
import time
from typing import Dict, Any, Optional
from ..logs.data_feeds_logger import DataFeedsLogger

class RealtimePublisher:
    """Real-time data publisher with Redis integration."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.redis = None
        self.logger = DataFeedsLogger("realtime_publisher")
        self._connect()

    def _connect(self):
        """Establish Redis connection with retry logic."""
        try:
            self.redis = redis.Redis(
                host=self.host, 
                port=self.port, 
                db=self.db, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis.ping()
            self.logger.log(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            self.logger.log_error(f"Failed to connect to Redis: {e}")
            self.redis = None

    def publish(self, channel: str, data: Dict[str, Any]) -> bool:
        """Publish data to a Redis channel with error handling."""
        if not self.redis:
            self.logger.log_warning("Redis not connected, attempting to reconnect...")
            self._connect()
            if not self.redis:
                return False
        
        try:
            # Add metadata to data
            enriched_data = {
                **data,
                "published_at": time.time(),
                "channel": channel
            }
            
            # Publish to Redis
            result = self.redis.publish(channel, json.dumps(enriched_data))
            
            if result > 0:
                self.logger.log_metric("messages_published", 1, {"channel": channel})
                return True
            else:
                self.logger.log_warning(f"No subscribers for channel: {channel}")
                return False
                
        except redis.ConnectionError as e:
            self.logger.log_error(f"Redis connection error: {e}")
            self._connect()  # Try to reconnect
            return False
            
        except Exception as e:
            self.logger.log_error(f"Error publishing to {channel}: {e}")
            return False

    def publish_batch(self, channel: str, data_list: list) -> int:
        """Publish multiple data points to a Redis channel."""
        if not self.redis:
            self.logger.log_warning("Redis not connected, attempting to reconnect...")
            self._connect()
            if not self.redis:
                return 0
        
        try:
            published_count = 0
            for data in data_list:
                if self.publish(channel, data):
                    published_count += 1
            
            self.logger.log_metric("batch_published", published_count, {
                "channel": channel,
                "total_items": len(data_list)
            })
            
            return published_count
            
        except Exception as e:
            self.logger.log_error(f"Error publishing batch to {channel}: {e}")
            return 0

    def get_subscriber_count(self, channel: str) -> int:
        """Get number of subscribers for a channel."""
        if not self.redis:
            return 0
        
        try:
            return self.redis.pubsub_numsub(channel)[0][1]
        except Exception as e:
            self.logger.log_error(f"Error getting subscriber count for {channel}: {e}")
            return 0

    def close(self):
        """Close Redis connection gracefully."""
        try:
            if self.redis:
                self.redis.close()
                self.logger.log("Redis connection closed")
        except Exception as e:
            self.logger.log_error(f"Error closing Redis connection: {e}")

    def is_connected(self) -> bool:
        """Check if Redis connection is active."""
        if not self.redis:
            return False
        
        try:
            self.redis.ping()
            return True
        except Exception:
            return False