#!/usr/bin/env python3
"""
Parallel Agent Runner
Manages all trading agents in parallel with comprehensive coordination and monitoring.
"""

import asyncio
import time
import signal
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import redis

# Import all our cleaned agents
from .core.core_agent import CoreAgent
from .data_feeds.data_feeds_agent import DataFeedsAgent
from .market_conditions.market_conditions_agent import MarketConditionsAgent
from .intelligence.intelligence_agent import IntelligenceAgent
from .strategy_engine.strategy_engine_agent import StrategyEngineAgent
from .risk_management.risk_management_agent import RiskManagementAgent
from .execution.python_bridge import ExecutionBridge
from .validation.python_bridge import ValidationBridge
from .fees_monitor.fees_monitor_agent import FeesMonitorAgent
from .adapters.adapters_agent import AdaptersAgent
from .failure_prevention.failure_prevention_agent import FailurePreventionAgent

class AgentStatus(Enum):
    """Agent status enumeration"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    STOPPING = "stopping"

@dataclass
class AgentInfo:
    """Information about an agent"""
    name: str
    agent: Any
    status: AgentStatus
    start_time: Optional[float] = None
    error_message: Optional[str] = None
    restart_count: int = 0
    last_heartbeat: Optional[float] = None

class ParallelAgentRunner:
    """
    Parallel Agent Runner
    Manages all trading agents in parallel with comprehensive coordination.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = self._init_logger()
        
        # Initialize Redis
        self._init_redis()
        
        # Agent management
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        
        # Monitoring
        self.monitoring_task = None
        self.heartbeat_interval = self.config.get('heartbeat_interval', 30)
        self.restart_delay = self.config.get('restart_delay', 5)
        self.max_restarts = self.config.get('max_restarts', 3)
        
        # Performance metrics
        self.metrics = {
            'total_agents': 0,
            'running_agents': 0,
            'error_agents': 0,
            'total_restarts': 0,
            'uptime_seconds': 0
        }
        
        # Signal handling
        self._setup_signal_handlers()
        
    def _init_logger(self):
        """Initialize runner logger"""
        from .core.logs.core_agent_logger import CoreAgentLogger
        return CoreAgentLogger("parallel_agent_runner")
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            redis_host = self.config.get('redis_host', 'localhost')
            redis_port = self.config.get('redis_port', 6379)
            redis_db = self.config.get('redis_db', 0)
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            self.redis_client.ping()
            self.logger.log_info("Parallel Agent Runner Redis connection established")
            
        except Exception as e:
            self.logger.log_error("Redis connection failed", str(e), "ParallelAgentRunner")
            self.redis_client = None
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.log_info(f"Received signal {signum}, initiating graceful shutdown")
            asyncio.create_task(self.stop_all_agents())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _initialize_agents(self):
        """Initialize all agents"""
        try:
            # Core orchestrator
            self.agents['core'] = AgentInfo(
                name='core',
                agent=CoreAgent(self.config),
                status=AgentStatus.STOPPED
            )
            
            # Data collection and market sensing
            self.agents['data_feeds'] = AgentInfo(
                name='data_feeds',
                agent=DataFeedsAgent(self.config),
                status=AgentStatus.STOPPED
            )
            
            self.agents['market_conditions'] = AgentInfo(
                name='market_conditions',
                agent=MarketConditionsAgent(self.config),
                status=AgentStatus.STOPPED
            )
            
            # Analysis and intelligence
            self.agents['intelligence'] = AgentInfo(
                name='intelligence',
                agent=IntelligenceAgent(self.config),
                status=AgentStatus.STOPPED
            )
            
            # Strategy and risk management
            self.agents['strategy_engine'] = AgentInfo(
                name='strategy_engine',
                agent=StrategyEngineAgent(self.config),
                status=AgentStatus.STOPPED
            )
            
            self.agents['risk_management'] = AgentInfo(
                name='risk_management',
                agent=RiskManagementAgent(self.config),
                status=AgentStatus.STOPPED
            )
            
            # Execution and validation
            self.agents['execution'] = AgentInfo(
                name='execution',
                agent=ExecutionBridge(self.config),
                status=AgentStatus.STOPPED
            )
            
            self.agents['validation'] = AgentInfo(
                name='validation',
                agent=ValidationBridge(self.config),
                status=AgentStatus.STOPPED
            )
            
            # Monitoring and optimization
            self.agents['fees_monitor'] = AgentInfo(
                name='fees_monitor',
                agent=FeesMonitorAgent(self.config),
                status=AgentStatus.STOPPED
            )
            
            self.agents['adapters'] = AgentInfo(
                name='adapters',
                agent=AdaptersAgent(self.config),
                status=AgentStatus.STOPPED
            )
            
            self.agents['failure_prevention'] = AgentInfo(
                name='failure_prevention',
                agent=FailurePreventionAgent(self.config),
                status=AgentStatus.STOPPED
            )
            
            self.metrics['total_agents'] = len(self.agents)
            self.logger.log_info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            self.logger.log_error("Agent initialization failed", str(e), "ParallelAgentRunner")
            raise
    
    async def start_all_agents(self):
        """Start all agents in parallel"""
        try:
            if self.is_running:
                self.logger.log_info("Agent runner is already running")
                return
            
            self.logger.log_info("Starting all agents in parallel...")
            self.is_running = True
            
            # Initialize agents
            self._initialize_agents()
            
            # Start all agents concurrently
            start_tasks = []
            for agent_name, agent_info in self.agents.items():
                task = asyncio.create_task(self._start_agent(agent_name, agent_info))
                start_tasks.append(task)
            
            # Wait for all agents to start
            await asyncio.gather(*start_tasks, return_exceptions=True)
            
            # Start monitoring
            self.monitoring_task = asyncio.create_task(self._monitor_agents())
            
            self.logger.log_info("All agents started successfully")
            
        except Exception as e:
            self.logger.log_error("Failed to start all agents", str(e), "ParallelAgentRunner")
            raise
    
    async def stop_all_agents(self):
        """Stop all agents gracefully"""
        try:
            if not self.is_running:
                self.logger.log_info("Agent runner is not running")
                return
            
            self.logger.log_info("Stopping all agents...")
            self.is_running = False
            
            # Stop monitoring
            if self.monitoring_task:
                self.monitoring_task.cancel()
            
            # Stop all agent tasks
            stop_tasks = []
            for agent_name, task in self.agent_tasks.items():
                if not task.done():
                    task.cancel()
                    stop_tasks.append(task)
            
            # Wait for all tasks to complete
            if stop_tasks:
                await asyncio.gather(*stop_tasks, return_exceptions=True)
            
            # Stop all agents
            for agent_name, agent_info in self.agents.items():
                await self._stop_agent(agent_name, agent_info)
            
            self.logger.log_info("All agents stopped successfully")
            
        except Exception as e:
            self.logger.log_error("Failed to stop all agents", str(e), "ParallelAgentRunner")
            raise
    
    async def _start_agent(self, agent_name: str, agent_info: AgentInfo):
        """Start a single agent"""
        try:
            self.logger.log_info(f"Starting agent: {agent_name}")
            agent_info.status = AgentStatus.STARTING
            agent_info.start_time = time.time()
            
            # Start the agent
            if hasattr(agent_info.agent, 'start'):
                await agent_info.agent.start()
            
            # Update status
            agent_info.status = AgentStatus.RUNNING
            agent_info.last_heartbeat = time.time()
            
            # Create monitoring task
            task = asyncio.create_task(self._monitor_agent(agent_name, agent_info))
            self.agent_tasks[agent_name] = task
            
            self.metrics['running_agents'] += 1
            self.logger.log_info(f"Agent {agent_name} started successfully")
            
        except Exception as e:
            agent_info.status = AgentStatus.ERROR
            agent_info.error_message = str(e)
            self.metrics['error_agents'] += 1
            self.logger.log_error(f"Failed to start agent {agent_name}", str(e), "ParallelAgentRunner")
    
    async def _stop_agent(self, agent_name: str, agent_info: AgentInfo):
        """Stop a single agent"""
        try:
            self.logger.log_info(f"Stopping agent: {agent_name}")
            agent_info.status = AgentStatus.STOPPING
            
            # Stop the agent
            if hasattr(agent_info.agent, 'stop'):
                await agent_info.agent.stop()
            
            # Update status
            agent_info.status = AgentStatus.STOPPED
            agent_info.start_time = None
            agent_info.error_message = None
            
            self.logger.log_info(f"Agent {agent_name} stopped successfully")
            
        except Exception as e:
            self.logger.log_error(f"Failed to stop agent {agent_name}", str(e), "ParallelAgentRunner")
    
    async def _monitor_agent(self, agent_name: str, agent_info: AgentInfo):
        """Monitor a single agent"""
        try:
            while self.is_running and agent_info.status == AgentStatus.RUNNING:
                try:
                    # Check agent health
                    if hasattr(agent_info.agent, 'is_connected'):
                        is_healthy = agent_info.agent.is_connected()
                    else:
                        is_healthy = True
                    
                    if is_healthy:
                        agent_info.last_heartbeat = time.time()
                        agent_info.error_message = None
                    else:
                        raise Exception("Agent health check failed")
                    
                    await asyncio.sleep(self.heartbeat_interval)
                    
                except Exception as e:
                    self.logger.log_error(f"Agent {agent_name} health check failed", str(e), "ParallelAgentRunner")
                    agent_info.status = AgentStatus.ERROR
                    agent_info.error_message = str(e)
                    self.metrics['error_agents'] += 1
                    
                    # Attempt restart if within limits
                    if agent_info.restart_count < self.max_restarts:
                        await self._restart_agent(agent_name, agent_info)
                    else:
                        self.logger.log_error(f"Agent {agent_name} exceeded max restarts", "ParallelAgentRunner")
                        break
                    
        except asyncio.CancelledError:
            self.logger.log_info(f"Agent {agent_name} monitoring cancelled")
        except Exception as e:
            self.logger.log_error(f"Agent {agent_name} monitoring failed", str(e), "ParallelAgentRunner")
    
    async def _restart_agent(self, agent_name: str, agent_info: AgentInfo):
        """Restart a failed agent"""
        try:
            self.logger.log_info(f"Restarting agent: {agent_name}")
            agent_info.restart_count += 1
            self.metrics['total_restarts'] += 1
            
            # Stop the agent
            await self._stop_agent(agent_name, agent_info)
            
            # Wait before restart
            await asyncio.sleep(self.restart_delay)
            
            # Start the agent
            await self._start_agent(agent_name, agent_info)
            
        except Exception as e:
            self.logger.log_error(f"Failed to restart agent {agent_name}", str(e), "ParallelAgentRunner")
    
    async def _monitor_agents(self):
        """Monitor all agents and report status"""
        try:
            while self.is_running:
                try:
                    # Update metrics
                    running_count = sum(1 for info in self.agents.values() if info.status == AgentStatus.RUNNING)
                    error_count = sum(1 for info in self.agents.values() if info.status == AgentStatus.ERROR)
                    
                    self.metrics['running_agents'] = running_count
                    self.metrics['error_agents'] = error_count
                    
                    # Report status
                    await self._report_agent_status()
                    
                    # Check for critical failures
                    if error_count > len(self.agents) // 2:
                        self.logger.log_error("Critical: More than half of agents are in error state", "ParallelAgentRunner")
                    
                    await asyncio.sleep(60)  # Report every minute
                    
                except Exception as e:
                    self.logger.log_error("Agent monitoring error", str(e), "ParallelAgentRunner")
                    await asyncio.sleep(30)
                    
        except asyncio.CancelledError:
            self.logger.log_info("Agent monitoring cancelled")
        except Exception as e:
            self.logger.log_error("Agent monitoring failed", str(e), "ParallelAgentRunner")
    
    async def _report_agent_status(self):
        """Report agent status to Redis"""
        try:
            if not self.redis_client:
                return
            
            status_report = {
                'timestamp': int(time.time()),
                'metrics': self.metrics,
                'agents': {}
            }
            
            for agent_name, agent_info in self.agents.items():
                status_report['agents'][agent_name] = {
                    'status': agent_info.status.value,
                    'start_time': agent_info.start_time,
                    'error_message': agent_info.error_message,
                    'restart_count': agent_info.restart_count,
                    'last_heartbeat': agent_info.last_heartbeat
                }
            
            # Publish to Redis
            self.redis_client.publish('agent_runner:status', str(status_report))
            self.redis_client.set('agent_runner:latest_status', str(status_report))
            
        except Exception as e:
            self.logger.log_error("Failed to report agent status", str(e), "ParallelAgentRunner")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        try:
            status = {
                'is_running': self.is_running,
                'metrics': self.metrics,
                'agents': {}
            }
            
            for agent_name, agent_info in self.agents.items():
                status['agents'][agent_name] = {
                    'status': agent_info.status.value,
                    'start_time': agent_info.start_time,
                    'error_message': agent_info.error_message,
                    'restart_count': agent_info.restart_count,
                    'last_heartbeat': agent_info.last_heartbeat
                }
            
            return status
            
        except Exception as e:
            self.logger.log_error("Failed to get agent status", str(e), "ParallelAgentRunner")
            return {'error': str(e)}
    
    async def restart_agent(self, agent_name: str):
        """Manually restart a specific agent"""
        try:
            if agent_name not in self.agents:
                raise ValueError(f"Agent {agent_name} not found")
            
            agent_info = self.agents[agent_name]
            await self._restart_agent(agent_name, agent_info)
            
        except Exception as e:
            self.logger.log_error(f"Failed to restart agent {agent_name}", str(e), "ParallelAgentRunner")
            raise
    
    async def get_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """Get health status of a specific agent"""
        try:
            if agent_name not in self.agents:
                return {'error': f"Agent {agent_name} not found"}
            
            agent_info = self.agents[agent_name]
            
            health = {
                'name': agent_name,
                'status': agent_info.status.value,
                'start_time': agent_info.start_time,
                'uptime': time.time() - agent_info.start_time if agent_info.start_time else 0,
                'restart_count': agent_info.restart_count,
                'last_heartbeat': agent_info.last_heartbeat,
                'error_message': agent_info.error_message
            }
            
            # Get agent-specific health if available
            if hasattr(agent_info.agent, 'get_agent_status'):
                try:
                    agent_status = agent_info.agent.get_agent_status()
                    health['agent_status'] = agent_status
                except Exception as e:
                    health['agent_status_error'] = str(e)
            
            return health
            
        except Exception as e:
            self.logger.log_error(f"Failed to get health for agent {agent_name}", str(e), "ParallelAgentRunner")
            return {'error': str(e)}
    
    def is_connected(self) -> bool:
        """Check if agent runner is connected"""
        try:
            return (self.redis_client is not None and 
                   self.is_running)
        except:
            return False

# Convenience functions for easy usage
async def run_all_agents(config: Dict[str, Any] = None):
    """Run all agents in parallel"""
    runner = ParallelAgentRunner(config)
    try:
        await runner.start_all_agents()
        
        # Keep running until interrupted
        while runner.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nReceived interrupt, shutting down...")
    except Exception as e:
        print(f"Error running agents: {e}")
    finally:
        await runner.stop_all_agents()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run all trading agents in parallel')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--redis-host', default='localhost', help='Redis host')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis port')
    parser.add_argument('--redis-db', type=int, default=0, help='Redis database')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {
        'redis_host': args.redis_host,
        'redis_port': args.redis_port,
        'redis_db': args.redis_db,
        'heartbeat_interval': 30,
        'restart_delay': 5,
        'max_restarts': 3
    }
    
    # Load from file if provided
    if args.config:
        import json
        try:
            with open(args.config, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    # Run all agents
    asyncio.run(run_all_agents(config))

if __name__ == "__main__":
    main()
