#!/usr/bin/env python3
"""
Test script for Execution Agent
Tests both Python bridge and training module functionality.
"""

import asyncio
import json
import time
from typing import Dict, Any
from python_bridge import ExecutionBridge
from learning_layer.internal.training_module import TrainingModule

def create_test_config() -> Dict[str, Any]:
    """Create test configuration for execution agent."""
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "signal_processing_interval": 1,
        "training": {
            "accuracy_threshold": 0.85,
            "min_training_samples": 10,
            "retrain_interval": 3600,
            "model_update_threshold": 0.02
        }
    }

async def test_execution_bridge():
    """Test the execution bridge functionality."""
    print("🚀 Starting Execution Bridge Test...")
    
    # Create test configuration
    config = create_test_config()
    
    try:
        # Initialize bridge
        print("📋 Initializing Execution Bridge...")
        bridge = ExecutionBridge(config)
        
        # Test bridge status
        status = await bridge.get_bridge_status()
        print(f"✅ Bridge Status: {json.dumps(status, indent=2)}")
        
        # Test Redis connection
        print("🔗 Testing Redis connection...")
        if bridge.redis_client:
            try:
                bridge.redis_client.ping()
                print("✅ Redis connection successful")
            except Exception as e:
                print(f"❌ Redis connection failed: {e}")
        else:
            print("⚠️ Redis not available")
        
        # Test signal sending
        print("📡 Testing signal sending...")
        test_signal = {
            "symbol": "BTC/USD",
            "signal": "BUY",
            "size": 0.1,
            "expected_price": 50000.0
        }
        
        success = await bridge.send_signal(test_signal)
        if success:
            print("✅ Signal sent successfully")
        else:
            print("❌ Signal sending failed")
        
        # Test invalid signal
        print("🚫 Testing invalid signal rejection...")
        invalid_signal = {
            "symbol": "BTC/USD",
            "signal": "INVALID",
            "size": -1.0
        }
        
        success = await bridge.send_signal(invalid_signal)
        if not success:
            print("✅ Invalid signal correctly rejected")
        else:
            print("❌ Invalid signal should have been rejected")
        
        print("🎉 Execution Bridge tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_training_module():
    """Test the training module functionality."""
    print("🧠 Starting Training Module Test...")
    
    try:
        # Create test configuration
        config = create_test_config()["training"]
        
        # Initialize training module
        print("📋 Initializing Training Module...")
        training_module = TrainingModule(config)
        
        # Create test training data
        print("📊 Creating test training data...")
        import pandas as pd
        import numpy as np
        
        test_data = pd.DataFrame({
            "symbol": ["BTC/USD", "ETH/USD", "BTC/USD", "ETH/USD", "BTC/USD"],
            "execution_time": [0.001, 0.002, 0.0015, 0.003, 0.0012],
            "slippage": [0.0001, 0.0002, 0.00015, 0.0003, 0.00012],
            "volume": [0.1, 0.2, 0.15, 0.3, 0.12],
            "price": [50000, 3000, 50100, 3010, 50050],
            "market_condition": ["normal", "volatile", "normal", "volatile", "normal"]
        })
        
        # Test model training
        print("🏋️ Testing model training...")
        models = await training_module.train_execution_model(test_data)
        
        if models:
            print(f"✅ Successfully trained {len(models)} models")
            for model in models:
                print(f"   - {model.get('symbol')}: {model.get('accuracy', 0):.2%} accuracy")
        else:
            print("❌ Model training failed")
        
        # Test model performance retrieval
        print("📈 Testing model performance retrieval...")
        for symbol in ["BTC/USD", "ETH/USD"]:
            performance = await training_module.get_model_performance(symbol)
            if performance:
                print(f"   - {symbol}: {performance.get('accuracy', 0):.2%} accuracy")
            else:
                print(f"   - {symbol}: No performance data available")
        
        # Test stats
        print("📊 Testing training module stats...")
        stats = training_module.get_stats()
        print(f"✅ Training stats: {json.dumps(stats, indent=2)}")
        
        print("🎉 Training Module tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Training module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_redis_integration():
    """Test Redis integration for execution agent."""
    print("🔗 Testing Redis integration...")
    
    try:
        import redis
        redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        
        # Test basic Redis operations
        redis_client.set("test_execution_key", "test_value")
        value = redis_client.get("test_execution_key")
        print(f"✅ Redis test: {value}")
        
        # Test execution specific operations
        test_execution_data = {
            "symbol": "BTC/USD",
            "signal": "BUY",
            "size": 0.1,
            "latency_ms": 1.5,
            "success": "true",
            "timestamp": int(time.time())
        }
        
        execution_key = f"execution:orders:BTC/USD:{int(time.time())}"
        redis_client.hset(execution_key, mapping=test_execution_data)
        redis_client.expire(execution_key, 3600)  # 1 hour
        
        # Test signal queue
        test_signal = {
            "symbol": "ETH/USD",
            "signal": "SELL",
            "size": 0.05,
            "expected_price": 3000.0
        }
        redis_client.rpush("execution:signals", json.dumps(test_signal))
        
        signal_count = redis_client.llen("execution:signals")
        print(f"✅ Execution test data count: {signal_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

async def test_short_run():
    """Test a short run of the execution bridge."""
    print("🚀 Testing short run of Execution Bridge...")
    
    config = create_test_config()
    bridge = ExecutionBridge(config)
    
    try:
        # Start the bridge
        print("📡 Starting bridge for 10 seconds...")
        start_task = asyncio.create_task(bridge.start())
        
        # Wait for 10 seconds
        await asyncio.sleep(10)
        
        # Stop the bridge
        print("🛑 Stopping bridge...")
        await bridge.stop()
        
        # Get final stats
        final_status = await bridge.get_bridge_status()
        print(f"✅ Final status: {json.dumps(final_status, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Short run test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Execution Agent Tests...")
    
    # Test Redis integration first
    redis_ok = await test_redis_integration()
    if not redis_ok:
        print("⚠️ Redis not available, some tests may fail")
    
    # Test training module
    training_ok = await test_training_module()
    
    # Test execution bridge
    bridge_ok = await test_execution_bridge()
    
    # Test short run (optional)
    if bridge_ok:
        print("\n🔄 Testing short run...")
        short_run_ok = await test_short_run()
        if short_run_ok:
            print("✅ Short run test completed successfully!")
        else:
            print("❌ Short run test failed!")
    
    if bridge_ok and training_ok:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    
    return bridge_ok and training_ok

if __name__ == "__main__":
    asyncio.run(main()) 