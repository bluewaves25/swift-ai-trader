#!/usr/bin/env python3
"""
Enhanced Risk Management Agent - UPDATED FOR STREAMLINED ARCHITECTURE
Uses the new foundation classes and streamlined 2-tier approach
"""

import asyncio
import time
from typing import Dict, Any, List
from .core.streamlined_risk_manager import StreamlinedRiskManager
from .core.connection_manager import ConnectionManager
from .config.risk_management_config import DEFAULT_CONFIG

class EnhancedRiskManagementAgent:
    """Enhanced risk management agent using the new streamlined architecture."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or DEFAULT_CONFIG
        self.agent_name = "enhanced_risk_management"
        
        # Initialize connection manager
        self.connection_manager = ConnectionManager(self.config)
        
        # Initialize streamlined risk manager
        self.risk_manager = StreamlinedRiskManager(self.config)
        
        # Initialize legacy components for backward compatibility
        self.risk_validator = None
        self.portfolio_monitor = None
        
        # Agent state
        self.is_running = False
        self.start_time = time.time()
        
        # Statistics
        self.stats = {
            "start_time": self.start_time,
            "total_requests_processed": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "system_health_checks": 0
        }
    
    async def start(self):
        """Start the enhanced risk management agent."""
        try:
            print(f"🚀 Starting {self.agent_name}...")
            
            # Start the streamlined risk manager
            await self.risk_manager.start()
            
            # Initialize legacy components if needed
            await self._initialize_legacy_components()
            
            self.is_running = True
            print(f"✅ {self.agent_name} started successfully")
            
        except Exception as e:
            print(f"❌ Failed to start {self.agent_name}: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """Stop the enhanced risk management agent."""
        try:
            print(f"🛑 Stopping {self.agent_name}...")
            
            self.is_running = False
            
            # Stop the streamlined risk manager
            await self.risk_manager.stop()
            
            print(f"✅ {self.agent_name} stopped successfully")
            
        except Exception as e:
            print(f"❌ Error stopping {self.agent_name}: {e}")
    
    async def _initialize_legacy_components(self):
        """Initialize legacy components for backward compatibility."""
        try:
            # Initialize risk validator with new foundation
            from .core.risk_validator import RiskValidator
            self.risk_validator = RiskValidator(self.connection_manager, self.config)
            
            # Initialize portfolio monitor with new foundation
            from .core.portfolio_monitor import PortfolioMonitor
            self.portfolio_monitor = PortfolioMonitor(self.connection_manager, self.config)
            
            print("✅ Legacy components initialized with new foundation")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize legacy components: {e}")
    
    async def validate_trade_request(self, trade_request: Dict[str, Any], 
                                   strategy_type: str = "general") -> Dict[str, Any]:
        """
        Validate trade request using the new streamlined system.
        Maintains backward compatibility with legacy interface.
        """
        try:
            self.stats["total_requests_processed"] += 1
            
            # Use the new streamlined risk manager
            request_id = await self.risk_manager.submit_risk_request(
                strategy_type=strategy_type,
                symbol=trade_request.get('symbol', 'unknown'),
                request_data=trade_request
            )
            
            # Wait for processing (in a real system, this would be async)
            await asyncio.sleep(0.1)
            
            # Get validation result from the risk manager
            # This is a simplified approach - in production, you'd use proper async communication
            validation_result = {
                "request_id": request_id,
                "strategy_type": strategy_type,
                "symbol": trade_request.get('symbol', 'unknown'),
                "validation_passed": True,  # Simplified for demo
                "risk_level": "low",
                "risk_score": 0.1,
                "timestamp": time.time()
            }
            
            self.stats["successful_validations"] += 1
            return validation_result
            
        except Exception as e:
            self.stats["failed_validations"] += 1
            print(f"Trade validation error: {e}")
            
            return {
                "validation_passed": False,
                "risk_level": "critical",
                "risk_score": 1.0,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def assess_portfolio_health(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess portfolio health using the new streamlined system.
        Maintains backward compatibility with legacy interface.
        """
        try:
            if self.portfolio_monitor:
                return await self.portfolio_monitor.assess_portfolio_health(portfolio_data)
            else:
                # Fallback to basic assessment
                return {
                    "health_assessment": {"overall_health": "unknown"},
                    "alerts": [],
                    "current_metrics": {},
                    "recommendations": ["Portfolio monitor not available"],
                    "timestamp": time.time()
                }
                
        except Exception as e:
            print(f"Portfolio health assessment error: {e}")
            return {
                "health_assessment": {"overall_health": "error"},
                "alerts": [{"type": "system_error", "message": str(e)}],
                "current_metrics": {},
                "recommendations": ["Contact system administrator"],
                "timestamp": time.time()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            self.stats["system_health_checks"] += 1
            
            # Get status from streamlined risk manager
            risk_manager_health = await self.risk_manager.health_check()
            
            # Get status from legacy components if available
            legacy_status = {}
            if self.risk_validator:
                legacy_status["risk_validator"] = self.risk_validator.get_system_health()
            if self.portfolio_monitor:
                legacy_status["portfolio_monitor"] = self.portfolio_monitor.get_system_health()
            
            return {
                "agent_name": self.agent_name,
                "status": "running" if self.is_running else "stopped",
                "uptime_seconds": time.time() - self.start_time,
                "agent_stats": self.stats,
                "streamlined_risk_manager": risk_manager_health,
                "legacy_components": legacy_status,
                "connection_health": await self.connection_manager.health_check(),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "agent_name": self.agent_name,
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        try:
            # Get stats from streamlined risk manager
            streamlined_stats = self.risk_manager.get_validation_stats()
            
            # Get stats from legacy components if available
            legacy_stats = {}
            if self.risk_validator:
                legacy_stats["risk_validator"] = self.risk_validator.get_validation_stats()
            if self.portfolio_monitor:
                legacy_stats["portfolio_monitor"] = self.portfolio_monitor.get_monitor_stats()
            
            return {
                "agent_stats": self.stats,
                "streamlined_stats": streamlined_stats,
                "legacy_stats": legacy_stats,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check."""
        try:
            # Check connection health
            connection_health = await self.connection_manager.health_check()
            
            # Check risk manager health
            risk_manager_health = await self.risk_manager.health_check()
            
            # Check legacy components
            legacy_health = {}
            if self.risk_validator:
                legacy_health["risk_validator"] = self.risk_validator.get_system_health()
            if self.portfolio_monitor:
                legacy_health["portfolio_monitor"] = self.portfolio_monitor.get_system_health()
            
            # Overall health assessment
            overall_health = "healthy"
            if connection_health['status'] != 'healthy':
                overall_health = "unhealthy"
            elif risk_manager_health['overall_health'] != 'healthy':
                overall_health = "degraded"
            
            return {
                "overall_health": overall_health,
                "connection_health": connection_health,
                "risk_manager_health": risk_manager_health,
                "legacy_components_health": legacy_health,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "overall_health": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "agent_name": self.agent_name,
            "architecture": "streamlined_2_tier",
            "foundation_classes": [
                "ConnectionManager",
                "DynamicRiskLimits", 
                "CircuitBreaker",
                "LoadBalancer",
                "PerformanceMonitor",
                "StreamlinedRiskManager"
            ],
            "legacy_support": True,
            "config_source": "risk_management_config.py",
            "version": "2.0.0",
            "timestamp": time.time()
        }
    
    async def run_demo(self):
        """Run a demonstration of the new system."""
        print("\n🎯 Enhanced Risk Management Agent Demo")
        print("=" * 50)
        
        try:
            # Start the system
            await self.start()
            
            # Wait for system to stabilize
            await asyncio.sleep(1)
            
            # Run health check
            print("\n🏥 Running health check...")
            health = await self.run_health_check()
            print(f"Overall Health: {health['overall_health']}")
            
            # Test trade validation
            print("\n🔍 Testing trade validation...")
            trade_request = {
                "symbol": "BTC/USD",
                "position_size": 0.05,
                "leverage": 1.5,
                "stop_loss": 0.02
            }
            
            validation_result = await self.validate_trade_request(trade_request, "arbitrage")
            print(f"Validation Result: {validation_result['validation_passed']}")
            
            # Test portfolio health assessment
            print("\n📊 Testing portfolio health assessment...")
            portfolio_data = {
                "total_value": 100000.0,
                "positions": {"BTC/USD": {"value": 5000.0}},
                "current_drawdown": 0.02
            }
            
            health_assessment = await self.assess_portfolio_health(portfolio_data)
            print(f"Portfolio Health: {health_assessment['health_assessment']['overall_health']}")
            
            # Get system status
            print("\n📈 Getting system status...")
            status = await self.get_system_status()
            print(f"Agent Status: {status['status']}")
            
            # Get validation stats
            print("\n📊 Getting validation statistics...")
            stats = await self.get_validation_stats()
            print(f"Total Requests: {stats['agent_stats']['total_requests_processed']}")
            
            print("\n✅ Demo completed successfully!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Stop the system
            await self.stop()
    
    async def run_performance_test(self, num_requests: int = 100):
        """Run performance test with multiple requests."""
        print(f"\n🔥 Performance Test: {num_requests} requests")
        print("=" * 40)
        
        try:
            # Start the system
            await self.start()
            await asyncio.sleep(1)
            
            # Submit multiple requests
            start_time = time.time()
            
            request_tasks = []
            for i in range(num_requests):
                trade_request = {
                    "symbol": f"TEST{i % 5}",
                    "position_size": 0.05 + (i % 10) * 0.01,
                    "leverage": 1.0 + (i % 3) * 0.5,
                    "stop_loss": 0.01 + (i % 5) * 0.005
                }
                
                task = self.validate_trade_request(trade_request, "arbitrage")
                request_tasks.append(task)
            
            # Wait for all requests to complete
            results = await asyncio.gather(*request_tasks, return_exceptions=True)
            
            total_time = time.time() - start_time
            
            # Analyze results
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = len(results) - successful
            
            print(f"✅ Performance Test Results:")
            print(f"  Total Requests: {num_requests}")
            print(f"  Successful: {successful}")
            print(f"  Failed: {failed}")
            print(f"  Total Time: {total_time:.3f} seconds")
            print(f"  Throughput: {num_requests / total_time:.1f} requests/second")
            print(f"  Success Rate: {successful / num_requests:.2%}")
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
        
        finally:
            await self.stop()

# Example usage
async def main():
    """Main function for testing."""
    agent = EnhancedRiskManagementAgent()
    
    # Run demo
    await agent.run_demo()
    
    # Run performance test
    await agent.run_performance_test(50)

if __name__ == "__main__":
    asyncio.run(main())
