#!/usr/bin/env python3
"""
Redis Mock for development/testing when Redis server is not available
Provides basic in-memory storage that mimics Redis functionality
"""

import json
import time
import threading
from typing import Dict, Any, List, Optional, Union
from collections import defaultdict, deque


class RedisMock:
    """Simple Redis mock using in-memory storage."""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._lists: Dict[str, deque] = defaultdict(deque)
        self._hashes: Dict[str, Dict[str, str]] = defaultdict(dict)
        self._expiry: Dict[str, float] = {}
        self._pubsub_channels: Dict[str, List] = defaultdict(list)
        self._lock = threading.RLock()
        self._connected = True
        
        print("Redis Mock: In-memory Redis mock initialized")
    
    def ping(self) -> bool:
        """Mock ping."""
        return self._connected
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Mock set."""
        with self._lock:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self._data[key] = str(value)
            
            if ex:
                self._expiry[key] = time.time() + ex
            
            return True
    
    def setex(self, key: str, time_seconds: int, value: Any) -> bool:
        """Mock setex."""
        return self.set(key, value, ex=time_seconds)
    
    def get(self, key: str) -> Optional[str]:
        """Mock get."""
        with self._lock:
            # Check expiry
            if key in self._expiry and time.time() > self._expiry[key]:
                self._cleanup_expired_key(key)
                return None
            
            return self._data.get(key)
    
    def delete(self, *keys) -> int:
        """Mock delete."""
        with self._lock:
            count = 0
            for key in keys:
                if key in self._data:
                    del self._data[key]
                    count += 1
                if key in self._lists:
                    del self._lists[key]
                    count += 1
                if key in self._hashes:
                    del self._hashes[key]
                    count += 1
                if key in self._expiry:
                    del self._expiry[key]
            return count
    
    def exists(self, *keys) -> int:
        """Mock exists."""
        with self._lock:
            count = 0
            for key in keys:
                if (key in self._data or key in self._lists or key in self._hashes):
                    # Check expiry
                    if key in self._expiry and time.time() > self._expiry[key]:
                        self._cleanup_expired_key(key)
                    else:
                        count += 1
            return count
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Mock keys - simple pattern matching."""
        with self._lock:
            all_keys = set(self._data.keys()) | set(self._lists.keys()) | set(self._hashes.keys())
            
            if pattern == "*":
                return list(all_keys)
            
            # Simple pattern matching
            if "*" in pattern:
                prefix = pattern.replace("*", "")
                return [key for key in all_keys if key.startswith(prefix)]
            else:
                return [key for key in all_keys if key == pattern]
    
    # List operations
    def lpush(self, key: str, *values) -> int:
        """Mock lpush."""
        with self._lock:
            for value in values:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                self._lists[key].appendleft(str(value))
            return len(self._lists[key])
    
    def rpush(self, key: str, *values) -> int:
        """Mock rpush."""
        with self._lock:
            for value in values:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                self._lists[key].append(str(value))
            return len(self._lists[key])
    
    def lpop(self, key: str) -> Optional[str]:
        """Mock lpop."""
        with self._lock:
            if key in self._lists and self._lists[key]:
                return self._lists[key].popleft()
            return None
    
    def rpop(self, key: str) -> Optional[str]:
        """Mock rpop."""
        with self._lock:
            if key in self._lists and self._lists[key]:
                return self._lists[key].pop()
            return None
    
    def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Mock lrange."""
        with self._lock:
            if key not in self._lists:
                return []
            
            lst = list(self._lists[key])
            if end == -1:
                return lst[start:]
            return lst[start:end+1]
    
    def llen(self, key: str) -> int:
        """Mock llen."""
        with self._lock:
            return len(self._lists.get(key, []))
    
    def lindex(self, key: str, index: int) -> Optional[str]:
        """Mock lindex."""
        with self._lock:
            if key not in self._lists:
                return None
            try:
                return list(self._lists[key])[index]
            except IndexError:
                return None
    
    def ltrim(self, key: str, start: int, end: int) -> bool:
        """Mock ltrim."""
        with self._lock:
            if key in self._lists:
                lst = list(self._lists[key])
                if end == -1:
                    trimmed = lst[start:]
                else:
                    trimmed = lst[start:end+1]
                self._lists[key] = deque(trimmed)
            return True
    
    def lrem(self, key: str, count: int, value: str) -> int:
        """Mock lrem."""
        with self._lock:
            if key not in self._lists:
                return 0
            
            removed = 0
            lst = self._lists[key]
            
            if count == 0:  # Remove all occurrences
                while value in lst:
                    lst.remove(value)
                    removed += 1
            elif count > 0:  # Remove first count occurrences
                for _ in range(count):
                    try:
                        lst.remove(value)
                        removed += 1
                    except ValueError:
                        break
            else:  # Remove last |count| occurrences
                lst_copy = list(lst)
                lst.clear()
                
                for _ in range(abs(count)):
                    try:
                        lst_copy.remove(value)
                        removed += 1
                    except ValueError:
                        break
                
                lst.extend(lst_copy)
            
            return removed
    
    # Hash operations
    def hset(self, key: str, field: str = None, value: str = None, mapping: Dict[str, Any] = None) -> int:
        """Mock hset."""
        with self._lock:
            count = 0
            
            if mapping:
                for k, v in mapping.items():
                    if isinstance(v, (dict, list)):
                        v = json.dumps(v)
                    if k not in self._hashes[key]:
                        count += 1
                    self._hashes[key][k] = str(v)
            
            if field is not None and value is not None:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                if field not in self._hashes[key]:
                    count += 1
                self._hashes[key][field] = str(value)
            
            return count
    
    def hget(self, key: str, field: str) -> Optional[str]:
        """Mock hget."""
        with self._lock:
            return self._hashes.get(key, {}).get(field)
    
    def hgetall(self, key: str) -> Dict[str, str]:
        """Mock hgetall."""
        with self._lock:
            return self._hashes.get(key, {}).copy()
    
    def hdel(self, key: str, *fields) -> int:
        """Mock hdel."""
        with self._lock:
            if key not in self._hashes:
                return 0
            
            count = 0
            for field in fields:
                if field in self._hashes[key]:
                    del self._hashes[key][field]
                    count += 1
            
            return count
    
    def hlen(self, key: str) -> int:
        """Mock hlen."""
        with self._lock:
            return len(self._hashes.get(key, {}))
    
    def hkeys(self, key: str) -> List[str]:
        """Mock hkeys."""
        with self._lock:
            return list(self._hashes.get(key, {}).keys())
    
    def hvals(self, key: str) -> List[str]:
        """Mock hvals."""
        with self._lock:
            return list(self._hashes.get(key, {}).values())
    
    # Pub/Sub operations
    def publish(self, channel: str, message: str) -> int:
        """Mock publish."""
        with self._lock:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            
            # Store for mock subscribers
            self._pubsub_channels[channel].append({
                "type": "message",
                "channel": channel,
                "data": str(message),
                "timestamp": time.time()
            })
            
            # Keep only last 100 messages per channel
            if len(self._pubsub_channels[channel]) > 100:
                self._pubsub_channels[channel] = self._pubsub_channels[channel][-100:]
            
            return 1  # Number of subscribers (mock)
    
    def pubsub(self):
        """Mock pubsub."""
        return MockPubSub(self)
    
    def _cleanup_expired_key(self, key: str):
        """Clean up expired key."""
        if key in self._data:
            del self._data[key]
        if key in self._lists:
            del self._lists[key]
        if key in self._hashes:
            del self._hashes[key]
        if key in self._expiry:
            del self._expiry[key]
    
    def close(self):
        """Mock close."""
        self._connected = False
        print("Redis Mock: Connection closed")


class MockPubSub:
    """Mock pubsub object."""
    
    def __init__(self, redis_mock: RedisMock):
        self._redis = redis_mock
        self._subscribed_channels = set()
    
    def subscribe(self, *channels):
        """Mock subscribe."""
        for channel in channels:
            self._subscribed_channels.add(channel)
    
    def unsubscribe(self, *channels):
        """Mock unsubscribe."""
        for channel in channels:
            self._subscribed_channels.discard(channel)
    
    def get_message(self, timeout=None):
        """Mock get_message."""
        # Return None for simplicity
        return None
    
    def listen(self):
        """Mock listen."""
        while True:
            yield None  # Simplified mock


class AsyncRedisMock:
    """Async wrapper for Redis mock."""
    
    def __init__(self, redis_mock: RedisMock):
        self._redis = redis_mock
    
    async def ping(self) -> bool:
        """Async ping."""
        return self._redis.ping()
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Async set."""
        return self._redis.set(key, value, ex=ex)
    
    async def setex(self, key: str, time_seconds: int, value: Any) -> bool:
        """Async setex."""
        return self._redis.setex(key, time_seconds, value)
    
    async def get(self, key: str) -> Optional[str]:
        """Async get."""
        return self._redis.get(key)
    
    async def delete(self, *keys) -> int:
        """Async delete."""
        return self._redis.delete(*keys)
    
    async def exists(self, *keys) -> int:
        """Async exists."""
        return self._redis.exists(*keys)
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Async keys."""
        return self._redis.keys(pattern)
    
    async def lpush(self, key: str, *values) -> int:
        """Async lpush."""
        return self._redis.lpush(key, *values)
    
    async def rpush(self, key: str, *values) -> int:
        """Async rpush."""
        return self._redis.rpush(key, *values)
    
    async def lpop(self, key: str) -> Optional[str]:
        """Async lpop."""
        return self._redis.lpop(key)
    
    async def rpop(self, key: str) -> Optional[str]:
        """Async rpop."""
        return self._redis.rpop(key)
    
    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Async lrange."""
        return self._redis.lrange(key, start, end)
    
    async def llen(self, key: str) -> int:
        """Async llen."""
        return self._redis.llen(key)
    
    async def lindex(self, key: str, index: int) -> Optional[str]:
        """Async lindex."""
        return self._redis.lindex(key, index)
    
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Async ltrim."""
        return self._redis.ltrim(key, start, end)
    
    async def lrem(self, key: str, count: int, value: str) -> int:
        """Async lrem."""
        return self._redis.lrem(key, count, value)
    
    async def hset(self, key: str, field: str = None, value: str = None, mapping: Dict[str, Any] = None) -> int:
        """Async hset."""
        return self._redis.hset(key, field, value, mapping)
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Async hget."""
        return self._redis.hget(key, field)
    
    async def hgetall(self, key: str) -> Dict[str, str]:
        """Async hgetall."""
        return self._redis.hgetall(key)
    
    async def hdel(self, key: str, *fields) -> int:
        """Async hdel."""
        return self._redis.hdel(key, *fields)
    
    async def publish(self, channel: str, message: str) -> int:
        """Async publish."""
        return self._redis.publish(channel, message)
    
    async def close(self):
        """Async close."""
        self._redis.close()


# Global instance
_global_redis_mock = None

def get_redis_mock():
    """Get global Redis mock instance."""
    global _global_redis_mock
    if _global_redis_mock is None:
        _global_redis_mock = RedisMock()
    return _global_redis_mock

def get_async_redis_mock():
    """Get async Redis mock instance."""
    return AsyncRedisMock(get_redis_mock())