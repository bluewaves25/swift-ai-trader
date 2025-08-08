#!/usr/bin/env python3
"""
Test script for Market Conditions Agent
Tests supply and demand analysis functionality.
"""

import asyncio
import json
import time
from typing import Dict, Any
from market_conditions_agent import MarketConditionsAgent
from supply.detector import SupplyDetector
from demand.intensity_reader import DemandIntensityReader

def create_test_config() -> Dict[str, Any]:
    """Create test configuration for market conditions agent."""
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "supply_analysis_interval": 300,
        "demand_analysis_interval": 300,
        "anomaly_detection_interval": 60,
        "trend_prediction_interval": 900,
        "market_regime_interval": 1800,
        "stats_interval": 300,
        "supply": {
            "volume_threshold": 1.5,
            "price_threshold": 0.02,
            "volatility_threshold": 0.05,
            "analysis_window": 3600
        },
        "demand": {
            "intensity_threshold": 1.5,
            "price_sensitivity": 0.02,
            "volume_weight": 0.6,
            "price_weight": 0.4,
            "analysis_window": 3600
        }
    }

async def test_market_conditions_agent():
    """Test the market conditions agent functionality."""
    print("🌊 Starting Market Conditions Agent Test...")
    
    # Create test configuration
    config = create_test_config()
    
    try:
        # Initialize agent
        print("📋 Initializing Market Conditions Agent...")
        agent = MarketConditionsAgent(config)
        
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
        
        # Test component initialization
        print("🔧 Testing component initialization...")
        if hasattr(agent, 'supply_detector'):
            print("✅ Supply detector initialized")
        else:
            print("❌ Supply detector not initialized")
            
        if hasattr(agent, 'demand_intensity_reader'):
            print("✅ Demand intensity reader initialized")
        else:
            print("❌ Demand intensity reader not initialized")
        
        print("🎉 Market Conditions Agent tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_supply_detector():
    """Test supply detector functionality."""
    print("📦 Testing Supply Detector...")
    
    try:
        config = create_test_config()["supply"]
        
        # Initialize supply detector
        print("📋 Initializing Supply Detector...")
        supply_detector = SupplyDetector(config)
        
        # Create test market data
        print("📊 Creating test market data...")
        test_market_data = [
            {
                "symbol": "BTC/USD",
                "volume": 1500.0,
                "offers": 50.0,
                "avg_volume": 1000.0,
                "price": 50000.0,
                "price_change": 0.03,
                "volatility": 0.06
            },
            {
                "symbol": "ETH/USD",
                "volume": 800.0,
                "offers": 30.0,
                "avg_volume": 1000.0,
                "price": 3000.0,
                "price_change": -0.01,
                "volatility": 0.04
            },
            {
                "symbol": "ADA/USD",
                "volume": 2000.0,
                "offers": 80.0,
                "avg_volume": 1000.0,
                "price": 1.0,
                "price_change": 0.05,
                "volatility": 0.08
            }
        ]
        
        # Test supply behavior classification
        print("🏷️ Testing supply behavior classification...")
        supply_result = await supply_detector.classify_supply_behavior(test_market_data)
        
        if supply_result:
            print(f"✅ Supply analysis result: {json.dumps(supply_result, indent=2)}")
        else:
            print("❌ Supply analysis failed")
        
        # Test anomaly detection
        print("🚨 Testing supply anomaly detection...")
        anomalies = await supply_detector.detect_supply_anomalies(test_market_data)
        
        if anomalies:
            print(f"✅ Detected {len(anomalies)} supply anomalies")
            for anomaly in anomalies:
                print(f"   - {anomaly.get('description', 'Unknown anomaly')}")
        else:
            print("✅ No supply anomalies detected")
        
        # Test trend prediction
        print("🔮 Testing supply trend prediction...")
        trends = await supply_detector.predict_supply_trends(test_market_data)
        
        if trends:
            print(f"✅ Generated supply trend predictions: {json.dumps(trends, indent=2)}")
        else:
            print("❌ Supply trend prediction failed")
        
        # Test stats
        print("📊 Testing supply detector stats...")
        stats = supply_detector.get_stats()
        print(f"✅ Supply detector stats: {json.dumps(stats, indent=2)}")
        
        print("🎉 Supply Detector tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Supply detector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_demand_intensity_reader():
    """Test demand intensity reader functionality."""
    print("📈 Testing Demand Intensity Reader...")
    
    try:
        config = create_test_config()["demand"]
        
        # Initialize demand intensity reader
        print("📋 Initializing Demand Intensity Reader...")
        demand_reader = DemandIntensityReader(config)
        
        # Create test market data
        print("📊 Creating test market data...")
        test_market_data = [
            {
                "symbol": "BTC/USD",
                "buy_volume": 1200.0,
                "avg_buy_volume": 1000.0,
                "price_change": 0.02,
                "bid_volume": 800.0,
                "spread": 0.005
            },
            {
                "symbol": "ETH/USD",
                "buy_volume": 600.0,
                "avg_buy_volume": 1000.0,
                "price_change": -0.01,
                "bid_volume": 400.0,
                "spread": 0.008
            },
            {
                "symbol": "ADA/USD",
                "buy_volume": 1800.0,
                "avg_buy_volume": 1000.0,
                "price_change": 0.04,
                "bid_volume": 1200.0,
                "spread": 0.003
            }
        ]
        
        # Test demand intensity measurement
        print("📏 Testing demand intensity measurement...")
        demand_result = await demand_reader.measure_demand_intensity(test_market_data)
        
        if demand_result:
            print(f"✅ Demand analysis result: {json.dumps(demand_result, indent=2)}")
        else:
            print("❌ Demand analysis failed")
        
        # Test anomaly detection
        print("🚨 Testing demand anomaly detection...")
        anomalies = await demand_reader.detect_demand_anomalies(test_market_data)
        
        if anomalies:
            print(f"✅ Detected {len(anomalies)} demand anomalies")
            for anomaly in anomalies:
                print(f"   - {anomaly.get('description', 'Unknown anomaly')}")
        else:
            print("✅ No demand anomalies detected")
        
        # Test trend prediction
        print("🔮 Testing demand trend prediction...")
        trends = await demand_reader.predict_demand_trends(test_market_data)
        
        if trends:
            print(f"✅ Generated demand trend predictions: {json.dumps(trends, indent=2)}")
        else:
            print("❌ Demand trend prediction failed")
        
        # Test stats
        print("📊 Testing demand intensity reader stats...")
        stats = demand_reader.get_stats()
        print(f"✅ Demand intensity reader stats: {json.dumps(stats, indent=2)}")
        
        print("🎉 Demand Intensity Reader tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Demand intensity reader test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_redis_integration():
    """Test Redis integration for market conditions agent."""
    print("🔗 Testing Redis integration...")
    
    try:
        import redis
        redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        
        # Test basic Redis operations
        redis_client.set("test_market_conditions_key", "test_value")
        value = redis_client.get("test_market_conditions_key")
        print(f"✅ Redis test: {value}")
        
        # Test market conditions specific operations
        test_market_data = {
            "symbol": "BTC/USD",
            "volume": 1500.0,
            "buy_volume": 1200.0,
            "price": 50000.0,
            "price_change": 0.02,
            "volatility": 0.05,
            "timestamp": int(time.time())
        }
        
        market_key = f"market_data:BTC/USD:{int(time.time())}"
        redis_client.hset(market_key, mapping=test_market_data)
        redis_client.expire(market_key, 3600)  # 1 hour
        
        # Test supply and demand data
        supply_data = {
            "symbol": "BTC/USD",
            "behavior": "high_supply",
            "volume": 1500.0,
            "timestamp": int(time.time())
        }
        
        demand_data = {
            "symbol": "BTC/USD",
            "intensity": "high_demand",
            "buy_volume": 1200.0,
            "timestamp": int(time.time())
        }
        
        redis_client.hset("market_conditions:supply:BTC/USD", mapping=supply_data)
        redis_client.hset("market_conditions:demand:BTC/USD", mapping=demand_data)
        
        data_count = len(redis_client.keys("market_conditions:*"))
        print(f"✅ Market conditions test data count: {data_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

async def test_short_run():
    """Test a short run of the market conditions agent."""
    print("🚀 Testing short run of Market Conditions Agent...")
    
    config = create_test_config()
    agent = MarketConditionsAgent(config)
    
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
    print("🚀 Starting Market Conditions Agent Tests...")
    
    # Test Redis integration first
    redis_ok = await test_redis_integration()
    if not redis_ok:
        print("⚠️ Redis not available, some tests may fail")
    
    # Test supply detector
    supply_ok = await test_supply_detector()
    
    # Test demand intensity reader
    demand_ok = await test_demand_intensity_reader()
    
    # Test market conditions agent
    agent_ok = await test_market_conditions_agent()
    
    # Test short run (optional)
    if agent_ok:
        print("\n🔄 Testing short run...")
        short_run_ok = await test_short_run()
        if short_run_ok:
            print("✅ Short run test completed successfully!")
        else:
            print("❌ Short run test failed!")
    
    if agent_ok and supply_ok and demand_ok:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    
    return agent_ok and supply_ok and demand_ok

if __name__ == "__main__":
    asyncio.run(main()) 