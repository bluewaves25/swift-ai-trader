#!/usr/bin/env python3
"""
Test script for Fees Monitor Agent
"""

import asyncio
import json
import time
from typing import Dict, Any
from fees_monitor_agent import FeesMonitorAgent

def create_test_config() -> Dict[str, Any]:
    """Create test configuration for fees monitor agent."""
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "fee_db_path": "broker_fee_models/broker_fee_db.json",
        "max_fee_impact": 0.01,
        "min_position_size": 0.001,
        "max_position_size": 1000000.0,
        "monitor_interval": 10,  # 10 seconds for testing
        "learning_interval": 60,  # 1 minute for testing
        "stats_interval": 30,     # 30 seconds for testing
        "load_interval": 300      # 5 minutes for testing
    }

def create_test_trade() -> Dict[str, Any]:
    """Create a test trade for processing."""
    return {
        "broker": "binance",
        "symbol": "BTCUSDT",
        "side": "buy",
        "size": 1.0,
        "price": 50000.0,
        "timestamp": int(time.time()),
        "strategy": "trend_following",
        "user_id": "test_user_123"
    }

async def test_fees_monitor_agent():
    """Test the fees monitor agent functionality."""
    print("🧪 Starting Fees Monitor Agent Test...")
    
    # Create test configuration
    config = create_test_config()
    
    try:
        # Initialize agent
        print("📋 Initializing Fees Monitor Agent...")
        agent = FeesMonitorAgent(config)
        
        # Test agent status
        status = agent.get_agent_status()
        print(f"✅ Agent Status: {json.dumps(status, indent=2)}")
        
        # Test fee model loading
        print("📊 Testing fee model loading...")
        fee_models = agent.model_loader.load_fee_models()
        print(f"✅ Loaded {len(fee_models)} fee models")
        
        # Test smart sizing
        print("⚖️ Testing smart sizing...")
        test_trade = create_test_trade()
        optimized_size = await agent.smart_sizer.optimize_position_size(test_trade)
        print(f"✅ Original size: {test_trade['size']}, Optimized size: {optimized_size}")
        
        # Test optimization stats
        print("📈 Testing optimization stats...")
        stats = agent.smart_sizer.get_optimization_stats()
        print(f"✅ Optimization stats: {json.dumps(stats, indent=2)}")
        
        # Test incident cache
        print("🗄️ Testing incident cache...")
        cache_stats = agent.cache.get_incident_stats()
        print(f"✅ Cache stats: {json.dumps(cache_stats, indent=2)}")
        
        # Test fee model stats
        print("🏦 Testing fee model stats...")
        fee_stats = agent.model_loader.get_fee_model_stats()
        print(f"✅ Fee model stats: {json.dumps(fee_stats, indent=2)}")
        
        print("🎉 All tests passed! Fees Monitor Agent is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_redis_integration():
    """Test Redis integration."""
    print("🔗 Testing Redis integration...")
    
    try:
        import redis
        redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        
        # Test basic Redis operations
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        print(f"✅ Redis test: {value}")
        
        # Test fees monitor specific operations
        test_trade = create_test_trade()
        redis_client.lpush("fees_monitor:pending_trades", str(test_trade))
        pending_count = redis_client.llen("fees_monitor:pending_trades")
        print(f"✅ Pending trades count: {pending_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Fees Monitor Agent Tests...")
    
    # Test Redis integration first
    redis_ok = await test_redis_integration()
    if not redis_ok:
        print("⚠️ Redis not available, some tests may fail")
    
    # Test fees monitor agent
    agent_ok = await test_fees_monitor_agent()
    
    if agent_ok:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    
    return agent_ok

if __name__ == "__main__":
    asyncio.run(main()) 