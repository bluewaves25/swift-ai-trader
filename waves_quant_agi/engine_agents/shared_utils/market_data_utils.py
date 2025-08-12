#!/usr/bin/env python3
"""
Shared Market Data Utilities
Replaces duplicate market data methods across all agents.
"""

import json
import time
from typing import Dict, Any, Optional
from .redis_connector import SharedRedisConnector

class MarketDataUtils:
    """Shared market data utilities for all agents."""
    
    def __init__(self, redis_conn: SharedRedisConnector):
        self.redis_conn = redis_conn
    
    def get_current_market_data(self, symbol: str = "BTCUSD") -> Dict[str, Any]:
        """Get current market data from Redis."""
        try:
            market_data = self.redis_conn.get_latest_market_data(symbol)
            
            if not market_data:
                # Return empty dict instead of hardcoded test data
                return {}
            
            return market_data
            
        except Exception as e:
            print(f"Error getting market data: {e}")
            return {}
    
    def get_performance_data(self, agent_name: str) -> Dict[str, Any]:
        """Get performance data for a specific agent."""
        try:
            performance_data = self.redis_conn.hgetall(f"performance:{agent_name}")
            
            if not performance_data:
                # Return empty dict instead of hardcoded test data
                return {}
            
            # Convert bytes to strings and parse JSON
            parsed_data = {}
            for key, value in performance_data.items():
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                if isinstance(value, bytes):
                    try:
                        parsed_data[key] = json.loads(value.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        parsed_data[key] = value.decode('utf-8')
                else:
                    parsed_data[key] = value
            
            return parsed_data
            
        except Exception as e:
            print(f"Error getting performance data: {e}")
            return {}

# Global instance
_market_data_utils: Optional[MarketDataUtils] = None

def get_market_data_utils(redis_conn: SharedRedisConnector) -> MarketDataUtils:
    """Get the global market data utils instance."""
    global _market_data_utils
    
    if _market_data_utils is None:
        _market_data_utils = MarketDataUtils(redis_conn)
    
    return _market_data_utils
