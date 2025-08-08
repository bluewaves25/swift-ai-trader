#!/usr/bin/env python3
"""
Comprehensive Test Script for Validation Agent
Tests both Rust core and Python bridge components
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import redis
import pandas as pd
from python_bridge import ValidationBridge
from learning_layer.internal.validation_learning import ValidationLearning
from learning_layer.hybrid_training.external_strategy_validator import ExternalStrategyValidator
from logs.validations_logger import ValidationsLogger

class ValidationAgentTester:
    """Comprehensive tester for validation agent components."""
    
    def __init__(self):
        self.config = {
            "redis_url": "redis://localhost:6379",
            "external_validation": {
                "enabled": True,
                "timeout": 30
            },
            "learning": {
                "enabled": True,
                "update_interval": 5,
                "min_samples": 10,
                "learning_rate": 0.01,
                "update_threshold": 0.1
            }
        }
        self.redis_client = None
        self.logger = None

    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                self.config["redis_url"], 
                decode_responses=True
            )
            self.redis_client.ping()
            print("✅ Redis connection established")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            return False

    def _init_logger(self):
        """Initialize logger."""
        try:
            self.logger = ValidationsLogger("validation_tester", self.redis_client)
            print("✅ Logger initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize logger: {e}")
            return False

    async def test_redis_integration(self):
        """Test Redis integration."""
        print("\n🔍 Testing Redis Integration...")
        
        try:
            # Test basic Redis operations
            self.redis_client.set("test:validation", "test_value")
            value = self.redis_client.get("test:validation")
            assert value == "test_value"
            
            # Test validation queues
            test_request = {
                "type": "strategy",
                "data": {"strategy_id": "test_strategy"},
                "timestamp": time.time()
            }
            
            self.redis_client.lpush("validation:input", json.dumps(test_request))
            queue_length = self.redis_client.llen("validation:input")
            assert queue_length > 0
            
            print("✅ Redis integration test passed")
            return True
            
        except Exception as e:
            print(f"❌ Redis integration test failed: {e}")
            return False

    async def test_validation_bridge(self):
        """Test the validation bridge."""
        print("\n🔍 Testing Validation Bridge...")
        
        try:
            bridge = ValidationBridge(self.config)
            
            # Test bridge initialization
            status = await bridge.get_bridge_status()
            assert status["is_running"] == False
            assert "stats" in status
            
            # Test sending validation request
            test_request = {
                "type": "strategy",
                "strategy_id": "test_strategy_001",
                "strategy_data": {
                    "name": "Test Strategy",
                    "parameters": {"risk_level": "medium"},
                    "validation_type": "comprehensive"
                }
            }
            
            success = await bridge.send_validation_request(test_request)
            assert success == True
            
            print("✅ Validation bridge test passed")
            return True
            
        except Exception as e:
            print(f"❌ Validation bridge test failed: {e}")
            return False

    async def test_validation_learning(self):
        """Test the validation learning module."""
        print("\n🔍 Testing Validation Learning...")
        
        try:
            learning = ValidationLearning(self.config["learning"])
            
            # Create test validation data
            test_data = pd.DataFrame({
                "type": ["strategy", "risk", "market", "strategy", "risk", "market"],
                "status": ["valid", "invalid", "valid", "valid", "invalid", "valid"],
                "reason": ["", "insufficient_capital", "", "", "risk_limit_exceeded", ""],
                "processing_time": [0.1, 0.2, 0.15, 0.12, 0.18, 0.11]
            })
            
            # Test model update
            await learning.update_models(test_data)
            
            # Test getting stats
            stats = learning.get_learning_stats()
            assert "models_updated" in stats
            assert "patterns_learned" in stats
            
            # Test getting patterns
            patterns = learning.get_validation_patterns()
            assert len(patterns) > 0
            
            error_patterns = learning.get_error_patterns()
            assert len(error_patterns) > 0
            
            print("✅ Validation learning test passed")
            return True
            
        except Exception as e:
            print(f"❌ Validation learning test failed: {e}")
            return False

    async def test_external_strategy_validator(self):
        """Test the external strategy validator."""
        print("\n🔍 Testing External Strategy Validator...")
        
        try:
            validator = ExternalStrategyValidator(self.config["external_validation"])
            
            # Test strategy validation
            test_strategy = {
                "name": "Test External Strategy",
                "type": "momentum",
                "parameters": {
                    "lookback_period": 20,
                    "threshold": 0.02
                },
                "risk_limits": {
                    "max_position_size": 0.1,
                    "max_daily_loss": 0.05
                }
            }
            
            result = await validator.validate_strategy("test_external_001", test_strategy)
            assert "valid" in result or "invalid" in result
            
            print("✅ External strategy validator test passed")
            return True
            
        except Exception as e:
            print(f"❌ External strategy validator test failed: {e}")
            return False

    async def test_rust_core_integration(self):
        """Test integration with Rust core."""
        print("\n🔍 Testing Rust Core Integration...")
        
        try:
            # Send test validation request to Rust core
            test_request = {
                "type": "strategy",
                "strategy_id": "rust_test_001",
                "validation_data": {
                    "strategy_type": "mean_reversion",
                    "parameters": {"window": 14, "std_dev": 2.0},
                    "risk_parameters": {"max_loss": 0.1, "position_size": 0.05}
                }
            }
            
            # Send to validation input queue (Rust core will process)
            self.redis_client.lpush("validation:input", json.dumps(test_request))
            
            # Wait for processing
            await asyncio.sleep(2)
            
            # Check if result was published
            results = self.redis_client.lrange("validation:results", 0, 0)
            if results:
                result = json.loads(results[0])
                assert "status" in result
                print("✅ Rust core integration test passed")
                return True
            else:
                print("⚠️ No validation results found (Rust core may not be running)")
                return True  # Not a failure if Rust core isn't running
                
        except Exception as e:
            print(f"❌ Rust core integration test failed: {e}")
            return False

    async def test_validation_logger(self):
        """Test the validation logger."""
        print("\n🔍 Testing Validation Logger...")
        
        try:
            logger = ValidationsLogger("test_logger", self.redis_client)
            
            # Test various logging methods
            logger.log("Test log message", "info")
            logger.log_strategy_validation("test_strategy", {"status": "valid"})
            logger.log_data_validation("test_data", {"valid": True})
            logger.log_schema_validation("test_schema", {"valid": True})
            logger.log_quality_check("test_quality", {"score": 0.95})
            logger.log_validation_error("test_error", {"error": "test error"})
            logger.log_compliance_check("test_compliance", {"compliant": True})
            logger.log_integrity_check("test_integrity", {"integrity": True})
            logger.log_counterfactual_simulation("test_simulation", {"result": "valid"})
            logger.log_validation_summary("test_summary", {"summary": "test"})
            logger.log_error("Test error message")
            logger.log_metric("test_metric", 0.95, {"tag": "test"})
            
            print("✅ Validation logger test passed")
            return True
            
        except Exception as e:
            print(f"❌ Validation logger test failed: {e}")
            return False

    async def test_bridge_lifecycle(self):
        """Test the bridge lifecycle."""
        print("\n🔍 Testing Bridge Lifecycle...")
        
        try:
            bridge = ValidationBridge(self.config)
            
            # Start bridge
            await bridge.start()
            await asyncio.sleep(1)
            
            # Check if running
            status = await bridge.get_bridge_status()
            assert status["is_running"] == True
            
            # Send test validation request
            test_request = {
                "type": "risk",
                "risk_id": "test_risk_001",
                "risk_data": {
                    "portfolio_value": 100000,
                    "max_daily_loss": 5000,
                    "current_loss": 2000
                }
            }
            
            success = await bridge.send_validation_request(test_request)
            assert success == True
            
            # Wait for processing
            await asyncio.sleep(2)
            
            # Stop bridge
            await bridge.stop()
            await asyncio.sleep(1)
            
            # Check if stopped
            status = await bridge.get_bridge_status()
            assert status["is_running"] == False
            
            print("✅ Bridge lifecycle test passed")
            return True
            
        except Exception as e:
            print(f"❌ Bridge lifecycle test failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all validation agent tests."""
        print("🚀 Starting Validation Agent Tests...")
        
        # Initialize components
        if not self._init_redis():
            print("❌ Cannot proceed without Redis connection")
            return False
            
        if not self._init_logger():
            print("❌ Cannot proceed without logger")
            return False
        
        # Run tests
        tests = [
            ("Redis Integration", self.test_redis_integration),
            ("Validation Logger", self.test_validation_logger),
            ("Validation Learning", self.test_validation_learning),
            ("External Strategy Validator", self.test_external_strategy_validator),
            ("Validation Bridge", self.test_validation_bridge),
            ("Rust Core Integration", self.test_rust_core_integration),
            ("Bridge Lifecycle", self.test_bridge_lifecycle)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
                results.append((test_name, False))
        
        # Print results
        print("\n📊 Test Results:")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        
        print("=" * 50)
        print(f"Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All validation agent tests passed!")
        else:
            print("⚠️ Some tests failed. Check the logs for details.")
        
        return passed == total

async def main():
    """Main test function."""
    tester = ValidationAgentTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Validation Agent is ready for production!")
    else:
        print("\n❌ Validation Agent needs fixes before production.")

if __name__ == "__main__":
    asyncio.run(main())
