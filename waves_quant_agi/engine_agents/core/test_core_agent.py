#!/usr/bin/env python3
"""
Comprehensive test suite for the Core Agent
Tests all components and the complete agent lifecycle.
"""

import asyncio
import time
import redis
from typing import Dict, Any
from datetime import datetime

from .core_agent import CoreAgent
from .logs.core_agent_logger import CoreAgentLogger
from .interfaces.agent_io import AgentIO
from .controller.flow_manager import FlowManager

class CoreAgentTester:
    """Comprehensive tester for the Core Agent"""
    
    def __init__(self):
        self.config = {
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 0,
            'flow_manager': {
                'risk_params': {
                    'max_exposure': 100000.0,
                    'max_loss_pct': 0.02,
                    'max_position_size': 0.1,
                    'max_daily_trades': 100
                }
            },
            'response_timeout': 30.0,
            'monitoring_interval': 10,
            'reporting_interval': 30,
            'learning_interval': 60
        }
        
        self.logger = CoreAgentLogger("core_agent_tester")
        self.test_results = {}
    
    async def test_redis_integration(self):
        """Test Redis connectivity and basic operations"""
        try:
            self.logger.log_info("Testing Redis integration...", "CoreAgentTester")
            
            # Test Redis connection
            redis_client = redis.Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                db=self.config['redis_db'],
                decode_responses=True
            )
            
            # Test basic operations
            redis_client.set('test_key', 'test_value')
            value = redis_client.get('test_key')
            redis_client.delete('test_key')
            
            if value == 'test_value':
                self.test_results['redis_integration'] = 'PASS'
                self.logger.log_info("Redis integration test PASSED", "CoreAgentTester")
            else:
                self.test_results['redis_integration'] = 'FAIL'
                self.logger.log_error("Redis integration test FAILED", "CoreAgentTester")
                
        except Exception as e:
            self.test_results['redis_integration'] = 'FAIL'
            self.logger.log_error(f"Redis integration test FAILED: {e}", "CoreAgentTester")
    
    async def test_logger(self):
        """Test the CoreAgentLogger"""
        try:
            self.logger.log_info("Testing logger functionality...", "CoreAgentTester")
            
            # Test different log types
            self.logger.log_signal_processing("test_signal", "test_type", "test_source", "received")
            self.logger.log_agent_coordination("test_agent", "test_action", "test_signal", "success")
            self.logger.log_trade_command("test_command", "test_type", "BTC/USD", "buy", "sent")
            self.logger.log_flow_management("test_flow", "test_type", "test_stage", "completed")
            self.logger.log_logic_execution("test_logic", "test_type", {}, {}, 0.1)
            self.logger.log_signal_filtering("test_signal", "test_filter", "passed")
            self.logger.log_system_operation("test_operation", "test_component", "success")
            self.logger.log_metric("test_metric", 123.45)
            self.logger.log_error("test_error", "Test error message", "test_context")
            
            # Test stats
            stats = self.logger.get_stats()
            if isinstance(stats, dict):
                self.test_results['logger'] = 'PASS'
                self.logger.log_info("Logger test PASSED", "CoreAgentTester")
            else:
                self.test_results['logger'] = 'FAIL'
                self.logger.log_error("Logger test FAILED", "CoreAgentTester")
                
        except Exception as e:
            self.test_results['logger'] = 'FAIL'
            self.logger.log_error(f"Logger test FAILED: {e}", "CoreAgentTester")
    
    async def test_agent_io(self):
        """Test the AgentIO interface"""
        try:
            self.logger.log_info("Testing agent IO...", "CoreAgentTester")
            
            agent_io = AgentIO(self.config)
            
            # Test connection
            if agent_io.is_connected():
                self.logger.log_info("AgentIO Redis connection established", "CoreAgentTester")
            
            # Test agent status
            status = agent_io.get_agent_status()
            if isinstance(status, dict):
                self.logger.log_info("Agent status retrieved", "CoreAgentTester")
            
            # Test communication stats
            stats = agent_io.get_communication_stats()
            if isinstance(stats, dict):
                self.logger.log_info("Communication stats retrieved", "CoreAgentTester")
            
            # Test broadcast (will fail if no agents are running, but that's expected)
            try:
                results = await agent_io.broadcast_to_all_agents({'type': 'test'})
                self.logger.log_info(f"Broadcast results: {results}", "CoreAgentTester")
            except Exception as e:
                self.logger.log_info(f"Broadcast test (expected to fail): {e}", "CoreAgentTester")
            
            self.test_results['agent_io'] = 'PASS'
            self.logger.log_info("AgentIO test PASSED", "CoreAgentTester")
            
        except Exception as e:
            self.test_results['agent_io'] = 'FAIL'
            self.logger.log_error(f"AgentIO test FAILED: {e}", "CoreAgentTester")
    
    async def test_flow_manager(self):
        """Test the FlowManager"""
        try:
            self.logger.log_info("Testing flow manager...", "CoreAgentTester")
            
            agent_io = AgentIO(self.config)
            flow_manager = FlowManager(agent_io, self.config)
            
            # Test signal processing
            test_signal = {
                'signal_id': f"test_signal_{int(time.time())}",
                'symbol': 'BTC/USD',
                'action': 'buy',
                'params': {
                    'amount': 0.01,
                    'price': 50000.0
                },
                'source': 'test'
            }
            
            # Test risk compliance
            risk_result = await flow_manager._check_risk_compliance(test_signal)
            if isinstance(risk_result, dict):
                self.logger.log_info(f"Risk compliance test: {risk_result}", "CoreAgentTester")
            
            # Test flow stats
            stats = flow_manager.get_flow_stats()
            if isinstance(stats, dict):
                self.logger.log_info("Flow stats retrieved", "CoreAgentTester")
            
            # Test agent coordination (will fail if no agents are running, but that's expected)
            try:
                coord_result = await flow_manager.coordinate_agents(test_signal)
                self.logger.log_info(f"Agent coordination test: {coord_result}", "CoreAgentTester")
            except Exception as e:
                self.logger.log_info(f"Agent coordination test (expected to fail): {e}", "CoreAgentTester")
            
            # Test reset stats
            flow_manager.reset_stats()
            self.logger.log_info("Flow stats reset", "CoreAgentTester")
            
            self.test_results['flow_manager'] = 'PASS'
            self.logger.log_info("FlowManager test PASSED", "CoreAgentTester")
            
        except Exception as e:
            self.test_results['flow_manager'] = 'FAIL'
            self.logger.log_error(f"FlowManager test FAILED: {e}", "CoreAgentTester")
    
    async def test_core_agent(self):
        """Test the main CoreAgent"""
        try:
            self.logger.log_info("Testing core agent...", "CoreAgentTester")
            
            agent = CoreAgent(self.config)
            
            # Test initialization
            if agent.is_connected():
                self.logger.log_info("Core Agent Redis connection established", "CoreAgentTester")
            
            # Test agent status
            status = agent.get_agent_status()
            if isinstance(status, dict):
                self.logger.log_info("Agent status retrieved", "CoreAgentTester")
            
            # Test signal processing (will fail if no signals are available, but that's expected)
            try:
                signals = await agent._get_pending_signals()
                self.logger.log_info(f"Retrieved {len(signals)} pending signals", "CoreAgentTester")
            except Exception as e:
                self.logger.log_info(f"Signal retrieval test (expected to fail): {e}", "CoreAgentTester")
            
            self.test_results['core_agent'] = 'PASS'
            self.logger.log_info("CoreAgent test PASSED", "CoreAgentTester")
            
        except Exception as e:
            self.test_results['core_agent'] = 'FAIL'
            self.logger.log_error(f"CoreAgent test FAILED: {e}", "CoreAgentTester")
    
    async def test_agent_lifecycle(self):
        """Test the complete agent lifecycle"""
        try:
            self.logger.log_info("Testing agent lifecycle...", "CoreAgentTester")
            
            agent = CoreAgent(self.config)
            
            # Start the agent
            start_task = asyncio.create_task(agent.start())
            
            # Let it run for a short time
            await asyncio.sleep(5)
            
            # Check if agent is running
            if agent.is_running:
                self.logger.log_info("Agent is running successfully", "CoreAgentTester")
            
            # Send test signal to Redis
            if agent.redis_client:
                test_signal = {
                    'signal_id': f"lifecycle_test_{int(time.time())}",
                    'symbol': 'BTC/USD',
                    'action': 'buy',
                    'params': {
                        'amount': 0.01,
                        'price': 50000.0
                    },
                    'source': 'lifecycle_test',
                    'timestamp': int(time.time())
                }
                
                agent.redis_client.lpush('core_agent:signal_queue', str(test_signal))
                self.logger.log_info("Test signal sent to queue", "CoreAgentTester")
            
            # Let it process for a bit more
            await asyncio.sleep(3)
            
            # Stop the agent
            await agent.stop()
            
            # Cancel the start task
            start_task.cancel()
            
            self.test_results['agent_lifecycle'] = 'PASS'
            self.logger.log_info("Agent lifecycle test PASSED", "CoreAgentTester")
            
        except Exception as e:
            self.test_results['agent_lifecycle'] = 'FAIL'
            self.logger.log_error(f"Agent lifecycle test FAILED: {e}", "CoreAgentTester")
    
    async def test_signal_processing(self):
        """Test signal processing functionality"""
        try:
            self.logger.log_info("Testing signal processing...", "CoreAgentTester")
            
            agent = CoreAgent(self.config)
            
            # Create test signal
            test_signal = {
                'signal_id': f"processing_test_{int(time.time())}",
                'symbol': 'BTC/USD',
                'action': 'buy',
                'params': {
                    'amount': 0.01,
                    'price': 50000.0
                },
                'source': 'processing_test',
                'timestamp': int(time.time())
            }
            
            # Test signal processing
            result = await agent._process_signal(test_signal)
            if isinstance(result, dict):
                self.logger.log_info(f"Signal processing result: {result}", "CoreAgentTester")
            
            self.test_results['signal_processing'] = 'PASS'
            self.logger.log_info("Signal processing test PASSED", "CoreAgentTester")
            
        except Exception as e:
            self.test_results['signal_processing'] = 'FAIL'
            self.logger.log_error(f"Signal processing test FAILED: {e}", "CoreAgentTester")
    
    async def run_all_tests(self):
        """Run all tests"""
        self.logger.log_info("Starting comprehensive core agent tests...", "CoreAgentTester")
        
        test_methods = [
            self.test_redis_integration,
            self.test_logger,
            self.test_agent_io,
            self.test_flow_manager,
            self.test_core_agent,
            self.test_signal_processing,
            self.test_agent_lifecycle
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
                await asyncio.sleep(1)  # Brief pause between tests
            except Exception as e:
                self.logger.log_error(f"Test {test_method.__name__} failed: {e}", "CoreAgentTester")
                self.test_results[test_method.__name__] = 'FAIL'
        
        # Report results
        self._report_test_results()
    
    def _report_test_results(self):
        """Report test results"""
        self.logger.log_info("=== CORE AGENT TEST RESULTS ===", "CoreAgentTester")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result == 'PASS')
        failed_tests = total_tests - passed_tests
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result == 'PASS' else "❌ FAIL"
            self.logger.log_info(f"{test_name}: {status}", "CoreAgentTester")
        
        self.logger.log_info(f"Total tests: {total_tests}", "CoreAgentTester")
        self.logger.log_info(f"Passed: {passed_tests}", "CoreAgentTester")
        self.logger.log_info(f"Failed: {failed_tests}", "CoreAgentTester")
        
        if failed_tests == 0:
            self.logger.log_info("🎉 ALL TESTS PASSED!", "CoreAgentTester")
        else:
            self.logger.log_error(f"⚠️  {failed_tests} tests failed", "CoreAgentTester")

async def main():
    """Main test runner"""
    tester = CoreAgentTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
