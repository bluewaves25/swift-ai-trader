#!/usr/bin/env python3
"""
Connection Manager - Centralized connection management
Eliminates duplicate Redis connections across all modules
Provides connection pooling and failover capabilities
"""

import os
import redis
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

class ConnectionManager:
    """Centralized connection manager for Redis and other services."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_pool = None
        self.redis_client = None
        self.connection_status = "disconnected"
        self.retry_count = 0
        self.max_retries = 5
        
        # Initialize Redis connection
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection pool."""
        try:
            self.redis_pool = redis.ConnectionPool(
                host=os.getenv('REDIS_HOST', self.config.get('redis_host', 'localhost')),
                port=int(os.getenv('REDIS_PORT', self.config.get('redis_port', 6379))),
                db=int(os.getenv('REDIS_DB', self.config.get('redis_db', 0))),
                max_connections=50,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Test connection
            self.redis_client.ping()
            self.connection_status = "connected"
            self.retry_count = 0
            
        except Exception as e:
            self.connection_status = "failed"
            print(f"Redis connection failed: {e}")
    
    def get_redis_client(self) -> redis.Redis:
        """Get Redis client instance."""
        if self.connection_status != "connected":
            self._initialize_redis()
        return self.redis_client
    
    async def health_check(self) -> Dict[str, Any]:
        """Check connection health."""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return {
                    "status": "healthy",
                    "connection": "connected",
                    "timestamp": asyncio.get_event_loop().time()
                }
        except Exception as e:
            self.connection_status = "failed"
            return {
                "status": "unhealthy",
                "connection": "failed",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    @asynccontextmanager
    async def get_redis_connection(self):
        """Context manager for Redis operations with error handling."""
        try:
            client = self.get_redis_client()
            yield client
        except Exception as e:
            self.connection_status = "failed"
            raise e
    
    def close_connections(self):
        """Close all connections."""
        if self.redis_pool:
            self.redis_pool.disconnect()
        self.connection_status = "disconnected"
