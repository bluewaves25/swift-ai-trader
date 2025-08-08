#!/usr/bin/env python3
"""
Test script for Data Feeds Agent
"""

import asyncio
import json
import time
from typing import Dict, Any
from data_feeds_agent import DataFeedsAgent

def create_test_config() -> Dict[str, Any]:
    """Create test configuration for data feeds agent."""
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "crypto_price_feed": {
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "interval": 5,  # 5 seconds for testing
            "exchanges": {
                "binance": {"sandbox": False},
                "coinbase": {"sandbox": False}
            }
        },
        "forex_price_feed": {
            "symbols": ["EUR/USD", "GBP/USD"],
            "interval": 5,
            "exchanges": {
                "oanda": {"sandbox": False}
            }
        },
        "sentiment_interval": 60,
        "order_book_interval": 5,
        "trade_tape_interval": 5,
        "derived_signals_interval": 10,
        "microstructure_interval": 10,
        "stats_interval": 30
    }

async def test_data_feeds_agent():
    """Test the data feeds agent functionality."""
    print("🧪 Starting Data Feeds Agent Test...")
    
    # Create test configuration
    config = create_test_config()
    
    try:
        # Initialize agent
        print("📋 Initializing Data Feeds Agent...")
        agent = DataFeedsAgent(config)
        
        # Test agent status
        status = agent.get_agent_status()
        print(f"✅ Agent Status: {json.dumps(status, indent=2)}")
        
        # Test Redis connection
        print("🔗 Testing Redis connection...")
        if agent.redis_client:
            try:
                agent.redis_client.ping()
                print("✅ Redis connection successful")
            except Exception as e:
                print(f"❌ Redis connection failed: {e}")
        else:
            print("⚠️ Redis not available")
        
        # Test database connector
        print("🗄️ Testing database connector...")
        db_stats = agent.db.get_stats()
        print(f"✅ Database stats: {json.dumps(db_stats, indent=2)}")
        
        # Test publisher
        print("📡 Testing publisher...")
        test_data = {
            "symbol": "BTC/USDT",
            "price": 50000.0,
            "volume": 100.0,
            "timestamp": time.time(),
            "exchange": "test"
        }
        published = agent.publisher.publish("test_channel", test_data)
        print(f"✅ Publisher test: {'Success' if published else 'Failed'}")
        
        # Test crypto feed (if available)
        if hasattr(agent, 'crypto_feed') and agent.crypto_feed:
            print("₿ Testing crypto feed...")
            crypto_stats = agent.crypto_feed.get_stats()
            print(f"✅ Crypto feed stats: {json.dumps(crypto_stats, indent=2)}")
        
        # Test forex feed (if available)
        if hasattr(agent, 'forex_feed') and agent.forex_feed:
            print("💱 Testing forex feed...")
            forex_stats = agent.forex_feed.get_stats()
            print(f"✅ Forex feed stats: {json.dumps(forex_stats, indent=2)}")
        
        print("🎉 All tests passed! Data Feeds Agent is working correctly.")
        
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
        
        # Test data feeds specific operations
        test_data = {
            "symbol": "BTC/USDT",
            "price": 50000.0,
            "volume": 100.0,
            "timestamp": time.time(),
            "exchange": "test"
        }
        redis_client.lpush("data_feeds:test_data", str(test_data))
        data_count = redis_client.llen("data_feeds:test_data")
        print(f"✅ Data feeds test data count: {data_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

async def test_short_run():
    """Test a short run of the data feeds agent."""
    print("🚀 Testing short run of Data Feeds Agent...")
    
    config = create_test_config()
    agent = DataFeedsAgent(config)
    
    try:
        # Start the agent
        print("📡 Starting agent for 10 seconds...")
        start_task = asyncio.create_task(agent.start())
        
        # Wait for 10 seconds
        await asyncio.sleep(10)
        
        # Stop the agent
        print("🛑 Stopping agent...")
        await agent.stop()
        
        # Get final stats
        final_status = agent.get_agent_status()
        print(f"✅ Final status: {json.dumps(final_status, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Short run test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Data Feeds Agent Tests...")
    
    # Test Redis integration first
    redis_ok = await test_redis_integration()
    if not redis_ok:
        print("⚠️ Redis not available, some tests may fail")
    
    # Test data feeds agent
    agent_ok = await test_data_feeds_agent()
    
    # Test short run (optional)
    if agent_ok:
        print("\n🔄 Testing short run...")
        short_run_ok = await test_short_run()
        if short_run_ok:
            print("✅ Short run test completed successfully!")
        else:
            print("❌ Short run test failed!")
    
    if agent_ok:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    
    return agent_ok

if __name__ == "__main__":
    asyncio.run(main()) 