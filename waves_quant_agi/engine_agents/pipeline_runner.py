#!/usr/bin/env python3
"""
Pipeline Runner - Main coordinator for the AI trading engine pipeline
Replaces the old parallel_agents.py with a clean, orchestrated approach
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

from engine_agents.core.pipeline_orchestrator import PipelineOrchestrator
from shared_utils.redis_connector import SharedRedisConnector

class PipelineRunner:
    """Main pipeline runner for the AI trading engine."""
    
    def __init__(self):
        """Initialize the pipeline runner."""
        # Load environment variables
        load_dotenv()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Agent registry with clear roles
        self.agent_registry = {
            'communication_hub': {
                'class': 'CommunicationHub',
                'module': 'engine_agents.communication.communication_hub',
                'role': 'Inter-agent communication only',
                'startup_order': 1
            },
            'core': {
                'class': 'EnhancedCoreAgent',
                'module': 'engine_agents.core.enhanced_core_agent',
                'role': 'System coordination + ALL system monitoring',
                'startup_order': 2
            },
            'data_feeds': {
                'class': 'DataFeedsAgent',
                'module': 'engine_agents.data_feeds.data_feeds_agent',
                'role': 'Data collection/distribution only',
                'startup_order': 3
            },
            'validation': {
                'class': 'EnhancedValidationAgentV2',
                'module': 'engine_agents.validation.enhanced_validation_agent_v2',
                'role': 'Data validation only',
                'startup_order': 4
            },
            'market_conditions': {
                'class': 'EnhancedMarketConditionsAgent',
                'module': 'engine_agents.market_conditions.enhanced_market_conditions_agent',
                'role': 'Anomaly detection only',
                'startup_order': 5
            },
            'intelligence': {
                'class': 'EnhancedIntelligenceAgent',
                'module': 'engine_agents.intelligence.enhanced_intelligence_agent',
                'role': 'Pattern recognition only',
                'startup_order': 6
            },
            'strategy_engine': {
                'class': 'StrategyEnhancementManager',
                'module': 'engine_agents.strategy_engine.strategy_enhancement_manager',
                'role': 'Strategy management + optimization + learning',
                'startup_order': 7
            },
            'risk_management': {
                'class': 'EnhancedRiskManagementAgent',
                'module': 'engine_agents.risk_management.enhanced_risk_management_agent',
                'role': 'Risk validation + portfolio monitoring only',
                'startup_order': 8
            },
            'execution': {
                'class': 'EnhancedExecutionAgentV2',
                'module': 'engine_agents.execution.enhanced_execution_agent_v2',
                'role': 'Order execution + slippage only',
                'startup_order': 9
            },
            'adapters': {
                'class': 'EnhancedAdaptersAgentV2',
                'module': 'engine_agents.adapters.enhanced_adapters_agent_v2',
                'role': 'Connection management only',
                'startup_order': 10
            },
            'failure_prevention': {
                'class': 'EnhancedFailurePreventionAgentV2',
                'module': 'engine_agents.failure_prevention.enhanced_failure_prevention_agent_v2',
                'role': 'Failure prediction only',
                'startup_order': 11
            },
            'fees_monitor': {
                'class': 'EnhancedFeesMonitorAgentV3',
                'module': 'engine_agents.fees_monitor.enhanced_fees_monitor_agent_v3',
                'role': 'Cost tracking only (NOT optimization)',
                'startup_order': 12
            }
        }
        
        # Pipeline state
        self.pipeline_state = {
            "status": "initializing",
            "start_time": time.time(),
            "agents_started": 0,
            "total_agents": len(self.agent_registry),
            "current_phase": "initialization"
        }
        
        # Agent instances
        self.agents = {}
        self.agent_tasks = {}
        
        # Pipeline orchestrator
        self.pipeline_orchestrator = None
        
        # Redis connection
        self.redis_conn = None
        
        # Load configuration
        self.config = self._load_config()
        
        self.logger.info("🚀 Pipeline Runner initialized")
    
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
    
    async def start(self):
        """Start the complete pipeline."""
        try:
            self.logger.info("🚀 Starting AI Trading Engine Pipeline...")
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Initialize pipeline orchestrator
            await self._initialize_pipeline_orchestrator()
            
            # Start agents in sequence
            await self._start_agents_sequentially()
            
            # Start pipeline orchestrator
            await self.pipeline_orchestrator.start()
            
            # Update pipeline state
            self.pipeline_state["status"] = "running"
            self.pipeline_state["current_phase"] = "operational"
            
            self.logger.info("✅ AI Trading Engine Pipeline started successfully")
            
            # Start monitoring loop
            await self._monitoring_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Error starting pipeline: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the complete pipeline."""
        try:
            self.logger.info("🛑 Stopping AI Trading Engine Pipeline...")
            
            # Stop pipeline orchestrator
            if self.pipeline_orchestrator:
                await self.pipeline_orchestrator.stop()
            
            # Stop all agents
            await self._stop_all_agents()
            
            # Close Redis connection
            if self.redis_conn:
                await self.redis_conn.close()
            
            self.pipeline_state["status"] = "stopped"
            self.logger.info("✅ AI Trading Engine Pipeline stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping pipeline: {e}")
    
    async def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_conn = SharedRedisConnector(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                db=self.config['redis_db']
            )
            await self.redis_conn.ensure_async_connection()
            self.logger.info("✅ Redis connection established")
            
        except Exception as e:
            self.logger.error(f"❌ Error connecting to Redis: {e}")
            raise
    
    async def _initialize_pipeline_orchestrator(self):
        """Initialize the pipeline orchestrator."""
        try:
            self.pipeline_orchestrator = PipelineOrchestrator(
                redis_conn=self.redis_conn,
                logger=self.logger
            )
            self.logger.info("✅ Pipeline Orchestrator initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing Pipeline Orchestrator: {e}")
            raise
    
    async def _start_agents_sequentially(self):
        """Start agents in the correct sequence."""
        try:
            # Sort agents by startup order
            sorted_agents = sorted(
                self.agent_registry.items(),
                key=lambda x: x[1]['startup_order']
            )
            
            for agent_name, agent_info in sorted_agents:
                try:
                    self.logger.info(f"🚀 Starting {agent_name} (Order: {agent_info['startup_order']})...")
                    
                    # Start agent
                    agent_instance = await self._start_single_agent(agent_name, agent_info)
                    
                    if agent_instance:
                        self.agents[agent_name] = agent_instance
                        self.pipeline_state["agents_started"] += 1
                        
                        # Wait for agent to be ready
                        await self._wait_for_agent_ready(agent_name)
                        
                        self.logger.info(f"✅ {agent_name} started successfully")
                        
                        # Update pipeline phase
                        await self._update_pipeline_phase()
                        
                    else:
                        self.logger.warning(f"⚠️ Failed to start {agent_name} - continuing with other agents")
                        # Don't raise exception, continue with other agents
                        continue
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Error starting {agent_name}: {e} - continuing with other agents")
                    # Don't raise exception, continue with other agents
                    continue
            
            if self.pipeline_state["agents_started"] > 0:
                self.logger.info(f"✅ {self.pipeline_state['agents_started']} out of {self.pipeline_state['total_agents']} agents started successfully")
            else:
                raise Exception("No agents could be started")
            
        except Exception as e:
            self.logger.error(f"❌ Critical error in agent startup: {e}")
            raise
    
    async def _start_single_agent(self, agent_name: str, agent_info: Dict[str, Any]):
        """Start a single agent."""
        try:
            # Dynamic import using full package path
            try:
                module_path = agent_info['module']
                module = __import__(module_path, fromlist=[agent_info['class']])
                agent_class = getattr(module, agent_info['class'])
            except ImportError as e:
                self.logger.error(f"Import error for {agent_name}: {e}")
                return None
            
            # Create agent instance - all agents extend BaseAgent which expects (agent_name, config)
            agent_instance = agent_class(agent_name, self.config)
            
            # Start agent
            await agent_instance.start()
            
            return agent_instance
            
        except Exception as e:
            self.logger.error(f"Error starting {agent_name}: {e}")
            return None
    
    async def _wait_for_agent_ready(self, agent_name: str):
        """Wait for an agent to be ready."""
        try:
            max_wait_time = 30  # 30 seconds max wait
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                # Check if agent is ready (this would check Redis or agent status)
                if await self._is_agent_ready(agent_name):
                    return True
                
                await asyncio.sleep(0.5)
            
            raise Exception(f"Agent {agent_name} did not become ready within {max_wait_time} seconds")
            
        except Exception as e:
            self.logger.error(f"Error waiting for {agent_name} to be ready: {e}")
            raise
    
    async def _is_agent_ready(self, agent_name: str) -> bool:
        """Check if an agent is ready."""
        try:
            # This would typically check Redis for agent status
            # For now, assume agent is ready after startup
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking agent readiness: {e}")
            return False
    
    async def _update_pipeline_phase(self):
        """Update pipeline phase based on agent status."""
        try:
            if self.pipeline_state["agents_started"] == 1:
                self.pipeline_state["current_phase"] = "communication_established"
            elif self.pipeline_state["agents_started"] == 2:
                self.pipeline_state["current_phase"] = "core_coordination_active"
            elif self.pipeline_state["agents_started"] == 6:
                self.pipeline_state["current_phase"] = "data_pipeline_active"
            elif self.pipeline_state["agents_started"] == 8:
                self.pipeline_state["current_phase"] = "trading_pipeline_active"
            elif self.pipeline_state["agents_started"] == self.pipeline_state["total_agents"]:
                self.pipeline_state["current_phase"] = "fully_operational"
            
            self.logger.info(f"🔄 Pipeline phase updated: {self.pipeline_state['current_phase']}")
            
        except Exception as e:
            self.logger.error(f"Error updating pipeline phase: {e}")
    
    async def _stop_all_agents(self):
        """Stop all running agents."""
        try:
            for agent_name, agent_instance in self.agents.items():
                try:
                    self.logger.info(f"🛑 Stopping {agent_name}...")
                    await agent_instance.stop()
                    self.logger.info(f"✅ {agent_name} stopped successfully")
                except Exception as e:
                    self.logger.error(f"❌ Error stopping {agent_name}: {e}")
            
            self.agents.clear()
            
        except Exception as e:
            self.logger.error(f"Error stopping agents: {e}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for the pipeline."""
        try:
            while self.pipeline_state["status"] == "running":
                try:
                    # Get pipeline status
                    pipeline_status = await self.pipeline_orchestrator.get_pipeline_status()
                    
                    # Get signal tracking
                    signal_tracking = await self.pipeline_orchestrator.get_signal_tracking()
                    
                    # Get execution tracking
                    execution_tracking = await self.pipeline_orchestrator.get_execution_tracking()
                    
                    # Get performance analysis
                    performance_analysis = await self.pipeline_orchestrator.get_performance_analysis()
                    
                    # Log pipeline status
                    self._log_pipeline_status(pipeline_status, signal_tracking, execution_tracking, performance_analysis)
                    
                    # Check for critical issues
                    await self._check_critical_issues(pipeline_status, performance_analysis)
                    
                    await asyncio.sleep(5.0)  # 5 second monitoring cycle
                    
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(10.0)
                    
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
    
    def _log_pipeline_status(self, pipeline_status: Dict[str, Any], signal_tracking: Dict[str, Any], 
                            execution_tracking: Dict[str, Any], performance_analysis: Dict[str, Any]):
        """Log current pipeline status."""
        try:
            self.logger.info("📊 PIPELINE STATUS UPDATE")
            self.logger.info(f"   Phase: {pipeline_status.get('phase', 'unknown')}")
            self.logger.info(f"   Health: {pipeline_status.get('health', 0.0):.2f}")
            self.logger.info(f"   Signals: {signal_tracking.get('active_signals', 0)} active, {signal_tracking.get('processed_signals', 0)} processed")
            self.logger.info(f"   Orders: {execution_tracking.get('active_orders', 0)} active, {execution_tracking.get('processed_orders', 0)} processed")
            self.logger.info(f"   Throughput: {pipeline_status.get('metrics', {}).get('system_throughput', 0.0):.2f} ops/sec")
            
        except Exception as e:
            self.logger.error(f"Error logging pipeline status: {e}")
    
    async def _check_critical_issues(self, pipeline_status: Dict[str, Any], performance_analysis: Dict[str, Any]):
        """Check for critical issues in the pipeline."""
        try:
            # Check pipeline health
            if pipeline_status.get('health', 1.0) < 0.5:
                self.logger.critical("🚨 CRITICAL: Pipeline health is critically low!")
                
            # Check for bottlenecks
            bottlenecks = performance_analysis.get('bottleneck_analysis', {})
            for bottleneck_name, bottleneck_info in bottlenecks.items():
                if bottleneck_info.get('severity') == 'high':
                    self.logger.critical(f"🚨 CRITICAL: High severity bottleneck detected: {bottleneck_name}")
                    
            # Check circuit breakers
            circuit_breakers = performance_analysis.get('circuit_breakers', {})
            for breaker_name, breaker_info in circuit_breakers.items():
                if breaker_info.get('active', False):
                    self.logger.warning(f"⚠️ Circuit breaker active: {breaker_name}")
                    
        except Exception as e:
            self.logger.error(f"Error checking critical issues: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get complete pipeline status."""
        try:
            if not self.pipeline_orchestrator:
                return {"error": "Pipeline orchestrator not initialized"}
            
            pipeline_status = await self.pipeline_orchestrator.get_pipeline_status()
            signal_tracking = await self.pipeline_orchestrator.get_signal_tracking()
            execution_tracking = await self.pipeline_orchestrator.get_execution_tracking()
            performance_analysis = await self.pipeline_orchestrator.get_performance_analysis()
            
            return {
                "pipeline_state": self.pipeline_state,
                "pipeline_status": pipeline_status,
                "signal_tracking": signal_tracking,
                "execution_tracking": execution_tracking,
                "performance_analysis": performance_analysis,
                "agents": {
                    name: {
                        "status": "running" if agent else "stopped",
                        "role": self.agent_registry[name]["role"]
                    }
                    for name, agent in self.agents.items()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting pipeline status: {e}")
            return {"error": str(e)}
    
    async def submit_signal(self, signal_data: Dict[str, Any]) -> str:
        """Submit a signal to the pipeline."""
        try:
            if not self.pipeline_orchestrator:
                raise Exception("Pipeline orchestrator not initialized")
            
            return await self.pipeline_orchestrator.submit_signal(signal_data)
            
        except Exception as e:
            self.logger.error(f"Error submitting signal: {e}")
            return None
    
    async def submit_execution(self, order_data: Dict[str, Any]) -> str:
        """Submit an order to the pipeline."""
        try:
            if not self.pipeline_orchestrator:
                raise Exception("Pipeline orchestrator not initialized")
            
            return await self.pipeline_orchestrator.submit_execution(order_data)
            
        except Exception as e:
            self.logger.error(f"Error submitting order: {e}")
            return None

# ============= MAIN EXECUTION =============

async def main():
    """Main execution function."""
    pipeline_runner = PipelineRunner()
    
    try:
        # Start the pipeline
        await pipeline_runner.start()
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
    finally:
        # Stop the pipeline
        await pipeline_runner.stop()

if __name__ == "__main__":
    # Run the pipeline
    asyncio.run(main())
