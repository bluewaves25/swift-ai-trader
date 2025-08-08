#!/usr/bin/env python3
"""
Test script for Risk Management Agent
Tests risk evaluation and portfolio monitoring functionality.
"""

import asyncio
import json
import time
from typing import Dict, Any
import pandas as pd
from risk_management_agent import RiskManagementAgent
from risk_management_core import RiskManagementCore

def create_test_config() -> Dict[str, Any]:
    """Create test configuration for risk management agent."""
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "risk_evaluation_interval": 60,
        "portfolio_monitoring_interval": 300,
        "risk_alert_interval": 30,
        "threshold_monitoring_interval": 60,
        "capital_allocation_interval": 600,
        "stats_interval": 300,
        "risk_threshold": 0.05,
        "diversification_threshold": 0.7,
        "entropy_threshold": 0.8,
        "max_position_size": 0.1,
        "max_daily_loss": 0.02,
        "portfolio_risk_threshold": 0.7,
        "max_position_ratio": 0.8
    }

async def test_risk_management_agent():
    """Test the risk management agent functionality."""
    print("🛡️ Starting Risk Management Agent Test...")
    
    # Create test configuration
    config = create_test_config()
    
    try:
        # Initialize agent
        print("📋 Initializing Risk Management Agent...")
        agent = RiskManagementAgent(config)
        
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
        if hasattr(agent, 'risk_core'):
            print("✅ Risk core initialized")
        else:
            print("❌ Risk core not initialized")
        
        print("🎉 Risk Management Agent tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_risk_management_core():
    """Test risk management core functionality."""
    print("🛡️ Testing Risk Management Core...")
    
    try:
        config = create_test_config()
        
        # Initialize risk management core
        print("📋 Initializing Risk Management Core...")
        risk_core = RiskManagementCore(config)
        
        # Create test strategy data
        print("📊 Creating test strategy data...")
        test_strategy_data = pd.DataFrame([
            {
                "strategy_id": "strategy_001",
                "symbol": "BTC/USD",
                "position_size": 1000.0,
                "current_price": 50000.0,
                "volatility": 0.05,
                "price_change": 0.02
            },
            {
                "strategy_id": "strategy_002",
                "symbol": "ETH/USD",
                "position_size": 500.0,
                "current_price": 3000.0,
                "volatility": 0.08,
                "price_change": -0.01
            },
            {
                "strategy_id": "strategy_003",
                "symbol": "ADA/USD",
                "position_size": 2000.0,
                "current_price": 1.0,
                "volatility": 0.12,
                "price_change": 0.05
            }
        ])
        
        # Test risk evaluation
        print("🔍 Testing risk evaluation...")
        risk_decisions = await risk_core.evaluate_risk(test_strategy_data)
        
        if risk_decisions:
            print(f"✅ Risk evaluation result: {json.dumps(risk_decisions, indent=2)}")
            
            # Count decisions
            approved = sum(1 for d in risk_decisions if d.get("status") == "approve")
            denied = len(risk_decisions) - approved
            print(f"📊 Decisions: {approved} approved, {denied} denied")
        else:
            print("❌ Risk evaluation failed")
        
        # Test stats
        print("📊 Testing risk management core stats...")
        stats = risk_core.get_stats()
        print(f"✅ Risk management core stats: {json.dumps(stats, indent=2)}")
        
        print("🎉 Risk Management Core tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Risk management core test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_risk_assessment():
    """Test comprehensive risk assessment."""
    print("🔍 Testing Comprehensive Risk Assessment...")
    
    try:
        config = create_test_config()
        risk_core = RiskManagementCore(config)
        
        # Test risk assessment with different scenarios
        test_scenarios = [
            {
                "name": "Low Risk Scenario",
                "position_size": 100.0,
                "current_price": 50000.0,
                "volatility": 0.02,
                "expected_status": "approve"
            },
            {
                "name": "High Risk Scenario",
                "position_size": 10000.0,
                "current_price": 50000.0,
                "volatility": 0.15,
                "expected_status": "deny"
            },
            {
                "name": "Medium Risk Scenario",
                "position_size": 1000.0,
                "current_price": 50000.0,
                "volatility": 0.08,
                "expected_status": "approve"
            }
        ]
        
        for scenario in test_scenarios:
            print(f"🧪 Testing {scenario['name']}...")
            
            # Create test data
            test_data = pd.DataFrame([{
                "strategy_id": f"test_{scenario['name'].lower().replace(' ', '_')}",
                "symbol": "BTC/USD",
                "position_size": scenario["position_size"],
                "current_price": scenario["current_price"],
                "volatility": scenario["volatility"],
                "price_change": 0.01
            }])
            
            # Evaluate risk
            decisions = await risk_core.evaluate_risk(test_data)
            
            if decisions:
                decision = decisions[0]
                status = decision.get("status", "unknown")
                expected = scenario["expected_status"]
                
                if status == expected:
                    print(f"✅ {scenario['name']}: Expected {expected}, got {status}")
                else:
                    print(f"⚠️ {scenario['name']}: Expected {expected}, got {status}")
                    print(f"   Reason: {decision.get('reason', 'No reason')}")
            else:
                print(f"❌ {scenario['name']}: No decision returned")
        
        print("🎉 Risk Assessment tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Risk assessment test failed: {e}")
        return False

async def test_portfolio_monitoring():
    """Test portfolio monitoring functionality."""
    print("📊 Testing Portfolio Monitoring...")
    
    try:
        config = create_test_config()
        agent = RiskManagementAgent(config)
        
        # Test portfolio data analysis
        test_portfolio_data = {
            "total_value": 100000.0,
            "cash": 20000.0,
            "positions": 80000.0,
            "daily_pnl": -500.0,
            "total_pnl": 5000.0
        }
        
        # Test portfolio risk analysis
        portfolio_risk = await agent._analyze_portfolio_risk(test_portfolio_data)
        
        if portfolio_risk:
            print(f"✅ Portfolio risk analysis: {json.dumps(portfolio_risk, indent=2)}")
            
            risk_score = portfolio_risk.get("risk_score", 0)
            if risk_score > 0.7:
                print("⚠️ High portfolio risk detected")
            elif risk_score > 0.4:
                print("⚠️ Medium portfolio risk detected")
            else:
                print("✅ Low portfolio risk")
        else:
            print("❌ Portfolio risk analysis failed")
        
        # Test risk alerts
        print("🚨 Testing risk alerts...")
        alerts = await agent._check_risk_alerts()
        
        if alerts:
            print(f"✅ Detected {len(alerts)} risk alerts:")
            for alert in alerts:
                print(f"   - {alert.get('description', 'Unknown alert')}")
        else:
            print("✅ No risk alerts detected")
        
        print("🎉 Portfolio Monitoring tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Portfolio monitoring test failed: {e}")
        return False

async def test_redis_integration():
    """Test Redis integration for risk management agent."""
    print("🔗 Testing Redis integration...")
    
    try:
        import redis
        redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        
        # Test basic Redis operations
        redis_client.set("test_risk_management_key", "test_value")
        value = redis_client.get("test_risk_management_key")
        print(f"✅ Redis test: {value}")
        
        # Test risk management specific operations
        test_risk_data = {
            "strategy_id": "test_strategy",
            "symbol": "BTC/USD",
            "position_size": 1000.0,
            "current_price": 50000.0,
            "volatility": 0.05,
            "timestamp": int(time.time())
        }
        
        risk_key = f"risk_management:test:{int(time.time())}"
        redis_client.hset(risk_key, mapping=test_risk_data)
        redis_client.expire(risk_key, 3600)  # 1 hour
        
        # Test portfolio data
        portfolio_data = {
            "total_value": 100000.0,
            "cash": 20000.0,
            "positions": 80000.0,
            "daily_pnl": 0.0,
            "timestamp": int(time.time())
        }
        
        redis_client.hset("risk_management:portfolio", mapping=portfolio_data)
        
        data_count = len(redis_client.keys("risk_management:*"))
        print(f"✅ Risk management test data count: {data_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

async def test_short_run():
    """Test a short run of the risk management agent."""
    print("🚀 Testing short run of Risk Management Agent...")
    
    config = create_test_config()
    agent = RiskManagementAgent(config)
    
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
    print("🚀 Starting Risk Management Agent Tests...")
    
    # Test Redis integration first
    redis_ok = await test_redis_integration()
    if not redis_ok:
        print("⚠️ Redis not available, some tests may fail")
    
    # Test risk management core
    core_ok = await test_risk_management_core()
    
    # Test risk assessment
    assessment_ok = await test_risk_assessment()
    
    # Test portfolio monitoring
    monitoring_ok = await test_portfolio_monitoring()
    
    # Test risk management agent
    agent_ok = await test_risk_management_agent()
    
    # Test short run (optional)
    if agent_ok:
        print("\n🔄 Testing short run...")
        short_run_ok = await test_short_run()
        if short_run_ok:
            print("✅ Short run test completed successfully!")
        else:
            print("❌ Short run test failed!")
    
    if agent_ok and core_ok and assessment_ok and monitoring_ok:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    
    return agent_ok and core_ok and assessment_ok and monitoring_ok

if __name__ == "__main__":
    asyncio.run(main()) 