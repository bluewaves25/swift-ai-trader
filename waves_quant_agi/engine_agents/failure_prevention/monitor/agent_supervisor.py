# failure_prevention/monitor/agent_supervisor.py
"""
Agent Supervisor - Monitors agent behavior, response times, and failures
"""

import asyncio
import time
import redis
from typing import Dict, Any, Set, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
from ..logs.failure_agent_logger import FailureAgentLogger
from .. import FailureType, AlertLevel

class AgentSupervisor:
    """Supervises trading agents and their performance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
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
            self.logger.log_info("AgentSupervisor Redis connection established")
        except Exception as e:
            self.logger.log_error("Redis connection failed", str(e), "AgentSupervisor")
            self.redis_client = None
        
        self.is_running = False
        
        # Agent tracking
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.failed_agents: Set[str] = set()
        self.suspended_agents: Set[str] = set()
        
        # Thresholds
        self.response_timeout = config.get('response_timeout', 30.0)  # seconds
        self.failure_threshold = config.get('failure_threshold', 5)  # failures in window
        self.failure_window = config.get('failure_window', 300)  # 5 minutes
        self.health_check_interval = config.get('health_check_interval', 60)  # seconds
        self.cleanup_interval = config.get('cleanup_interval', 3600)  # 1 hour
        
        # Performance tracking
        self.agent_performance = defaultdict(list)
        self.agent_stats = defaultdict(dict)
        
    async def start(self):
        """Start agent supervision"""
        self.is_running = True
        self.logger.log_info("Agent supervision started", "AgentSupervisor")
        
        # Start monitoring tasks
        tasks = [
            self._monitor_agent_health(),
            self._cleanup_old_metrics(),
            self._report_agent_stats()
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.log_error("Error in agent supervision", str(e), "AgentSupervisor")
            await self.stop()
    
    async def stop(self):
        """Stop agent supervision"""
        self.is_running = False
        self.logger.log_info("Agent supervision stopped", "AgentSupervisor")
    
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register an agent for monitoring"""
        try:
            self.registered_agents[agent_id] = {
                'info': agent_info,
                'registered_at': datetime.now(),
                'last_heartbeat': datetime.now(),
                'status': 'active',
                'failure_count': 0,
                'total_calls': 0,
                'successful_calls': 0,
                'avg_response_time': 0.0
            }
            
            # Store in Redis
            if self.redis_client:
                agent_data = {
                    'agent_id': agent_id,
                    'info': str(agent_info),
                    'registered_at': str(datetime.now()),
                    'status': 'active'
                }
                self.redis_client.hset(f"agent_supervisor:agents", agent_id, str(agent_data))
            
            self.logger.log_agent_supervision(
                agent_id=agent_id,
                action="register",
                status="active",
                metadata=agent_info
            )
            
        except Exception as e:
            self.logger.log_error(f"Failed to register agent {agent_id}", str(e), "AgentSupervisor")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        try:
            if agent_id in self.registered_agents:
                del self.registered_agents[agent_id]
                self.failed_agents.discard(agent_id)
                self.suspended_agents.discard(agent_id)
                
                # Remove from Redis
                if self.redis_client:
                    self.redis_client.hdel("agent_supervisor:agents", agent_id)
                
                self.logger.log_agent_supervision(
                    agent_id=agent_id,
                    action="unregister",
                    status="removed"
                )
                
        except Exception as e:
            self.logger.log_error(f"Failed to unregister agent {agent_id}", str(e), "AgentSupervisor")
    
    async def record_agent_call(self, agent_id: str, call_type: str, 
                               start_time: float, end_time: float, 
                               success: bool, error: Optional[str] = None):
        """Record an agent call for monitoring"""
        try:
            if agent_id not in self.registered_agents:
                return
            
            duration = end_time - start_time
            
            # Record metrics
            call_record = {
                'timestamp': datetime.now(),
                'call_type': call_type,
                'duration': duration,
                'success': success,
                'error': error
            }
            
            self.agent_metrics[agent_id].append(call_record)
            
            # Update agent stats
            agent = self.registered_agents[agent_id]
            agent['total_calls'] += 1
            agent['last_heartbeat'] = datetime.now()
            
            if success:
                agent['successful_calls'] += 1
            
            # Update average response time
            recent_calls = [call['duration'] for call in list(self.agent_metrics[agent_id])[-10:]]
            agent['avg_response_time'] = sum(recent_calls) / len(recent_calls) if recent_calls else 0.0
            
            # Store metrics in Redis
            if self.redis_client:
                metrics_data = {
                    'agent_id': agent_id,
                    'call_type': call_type,
                    'duration': duration,
                    'success': success,
                    'timestamp': str(datetime.now())
                }
                self.redis_client.lpush(f"agent_supervisor:metrics:{agent_id}", str(metrics_data))
                self.redis_client.ltrim(f"agent_supervisor:metrics:{agent_id}", 0, 999)
            
            # Check for issues
            if not success:
                await self._handle_agent_failure(agent_id, call_type, error)
            elif duration > self.response_timeout:
                await self._handle_slow_response(agent_id, call_type, duration)
            
            # Update performance tracking
            self.agent_performance[agent_id].append({
                'timestamp': datetime.now(),
                'duration': duration,
                'success': success,
                'call_type': call_type
            })
            
        except Exception as e:
            self.logger.log_error(f"Failed to record agent call for {agent_id}", str(e), "AgentSupervisor")
    
    async def _handle_agent_failure(self, agent_id: str, call_type: str, error: str):
        """Handle agent failure"""
        try:
            agent = self.registered_agents[agent_id]
            agent['failure_count'] += 1
            
            failure_count = self._count_recent_failures(agent_id)
            
            self.logger.log_incident(
                incident_type="agent_failure",
                source=agent_id,
                description=f"Agent failure in {call_type}: {error}",
                failure_count=failure_count,
                metadata={'call_type': call_type, 'error': error}
            )
            
            if failure_count >= self.failure_threshold:
                await self._suspend_agent(agent_id, f"Failure threshold reached: {failure_count}")
            
        except Exception as e:
            self.logger.log_error(f"Failed to handle agent failure for {agent_id}", str(e), "AgentSupervisor")
    
    async def _handle_slow_response(self, agent_id: str, call_type: str, duration: float):
        """Handle slow agent response"""
        try:
            self.logger.log_alert(
                alert_type="slow_response",
                severity="medium",
                source=agent_id,
                description=f"Slow response in {call_type}: {duration:.2f}s",
                metadata={'call_type': call_type, 'duration': duration, 'threshold': self.response_timeout}
            )
            
        except Exception as e:
            self.logger.log_error(f"Failed to handle slow response for {agent_id}", str(e), "AgentSupervisor")
    
    def _count_recent_failures(self, agent_id: str) -> int:
        """Count recent failures for an agent"""
        try:
            cutoff_time = datetime.now() - timedelta(seconds=self.failure_window)
            recent_failures = 0
            
            for call_record in self.agent_metrics[agent_id]:
                if (call_record['timestamp'] > cutoff_time and 
                    not call_record['success']):
                    recent_failures += 1
            
            return recent_failures
            
        except Exception as e:
            self.logger.log_error(f"Failed to count recent failures for {agent_id}", str(e), "AgentSupervisor")
            return 0
    
    async def _suspend_agent(self, agent_id: str, reason: str):
        """Suspend an agent"""
        try:
            if agent_id not in self.suspended_agents:
                self.suspended_agents.add(agent_id)
                self.registered_agents[agent_id]['status'] = 'suspended'
                
                # Update Redis
                if self.redis_client:
                    self.redis_client.hset(f"agent_supervisor:agents", agent_id, 
                                         str({'status': 'suspended', 'reason': reason}))
                
                self.logger.log_agent_supervision(
                    agent_id=agent_id,
                    action="suspend",
                    status="suspended",
                    metadata={'reason': reason}
                )
                
        except Exception as e:
            self.logger.log_error(f"Failed to suspend agent {agent_id}", str(e), "AgentSupervisor")
    
    async def _monitor_agent_health(self):
        """Monitor agent health continuously"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for agent_id, agent in self.registered_agents.items():
                    # Check for stale heartbeats
                    if agent['status'] == 'active':
                        time_since_heartbeat = (current_time - agent['last_heartbeat']).total_seconds()
                        
                        if time_since_heartbeat > self.response_timeout * 2:
                            await self._handle_agent_failure(
                                agent_id, 
                                "heartbeat_timeout", 
                                f"No heartbeat for {time_since_heartbeat:.1f}s"
                            )
                
                # Log health metrics
                active_count = len([a for a in self.registered_agents.values() if a['status'] == 'active'])
                suspended_count = len(self.suspended_agents)
                failed_count = len(self.failed_agents)
                
                self.logger.log_metric(
                    metric_name="agent_health",
                    value=active_count,
                    tags={'status': 'active', 'total': len(self.registered_agents)}
                )
                
                self.logger.log_metric(
                    metric_name="agent_health",
                    value=suspended_count,
                    tags={'status': 'suspended', 'total': len(self.registered_agents)}
                )
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.log_error("Error in agent health monitoring", str(e), "AgentSupervisor")
                await asyncio.sleep(60)  # Retry after 1 minute
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics periodically"""
        while self.is_running:
            try:
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for agent_id in list(self.agent_metrics.keys()):
                    # Remove old metrics
                    self.agent_metrics[agent_id] = deque(
                        [m for m in self.agent_metrics[agent_id] 
                         if m['timestamp'] > cutoff_time],
                        maxlen=100
                    )
                
                # Clean up Redis old metrics
                if self.redis_client:
                    for agent_id in self.registered_agents:
                        old_keys = self.redis_client.lrange(f"agent_supervisor:metrics:{agent_id}", 100, -1)
                        if old_keys:
                            self.redis_client.ltrim(f"agent_supervisor:metrics:{agent_id}", 0, 99)
                
                await asyncio.sleep(self.cleanup_interval)
                
            except Exception as e:
                self.logger.log_error("Error in metrics cleanup", str(e), "AgentSupervisor")
                await asyncio.sleep(300)  # Retry after 5 minutes
    
    async def _report_agent_stats(self):
        """Report agent statistics periodically"""
        while self.is_running:
            try:
                for agent_id, agent in self.registered_agents.items():
                    # Calculate success rate
                    total_calls = agent['total_calls']
                    successful_calls = agent['successful_calls']
                    success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
                    
                    # Store stats
                    self.agent_stats[agent_id] = {
                        'total_calls': total_calls,
                        'successful_calls': successful_calls,
                        'success_rate': success_rate,
                        'avg_response_time': agent['avg_response_time'],
                        'failure_count': agent['failure_count'],
                        'status': agent['status']
                    }
                    
                    # Log metrics
                    self.logger.log_metric(
                        metric_name="agent_success_rate",
                        value=success_rate,
                        tags={'agent_id': agent_id}
                    )
                    
                    self.logger.log_metric(
                        metric_name="agent_response_time",
                        value=agent['avg_response_time'],
                        tags={'agent_id': agent_id}
                    )
                
                await asyncio.sleep(300)  # Report every 5 minutes
                
            except Exception as e:
                self.logger.log_error("Error in agent stats reporting", str(e), "AgentSupervisor")
                await asyncio.sleep(60)
    
    async def _report_issue(self, failure_type: FailureType, alert_level: AlertLevel, description: str):
        """Report an issue to the main failure prevention system"""
        try:
            # This would typically communicate with the main failure prevention agent
            issue_data = {
                'failure_type': failure_type.value,
                'alert_level': alert_level.value,
                'description': description,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.redis_client:
                self.redis_client.publish('failure_prevention:issues', str(issue_data))
            
        except Exception as e:
            self.logger.log_error("Failed to report issue", str(e), "AgentSupervisor")
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        try:
            if agent_id in self.registered_agents:
                agent = self.registered_agents[agent_id]
                return {
                    'agent_id': agent_id,
                    'status': agent['status'],
                    'registered_at': agent['registered_at'],
                    'last_heartbeat': agent['last_heartbeat'],
                    'total_calls': agent['total_calls'],
                    'successful_calls': agent['successful_calls'],
                    'avg_response_time': agent['avg_response_time'],
                    'failure_count': agent['failure_count'],
                    'stats': self.agent_stats.get(agent_id, {})
                }
            return None
            
        except Exception as e:
            self.logger.log_error(f"Failed to get agent status for {agent_id}", str(e), "AgentSupervisor")
            return None
    
    def get_all_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        try:
            status = {
                'total_agents': len(self.registered_agents),
                'active_agents': len([a for a in self.registered_agents.values() if a['status'] == 'active']),
                'suspended_agents': len(self.suspended_agents),
                'failed_agents': len(self.failed_agents),
                'agents': {}
            }
            
            for agent_id in self.registered_agents:
                status['agents'][agent_id] = self.get_agent_status(agent_id)
            
            return status
            
        except Exception as e:
            self.logger.log_error("Failed to get all agents status", str(e), "AgentSupervisor")
            return {'error': str(e)}
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get comprehensive agent statistics"""
        try:
            stats = {
                'total_agents': len(self.registered_agents),
                'agent_stats': self.agent_stats,
                'performance_summary': {},
                'redis_connected': self.redis_client is not None
            }
            
            # Calculate performance summary
            if self.agent_stats:
                total_calls = sum(stat['total_calls'] for stat in self.agent_stats.values())
                total_successful = sum(stat['successful_calls'] for stat in self.agent_stats.values())
                avg_response_time = sum(stat['avg_response_time'] for stat in self.agent_stats.values()) / len(self.agent_stats)
                
                stats['performance_summary'] = {
                    'total_calls': total_calls,
                    'total_successful_calls': total_successful,
                    'overall_success_rate': (total_successful / total_calls * 100) if total_calls > 0 else 0,
                    'avg_response_time': avg_response_time
                }
            
            return stats
            
        except Exception as e:
            self.logger.log_error("Failed to get agent stats", str(e), "AgentSupervisor")
            return {'error': str(e)}