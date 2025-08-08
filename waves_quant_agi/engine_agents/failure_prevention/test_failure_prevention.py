# failure_prevention/test_failure_prevention.py
"""
Comprehensive test suite for the Failure Prevention Agent
"""

import asyncio
import time
import redis
from typing import Dict, Any
from datetime import datetime

from .failure_prevention_agent import FailurePreventionAgent, FailureType, AlertLevel
from .logs.failure_agent_logger import FailureAgentLogger
from .memory.incident_cache import IncidentCache
from .monitor.agent_supervisor import AgentSupervisor
from .circuit_breakers.broker_breaker import BrokerBreaker

class FailurePreventionTester:
    """Comprehensive tester for the Failure Prevention Agent"""
    
    def __init__(self):
        self.config = {
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 0,
            'agent_supervision': {
                'response_timeout': 30.0,
                'failure_threshold': 5,
                'failure_window': 300,
                'health_check_interval': 60,
                'cleanup_interval': 3600
            },
            'broker_circuit_breakers': {
                'failure_threshold': 5,
                'recovery_timeout': 60,
                'half_open_max_calls': 3,
                'monitoring_interval': 30
            },
            'incident_cache': {
                'expiration_days': 7,
                'max_incidents': 10000
            },
            'monitoring_interval': 30,
            'reporting_interval': 300,
            'cleanup_interval': 3600,
            'intelligence_interval': 300
        }
        
        self.logger = FailureAgentLogger()
        self.test_results = {}
    
    async def test_redis_integration(self):
        """Test Redis connectivity and basic operations"""
        try:
            self.logger.log_info("Testing Redis integration...", "FailurePreventionTester")
            
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
                self.logger.log_info("Redis integration test PASSED", "FailurePreventionTester")
            else:
                self.test_results['redis_integration'] = 'FAIL'
                self.logger.log_error("Redis integration test FAILED", "FailurePreventionTester")
                
        except Exception as e:
            self.test_results['redis_integration'] = 'FAIL'
            self.logger.log_error(f"Redis integration test FAILED: {e}", "FailurePreventionTester")
    
    async def test_logger(self):
        """Test the FailureAgentLogger"""
        try:
            self.logger.log_info("Testing logger functionality...", "FailurePreventionTester")
            
            # Test different log types
            self.logger.log_alert("test_alert", "medium", "test_source", "Test alert message")
            self.logger.log_incident("test_incident", "test_source", "Test incident message")
            self.logger.log_circuit_breaker("test_breaker", "test_target", "test_action", "open")
            self.logger.log_agent_supervision("test_agent", "test_action", "active")
            self.logger.log_system_monitoring("test_component", "test_metric", 42.0)
            self.logger.log_recovery_action("test_recovery", "test_target", True)
            self.logger.log_metric("test_metric", 123.45)
            self.logger.log_error("test_error", "Test error message", "test_source")
            
            # Test stats
            stats = self.logger.get_stats()
            if isinstance(stats, dict):
                self.test_results['logger'] = 'PASS'
                self.logger.log_info("Logger test PASSED", "FailurePreventionTester")
            else:
                self.test_results['logger'] = 'FAIL'
                self.logger.log_error("Logger test FAILED", "FailurePreventionTester")
                
        except Exception as e:
            self.test_results['logger'] = 'FAIL'
            self.logger.log_error(f"Logger test FAILED: {e}", "FailurePreventionTester")
    
    async def test_incident_cache(self):
        """Test the IncidentCache"""
        try:
            self.logger.log_info("Testing incident cache...", "FailurePreventionTester")
            
            cache = IncidentCache(self.config['incident_cache'])
            
            # Test storing incidents
            test_incident = {
                'timestamp': int(time.time()),
                'type': 'test_incident',
                'source': 'test_source',
                'description': 'Test incident description',
                'failure_count': 1,
                'recovery_action': 'test_recovery'
            }
            
            result = cache.store_incident(test_incident)
            if result:
                self.logger.log_info("Incident stored successfully", "FailurePreventionTester")
            
            # Test retrieving incidents
            incidents = cache.retrieve_incidents()
            if len(incidents) > 0:
                self.logger.log_info(f"Retrieved {len(incidents)} incidents", "FailurePreventionTester")
            
            # Test stats
            stats = cache.get_incident_stats()
            if isinstance(stats, dict):
                self.logger.log_info("Incident stats retrieved", "FailurePreventionTester")
            
            # Test recent incidents
            recent = cache.get_recent_incidents(hours=24)
            self.logger.log_info(f"Retrieved {len(recent)} recent incidents", "FailurePreventionTester")
            
            self.test_results['incident_cache'] = 'PASS'
            self.logger.log_info("Incident cache test PASSED", "FailurePreventionTester")
            
        except Exception as e:
            self.test_results['incident_cache'] = 'FAIL'
            self.logger.log_error(f"Incident cache test FAILED: {e}", "FailurePreventionTester")
    
    async def test_agent_supervisor(self):
        """Test the AgentSupervisor"""
        try:
            self.logger.log_info("Testing agent supervisor...", "FailurePreventionTester")
            
            supervisor = AgentSupervisor(self.config['agent_supervision'])
            
            # Test agent registration
            test_agent_info = {
                'name': 'test_agent',
                'type': 'test_type',
                'version': '1.0.0'
            }
            
            supervisor.register_agent('test_agent_1', test_agent_info)
            supervisor.register_agent('test_agent_2', test_agent_info)
            
            # Test recording agent calls
            await supervisor.record_agent_call(
                'test_agent_1', 'test_call', 
                time.time() - 0.1, time.time(), 
                True
            )
            
            await supervisor.record_agent_call(
                'test_agent_2', 'test_call', 
                time.time() - 0.2, time.time(), 
                False, 'Test error'
            )
            
            # Test getting agent status
            status = supervisor.get_agent_status('test_agent_1')
            if status:
                self.logger.log_info("Agent status retrieved", "FailurePreventionTester")
            
            # Test getting all agents status
            all_status = supervisor.get_all_agents_status()
            if all_status:
                self.logger.log_info("All agents status retrieved", "FailurePreventionTester")
            
            # Test getting stats
            stats = supervisor.get_agent_stats()
            if isinstance(stats, dict):
                self.logger.log_info("Agent stats retrieved", "FailurePreventionTester")
            
            # Cleanup
            supervisor.unregister_agent('test_agent_1')
            supervisor.unregister_agent('test_agent_2')
            
            self.test_results['agent_supervisor'] = 'PASS'
            self.logger.log_info("Agent supervisor test PASSED", "FailurePreventionTester")
            
        except Exception as e:
            self.test_results['agent_supervisor'] = 'FAIL'
            self.logger.log_error(f"Agent supervisor test FAILED: {e}", "FailurePreventionTester")
    
    async def test_broker_breaker(self):
        """Test the BrokerBreaker"""
        try:
            self.logger.log_info("Testing broker breaker...", "FailurePreventionTester")
            
            breaker = BrokerBreaker(self.config['broker_circuit_breakers'])
            
            # Test circuit breaker activation
            await breaker.activate('test_broker_1', 'Test activation')
            
            # Test execution check
            can_execute = breaker.can_execute('test_broker_1')
            if not can_execute:
                self.logger.log_info("Circuit breaker correctly blocking execution", "FailurePreventionTester")
            
            # Test recording failures
            await breaker.record_failure('test_broker_2', 'Test failure')
            
            # Test recording success
            await breaker.record_success('test_broker_3')
            
            # Test getting broker status
            status = breaker.get_broker_status('test_broker_1')
            if status:
                self.logger.log_info("Broker status retrieved", "FailurePreventionTester")
            
            # Test getting all brokers status
            all_status = breaker.get_all_brokers_status()
            if all_status:
                self.logger.log_info("All brokers status retrieved", "FailurePreventionTester")
            
            # Test getting stats
            stats = breaker.get_broker_stats()
            if isinstance(stats, dict):
                self.logger.log_info("Broker stats retrieved", "FailurePreventionTester")
            
            self.test_results['broker_breaker'] = 'PASS'
            self.logger.log_info("Broker breaker test PASSED", "FailurePreventionTester")
            
        except Exception as e:
            self.test_results['broker_breaker'] = 'FAIL'
            self.logger.log_error(f"Broker breaker test FAILED: {e}", "FailurePreventionTester")
    
    async def test_failure_prevention_agent(self):
        """Test the main FailurePreventionAgent"""
        try:
            self.logger.log_info("Testing failure prevention agent...", "FailurePreventionTester")
            
            agent = FailurePreventionAgent(self.config)
            
            # Test agent initialization
            if agent.is_connected():
                self.logger.log_info("Agent Redis connection established", "FailurePreventionTester")
            
            # Test reporting events
            await agent.report_event(
                FailureType.AGENT_FAILURE,
                AlertLevel.MEDIUM,
                'test_source',
                'Test failure event',
                {'test_key': 'test_value'}
            )
            
            # Test getting agent status
            status = agent.get_agent_status()
            if status:
                self.logger.log_info("Agent status retrieved", "FailurePreventionTester")
            
            # Test getting incident stats
            incident_stats = agent.get_incident_stats()
            if isinstance(incident_stats, dict):
                self.logger.log_info("Incident stats retrieved", "FailurePreventionTester")
            
            self.test_results['failure_prevention_agent'] = 'PASS'
            self.logger.log_info("Failure prevention agent test PASSED", "FailurePreventionTester")
            
        except Exception as e:
            self.test_results['failure_prevention_agent'] = 'FAIL'
            self.logger.log_error(f"Failure prevention agent test FAILED: {e}", "FailurePreventionTester")
    
    async def test_agent_lifecycle(self):
        """Test the complete agent lifecycle"""
        try:
            self.logger.log_info("Testing agent lifecycle...", "FailurePreventionTester")
            
            agent = FailurePreventionAgent(self.config)
            
            # Start the agent
            start_task = asyncio.create_task(agent.start())
            
            # Let it run for a short time
            await asyncio.sleep(5)
            
            # Report some test events
            for i in range(3):
                await agent.report_event(
                    FailureType.AGENT_FAILURE,
                    AlertLevel.MEDIUM,
                    f'test_source_{i}',
                    f'Test failure event {i}',
                    {'iteration': i}
                )
                await asyncio.sleep(1)
            
            # Stop the agent
            await agent.stop()
            
            # Cancel the start task
            start_task.cancel()
            
            self.test_results['agent_lifecycle'] = 'PASS'
            self.logger.log_info("Agent lifecycle test PASSED", "FailurePreventionTester")
            
        except Exception as e:
            self.test_results['agent_lifecycle'] = 'FAIL'
            self.logger.log_error(f"Agent lifecycle test FAILED: {e}", "FailurePreventionTester")
    
    async def run_all_tests(self):
        """Run all tests"""
        self.logger.log_info("Starting comprehensive failure prevention tests...", "FailurePreventionTester")
        
        test_methods = [
            self.test_redis_integration,
            self.test_logger,
            self.test_incident_cache,
            self.test_agent_supervisor,
            self.test_broker_breaker,
            self.test_failure_prevention_agent,
            self.test_agent_lifecycle
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
                await asyncio.sleep(1)  # Brief pause between tests
            except Exception as e:
                self.logger.log_error(f"Test {test_method.__name__} failed: {e}", "FailurePreventionTester")
                self.test_results[test_method.__name__] = 'FAIL'
        
        # Report results
        self._report_test_results()
    
    def _report_test_results(self):
        """Report test results"""
        self.logger.log_info("=== FAILURE PREVENTION TEST RESULTS ===", "FailurePreventionTester")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result == 'PASS')
        failed_tests = total_tests - passed_tests
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result == 'PASS' else "❌ FAIL"
            self.logger.log_info(f"{test_name}: {status}", "FailurePreventionTester")
        
        self.logger.log_info(f"Total tests: {total_tests}", "FailurePreventionTester")
        self.logger.log_info(f"Passed: {passed_tests}", "FailurePreventionTester")
        self.logger.log_info(f"Failed: {failed_tests}", "FailurePreventionTester")
        
        if failed_tests == 0:
            self.logger.log_info("🎉 ALL TESTS PASSED!", "FailurePreventionTester")
        else:
            self.logger.log_error(f"⚠️  {failed_tests} tests failed", "FailurePreventionTester")

async def main():
    """Main test runner"""
    tester = FailurePreventionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
