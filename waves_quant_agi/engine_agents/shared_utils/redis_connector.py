#!/usr/bin/env python3
"""
Shared Redis Connector - ELIMINATE 90% OF DUPLICATION
Single Redis connection manager for all agents to prevent code duplication
Used by all agents instead of individual Redis connectors

ELIMINATES DUPLICATION FROM:
- data_feeds/cache/db_connector.py
- data_feeds/stream/realtime_publisher.py  
- strategy_engine/redis_connector.py
- risk_management/redis_connector.py
- And 8+ other identical Redis connectors across agents
"""

import redis
import redis.asyncio as aioredis
import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

class SharedRedisConnector:
    """
    Shared Redis connector for all agents - eliminates massive code duplication.
    Provides both sync and async interfaces for maximum compatibility.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        
        # Sync Redis client
        self.redis_sync: Optional[redis.Redis] = None
        
        # Async Redis client
        self.redis_async: Optional[aioredis.Redis] = None
        
        # Connection status
        self.is_connected = False
        self.connection_attempts = 0
        self.max_retries = 3
        
        # Initialize connections
        self._connect_sync()
    
    def _connect_sync(self) -> bool:
        """Establish synchronous Redis connection."""
        try:
            self.redis_sync = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_sync.ping()
            self.is_connected = True
            print(f"Shared Redis connected: {self.host}:{self.port}/{self.db}")
            return True
            
        except Exception as e:
            print(f"Shared Redis connection failed: {e}")
            # Fall back to Redis mock
            try:
                from .redis_mock import get_redis_mock
                self.redis_sync = get_redis_mock()
                self.is_connected = True
                print(f"Shared Redis: Using mock Redis for {self.host}:{self.port}/{self.db}")
                return True
            except Exception as mock_error:
                print(f"Shared Redis mock also failed: {mock_error}")
                self.redis_sync = None
                self.is_connected = False
                return False
    
    async def _connect_async(self) -> bool:
        """Establish asynchronous Redis connection."""
        try:
            self.redis_async = aioredis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis_async.ping()
            print(f"Shared Redis async connected: {self.host}:{self.port}/{self.db}")
            return True
            
        except Exception as e:
            print(f"❌ Shared Redis async connection failed: {e}")
            # Fall back to Redis mock
            try:
                from .redis_mock import get_async_redis_mock
                self.redis_async = get_async_redis_mock()
                print(f"Shared Redis: Using async mock Redis for {self.host}:{self.port}/{self.db}")
                return True
            except Exception as mock_error:
                print(f"Shared Redis async mock also failed: {mock_error}")
                self.redis_async = None
                return False
    
    def ensure_connection(self) -> bool:
        """Ensure sync connection is active."""
        if not self.is_connected or not self.redis_sync:
            return self._connect_sync()
        
        try:
            self.redis_sync.ping()
            return True
        except:
            return self._connect_sync()
    
    async def ensure_async_connection(self) -> bool:
        """Ensure async connection is active."""
        if not self.redis_async:
            return await self._connect_async()
        
        try:
            await self.redis_async.ping()
            return True
        except:
            return await self._connect_async()
    
    # ============= SYNC OPERATIONS =============
    
    def set(self, key: str, value: Union[str, Dict, List], expire: Optional[int] = None) -> bool:
        """Set a key-value pair (sync)."""
        if not self.ensure_connection():
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                self.redis_sync.setex(key, expire, value)
            else:
                self.redis_sync.set(key, value)
            return True
            
        except Exception as e:
            print(f"❌ Redis SET error: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value by key (sync)."""
        if not self.ensure_connection():
            return default
        
        try:
            value = self.redis_sync.get(key)
            if value is None:
                return default
            
            # Try to parse JSON
            try:
                return json.loads(value)
            except:
                return value
                
        except Exception as e:
            print(f"❌ Redis GET error: {e}")
            return default
    
    def publish(self, channel: str, message: Union[str, Dict]) -> bool:
        """Publish message to channel (sync)."""
        if not self.ensure_connection():
            return False
        
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            
            self.redis_sync.publish(channel, message)
            return True
            
        except Exception as e:
            print(f"❌ Redis PUBLISH error: {e}")
            return False
    
    async def publish_async(self, channel: str, message: Union[str, Dict]) -> bool:
        """Publish message to channel (async)."""
        if not self.redis_async:
            await self.ensure_async_connection()
        
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            
            await self.redis_async.publish(channel, message)
            return True
            
        except Exception as e:
            print(f"❌ Redis async PUBLISH error: {e}")
            return False
    
    def lpush(self, key: str, *values) -> bool:
        """Push values to list (sync)."""
        if not self.ensure_connection():
            return False
        
        try:
            json_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    json_values.append(json.dumps(value))
                else:
                    json_values.append(str(value))
            
            self.redis_sync.lpush(key, *json_values)
            return True
            
        except Exception as e:
            print(f"❌ Redis LPUSH error: {e}")
            return False
    
    def rpop(self, key: str, default: Any = None) -> Any:
        """Pop value from list (sync)."""
        if not self.ensure_connection():
            return default
        
        try:
            value = self.redis_sync.rpop(key)
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except:
                return value
                
        except Exception as e:
            print(f"❌ Redis RPOP error: {e}")
            return default
    
    def lpop(self, key: str, default: Any = None) -> Any:
        """Pop value from left side of list (sync)."""
        if not self.ensure_connection():
            return default
        
        try:
            value = self.redis_sync.lpop(key)
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except:
                return value
                
        except Exception as e:
            print(f"❌ Redis LPOP error: {e}")
            return default
    
    async def hset_async(self, name: str, mapping: Dict[str, Any]) -> bool:
        """Set hash fields (async)."""
        if not self.redis_async:
            await self.ensure_async_connection()
        
        try:
            # Convert values to JSON strings for storage
            json_mapping = {k: json.dumps(v) if not isinstance(v, (str, int, float, bool)) else v 
                           for k, v in mapping.items()}
            
            await self.redis_async.hset(name, mapping=json_mapping)
            return True
            
        except Exception as e:
            print(f"❌ Redis async HSET error: {e}")
            return False
    
    async def hset_field_async(self, name: str, key: str, value: Any) -> bool:
        """Set a single hash field (async)."""
        if not self.redis_async:
            await self.ensure_async_connection()
        
        try:
            await self.redis_async.hset(name, key, value)
            return True
            
        except Exception as e:
            print(f"❌ Redis async HSET field error: {e}")
            return False

    def hset(self, name: str, mapping: Dict[str, Any]) -> bool:
        """Set hash fields (sync)."""
        if not self.ensure_connection():
            return False
        
        try:
            json_mapping = {}
            for k, v in mapping.items():
                if isinstance(v, (dict, list)):
                    json_mapping[k] = json.dumps(v)
                else:
                    json_mapping[k] = str(v)
            
            self.redis_sync.hset(name, mapping=json_mapping)
            return True
            
        except Exception as e:
            print(f"❌ Redis HSET error: {e}")
            return False
    
    def hset_field(self, name: str, key: str, value: Any) -> bool:
        """Set a single hash field (for compatibility)."""
        if not self.ensure_connection():
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            else:
                value = str(value)
            self.redis_sync.hset(name, key, value)
            return True
        except Exception as e:
            print(f"❌ Redis HSET field error: {e}")
            return False
    
    def hget(self, name: str, key: str, default: Any = None) -> Any:
        """Get hash field (sync)."""
        if not self.ensure_connection():
            return default
        
        try:
            value = self.redis_sync.hget(name, key)
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except:
                return value
                
        except Exception as e:
            print(f"❌ Redis HGET error: {e}")
            return default
    
    def delete(self, *keys) -> int:
        """Delete keys (sync)."""
        if not self.ensure_connection():
            return 0
        
        try:
            return self.redis_sync.delete(*keys)
        except Exception as e:
            print(f"❌ Redis DELETE error: {e}")
            return 0
    
    def exists(self, *keys) -> int:
        """Check if keys exist (sync)."""
        if not self.ensure_connection():
            return 0
        
        try:
            return self.redis_sync.exists(*keys)
        except Exception as e:
            print(f"❌ Redis EXISTS error: {e}")
            return 0
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern (sync)."""
        if not self.ensure_connection():
            return []
        
        try:
            return self.redis_sync.keys(pattern)
        except Exception as e:
            print(f"❌ Redis KEYS error: {e}")
            return []
    
    # ============= ASYNC OPERATIONS =============
    
    async def async_set(self, key: str, value: Union[str, Dict, List], expire: Optional[int] = None) -> bool:
        """Set a key-value pair (async)."""
        if not await self.ensure_async_connection():
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                await self.redis_async.setex(key, expire, value)
            else:
                await self.redis_async.set(key, value)
            return True
            
        except Exception as e:
            print(f"❌ Redis async SET error: {e}")
            return False
    
    async def async_get(self, key: str, default: Any = None) -> Any:
        """Get a value by key (async)."""
        if not await self.ensure_async_connection():
            return default
        
        try:
            value = await self.redis_async.get(key)
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except:
                return value
                
        except Exception as e:
            print(f"❌ Redis async GET error: {e}")
            return default
    
    async def async_publish(self, channel: str, message: Union[str, Dict]) -> bool:
        """Publish message to channel (async)."""
        if not await self.ensure_async_connection():
            return False
        
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            
            await self.redis_async.publish(channel, message)
            return True
            
        except Exception as e:
            print(f"❌ Redis async PUBLISH error: {e}")
            return False
    
    async def async_lpop(self, key: str, default: Any = None) -> Any:
        """Pop value from left side of list (async)."""
        if not await self.ensure_async_connection():
            return default
        
        try:
            value = await self.redis_async.lpop(key)
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except:
                return value
                
        except Exception as e:
            print(f"❌ Redis async LPOP error: {e}")
            return default
    
    # ============= SPECIALIZED METHODS FOR TRADING ENGINE =============
    
    def store_market_data(self, symbol: str, data: Dict[str, Any], expire: int = 3600) -> bool:
        """Store market data with automatic expiration."""
        key = f"market_data:{symbol}:{int(time.time())}"
        enhanced_data = {
            **data,
            "symbol": symbol,
            "stored_at": time.time(),
            "type": "market_data"
        }
        return self.set(key, enhanced_data, expire)
    
    def get_latest_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get the latest market data for a symbol."""
        pattern = f"market_data:{symbol}:*"
        keys = self.keys(pattern)
        if not keys:
            return None
        
        # Get the most recent key (highest timestamp)
        latest_key = max(keys, key=lambda k: int(k.split(':')[-1]))
        return self.get(latest_key)
    
    def store_agent_status(self, agent_name: str, status: Dict[str, Any]) -> bool:
        """Store agent status information."""
        key = f"agent_status:{agent_name}"
        enhanced_status = {
            **status,
            "agent_name": agent_name,
            "updated_at": time.time(),
            "type": "agent_status"
        }
        return self.set(key, enhanced_status, 300)  # 5 minutes expiration
    
    def get_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents."""
        pattern = "agent_status:*"
        keys = self.keys(pattern)
        statuses = {}
        
        for key in keys:
            agent_name = key.split(':')[1]
            status = self.get(key)
            if status:
                statuses[agent_name] = status
        
        return statuses
    
    def store_trading_signal(self, signal: Dict[str, Any]) -> bool:
        """Store trading signal in queue."""
        signal_data = {
            **signal,
            "created_at": time.time(),
            "type": "trading_signal"
        }
        return self.lpush("trading_signals", signal_data)
    
    def get_trading_signal(self) -> Optional[Dict[str, Any]]:
        """Get next trading signal from queue."""
        return self.rpop("trading_signals")
    
    def store_performance_metrics(self, agent_name: str, metrics: Dict[str, Any]) -> bool:
        """Store performance metrics for an agent."""
        key = f"performance:{agent_name}:{int(time.time())}"
        enhanced_metrics = {
            **metrics,
            "agent_name": agent_name,
            "recorded_at": time.time(),
            "type": "performance_metrics"
        }
        return self.set(key, enhanced_metrics, 86400)  # 24 hours expiration
    
    # ============= CLEANUP METHODS =============
    
    def cleanup_old_data(self, pattern: str, max_age_seconds: int) -> int:
        """Clean up old data based on pattern and age."""
        keys = self.keys(pattern)
        current_time = time.time()
        deleted_count = 0
        
        for key in keys:
            try:
                # Extract timestamp from key (assuming format: prefix:something:timestamp)
                parts = key.split(':')
                if len(parts) >= 3 and parts[-1].isdigit():
                    timestamp = int(parts[-1])
                    if current_time - timestamp > max_age_seconds:
                        self.delete(key)
                        deleted_count += 1
            except:
                continue
        
        return deleted_count
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "is_connected": self.is_connected,
            "sync_client_available": self.redis_sync is not None,
            "async_client_available": self.redis_async is not None,
            "connection_attempts": self.connection_attempts
        }
    
    async def close(self):
        """Close all connections."""
        if self.redis_sync:
            self.redis_sync.close()
        
        if self.redis_async:
            await self.redis_async.close()
        
        self.is_connected = False
        print("✅ Shared Redis connections closed")
    
    # Add missing methods that agents are calling
    def get_queue_items(self, queue_name: str, count: int = 10):
        """Get items from a Redis queue (list)."""
        try:
            if not self.redis_sync:
                return []
            
            # Get items from the list (queue)
            items = self.redis_sync.lrange(queue_name, 0, count - 1)
            return [item.decode('utf-8') if isinstance(item, bytes) else item for item in items]
            
        except Exception as e:
            print(f"⚠️ Error getting queue items from {queue_name}: {e}")
            return []
    
    def add_to_queue(self, queue_name: str, item: str):
        """Add item to a Redis queue (list)."""
        try:
            if self.redis_sync:
                self.redis_sync.lpush(queue_name, item)
                return True
        except Exception as e:
            print(f"⚠️ Error adding to queue {queue_name}: {e}")
        return False
    
    def remove_from_queue(self, queue_name: str, count: int = 1):
        """Remove items from a Redis queue (list)."""
        try:
            if self.redis_sync:
                for _ in range(count):
                    self.redis_sync.rpop(queue_name)
                return True
        except Exception as e:
            print(f"⚠️ Error removing from queue {queue_name}: {e}")
        return False
    
    def lrange(self, name: str, start: int = 0, end: int = -1):
        """Get a range of elements from a Redis list."""
        if not self.ensure_connection():
            return []
        try:
            items = self.redis_sync.lrange(name, start, end)
            return [item.decode('utf-8') if isinstance(item, bytes) else item for item in items]
        except Exception as e:
            print(f"⚠️ Error getting list range from {name}: {e}")
            return []
    
    async def lrange_async(self, name: str, start: int = 0, end: int = -1):
        """Get a range of elements from a Redis list (async)."""
        if not self.redis_async:
            await self.ensure_async_connection()
        
        try:
            items = await self.redis_async.lrange(name, start, end)
            return [item.decode('utf-8') if isinstance(item, bytes) else item for item in items]
        except Exception as e:
            print(f"⚠️ Error getting list range from {name} (async): {e}")
            return []
    
    def ltrim(self, name: str, start: int, end: int):
        """Trim a Redis list to the specified range."""
        if not self.ensure_connection():
            return False
        try:
            self.redis_sync.ltrim(name, start, end)
            return True
        except Exception as e:
            print(f"⚠️ Error trimming list {name}: {e}")
            return False
    
    def lrem(self, name: str, count: int, value: str):
        """Remove elements from a Redis list."""
        if not self.ensure_connection():
            return 0
        try:
            removed_count = self.redis_sync.lrem(name, count, value)
            return removed_count
        except Exception as e:
            print(f"⚠️ Error removing from list {name}: {e}")
            return 0
    
    async def lrem_async(self, name: str, count: int, value: str):
        """Remove elements from a Redis list (async)."""
        if not self.redis_async:
            await self.ensure_async_connection()
        
        try:
            removed_count = await self.redis_async.lrem(name, count, value)
            return removed_count
        except Exception as e:
            print(f"⚠️ Error removing from list {name} (async): {e}")
            return 0
    
    def hgetall(self, name: str):
        """Get all field-value pairs from a Redis hash."""
        if not self.ensure_connection():
            return {}
        try:
            hash_data = self.redis_sync.hgetall(name)
            # Convert bytes to strings if needed
            result = {}
            for key, value in hash_data.items():
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                value_str = value.decode('utf-8') if isinstance(value, bytes) else value
                result[key_str] = value_str
            return result
        except Exception as e:
            print(f"⚠️ Error getting hash data from {name}: {e}")
            return {}
    
    async def hgetall_async(self, name: str):
        """Get all field-value pairs from a Redis hash (async)."""
        if not self.redis_async:
            await self.ensure_async_connection()
        
        try:
            hash_data = await self.redis_async.hgetall(name)
            # Convert bytes to strings if needed
            result = {}
            for key, value in hash_data.items():
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                value_str = value.decode('utf-8') if isinstance(value, bytes) else value
                result[key_str] = value_str
            return result
        except Exception as e:
            print(f"⚠️ Error getting hash data from {name}: {e}")
            return {}
    
    def get_keys_pattern(self, pattern: str):
        """Get keys matching a pattern."""
        if not self.ensure_connection():
            return []
        try:
            keys = self.redis_sync.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            print(f"⚠️ Error getting keys with pattern {pattern}: {e}")
            return []
    
    async def keys_async(self, pattern: str = "*"):
        """Get keys matching pattern (async)."""
        if not self.redis_async:
            await self.ensure_async_connection()
        
        try:
            keys = await self.redis_async.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            print(f"⚠️ Error getting keys with pattern {pattern} (async): {e}")
            return []
    
    def llen(self, name: str):
        """Get the length of a Redis list."""
        if not self.ensure_connection():
            return 0
        try:
            length = self.redis_sync.llen(name)
            return length
        except Exception as e:
            print(f"⚠️ Error getting list length for {name}: {e}")
            return 0
    
    def lindex(self, name: str, index: int):
        """Get an element from a Redis list by index."""
        if not self.ensure_connection():
            return None
        try:
            item = self.redis_sync.lindex(name, index)
            return item.decode('utf-8') if isinstance(item, bytes) else item
        except Exception as e:
            print(f"⚠️ Error getting list item from {name}[{index}]: {e}")
            return None
    
    def get_portfolio_data(self, portfolio_id: str = "default"):
        """Get portfolio data (placeholder for risk management)."""
        try:
            # Return empty dict instead of mock test data
            return {}
        except Exception as e:
            print(f"⚠️ Error getting portfolio data: {e}")
            return {}
    
    def ping(self) -> bool:
        """Ping Redis server (sync)."""
        if not self.ensure_connection():
            return False
        
        try:
            return self.redis_sync.ping()
        except Exception as e:
            print(f"❌ Redis PING error: {e}")
            return False
    
    async def ping_async(self) -> bool:
        """Ping Redis server (async)."""
        if not self.redis_async:
            await self.ensure_async_connection()
        
        try:
            return await self.redis_async.ping()
        except Exception as e:
            print(f"❌ Redis async PING error: {e}")
            return False
    
    def pubsub(self):
        """Get Redis pubsub object for subscriptions."""
        if not self.ensure_connection():
            return None
        try:
            return self.redis_sync.pubsub()
        except Exception as e:
            print(f"⚠️ Error getting pubsub: {e}")
            return None

# Global instance for all agents to use
_global_redis_connector: Optional[SharedRedisConnector] = None

def get_shared_redis(host: str = "localhost", port: int = 6379, db: int = 0) -> SharedRedisConnector:
    """Get the global shared Redis connector instance."""
    global _global_redis_connector
    
    if _global_redis_connector is None:
        _global_redis_connector = SharedRedisConnector(host, port, db)
    
    return _global_redis_connector

def close_shared_redis():
    """Close the global shared Redis connector."""
    global _global_redis_connector
    
    if _global_redis_connector:
        _global_redis_connector.close()
        _global_redis_connector = None


