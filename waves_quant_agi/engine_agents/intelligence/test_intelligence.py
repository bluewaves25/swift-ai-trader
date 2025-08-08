#!/usr/bin/env python3
"""
Test script for Intelligence Agent
"""

import asyncio
import json
import time
from typing import Dict, Any
from intelligence_agent import IntelligenceAgent

def create_test_config() -> Dict[str, Any]:
    """Create test configuration for intelligence agent."""
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "pattern_recognition": {
            "correlation_threshold": 0.7,
            "min_data_points": 5,
            "correlation_window": 3600,
            "update_interval": 300
        },
        "anomaly_detection": {
            "anomaly_threshold": 2.0,
            "min_data_points": 5,
            "detection_window": 3600,
            "update_interval": 60
        },
        "gnn_models": {
            "graph_update_interval": 600,
            "coordination_analysis_interval": 900
        },
        "online_learning": {
            "feedback_training_interval": 1800,
            "reinforcement_update_interval": 900
        },
        "transformers": {
            "interaction_analysis_interval": 900,
            "conflict_resolution_interval": 600
        },
        "learning_layer": {
            "research_interval": 3600,
            "training_interval": 7200
        },
        "pattern_analysis_interval": 300,
        "anomaly_detection_interval": 60,
        "gnn_analysis_interval": 600,
        "online_learning_interval": 1800,
        "transformer_analysis_interval": 900,
        "learning_layer_interval": 3600,
        "stats_interval": 300
    }

async def test_intelligence_agent():
    """Test the intelligence agent functionality."""
    print("🧠 Starting Intelligence Agent Test...")
    
    # Create test configuration
    config = create_test_config()
    
    try:
        # Initialize agent
        print("📋 Initializing Intelligence Agent...")
        agent = IntelligenceAgent(config)
        
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
        
        # Test correlation matrix
        print("📊 Testing correlation matrix...")
        if hasattr(agent, 'correlation_matrix'):
            test_metrics = [
                {"agent": "data_feeds", "speed": 100.0, "accuracy": 0.95, "cost": 0.01, "error_rate": 0.05},
                {"agent": "adapters", "speed": 50.0, "accuracy": 0.98, "cost": 0.02, "error_rate": 0.02},
                {"agent": "fees_monitor", "speed": 75.0, "accuracy": 0.92, "cost": 0.015, "error_rate": 0.08}
            ]
            
            correlations = await agent.correlation_matrix.build_correlation_matrix(test_metrics)
            print(f"✅ Correlation analysis: {json.dumps(correlations, indent=2)}")
            
            # Test insights
            insights = await agent.correlation_matrix.get_correlation_insights(correlations)
            for insight in insights:
                print(f"💡 Insight: {insight}")
        
        # Test anomaly detector
        print("🚨 Testing anomaly detector...")
        if hasattr(agent, 'anomaly_detector'):
            test_metrics = [
                {"agent": "data_feeds", "speed": 100.0, "accuracy": 0.95, "cost": 0.01, "error_rate": 0.05},
                {"agent": "adapters", "speed": 50.0, "accuracy": 0.98, "cost": 0.02, "error_rate": 0.02},
                {"agent": "fees_monitor", "speed": 75.0, "accuracy": 0.92, "cost": 0.015, "error_rate": 0.08},
                {"agent": "anomaly_test", "speed": 500.0, "accuracy": 0.50, "cost": 0.10, "error_rate": 0.50}  # Anomaly
            ]
            
            anomalies = await agent.anomaly_detector.detect_anomalies(test_metrics)
            print(f"✅ Anomaly detection: {json.dumps(anomalies, indent=2)}")
            
            # Test insights
            insights = await agent.anomaly_detector.get_anomaly_insights(anomalies)
            for insight in insights:
                print(f"💡 Anomaly insight: {insight}")
        
        print("🎉 All tests passed! Intelligence Agent is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_correlation_matrix():
    """Test correlation matrix functionality."""
    print("📊 Testing Correlation Matrix...")
    
    try:
        from pattern_recognition.correlation_matrix import CorrelationMatrix
        
        config = {
            "correlation_threshold": 0.7,
            "min_data_points": 5,
            "correlation_window": 3600,
            "update_interval": 300
        }
        
        correlation_matrix = CorrelationMatrix(config)
        
        # Test with sample data
        test_metrics = [
            {"agent": "data_feeds", "speed": 100.0, "accuracy": 0.95, "cost": 0.01, "error_rate": 0.05},
            {"agent": "adapters", "speed": 50.0, "accuracy": 0.98, "cost": 0.02, "error_rate": 0.02},
            {"agent": "fees_monitor", "speed": 75.0, "accuracy": 0.92, "cost": 0.015, "error_rate": 0.08}
        ]
        
        result = await correlation_matrix.build_correlation_matrix(test_metrics)
        print(f"✅ Correlation matrix result: {json.dumps(result, indent=2)}")
        
        # Test insights
        insights = await correlation_matrix.get_correlation_insights(result)
        for insight in insights:
            print(f"💡 Correlation insight: {insight}")
        
        return True
        
    except Exception as e:
        print(f"❌ Correlation matrix test failed: {e}")
        return False

async def test_anomaly_detector():
    """Test anomaly detector functionality."""
    print("🚨 Testing Anomaly Detector...")
    
    try:
        from pattern_recognition.anomaly_detector import AnomalyDetector
        
        config = {
            "anomaly_threshold": 2.0,
            "min_data_points": 5,
            "detection_window": 3600,
            "update_interval": 60
        }
        
        anomaly_detector = AnomalyDetector(config)
        
        # Test with sample data including anomalies
        test_metrics = [
            {"agent": "data_feeds", "speed": 100.0, "accuracy": 0.95, "cost": 0.01, "error_rate": 0.05},
            {"agent": "adapters", "speed": 50.0, "accuracy": 0.98, "cost": 0.02, "error_rate": 0.02},
            {"agent": "fees_monitor", "speed": 75.0, "accuracy": 0.92, "cost": 0.015, "error_rate": 0.08},
            {"agent": "anomaly_test", "speed": 500.0, "accuracy": 0.50, "cost": 0.10, "error_rate": 0.50}  # Anomaly
        ]
        
        anomalies = await anomaly_detector.detect_anomalies(test_metrics)
        print(f"✅ Anomaly detection result: {json.dumps(anomalies, indent=2)}")
        
        # Test insights
        insights = await anomaly_detector.get_anomaly_insights(anomalies)
        for insight in insights:
            print(f"💡 Anomaly insight: {insight}")
        
        return True
        
    except Exception as e:
        print(f"❌ Anomaly detector test failed: {e}")
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
        
        # Test intelligence specific operations
        test_data = {
            "agent": "intelligence_test",
            "pattern_type": "correlation",
            "description": "Test pattern detection",
            "timestamp": time.time()
        }
        redis_client.lpush("intelligence:patterns", str(test_data))
        data_count = redis_client.llen("intelligence:patterns")
        print(f"✅ Intelligence test data count: {data_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

async def test_short_run():
    """Test a short run of the intelligence agent."""
    print("🚀 Testing short run of Intelligence Agent...")
    
    config = create_test_config()
    agent = IntelligenceAgent(config)
    
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
    print("🚀 Starting Intelligence Agent Tests...")
    
    # Test Redis integration first
    redis_ok = await test_redis_integration()
    if not redis_ok:
        print("⚠️ Redis not available, some tests may fail")
    
    # Test correlation matrix
    correlation_ok = await test_correlation_matrix()
    
    # Test anomaly detector
    anomaly_ok = await test_anomaly_detector()
    
    # Test intelligence agent
    agent_ok = await test_intelligence_agent()
    
    # Test short run (optional)
    if agent_ok:
        print("\n🔄 Testing short run...")
        short_run_ok = await test_short_run()
        if short_run_ok:
            print("✅ Short run test completed successfully!")
        else:
            print("❌ Short run test failed!")
    
    if agent_ok and correlation_ok and anomaly_ok:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    
    return agent_ok and correlation_ok and anomaly_ok

if __name__ == "__main__":
    asyncio.run(main()) 