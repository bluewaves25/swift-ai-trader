import redis
import time
import json
from typing import Dict, Any, Optional, List
from ..logs.data_feeds_logger import DataFeedsLogger

class DBConnector:
    """Redis-based data connector for data feeds with caching and persistence."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.redis = None
        self.key_prefix = "data_feed:"
        self.logger = DataFeedsLogger("db_connector")
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

    def store(self, data: Dict[str, Any]) -> bool:
        """Store data in Redis with a unique key and error handling."""
        if not self.redis:
            self.logger.log_warning("Redis not connected, attempting to reconnect...")
            self._connect()
            if not self.redis:
                return False
        
        try:
            # Create unique key
            timestamp = data.get('timestamp', time.time())
            symbol = data.get('symbol', 'unknown')
            data_type = data.get('type', 'generic')
            exchange = data.get('exchange', 'unknown')
            
            key = f"{self.key_prefix}{timestamp}:{symbol}:{data_type}:{exchange}"
            
            # Add metadata
            enriched_data = {
                **data,
                "stored_at": time.time(),
                "key": key
            }
            
            # Store in Redis
            self.redis.hset(key, mapping=enriched_data)
            self.redis.expire(key, 86400)  # Expire after 24 hours
            
            # Add to data feed list for tracking
            list_key = f"{self.key_prefix}list:{data_type}"
            self.redis.lpush(list_key, key)
            self.redis.ltrim(list_key, 0, 9999)  # Keep last 10k entries
            
            self.logger.log_metric("data_stored", 1, {
                "symbol": symbol,
                "type": data_type,
                "exchange": exchange
            })
            
            return True
            
        except redis.ConnectionError as e:
            self.logger.log_error(f"Redis connection error: {e}")
            self._connect()
            return False
            
        except Exception as e:
            self.logger.log_error(f"Error storing data: {e}")
            return False

    def retrieve(self, key_pattern: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from Redis by key pattern with error handling."""
        if not self.redis:
            return None
        
        try:
            keys = self.redis.keys(f"{self.key_prefix}{key_pattern}")
            if not keys:
                return None
            
            # Get the most recent key
            key = keys[0]
            data = self.redis.hgetall(key)
            
            if not data:
                return None
            
            # Convert numeric fields
            numeric_fields = {"price", "volume", "timestamp", "sentiment", "slippage", "spread", "liquidity", "strength", "bid", "ask", "high", "low"}
            for k, v in data.items():
                if k in numeric_fields:
                    try:
                        data[k] = float(v)
                    except (ValueError, TypeError):
                        data[k] = 0.0
            
            return data
            
        except Exception as e:
            self.logger.log_error(f"Error retrieving data: {e}")
            return None

    def backfill(self, key_pattern: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Backfill data from Redis for gaps with error handling."""
        if not self.redis:
            return []
        
        try:
            keys = self.redis.keys(f"{self.key_prefix}{key_pattern}")
            keys = sorted(keys, reverse=True)[:limit]  # Get most recent first
            
            data_list = []
            for key in keys:
                try:
                    data = self.redis.hgetall(key)
                    if data:
                        # Convert numeric fields
                        numeric_fields = {"price", "volume", "timestamp", "sentiment", "slippage", "spread", "liquidity", "strength", "bid", "ask", "high", "low"}
                        for k, v in data.items():
                            if k in numeric_fields:
                                try:
                                    data[k] = float(v)
                                except (ValueError, TypeError):
                                    data[k] = 0.0
                        data_list.append(data)
                except Exception as e:
                    self.logger.log_error(f"Error processing key {key}: {e}")
                    continue
            
            self.logger.log_metric("data_backfilled", len(data_list), {"pattern": key_pattern})
            return data_list
            
        except Exception as e:
            self.logger.log_error(f"Error backfilling data: {e}")
            return []

    def get_latest_data(self, symbol: str, data_type: str = "price", exchange: str = None) -> Optional[Dict[str, Any]]:
        """Get the latest data for a specific symbol and type."""
        if not self.redis:
            return None
        
        try:
            pattern = f"*:{symbol}:{data_type}"
            if exchange:
                pattern += f":{exchange}"
            else:
                pattern += ":*"
            
            return self.retrieve(pattern)
            
        except Exception as e:
            self.logger.log_error(f"Error getting latest data for {symbol}: {e}")
            return None

    def get_data_range(self, symbol: str, data_type: str, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """Get data for a specific symbol and time range."""
        if not self.redis:
            return []
        
        try:
            pattern = f"*:{symbol}:{data_type}:*"
            keys = self.redis.keys(f"{self.key_prefix}{pattern}")
            
            data_list = []
            for key in keys:
                try:
                    data = self.redis.hgetall(key)
                    if data and 'timestamp' in data:
                        timestamp = float(data['timestamp'])
                        if start_time <= timestamp <= end_time:
                            # Convert numeric fields
                            numeric_fields = {"price", "volume", "timestamp", "sentiment", "slippage", "spread", "liquidity", "strength", "bid", "ask", "high", "low"}
                            for k, v in data.items():
                                if k in numeric_fields:
                                    try:
                                        data[k] = float(v)
                                    except (ValueError, TypeError):
                                        data[k] = 0.0
                            data_list.append(data)
                except Exception as e:
                    self.logger.log_error(f"Error processing key {key}: {e}")
                    continue
            
            # Sort by timestamp
            data_list.sort(key=lambda x: x.get('timestamp', 0))
            
            self.logger.log_metric("data_range_retrieved", len(data_list), {
                "symbol": symbol,
                "type": data_type,
                "start_time": start_time,
                "end_time": end_time
            })
            
            return data_list
            
        except Exception as e:
            self.logger.log_error(f"Error getting data range for {symbol}: {e}")
            return []

    def cleanup_old_data(self, days: int = 7) -> int:
        """Clean up data older than specified days."""
        if not self.redis:
            return 0
        
        try:
            cutoff_time = time.time() - (days * 86400)
            deleted_count = 0
            
            # Get all data feed keys
            all_keys = self.redis.keys(f"{self.key_prefix}*")
            
            for key in all_keys:
                try:
                    data = self.redis.hgetall(key)
                    if data and 'timestamp' in data:
                        timestamp = float(data['timestamp'])
                        if timestamp < cutoff_time:
                            self.redis.delete(key)
                            deleted_count += 1
                except Exception as e:
                    self.logger.log_error(f"Error processing key {key} for cleanup: {e}")
                    continue
            
            self.logger.log_metric("data_cleaned_up", deleted_count, {"days": days})
            return deleted_count
            
        except Exception as e:
            self.logger.log_error(f"Error cleaning up old data: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self.redis:
            return {"connected": False}
        
        try:
            # Get total keys
            total_keys = len(self.redis.keys(f"{self.key_prefix}*"))
            
            # Get data by type
            data_types = {}
            for key in self.redis.keys(f"{self.key_prefix}list:*"):
                data_type = key.split(":")[-1]
                count = self.redis.llen(key)
                data_types[data_type] = count
            
            return {
                "connected": True,
                "total_keys": total_keys,
                "data_by_type": data_types,
                "host": self.host,
                "port": self.port,
                "db": self.db
            }
            
        except Exception as e:
            self.logger.log_error(f"Error getting stats: {e}")
            return {"connected": False, "error": str(e)}

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