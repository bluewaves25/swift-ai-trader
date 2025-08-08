#!/usr/bin/env python3
"""
Core Agent - Central orchestrator for the trading system.
Coordinates all agents and manages the complete trading flow.
"""

import asyncio
import time
import redis
from typing import Dict, Any, Optional, List
from datetime import datetime

from .controller.flow_manager import FlowManager
from .controller.logic_executor import LogicExecutor
from .controller.signal_filter import SignalFilter
from .interfaces.agent_io import AgentIO
from .interfaces.trade_model import TradeCommand
from .pipeline.execution_pipeline import ExecutionPipeline
from .memory.recent_context import RecentContext
from .learning_layer.research_engine import ResearchEngine
from .learning_layer.training_module import TrainingModule
from .learning_layer.retraining_loop import RetrainingLoop
from .logs.core_agent_logger import CoreAgentLogger

class CoreAgent:
    """
    Main Core Agent orchestrator.
    Coordinates all trading agents and manages the complete trading flow.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = CoreAgentLogger("core_agent")
        
        # Initialize Redis
        self._init_redis()
        
        # Initialize components
        self._init_components()
        
        # Agent state
        self.is_running = False
        self.start_time = None
        self.stats = {
            'signals_processed': 0,
            'trades_executed': 0,
            'errors_encountered': 0,
            'uptime_seconds': 0
        }
        
        # Task management
        self.tasks = []
        
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
            self.logger.log_info("Redis connection established")
            
        except Exception as e:
            self.logger.log_error("Redis connection failed", str(e), "CoreAgent")
            self.redis_client = None
    
    def _init_components(self):
        """Initialize all core components"""
        try:
            # Initialize agent communication
            self.agent_io = AgentIO(self.config)
            
            # Initialize controllers
            self.flow_manager = FlowManager(self.agent_io, self.config)
            self.signal_filter = SignalFilter(self.config)
            self.logic_executor = LogicExecutor(self.signal_filter, self.flow_manager)
            
            # Initialize pipeline
            self.execution_pipeline = ExecutionPipeline(self.config)
            
            # Initialize memory
            self.recent_context = RecentContext(self.config)
            
            # Initialize learning components
            self.research_engine = ResearchEngine(self.config)
            self.training_module = TrainingModule(self.config)
            self.retraining_loop = RetrainingLoop(self.config)
            
            self.logger.log_info("All components initialized successfully")
            
        except Exception as e:
            self.logger.log_error("Component initialization failed", str(e), "CoreAgent")
            raise
    
    async def start(self):
        """Start the Core Agent"""
        try:
            if self.is_running:
                self.logger.log_info("Core Agent is already running")
                return
            
            self.logger.log_system_operation(
                operation="start",
                component="core_agent",
                status="initiating"
            )
            
            # Start background tasks
            self.tasks = [
                asyncio.create_task(self._signal_processing_loop()),
                asyncio.create_task(self._agent_coordination_loop()),
                asyncio.create_task(self._learning_loop()),
                asyncio.create_task(self._monitoring_loop()),
                asyncio.create_task(self._stats_reporting_loop())
            ]
            
            self.is_running = True
            self.start_time = time.time()
            
            self.logger.log_system_operation(
                operation="start",
                component="core_agent",
                status="started"
            )
            
            self.logger.log_info("Core Agent started successfully")
            
        except Exception as e:
            self.logger.log_error("Failed to start Core Agent", str(e), "CoreAgent")
            raise
    
    async def stop(self):
        """Stop the Core Agent"""
        try:
            if not self.is_running:
                self.logger.log_info("Core Agent is not running")
                return
            
            self.logger.log_system_operation(
                operation="stop",
                component="core_agent",
                status="initiating"
            )
            
            # Stop background tasks
            for task in self.tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
            self.is_running = False
            
            # Report final stats
            await self._report_final_stats()
            
            self.logger.log_system_operation(
                operation="stop",
                component="core_agent",
                status="stopped"
            )
            
            self.logger.log_info("Core Agent stopped successfully")
            
        except Exception as e:
            self.logger.log_error("Failed to stop Core Agent", str(e), "CoreAgent")
            raise
    
    async def _signal_processing_loop(self):
        """Main signal processing loop"""
        try:
            self.logger.log_info("Starting signal processing loop")
            
            while self.is_running:
                try:
                    # Get pending signals from Redis
                    signals = await self._get_pending_signals()
                    
                    for signal in signals:
                        if not self.is_running:
                            break
                        
                        # Process signal
                        result = await self._process_signal(signal)
                        
                        # Update stats
                        self.stats['signals_processed'] += 1
                        if result.get('success'):
                            self.stats['trades_executed'] += 1
                        else:
                            self.stats['errors_encountered'] += 1
                    
                    await asyncio.sleep(0.1)  # Small delay
                    
                except Exception as e:
                    self.logger.log_error("Signal processing loop error", str(e), "CoreAgent")
                    self.stats['errors_encountered'] += 1
                    await asyncio.sleep(1)  # Longer delay on error
            
        except asyncio.CancelledError:
            self.logger.log_info("Signal processing loop cancelled")
        except Exception as e:
            self.logger.log_error("Signal processing loop failed", str(e), "CoreAgent")
    
    async def _agent_coordination_loop(self):
        """Agent coordination and health monitoring loop"""
        try:
            self.logger.log_info("Starting agent coordination loop")
            
            while self.is_running:
                try:
                    # Check agent health
                    await self._check_agent_health()
                    
                    # Coordinate with agents
                    await self._coordinate_agents()
                    
                    await asyncio.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    self.logger.log_error("Agent coordination loop error", str(e), "CoreAgent")
                    await asyncio.sleep(10)  # Longer delay on error
            
        except asyncio.CancelledError:
            self.logger.log_info("Agent coordination loop cancelled")
        except Exception as e:
            self.logger.log_error("Agent coordination loop failed", str(e), "CoreAgent")
    
    async def _learning_loop(self):
        """Learning and optimization loop"""
        try:
            self.logger.log_info("Starting learning loop")
            
            while self.is_running:
                try:
                    # Update learning models
                    await self._update_learning_models()
                    
                    # Run research
                    await self._run_research()
                    
                    await asyncio.sleep(60)  # Run every minute
                    
                except Exception as e:
                    self.logger.log_error("Learning loop error", str(e), "CoreAgent")
                    await asyncio.sleep(120)  # Longer delay on error
            
        except asyncio.CancelledError:
            self.logger.log_info("Learning loop cancelled")
        except Exception as e:
            self.logger.log_error("Learning loop failed", str(e), "CoreAgent")
    
    async def _monitoring_loop(self):
        """System monitoring loop"""
        try:
            self.logger.log_info("Starting monitoring loop")
            
            while self.is_running:
                try:
                    # Monitor system health
                    await self._monitor_system_health()
                    
                    # Update uptime
                    if self.start_time:
                        self.stats['uptime_seconds'] = int(time.time() - self.start_time)
                    
                    await asyncio.sleep(10)  # Check every 10 seconds
                    
                except Exception as e:
                    self.logger.log_error("Monitoring loop error", str(e), "CoreAgent")
                    await asyncio.sleep(30)  # Longer delay on error
            
        except asyncio.CancelledError:
            self.logger.log_info("Monitoring loop cancelled")
        except Exception as e:
            self.logger.log_error("Monitoring loop failed", str(e), "CoreAgent")
    
    async def _stats_reporting_loop(self):
        """Statistics reporting loop"""
        try:
            self.logger.log_info("Starting stats reporting loop")
            
            while self.is_running:
                try:
                    # Report stats to Redis
                    await self._report_stats()
                    
                    await asyncio.sleep(30)  # Report every 30 seconds
                    
                except Exception as e:
                    self.logger.log_error("Stats reporting loop error", str(e), "CoreAgent")
                    await asyncio.sleep(60)  # Longer delay on error
            
        except asyncio.CancelledError:
            self.logger.log_info("Stats reporting loop cancelled")
        except Exception as e:
            self.logger.log_error("Stats reporting loop failed", str(e), "CoreAgent")
    
    async def _get_pending_signals(self) -> List[Dict[str, Any]]:
        """Get pending signals from Redis"""
        try:
            if not self.redis_client:
                return []
            
            # Get signals from various sources
            signals = []
            
            # Check core agent signal queue
            signal_data = self.redis_client.lpop('core_agent:signal_queue')
            if signal_data:
                try:
                    signal = eval(signal_data)
                    signals.append(signal)
                except:
                    pass
            
            # Check other agent notifications
            for agent in ['strategy', 'intelligence', 'market_conditions']:
                notification_data = self.redis_client.lpop(f'{agent}_agent:notifications')
                if notification_data:
                    try:
                        notification = eval(notification_data)
                        if notification.get('type') == 'signal':
                            signals.append(notification.get('data', {}))
                    except:
                        pass
            
            return signals
            
        except Exception as e:
            self.logger.log_error("Failed to get pending signals", str(e), "CoreAgent")
            return []
    
    async def _process_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single signal"""
        try:
            signal_id = signal.get('signal_id', f"signal_{int(time.time())}")
            
            self.logger.log_signal_processing(
                signal_id=signal_id,
                signal_type=signal.get('type', 'unknown'),
                source=signal.get('source', 'unknown'),
                status="received"
            )
            
            # Filter signal
            filter_result = self.signal_filter.filter_signal(signal)
            if not filter_result['passed']:
                self.logger.log_signal_filtering(
                    signal_id=signal_id,
                    filter_type="signal_filter",
                    filter_result="rejected",
                    filter_reason=filter_result['reason']
                )
                return {"success": False, "reason": filter_result['reason']}
            
            # Execute logic
            logic_result = self.logic_executor.execute_logic(signal)
            if not logic_result['success']:
                return {"success": False, "reason": logic_result['reason']}
            
            # Process through flow manager
            flow_result = await self.flow_manager.process_signal(signal)
            
            # Store in recent context
            self.recent_context.store_signal(signal, flow_result)
            
            return flow_result
            
        except Exception as e:
            self.logger.log_error("Signal processing failed", str(e), "CoreAgent")
            return {"success": False, "reason": f"Processing error: {str(e)}"}
    
    async def _check_agent_health(self):
        """Check health of all agents"""
        try:
            agent_status = self.agent_io.get_agent_status()
            
            for agent_name, status in agent_status.get('agent_availability', {}).items():
                if status == 'unavailable':
                    self.logger.log_system_operation(
                        operation="health_check",
                        component=f"agent_{agent_name}",
                        status="unavailable"
                    )
            
        except Exception as e:
            self.logger.log_error("Agent health check failed", str(e), "CoreAgent")
    
    async def _coordinate_agents(self):
        """Coordinate with all agents"""
        try:
            # Send heartbeat to all agents
            heartbeat = {
                'timestamp': int(time.time()),
                'type': 'heartbeat',
                'source': 'core_agent'
            }
            
            results = await self.agent_io.broadcast_to_all_agents(heartbeat)
            
            # Log coordination results
            for agent_name, success in results.items():
                if not success:
                    self.logger.log_system_operation(
                        operation="coordination",
                        component=f"agent_{agent_name}",
                        status="failed"
                    )
            
        except Exception as e:
            self.logger.log_error("Agent coordination failed", str(e), "CoreAgent")
    
    async def _update_learning_models(self):
        """Update learning models"""
        try:
            # Update training module
            await self.training_module.update_models()
            
            # Run retraining loop
            await self.retraining_loop.run_retraining_cycle()
            
        except Exception as e:
            self.logger.log_error("Learning model update failed", str(e), "CoreAgent")
    
    async def _run_research(self):
        """Run research engine"""
        try:
            await self.research_engine.run_research_cycle()
            
        except Exception as e:
            self.logger.log_error("Research failed", str(e), "CoreAgent")
    
    async def _monitor_system_health(self):
        """Monitor system health"""
        try:
            # Check component health
            components = [
                ('flow_manager', self.flow_manager.is_connected()),
                ('agent_io', self.agent_io.is_connected()),
                ('redis', self.redis_client is not None)
            ]
            
            for component_name, is_healthy in components:
                if not is_healthy:
                    self.logger.log_system_operation(
                        operation="health_check",
                        component=component_name,
                        status="unhealthy"
                    )
            
        except Exception as e:
            self.logger.log_error("System health monitoring failed", str(e), "CoreAgent")
    
    async def _report_stats(self):
        """Report statistics to Redis"""
        try:
            if not self.redis_client:
                return
            
            stats = {
                'timestamp': int(time.time()),
                'agent_stats': self.stats,
                'flow_stats': self.flow_manager.get_flow_stats(),
                'agent_status': self.agent_io.get_agent_status(),
                'communication_stats': self.agent_io.get_communication_stats()
            }
            
            # Store stats in Redis
            self.redis_client.set('core_agent:stats', str(stats))
            self.redis_client.publish('core_agent:stats_update', str(stats))
            
        except Exception as e:
            self.logger.log_error("Stats reporting failed", str(e), "CoreAgent")
    
    async def _report_final_stats(self):
        """Report final statistics"""
        try:
            self.logger.log_info("=== FINAL CORE AGENT STATS ===")
            self.logger.log_info(f"Signals processed: {self.stats['signals_processed']}")
            self.logger.log_info(f"Trades executed: {self.stats['trades_executed']}")
            self.logger.log_info(f"Errors encountered: {self.stats['errors_encountered']}")
            self.logger.log_info(f"Uptime: {self.stats['uptime_seconds']} seconds")
            
        except Exception as e:
            self.logger.log_error("Final stats reporting failed", str(e), "CoreAgent")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        try:
            status = {
                'is_running': self.is_running,
                'start_time': self.start_time,
                'stats': self.stats,
                'components': {
                    'flow_manager': self.flow_manager.is_connected(),
                    'agent_io': self.agent_io.is_connected(),
                    'redis': self.redis_client is not None
                }
            }
            
            return status
            
        except Exception as e:
            self.logger.log_error("Failed to get agent status", str(e), "CoreAgent")
            return {'error': str(e)}
    
    def is_connected(self) -> bool:
        """Check if agent is connected"""
        try:
            return (self.redis_client is not None and 
                   self.flow_manager.is_connected() and 
                   self.agent_io.is_connected())
        except:
            return False
