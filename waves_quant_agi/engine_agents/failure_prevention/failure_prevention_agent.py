# failure_prevention/failure_prevention_agent.py
"""
Failure Prevention Agent - Main Orchestrator
============================================

Coordinates all monitoring, circuit breaking, learning, and recovery operations
for the autonomous trading system.
"""

import asyncio
import time
import redis
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .logs.failure_agent_logger import FailureAgentLogger
from .memory.incident_cache import IncidentCache
from .monitor.agent_supervisor import AgentSupervisor
from .monitor.system_watcher import SystemWatcher
from .monitor.data_integrity_checker import DataIntegrityChecker
from .circuit_breakers.broker_breaker import BrokerBreaker
from .circuit_breakers.strategy_breaker import StrategyBreaker
from .circuit_breakers.trade_halt_switch import TradeHaltSwitch
from .redundancy.fallback_manager import FallbackManager
from .infrastructure.network_guard import NetworkGuard

class AlertLevel(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FailureType(Enum):
    """Types of failures the system can detect"""
    SYSTEM_LAG = "system_lag"
    MEMORY_LEAK = "memory_leak"
    AGENT_FAILURE = "agent_failure"
    DATA_CORRUPTION = "data_corruption"
    NETWORK_ISSUE = "network_issue"
    BROKER_DISCONNECT = "broker_disconnect"
    STRATEGY_LOOP = "strategy_loop"
    EXTERNAL_THREAT = "external_threat"

@dataclass
class FailureEvent:
    """Represents a detected failure event"""
    timestamp: datetime
    failure_type: FailureType
    alert_level: AlertLevel
    source: str
    description: str
    metadata: Dict[str, Any]
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None

class FailurePreventionAgent:
    """
    Main orchestrator for the failure prevention system.
    Coordinates all monitoring, circuit breaking, learning, and recovery operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        self.components = {}
        self.event_queue = asyncio.Queue()
        self.logger = FailureAgentLogger()
        
        # Redis configuration
        redis_host = self.config.get('redis_host', 'localhost')
        redis_port = self.config.get('redis_port', 6379)
        redis_db = self.config.get('redis_db', 0)
        
        # Initialize Redis
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=redis_db, 
                decode_responses=True
            )
            self.redis_client.ping()  # Test connection
            self.logger.log_info("FailurePreventionAgent Redis connection established")
        except Exception as e:
            self.logger.log_error("Redis connection failed", str(e), "FailurePreventionAgent")
            self.redis_client = None
        
        # Initialize all subsystems
        self._initialize_components()
        
        # Performance tracking
        self.stats = {
            'events_processed': 0,
            'alerts_generated': 0,
            'incidents_resolved': 0,
            'recovery_actions': 0,
            'start_time': datetime.now()
        }
    
    def _initialize_components(self):
        """Initialize all subsystem components"""
        try:
            # Initialize incident cache
            self.incident_cache = IncidentCache(self.config.get('incident_cache', {}))
            
            # Initialize monitoring components
            self.components = {
                'agent_supervisor': AgentSupervisor(self.config.get('agent_supervision', {})),
                'system_watcher': SystemWatcher(self.config.get('system_monitoring', {})),
                'data_checker': DataIntegrityChecker(self.config.get('data_integrity', {})),
                'broker_breaker': BrokerBreaker(self.config.get('broker_circuit_breakers', {})),
                'strategy_breaker': StrategyBreaker(self.config.get('strategy_circuit_breakers', {})),
                'trade_halt': TradeHaltSwitch(self.config.get('trade_halt', {})),
                'fallback_manager': FallbackManager(self.config.get('redundancy', {})),
                'network_guard': NetworkGuard(self.config.get('network_monitoring', {}))
            }
            
            self.logger.log_info("All failure prevention components initialized", "FailurePreventionAgent")
            
        except Exception as e:
            self.logger.log_error("Failed to initialize components", str(e), "FailurePreventionAgent")
    
    async def start(self):
        """Start the failure prevention agent"""
        try:
            self.logger.log_info("Starting Failure Prevention Agent...", "FailurePreventionAgent")
            self.is_running = True
            
            # Start all monitoring components
            tasks = []
            for name, component in self.components.items():
                if hasattr(component, 'start'):
                    task = asyncio.create_task(component.start())
                    tasks.append(task)
                    self.logger.log_info(f"Started {name}", "FailurePreventionAgent")
            
            # Start main event processing loop
            tasks.append(asyncio.create_task(self._process_events()))
            
            # Start monitoring and reporting loops
            tasks.append(asyncio.create_task(self._monitoring_loop()))
            tasks.append(asyncio.create_task(self._reporting_loop()))
            tasks.append(asyncio.create_task(self._cleanup_loop()))
            
            # Start intelligence gathering
            tasks.append(asyncio.create_task(self._intelligence_loop()))
            
            try:
                await asyncio.gather(*tasks)
            except Exception as e:
                self.logger.log_error(f"Error in main loop: {e}", "FailurePreventionAgent")
                await self.stop()
                
        except Exception as e:
            self.logger.log_error(f"Failed to start Failure Prevention Agent: {e}", "FailurePreventionAgent")
            await self.stop()
    
    async def stop(self):
        """Gracefully stop the failure prevention agent"""
        try:
            self.logger.log_info("Stopping Failure Prevention Agent...", "FailurePreventionAgent")
            self.is_running = False
            
            # Stop all components
            for name, component in self.components.items():
                if hasattr(component, 'stop'):
                    await component.stop()
                    self.logger.log_info(f"Stopped {name}", "FailurePreventionAgent")
            
            # Final stats report
            await self._report_final_stats()
            
        except Exception as e:
            self.logger.log_error(f"Error stopping Failure Prevention Agent: {e}", "FailurePreventionAgent")
    
    async def _process_events(self):
        """Main event processing loop"""
        while self.is_running:
            try:
                # Process events from the queue
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._handle_failure_event(event)
                self.stats['events_processed'] += 1
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.log_error(f"Error processing event: {e}", "FailurePreventionAgent")
    
    async def _handle_failure_event(self, event: FailureEvent):
        """Handle a detected failure event"""
        try:
            self.logger.log_alert(
                alert_type=event.failure_type.value,
                severity=event.alert_level.value,
                source=event.source,
                description=event.description,
                metadata=event.metadata
            )
            
            # Store incident
            incident_data = {
                'timestamp': int(event.timestamp.timestamp()),
                'type': event.failure_type.value,
                'source': event.source,
                'description': event.description,
                'alert_level': event.alert_level.value,
                'metadata': event.metadata
            }
            self.incident_cache.store_incident(incident_data)
            
            # Trigger appropriate circuit breakers
            if event.failure_type == FailureType.BROKER_DISCONNECT:
                await self.components['broker_breaker'].activate(event.source, event.description)
            elif event.failure_type == FailureType.STRATEGY_LOOP:
                await self.components['strategy_breaker'].activate(event.source, event.description)
            elif event.alert_level == AlertLevel.CRITICAL:
                await self.components['trade_halt'].emergency_stop()
            
            # Activate fallback systems if needed
            if event.alert_level in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
                await self.components['fallback_manager'].activate_fallback(event.failure_type)
            
            # Log for learning
            await self._log_for_learning(event)
            
            self.stats['alerts_generated'] += 1
            
        except Exception as e:
            self.logger.log_error(f"Error handling failure event: {e}", "FailurePreventionAgent")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.is_running:
            try:
                # Check system health
                system_health = await self._check_system_health()
                
                # Check agent health
                agent_health = await self._check_agent_health()
                
                # Check network health
                network_health = await self._check_network_health()
                
                # Log health metrics
                self.logger.log_metric(
                    metric_name="system_health_score",
                    value=system_health.get('overall_score', 0),
                    tags={'component': 'system'}
                )
                
                self.logger.log_metric(
                    metric_name="agent_health_score",
                    value=agent_health.get('overall_score', 0),
                    tags={'component': 'agents'}
                )
                
                self.logger.log_metric(
                    metric_name="network_health_score",
                    value=network_health.get('overall_score', 0),
                    tags={'component': 'network'}
                )
                
                await asyncio.sleep(self.config.get('monitoring_interval', 30))
                
            except Exception as e:
                self.logger.log_error(f"Error in monitoring loop: {e}", "FailurePreventionAgent")
                await asyncio.sleep(60)
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        try:
            # This would integrate with SystemWatcher
            return {
                'overall_score': 95.0,
                'cpu_usage': 45.2,
                'memory_usage': 67.8,
                'disk_usage': 23.1,
                'active_processes': 156
            }
        except Exception as e:
            self.logger.log_error(f"Error checking system health: {e}", "FailurePreventionAgent")
            return {'overall_score': 0}
    
    async def _check_agent_health(self) -> Dict[str, Any]:
        """Check agent health"""
        try:
            # This would integrate with AgentSupervisor
            return {
                'overall_score': 88.5,
                'active_agents': 8,
                'suspended_agents': 1,
                'failed_agents': 0,
                'avg_response_time': 0.15
            }
        except Exception as e:
            self.logger.log_error(f"Error checking agent health: {e}", "FailurePreventionAgent")
            return {'overall_score': 0}
    
    async def _check_network_health(self) -> Dict[str, Any]:
        """Check network health"""
        try:
            # This would integrate with NetworkGuard
            return {
                'overall_score': 92.3,
                'latency': 45.2,
                'packet_loss': 0.1,
                'bandwidth_usage': 67.8,
                'active_connections': 23
            }
        except Exception as e:
            self.logger.log_error(f"Error checking network health: {e}", "FailurePreventionAgent")
            return {'overall_score': 0}
    
    async def _reporting_loop(self):
        """Periodic reporting loop"""
        while self.is_running:
            try:
                # Report agent stats
                agent_stats = self.components['agent_supervisor'].get_agent_stats()
                broker_stats = self.components['broker_breaker'].get_broker_stats()
                
                # Log comprehensive stats
                self.logger.log_metric(
                    metric_name="failure_prevention_stats",
                    value=self.stats['events_processed'],
                    tags={'metric': 'events_processed'}
                )
                
                self.logger.log_metric(
                    metric_name="failure_prevention_stats",
                    value=self.stats['alerts_generated'],
                    tags={'metric': 'alerts_generated'}
                )
                
                # Publish stats to Redis
                if self.redis_client:
                    stats_data = {
                        'timestamp': int(time.time()),
                        'agent_stats': agent_stats,
                        'broker_stats': broker_stats,
                        'failure_prevention_stats': self.stats
                    }
                    self.redis_client.publish('failure_prevention:stats', str(stats_data))
                
                await asyncio.sleep(self.config.get('reporting_interval', 300))  # 5 minutes
                
            except Exception as e:
                self.logger.log_error(f"Error in reporting loop: {e}", "FailurePreventionAgent")
                await asyncio.sleep(60)
    
    async def _cleanup_loop(self):
        """Periodic cleanup loop"""
        while self.is_running:
            try:
                # Clean up old incidents
                deleted_count = self.incident_cache.cleanup_old_incidents(days=7)
                
                if deleted_count > 0:
                    self.logger.log_info(f"Cleaned up {deleted_count} old incidents", "FailurePreventionAgent")
                
                await asyncio.sleep(self.config.get('cleanup_interval', 3600))  # 1 hour
                
            except Exception as e:
                self.logger.log_error(f"Error in cleanup loop: {e}", "FailurePreventionAgent")
                await asyncio.sleep(300)
    
    async def _intelligence_loop(self):
        """Continuous external intelligence gathering and analysis"""
        while self.is_running:
            try:
                # Gather external intelligence (placeholder for future implementation)
                # await self.components['pattern_synthesizer'].gather_external_intelligence()
                
                # Sleep for intelligence gathering interval
                await asyncio.sleep(self.config.get('intelligence_interval', 300))  # 5 minutes
                
            except Exception as e:
                self.logger.log_error(f"Error in intelligence loop: {e}", "FailurePreventionAgent")
                await asyncio.sleep(60)  # Retry after 1 minute
    
    async def _log_for_learning(self, event: FailureEvent):
        """Log event for machine learning purposes"""
        try:
            # Store for learning analysis
            learning_data = {
                'timestamp': int(event.timestamp.timestamp()),
                'failure_type': event.failure_type.value,
                'alert_level': event.alert_level.value,
                'source': event.source,
                'description': event.description,
                'metadata': event.metadata
            }
            
            if self.redis_client:
                self.redis_client.lpush('failure_prevention:learning_data', str(learning_data))
                self.redis_client.ltrim('failure_prevention:learning_data', 0, 9999)
                
        except Exception as e:
            self.logger.log_error(f"Error logging for learning: {e}", "FailurePreventionAgent")
    
    async def report_event(self, failure_type: FailureType, alert_level: AlertLevel, 
                          source: str, description: str, metadata: Dict[str, Any] = None):
        """Public interface for reporting failure events"""
        try:
            event = FailureEvent(
                timestamp=datetime.now(),
                failure_type=failure_type,
                alert_level=alert_level,
                source=source,
                description=description,
                metadata=metadata or {}
            )
            await self.event_queue.put(event)
            
        except Exception as e:
            self.logger.log_error(f"Error reporting event: {e}", "FailurePreventionAgent")
    
    async def _report_final_stats(self):
        """Report final statistics before shutdown"""
        try:
            runtime = datetime.now() - self.stats['start_time']
            
            final_stats = {
                'runtime_seconds': runtime.total_seconds(),
                'events_processed': self.stats['events_processed'],
                'alerts_generated': self.stats['alerts_generated'],
                'incidents_resolved': self.stats['incidents_resolved'],
                'recovery_actions': self.stats['recovery_actions'],
                'shutdown_time': datetime.now().isoformat()
            }
            
            self.logger.log_info(f"Final stats: {final_stats}", "FailurePreventionAgent")
            
            if self.redis_client:
                self.redis_client.publish('failure_prevention:shutdown', str(final_stats))
                
        except Exception as e:
            self.logger.log_error(f"Error reporting final stats: {e}", "FailurePreventionAgent")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of the failure prevention agent"""
        try:
            status = {
                'is_running': self.is_running,
                'start_time': self.stats['start_time'].isoformat(),
                'runtime_seconds': (datetime.now() - self.stats['start_time']).total_seconds(),
                'stats': self.stats,
                'redis_connected': self.redis_client is not None,
                'components': {}
            }
            
            # Get component statuses
            for name, component in self.components.items():
                if hasattr(component, 'get_stats'):
                    status['components'][name] = component.get_stats()
                elif hasattr(component, 'is_connected'):
                    status['components'][name] = {'connected': component.is_connected()}
            
            return status
            
        except Exception as e:
            self.logger.log_error(f"Error getting agent status: {e}", "FailurePreventionAgent")
            return {'error': str(e)}
    
    def get_incident_stats(self) -> Dict[str, Any]:
        """Get incident statistics"""
        try:
            return self.incident_cache.get_incident_stats()
        except Exception as e:
            self.logger.log_error(f"Error getting incident stats: {e}", "FailurePreventionAgent")
            return {'error': str(e)}
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
            return False
        except:
            return False
