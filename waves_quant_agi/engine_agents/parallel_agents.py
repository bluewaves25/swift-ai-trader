#!/usr/bin/env python3
"""
Simplified Parallel Agent Runner - Clean implementation
"""

import os
import sys
import asyncio
import time
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SimpleParallelAgentRunner:
    """Simplified parallel agent runner with clean design."""
    
    def __init__(self):
        """Initialize the runner."""
        # Load environment variables
        load_dotenv()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Agent registry - simplified mapping
        self.agent_registry = {
            'communication_hub': ('CommunicationHub', 'communication.communication_hub'),
            'core': ('EnhancedCoreAgent', 'core.enhanced_core_agent'),
            'data_feeds': ('DataFeedsAgent', 'data_feeds.data_feeds_agent'),
            'market_conditions': ('EnhancedMarketConditionsAgent', 'market_conditions.enhanced_market_conditions_agent'),
            'strategy_engine': ('EnhancedStrategyEngineAgent', 'strategy_engine.enhanced_strategy_engine_agent'),
            'intelligence': ('EnhancedIntelligenceAgent', 'intelligence.enhanced_intelligence_agent'),
            'risk_management': ('EnhancedRiskManagementAgent', 'risk_management.enhanced_risk_management_agent'),
            'execution': ('EnhancedExecutionAgentV2', 'execution.enhanced_execution_agent_v2'),
            'adapters': ('EnhancedAdaptersAgentV2', 'adapters.enhanced_adapters_agent_v2'),
            'validation': ('EnhancedValidationAgentV2', 'validation.enhanced_validation_agent_v2'),
            'failure_prevention': ('EnhancedFailurePreventionAgentV2', 'failure_prevention.enhanced_failure_prevention_agent_v2'),
            'fees_monitor': ('EnhancedFeesMonitorAgentV3', 'fees_monitor.enhanced_fees_monitor_agent_v3'),
        }
        
        # Startup order
        self.startup_order = [
            'communication_hub',  # Start early as other agents depend on it
            'core',
            'data_feeds', 
            'market_conditions',
            'strategy_engine',
            'intelligence',
            'risk_management',
            'execution',
            'adapters',
            'validation',
            'failure_prevention',
            'fees_monitor'
        ]
        
        # Runtime state
        self.running = False
        self.agents = {}
        self.tasks = {}
        self.start_time = None
        
        # Load configuration
        self.config = self._load_config()
        
        self.logger.info("🚀 Simple Parallel Agent Runner initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment."""
        config = {
            'redis_host': os.getenv('REDIS_HOST', 'localhost'),
            'redis_port': int(os.getenv('REDIS_PORT', 6379)),
            'redis_db': int(os.getenv('REDIS_DB', 0)),
            'mt5_login': int(os.getenv('MT5_LOGIN', 12345678)),
            'mt5_password': os.getenv('MT5_PASSWORD', 'demo'),
            'mt5_server': os.getenv('MT5_SERVER', 'MetaQuotes-Demo'),
            'mt5_timeout': int(os.getenv('MT5_TIMEOUT', 60000))
        }
        
        self.logger.info(f"📋 Configuration loaded: MT5={config['mt5_login']}, Redis={config['redis_host']}:{config['redis_port']}")
        return config
    
    async def _start_single_agent(self, agent_name: str, class_name: str, module_path: str) -> bool:
        """Start a single agent."""
        try:
            self.logger.info(f"🚀 Starting {agent_name}...")
            
            # Dynamic import
            try:
                # Try full package path first
                module = __import__(f"engine_agents.{module_path}", fromlist=[class_name])
                agent_class = getattr(module, class_name)
            except ImportError:
                # Fallback to direct import
                module = __import__(module_path, fromlist=[class_name])
                agent_class = getattr(module, class_name)
            
            # Create agent instance
            agent_instance = agent_class(agent_name, self.config)
            
            # Start the agent
            await agent_instance.start()
            
            # Store agent and create monitoring task
            self.agents[agent_name] = agent_instance
            self.tasks[agent_name] = asyncio.create_task(self._monitor_agent(agent_name, agent_instance))
            

            
            self.logger.info(f"✅ {agent_name} started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start {agent_name}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    async def _monitor_agent(self, agent_name: str, agent_instance: Any):
        """Monitor a single agent."""
        try:
            while self.running and agent_name in self.agents:
                # Check if agent is still running
                if hasattr(agent_instance, 'is_running') and not agent_instance.is_running:
                    self.logger.warning(f"⚠️ {agent_name} stopped running")
                    break
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
        except Exception as e:
            self.logger.error(f"❌ Error monitoring {agent_name}: {e}")
        finally:
            self.logger.info(f"🛑 Monitoring stopped for {agent_name}")
    
    async def start(self):
        """Start all agents."""
        if self.running:
            self.logger.warning("⚠️ Runner already running")
            return
        
        self.logger.info("🚀 Starting all agents...")
        self.running = True
        self.start_time = time.time()
        
        # Track results
        successful_agents = []
        failed_agents = []
        
        # Start agents in order
        for agent_name in self.startup_order:
            if agent_name in self.agent_registry:
                class_name, module_path = self.agent_registry[agent_name]
                success = await self._start_single_agent(agent_name, class_name, module_path)
                
                if success:
                    successful_agents.append(agent_name)
                else:
                    failed_agents.append(agent_name)
                
                # Small delay between starts
                await asyncio.sleep(0.1)
        
        # Log results
        total = len(self.startup_order)
        success_count = len(successful_agents)
        failure_count = len(failed_agents)
        
        self.logger.info(f"📊 Startup complete: {success_count}/{total} successful, {failure_count} failed")
        
        if successful_agents:
            self.logger.info(f"✅ Running: {', '.join(successful_agents)}")
        if failed_agents:
            self.logger.warning(f"❌ Failed: {', '.join(failed_agents)}")
    
    async def stop(self):
        """Stop all agents."""
        if not self.running:
            return
        
        self.logger.info("🛑 Stopping all agents...")
        self.running = False
        
        # Stop all agents
        stop_tasks = []
        for agent_name, agent in self.agents.items():
            try:
                stop_tasks.append(agent.stop())
            except Exception as e:
                self.logger.error(f"❌ Error stopping {agent_name}: {e}")
        
        # Wait for agents to stop
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        # Cancel monitoring tasks
        for task in self.tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks.values(), return_exceptions=True)
        
        # Clear state
        self.agents.clear()
        self.tasks.clear()
        
        self.logger.info("✅ All agents stopped")
    
    async def run(self, timeout_seconds: int = None):
        """Main run loop with optional timeout."""
        try:
            await self.start()
            
            if timeout_seconds:
                self.logger.info(f"⏱️ Running for {timeout_seconds} seconds...")
                start_time = time.time()
                
                while self.running and (time.time() - start_time) < timeout_seconds:
                    await asyncio.sleep(1)
                    
                    # Log status every 10 seconds
                    elapsed = int(time.time() - start_time)
                    if elapsed % 10 == 0:
                        active_agents = sum(1 for agent in self.agents.values() if getattr(agent, 'is_running', False))
                        self.logger.info(f"📊 Status: {active_agents} agents running, elapsed: {elapsed}s")
                
                self.logger.info(f"⏱️ Timeout reached ({timeout_seconds}s)")
            else:
                self.logger.info("🔄 Running indefinitely...")
                while self.running:
                    await asyncio.sleep(1)
                    
                    # Log status every 30 seconds
                    if int(time.time()) % 30 == 0:
                        active_agents = sum(1 for agent in self.agents.values() if getattr(agent, 'is_running', False))
                        uptime = int(time.time() - self.start_time)
                        self.logger.info(f"📊 Status: {active_agents} agents running, uptime: {uptime}s")
        
        except KeyboardInterrupt:
            self.logger.info("🛑 Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        finally:
            await self.stop()

async def main():
    """Main entry point."""
    print("🚀 Starting Simple Parallel Agent Runner...")
    
    runner = SimpleParallelAgentRunner()
    
    try:
        # Run indefinitely (no timeout)
        await runner.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔄 Shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
