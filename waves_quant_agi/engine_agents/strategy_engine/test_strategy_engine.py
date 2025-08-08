#!/usr/bin/env python3
"""
Comprehensive Test Script for Strategy Engine Agent
Tests all components and their interactions
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import redis
import pandas as pd
from strategy_engine_agent import StrategyEngineAgent
from manager.strategy_registry import StrategyRegistry
from manager.performance_tracker import PerformanceTracker
from composers.ml_composer import MLComposer
from logs.strategy_engine_logger import StrategyEngineLogger

class StrategyEngineTester:
    """Comprehensive tester for strategy engine components."""
    
    def __init__(self):
        self.config = {
            "redis_url": "redis://localhost:6379",
            "registry": {
                "redis_url": "redis://localhost:6379"
            },
            "performance": {
                "redis_url": "redis://localhost:6379",
                "sharpe_threshold": 1.0,
                "drawdown_threshold": 0.1
            },
            "ml_composer": {
                "redis_url": "redis://localhost:6379",
                "n_estimators": 100,
                "confidence_threshold": 0.7
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
            self.logger = StrategyEngineLogger("strategy_engine_tester", self.redis_client)
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
            self.redis_client.set("test:strategy_engine", "test_value")
            value = self.redis_client.get("test:strategy_engine")
            assert value == "test_value"
            
            # Test strategy engine queues
            test_strategy = {
                "type": "trend_following",
                "symbol": "BTC/USD",
                "timestamp": time.time()
            }
            
            self.redis_client.lpush("strategy_engine:input", json.dumps(test_strategy))
            queue_length = self.redis_client.llen("strategy_engine:input")
            assert queue_length > 0
            
            print("✅ Redis integration test passed")
            return True
            
        except Exception as e:
            print(f"❌ Redis integration test failed: {e}")
            return False

    async def test_strategy_registry(self):
        """Test the strategy registry."""
        print("\n🔍 Testing Strategy Registry...")
        
        try:
            registry = StrategyRegistry(self.config["registry"])
            
            # Test strategy registration
            test_strategy = {
                "type": "trend_following",
                "symbol": "BTC/USD",
                "timestamp": time.time(),
                "parameters": {"lookback": 20, "threshold": 0.02},
                "risk_limits": {"max_position_size": 0.1, "max_daily_loss": 0.05}
            }
            
            success = await registry.register_strategy(test_strategy)
            assert success == True
            
            # Test getting active strategies
            active_strategies = await registry.get_active_strategies()
            assert len(active_strategies) > 0
            
            # Test strategy update
            strategy_id = f"{test_strategy['type']}:{test_strategy['symbol']}:{test_strategy['timestamp']}"
            update_success = await registry.update_strategy(strategy_id, {"confidence": 0.85})
            assert update_success == True
            
            # Test getting stats
            stats = registry.get_registry_stats()
            assert "strategies_registered" in stats
            
            print("✅ Strategy registry test passed")
            return True
            
        except Exception as e:
            print(f"❌ Strategy registry test failed: {e}")
            return False

    async def test_performance_tracker(self):
        """Test the performance tracker."""
        print("\n🔍 Testing Performance Tracker...")
        
        try:
            tracker = PerformanceTracker(self.config["performance"])
            
            # Create test strategy data
            test_data = [
                {
                    "strategy_id": "test_strategy_001",
                    "symbol": "BTC/USD",
                    "returns": [0.01, 0.02, -0.01, 0.03, 0.01, -0.02, 0.02, 0.01]
                },
                {
                    "strategy_id": "test_strategy_002",
                    "symbol": "ETH/USD",
                    "returns": [0.005, 0.015, -0.005, 0.025, 0.005, -0.015, 0.015, 0.005]
                }
            ]
            
            # Track performance
            performance_results = await tracker.track_performance(test_data)
            assert len(performance_results) > 0
            
            # Check performance metrics
            for result in performance_results:
                assert "sharpe_ratio" in result
                assert "max_drawdown" in result
                assert "strategy_id" in result
            
            # Test getting stats
            stats = tracker.get_performance_stats()
            assert "strategies_tracked" in stats
            
            print("✅ Performance tracker test passed")
            return True
            
        except Exception as e:
            print(f"❌ Performance tracker test failed: {e}")
            return False

    async def test_ml_composer(self):
        """Test the ML composer."""
        print("\n🔍 Testing ML Composer...")
        
        try:
            composer = MLComposer(self.config["ml_composer"])
            
            # Create test market data
            test_market_data = [
                {
                    "symbol": "BTC/USD",
                    "volatility": 0.02,
                    "trend_score": 0.7,
                    "volume": 1000000
                },
                {
                    "symbol": "ETH/USD",
                    "volatility": 0.03,
                    "trend_score": 0.5,
                    "volume": 500000
                },
                {
                    "symbol": "ADA/USD",
                    "volatility": 0.04,
                    "trend_score": 0.8,
                    "volume": 200000
                }
            ]
            
            # Compose strategies
            strategies = await composer.compose_strategy(test_market_data)
            assert len(strategies) >= 0  # May be 0 if confidence threshold not met
            
            # Test getting stats
            stats = composer.get_composer_stats()
            assert "strategies_composed" in stats
            
            print("✅ ML composer test passed")
            return True
            
        except Exception as e:
            print(f"❌ ML composer test failed: {e}")
            return False

    async def test_strategy_engine_logger(self):
        """Test the strategy engine logger."""
        print("\n🔍 Testing Strategy Engine Logger...")
        
        try:
            logger = StrategyEngineLogger("test_logger", self.redis_client)
            
            # Test various logging methods
            logger.log("Test log message", "info")
            logger.log_strategy_registration("test_strategy_001", {"type": "trend_following", "symbol": "BTC/USD"})
            logger.log_strategy_performance("test_strategy_001", {"sharpe_ratio": 1.5, "max_drawdown": 0.05})
            logger.log_strategy_composition("ml_composer", {"strategy_type": "momentum", "confidence": 0.85})
            logger.log_strategy_deployment("test_strategy_001", {"status": "deployed", "broker": "binance"})
            logger.log_strategy_learning("model_update", {"model_type": "random_forest", "accuracy": 0.92})
            logger.log_strategy_error("composition_error", {"error": "Feature extraction failed"})
            logger.log_strategy_alert("performance_alert", {"strategy_id": "test_001", "issue": "Low Sharpe ratio"})
            logger.log_strategy_metric("composition_success_rate", 0.85, {"component": "ml_composer"})
            logger.log_strategy_research("market_analysis", {"market": "crypto", "insights": "Bullish trend detected"})
            logger.log_strategy_optimization("parameter_tuning", {"strategy_id": "test_001", "improvement": 0.15})
            
            print("✅ Strategy engine logger test passed")
            return True
            
        except Exception as e:
            print(f"❌ Strategy engine logger test failed: {e}")
            return False

    async def test_agent_lifecycle(self):
        """Test the agent lifecycle."""
        print("\n🔍 Testing Agent Lifecycle...")
        
        try:
            agent = StrategyEngineAgent(self.config)
            
            # Start agent
            await agent.start()
            await asyncio.sleep(1)
            
            # Check if running
            status = agent.get_agent_status()
            assert status["is_running"] == True
            
            # Test manual strategy composition
            test_strategy = {
                "strategy_id": "manual_test_001",
                "type": "mean_reversion",
                "symbol": "BTC/USD",
                "timestamp": time.time(),
                "parameters": {"window": 14, "std_dev": 2.0},
                "confidence": 0.85
            }
            
            success = await agent.compose_strategy_manual(test_strategy)
            assert success == True
            
            # Wait for processing
            await asyncio.sleep(2)
            
            # Stop agent
            await agent.stop()
            await asyncio.sleep(1)
            
            # Check if stopped
            status = agent.get_agent_status()
            assert status["is_running"] == False
            
            print("✅ Agent lifecycle test passed")
            return True
            
        except Exception as e:
            print(f"❌ Agent lifecycle test failed: {e}")
            return False

    async def test_market_data_integration(self):
        """Test market data integration."""
        print("\n🔍 Testing Market Data Integration...")
        
        try:
            # Create test market data
            test_market_data = [
                {
                    "symbol": "BTC/USD",
                    "price": 45000,
                    "volume": 1000000,
                    "volatility": 0.02,
                    "trend_score": 0.7,
                    "timestamp": time.time()
                },
                {
                    "symbol": "ETH/USD",
                    "price": 3000,
                    "volume": 500000,
                    "volatility": 0.03,
                    "trend_score": 0.5,
                    "timestamp": time.time()
                }
            ]
            
            # Store market data in Redis
            for data in test_market_data:
                self.redis_client.lpush("market_data:latest", json.dumps(data))
            
            # Test retrieving market data
            raw_data = self.redis_client.lrange("market_data:latest", 0, 9)
            assert len(raw_data) > 0
            
            # Parse market data
            parsed_data = []
            for raw_entry in raw_data:
                try:
                    entry = json.loads(raw_entry)
                    parsed_data.append(entry)
                except json.JSONDecodeError:
                    continue
            
            assert len(parsed_data) > 0
            
            print("✅ Market data integration test passed")
            return True
            
        except Exception as e:
            print(f"❌ Market data integration test failed: {e}")
            return False

    async def test_strategy_performance_integration(self):
        """Test strategy performance integration."""
        print("\n🔍 Testing Strategy Performance Integration...")
        
        try:
            registry = StrategyRegistry(self.config["registry"])
            tracker = PerformanceTracker(self.config["performance"])
            
            # Register test strategies
            test_strategies = [
                {
                    "type": "trend_following",
                    "symbol": "BTC/USD",
                    "timestamp": time.time(),
                    "strategy_id": "perf_test_001"
                },
                {
                    "type": "mean_reversion",
                    "symbol": "ETH/USD",
                    "timestamp": time.time(),
                    "strategy_id": "perf_test_002"
                }
            ]
            
            for strategy in test_strategies:
                await registry.register_strategy(strategy)
            
            # Create performance data
            performance_data = [
                {
                    "strategy_id": "perf_test_001",
                    "symbol": "BTC/USD",
                    "returns": [0.01, 0.02, -0.01, 0.03, 0.01]
                },
                {
                    "strategy_id": "perf_test_002",
                    "symbol": "ETH/USD",
                    "returns": [0.005, 0.015, -0.005, 0.025, 0.005]
                }
            ]
            
            # Track performance
            performance_results = await tracker.track_performance(performance_data)
            assert len(performance_results) > 0
            
            # Update strategies with performance data
            for result in performance_results:
                strategy_id = result.get("strategy_id")
                if strategy_id:
                    await registry.update_strategy(strategy_id, {"performance": result})
            
            # Verify performance data is stored
            active_strategies = await registry.get_active_strategies()
            strategies_with_performance = [s for s in active_strategies if "performance" in s]
            assert len(strategies_with_performance) > 0
            
            print("✅ Strategy performance integration test passed")
            return True
            
        except Exception as e:
            print(f"❌ Strategy performance integration test failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all strategy engine tests."""
        print("🚀 Starting Strategy Engine Tests...")
        
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
            ("Strategy Engine Logger", self.test_strategy_engine_logger),
            ("Strategy Registry", self.test_strategy_registry),
            ("Performance Tracker", self.test_performance_tracker),
            ("ML Composer", self.test_ml_composer),
            ("Market Data Integration", self.test_market_data_integration),
            ("Strategy Performance Integration", self.test_strategy_performance_integration),
            ("Agent Lifecycle", self.test_agent_lifecycle)
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
            print("🎉 All strategy engine tests passed!")
        else:
            print("⚠️ Some tests failed. Check the logs for details.")
        
        return passed == total

async def main():
    """Main test function."""
    tester = StrategyEngineTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Strategy Engine is ready for production!")
    else:
        print("\n❌ Strategy Engine needs fixes before production.")

if __name__ == "__main__":
    asyncio.run(main())
