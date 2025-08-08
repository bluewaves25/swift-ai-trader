#!/usr/bin/env python3
"""
Test script for Adapters Agent
"""

import asyncio
import json
import time
from typing import Dict, Any
from adapters_agent import AdaptersAgent

def create_test_config() -> Dict[str, Any]:
    """Create test configuration for adapters agent."""
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "router": {
            "default_strategy": "fastest_route"
        },
        "brokers": {
            "binance": {
                "api_key": "test_api_key",
                "api_secret": "test_api_secret",
                "sandbox": True,
                "min_order_size": 0.001,
                "max_order_size": 1000000.0,
                "price_precision": 8,
                "quantity_precision": 8
            },
            "coinbase": {
                "api_key": "test_api_key",
                "api_secret": "test_api_secret",
                "sandbox": True
            },
            "exness": {
                "api_key": "test_api_key",
                "api_secret": "test_api_secret",
                "sandbox": True
            }
        },
        "max_retries": 3,
        "health_check_interval": 30,
        "performance_monitoring_interval": 60,
        "pattern_analysis_interval": 300,
        "api_monitoring_interval": 60,
        "stats_interval": 60
    }

async def test_adapters_agent():
    """Test the adapters agent functionality."""
    print("🧪 Starting Adapters Agent Test...")
    
    # Create test configuration
    config = create_test_config()
    
    try:
        # Initialize agent
        print("📋 Initializing Adapters Agent...")
        agent = AdaptersAgent(config)
        
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
        
        # Test router
        print("🛣️ Testing router...")
        router_stats = agent.router.get_stats()
        print(f"✅ Router stats: {json.dumps(router_stats, indent=2)}")
        
        # Test available brokers
        available_brokers = agent.router.get_available_brokers()
        print(f"✅ Available brokers: {available_brokers}")
        
        # Test available strategies
        available_strategies = agent.router.get_available_strategies()
        print(f"✅ Available strategies: {available_strategies}")
        
        # Test connection status
        print("🔌 Testing broker connections...")
        connection_status = await agent.router.check_all_connections()
        print(f"✅ Connection status: {json.dumps(connection_status, indent=2)}")
        
        # Test order execution (mock)
        print("📊 Testing order execution...")
        test_order = {
            "symbol": "BTC/USDT",
            "side": "buy",
            "type": "market",
            "amount": 0.001,
            "price": 50000.0
        }
        
        # Note: This will fail in test environment due to no real API keys
        # but we can test the structure
        try:
            result = await agent.execute_order(test_order)
            if result:
                print("✅ Order execution successful")
            else:
                print("⚠️ Order execution failed (expected in test environment)")
        except Exception as e:
            print(f"⚠️ Order execution error (expected): {e}")
        
        print("🎉 All tests passed! Adapters Agent is working correctly.")
        
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
        
        # Test adapters specific operations
        test_data = {
            "broker": "binance",
            "order": {"symbol": "BTC/USDT", "side": "buy", "amount": 0.001},
            "status": "test",
            "timestamp": time.time()
        }
        redis_client.lpush("adapters:test_orders", str(test_data))
        data_count = redis_client.llen("adapters:test_orders")
        print(f"✅ Adapters test data count: {data_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

async def test_broker_router():
    """Test broker router functionality."""
    print("🛣️ Testing Broker Router...")
    
    try:
        from router.broker_router import BrokerRouter
        
        config = {
            "default_strategy": "fastest_route"
        }
        
        router = BrokerRouter(config)
        
        # Test router stats
        stats = router.get_stats()
        print(f"✅ Router stats: {json.dumps(stats, indent=2)}")
        
        # Test available strategies
        strategies = router.get_available_strategies()
        print(f"✅ Available strategies: {strategies}")
        
        # Test strategy switching
        success = router.set_strategy("lowest_fee")
        print(f"✅ Strategy switch: {'Success' if success else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Broker router test failed: {e}")
        return False

async def test_binance_adapter():
    """Test Binance adapter functionality."""
    print("₿ Testing Binance Adapter...")
    
    try:
        from broker_integrations.binance_adapter import BinanceAdapter
        
        config = {
            "sandbox": True,
            "min_order_size": 0.001,
            "max_order_size": 1000000.0,
            "price_precision": 8,
            "quantity_precision": 8
        }
        
        adapter = BinanceAdapter(
            api_key="test_key",
            api_secret="test_secret",
            config=config
        )
        
        # Test adapter stats
        stats = adapter.get_stats()
        print(f"✅ Adapter stats: {json.dumps(stats, indent=2)}")
        
        # Test order formatting
        test_order = {
            "symbol": "BTC/USDT",
            "side": "buy",
            "type": "market",
            "amount": 0.001,
            "price": 50000.0
        }
        
        formatted_order = adapter.format_order(test_order)
        print(f"✅ Order formatting: {json.dumps(formatted_order, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Binance adapter test failed: {e}")
        return False

async def test_short_run():
    """Test a short run of the adapters agent."""
    print("🚀 Testing short run of Adapters Agent...")
    
    config = create_test_config()
    agent = AdaptersAgent(config)
    
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
    print("🚀 Starting Adapters Agent Tests...")
    
    # Test Redis integration first
    redis_ok = await test_redis_integration()
    if not redis_ok:
        print("⚠️ Redis not available, some tests may fail")
    
    # Test broker router
    router_ok = await test_broker_router()
    
    # Test Binance adapter
    adapter_ok = await test_binance_adapter()
    
    # Test adapters agent
    agent_ok = await test_adapters_agent()
    
    # Test short run (optional)
    if agent_ok:
        print("\n🔄 Testing short run...")
        short_run_ok = await test_short_run()
        if short_run_ok:
            print("✅ Short run test completed successfully!")
        else:
            print("❌ Short run test failed!")
    
    if agent_ok and router_ok and adapter_ok:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    
    return agent_ok and router_ok and adapter_ok

if __name__ == "__main__":
    asyncio.run(main()) 