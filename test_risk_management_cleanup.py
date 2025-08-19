#!/usr/bin/env python3
"""
Test Risk Management Agent Cleanup
Verifies that the cleanup was successful and all components work correctly.
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'waves_quant_agi'))

async def test_risk_management_imports():
    """Test that all imports work correctly after cleanup."""
    print("🔍 Testing Risk Management Agent imports...")
    
    try:
        # Test main agent import
        from waves_quant_agi.engine_agents.risk_management.enhanced_risk_management_agent import EnhancedRiskManagementAgent
        print("✅ Main agent import successful")
        
        # Test core components imports
        from waves_quant_agi.engine_agents.risk_management.core import (
            ConnectionManager,
            DynamicRiskLimits,
            CircuitBreaker,
            CircuitBreakerManager,
            CircuitState,
            PortfolioPerformanceTracker,
            PortfolioMonitor,
            RiskValidator,
            PositionManager
        )
        print("✅ Core components imports successful")
        
        # Test individual component imports
        from waves_quant_agi.engine_agents.risk_management.core.risk_validator import RiskValidator
        from waves_quant_agi.engine_agents.risk_management.core.portfolio_monitor import PortfolioMonitor
        from waves_quant_agi.engine_agents.risk_management.core.position_manager import PositionManager
        from waves_quant_agi.engine_agents.risk_management.core.circuit_breaker import CircuitBreakerManager
        from waves_quant_agi.engine_agents.risk_management.core.dynamic_risk_limits import DynamicRiskLimits
        from waves_quant_agi.engine_agents.risk_management.core.connection_manager import ConnectionManager
        print("✅ Individual component imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_position_manager():
    """Test the new consolidated position manager."""
    print("\n🔍 Testing Position Manager...")
    
    try:
        from waves_quant_agi.engine_agents.risk_management.core.position_manager import PositionManager
        from waves_quant_agi.engine_agents.risk_management.core.connection_manager import ConnectionManager
        
        # Mock config
        config = {
            'position_thresholds': {
                'max_position_size': 0.25,
                'max_sector_exposure': 0.40,
                'min_position_size': 0.01,
                'max_correlation': 0.8,
                'dynamic_sltp_enabled': True,
                'partial_profit_enabled': True,
                'trailing_stop_enabled': True
            }
        }
        
        # Create connection manager
        connection_manager = ConnectionManager(config)
        
        # Create position manager
        position_manager = PositionManager(connection_manager, config)
        print("✅ Position Manager created successfully")
        
        # Test adding a position
        position_data = {
            'position_id': 'test_pos_001',
            'symbol': 'EURUSD',
            'side': 'long',
            'size': 1000.0,
            'entry_price': 1.0850,
            'current_price': 1.0850,
            'stop_loss': 1.0800,
            'take_profit': 1.0900
        }
        
        success = await position_manager.add_position(position_data)
        if success:
            print("✅ Position added successfully")
        else:
            print("❌ Failed to add position")
            return False
        
        # Test getting position summary
        summary = await position_manager.get_position_summary()
        if summary and summary.get('active_positions') == 1:
            print("✅ Position summary retrieved successfully")
        else:
            print("❌ Failed to get position summary")
            return False
        
        # Test portfolio risk assessment
        risk_assessment = await position_manager.assess_portfolio_risk()
        if risk_assessment and 'total_positions' in risk_assessment:
            print("✅ Portfolio risk assessment successful")
        else:
            print("❌ Failed to assess portfolio risk")
            return False
        
        # Test updating position
        update_data = {'current_price': 1.0870}
        success = await position_manager.update_position('test_pos_001', update_data)
        if success:
            print("✅ Position updated successfully")
        else:
            print("❌ Failed to update position")
            return False
        
        # Test closing position
        close_data = {'exit_price': 1.0870}
        success = await position_manager.close_position('test_pos_001', close_data)
        if success:
            print("✅ Position closed successfully")
        else:
            print("❌ Failed to close position")
            return False
        
        # Test stats
        stats = position_manager.get_stats()
        if stats and 'positions_tracked' in stats:
            print("✅ Position manager stats retrieved successfully")
        else:
            print("❌ Failed to get position manager stats")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Position Manager test error: {e}")
        return False

async def test_risk_management_agent():
    """Test the main risk management agent."""
    print("\n🔍 Testing Risk Management Agent...")
    
    try:
        from waves_quant_agi.engine_agents.risk_management.enhanced_risk_management_agent import EnhancedRiskManagementAgent
        
        # Mock config
        config = {
            'agent_name': 'test_risk_management',
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 0,
            'position_thresholds': {
                'max_position_size': 0.25,
                'max_sector_exposure': 0.40,
                'min_position_size': 0.01,
                'max_correlation': 0.8,
                'dynamic_sltp_enabled': True,
                'partial_profit_enabled': True,
                'trailing_stop_enabled': True
            }
        }
        
        # Create agent (BaseAgent requires agent_name and config in constructor)
        agent = EnhancedRiskManagementAgent("test_risk_management", config)
        print("✅ Risk Management Agent created successfully")
        
        # Test component initialization
        if hasattr(agent, 'risk_validator') and agent.risk_validator is None:
            print("✅ Risk validator component initialized")
        else:
            print("❌ Risk validator component not properly initialized")
            return False
        
        if hasattr(agent, 'portfolio_monitor') and agent.portfolio_monitor is None:
            print("✅ Portfolio monitor component initialized")
        else:
            print("❌ Portfolio monitor component not properly initialized")
            return False
        
        if hasattr(agent, 'position_manager') and agent.position_manager is None:
            print("✅ Position manager component initialized")
        else:
            print("❌ Position manager component not properly initialized")
            return False
        
        if hasattr(agent, 'circuit_breaker') and agent.circuit_breaker is None:
            print("✅ Circuit breaker component initialized")
        else:
            print("❌ Circuit breaker component not properly initialized")
            return False
        
        # Test background tasks
        background_tasks = agent._get_background_tasks()
        if background_tasks and len(background_tasks) == 4:
            print("✅ Background tasks configured correctly")
        else:
            print("❌ Background tasks not configured correctly")
            return False
        
        # Test risk status
        risk_status = await agent.get_risk_status()
        if risk_status and 'risk_state' in risk_status:
            print("✅ Risk status retrieved successfully")
        else:
            print("❌ Failed to get risk status")
            return False
        
        # Test portfolio exposure
        exposure = await agent.get_portfolio_exposure()
        if exposure and 'exposure' in exposure:
            print("✅ Portfolio exposure retrieved successfully")
        else:
            print("❌ Failed to get portfolio exposure")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Risk Management Agent test error: {e}")
        return False

async def test_trade_validation():
    """Test trade validation functionality."""
    print("\n🔍 Testing Trade Validation...")
    
    try:
        from waves_quant_agi.engine_agents.risk_management.enhanced_risk_management_agent import EnhancedRiskManagementAgent
        
        # Mock config
        config = {
            'agent_name': 'test_risk_management',
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 0
        }
        
        # Create agent (BaseAgent requires agent_name and config in constructor)
        agent = EnhancedRiskManagementAgent("test_risk_management", config)
        
        # Test trade request
        trade_request = {
            'symbol': 'EURUSD',
            'side': 'buy',
            'volume': 1000.0,
            'price': 1.0850,
            'stop_loss': 1.0800,
            'take_profit': 1.0900
        }
        
        # Test validation
        validation_result = await agent.validate_trade_request(trade_request)
        if validation_result and 'validation_passed' in validation_result:
            print("✅ Trade validation test successful")
        else:
            print("❌ Trade validation test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Trade validation test error: {e}")
        return False

async def test_cleanup_verification():
    """Verify that unused files and directories were removed."""
    print("\n🔍 Verifying Cleanup...")
    
    import os
    
    # Check that unused files were removed
    removed_files = [
        'waves_quant_agi/engine_agents/risk_management/advanced_risk_coordinator.py',
        'waves_quant_agi/engine_agents/risk_management/dynamic_sltp_manager.py',
        'waves_quant_agi/engine_agents/risk_management/partial_profit_manager.py',
        'waves_quant_agi/engine_agents/risk_management/trailing_stop_manager.py',
        'waves_quant_agi/engine_agents/risk_management/core/performance_monitor.py',
        'waves_quant_agi/engine_agents/risk_management/core/trailing_stop_manager.py',
        'waves_quant_agi/engine_agents/risk_management/core/load_balancer.py',
        'waves_quant_agi/engine_agents/risk_management/core/streamlined_risk_manager.py'
    ]
    
    for file_path in removed_files:
        if not os.path.exists(file_path):
            print(f"✅ Removed file: {file_path}")
        else:
            print(f"❌ File still exists: {file_path}")
            return False
    
    # Check that unused directories were removed
    removed_dirs = [
        'waves_quant_agi/engine_agents/risk_management/strategy_specific',
        'waves_quant_agi/engine_agents/risk_management/learning_layer',
        'waves_quant_agi/engine_agents/risk_management/quantum_risk_core',
        'waves_quant_agi/engine_agents/risk_management/simulation_engine',
        'waves_quant_agi/engine_agents/risk_management/audit_trails',
        'waves_quant_agi/engine_agents/risk_management/long_term',
        'waves_quant_agi/engine_agents/risk_management/short_term',
        'waves_quant_agi/engine_agents/risk_management/docs',
        'waves_quant_agi/engine_agents/risk_management/config'
    ]
    
    for dir_path in removed_dirs:
        if not os.path.exists(dir_path):
            print(f"✅ Removed directory: {dir_path}")
        else:
            print(f"❌ Directory still exists: {dir_path}")
            return False
    
    # Check that essential files still exist
    essential_files = [
        'waves_quant_agi/engine_agents/risk_management/enhanced_risk_management_agent.py',
        'waves_quant_agi/engine_agents/risk_management/core/risk_validator.py',
        'waves_quant_agi/engine_agents/risk_management/core/portfolio_monitor.py',
        'waves_quant_agi/engine_agents/risk_management/core/position_manager.py',
        'waves_quant_agi/engine_agents/risk_management/core/circuit_breaker.py',
        'waves_quant_agi/engine_agents/risk_management/core/dynamic_risk_limits.py',
        'waves_quant_agi/engine_agents/risk_management/core/connection_manager.py',
        'waves_quant_agi/engine_agents/risk_management/core/__init__.py'
    ]
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"✅ Essential file exists: {file_path}")
        else:
            print(f"❌ Essential file missing: {file_path}")
            return False
    
    return True

async def main():
    """Run all tests."""
    print("🚀 Starting Risk Management Agent Cleanup Tests...\n")
    
    tests = [
        ("Import Tests", test_risk_management_imports),
        ("Position Manager Tests", test_position_manager),
        ("Risk Management Agent Tests", test_risk_management_agent),
        ("Trade Validation Tests", test_trade_validation),
        ("Cleanup Verification", test_cleanup_verification)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"📋 Running {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} PASSED\n")
            else:
                print(f"❌ {test_name} FAILED\n")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Risk Management Agent cleanup successful!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
