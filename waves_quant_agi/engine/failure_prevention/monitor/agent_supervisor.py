# failure_prevention/monitor/agent_supervisor.py
"""
Agent Supervisor - Monitors agent behavior, response times, and failures
"""

import asyncio
import time
from typing import Dict, Any, Set, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from ..logs.failure_agent_logger import FailureLogger
from .. import FailureType, AlertLevel

class AgentSupervisor:
    """Supervises trading agents and their performance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = FailureLogger("AgentSupervisor")
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
        
        # Performance tracking
        self.agent_performance = defaultdict(list)
        
    async def start(self):
        """Start agent supervision"""
        self.is_running = True
        self.logger.info("Agent supervision started")
        
        await asyncio.gather(
            self._monitor_agent_health(),
            self._cleanup_old_metrics()
        )
    
    async def stop(self):
        """Stop agent supervision"""
        self.is_running = False
        self.logger.info("Agent supervision stopped")
    
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register an agent for monitoring"""
        self.registered_agents[agent_id] = {
            'info': agent_info,
            'registered_at': datetime.now(),
            'last_heartbeat': datetime.now(),
            'status': 'active',
            'failure_count': 0
        }
        self.logger.info(f"Registered agent: {agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            self.failed_agents.discard(agent_id)
            self.suspended_agents.discard(agent_id)
            self.logger.info(f"Unregistered agent: {agent_id}")
    
    async def record_agent_call(self, agent_id: str, call_type: str, 
                               start_time: float, end_time: float, 
                               success: bool, error: Optional[str] = None):
        """Record an agent call for monitoring"""
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
        
        # Update agent heartbeat
        self.registered_agents[agent_id]['last_heartbeat'] = datetime.now()
        
        # Check for issues
        if not success:
            await self._handle_agent_failure(agent_id, call_type, error)
        elif duration > self.response_timeout:
            await self._handle_slow_response(agent_id, call_type, duration)
        
        # Update performance tracking
        self.agent_performance[agent_id].append({
            'timestamp': datetime.now(),
            'duration': duration,
            'success': success
        })
        
        # Limit performance history
        if len(self.agent_performance[agent_id]) > 1000:
            self.agent_performance[agent_id] = self.agent_performance[agent_id][-500:]
    
    async def _handle_agent_failure(self, agent_id: str, call_type: str, error: str):
        """Handle agent failure"""
        self.registered_agents[agent_id]['failure_count'] += 1
        
        # Check failure rate in time window
        recent_failures = self._count_recent_failures(agent_id)
        
        if recent_failures >= self.failure_threshold:
            await self._suspend_agent(agent_id, f"Too many failures: {recent_failures}")
        
        await self._report_issue(
            FailureType.AGENT_FAILURE,
            AlertLevel.MEDIUM if recent_failures < self.failure_threshold else AlertLevel.HIGH,
            f"Agent {agent_id} failed on {call_type}: {error}"
        )
    
    async def _handle_slow_response(self, agent_id: str, call_type: str, duration: float):
        """Handle slow agent response"""
        await self._report_issue(
            FailureType.SYSTEM_LAG,
            AlertLevel.LOW if duration < self.response_timeout * 2 else AlertLevel.MEDIUM,
            f"Agent {agent_id} slow response on {call_type}: {duration:.2f}s"
        )
    
    def _count_recent_failures(self, agent_id: str) -> int:
        """Count failures in the recent time window"""
        if agent_id not in self.agent_metrics:
            return 0
        
        cutoff_time = datetime.now() - timedelta(seconds=self.failure_window)
        recent_calls = [
            call for call in self.agent_metrics[agent_id]
            if call['timestamp'] > cutoff_time
        ]
        
        return sum(1 for call in recent_calls if not call['success'])
    
    async def _suspend_agent(self, agent_id: str, reason: str):
        """Suspend a problematic agent"""
        self.suspended_agents.add(agent_id)
        self.registered_agents[agent_id]['status'] = 'suspended'
        
        self.logger.warning(f"Suspended agent {agent_id}: {reason}")
        
        await self._report_issue(
            FailureType.AGENT_FAILURE,
            AlertLevel.HIGH,
            f"Agent {agent_id} suspended: {reason}"
        )
    
    async def _monitor_agent_health(self):
        """Monitor overall agent health"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for agent_id, agent_data in self.registered_agents.items():
                    # Check for stale agents (no heartbeat)
                    time_since_heartbeat = current_time - agent_data['last_heartbeat']
                    
                    if time_since_heartbeat > timedelta(minutes=5):
                        if agent_id not in self.failed_agents:
                            self.failed_agents.add(agent_id)
                            agent_data['status'] = 'failed'
                            
                            await self._report_issue(
                                FailureType.AGENT_FAILURE,
                                AlertLevel.HIGH,
                                f"Agent {agent_id} appears to be dead (no heartbeat for {time_since_heartbeat})"
                            )
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring agent health: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_metrics(self):
        """Clean up old performance metrics"""
        while self.is_running:
            try:
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for agent_id in list(self.agent_performance.keys()):
                    self.agent_performance[agent_id] = [
                        metric for metric in self.agent_performance[agent_id]
                        if metric['timestamp'] > cutoff_time
                    ]
                    
                    if not self.agent_performance[agent_id]:
                        del self.agent_performance[agent_id]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up metrics: {e}")
                await asyncio.sleep(3600)
    
    async def _report_issue(self, failure_type: FailureType, alert_level: AlertLevel, description: str):
        """Report a detected issue"""
        self.logger.warning(f"Agent issue detected: {description}")
        
        issue_data = {
            'type': failure_type.value,
            'level': alert_level.value,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'source': 'AgentSupervisor'
        }
        
        await self.logger.log_failure(issue_data)
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        if agent_id not in self.registered_agents:
            return None
        
        agent_data = self.registered_agents[agent_id]
        recent_metrics = list(self.agent_metrics[agent_id])[-10:]  # Last 10 calls
        
        return {
            'agent_id': agent_id,
            'status': agent_data['status'],
            'registered_at': agent_data['registered_at'],
            'last_heartbeat': agent_data['last_heartbeat'],
            'failure_count': agent_data['failure_count'],
            'recent_calls': len(recent_metrics),
            'recent_success_rate': sum(1 for m in recent_metrics if m['success']) / max(len(recent_metrics), 1),
            'is_suspended': agent_id in self.suspended_agents,
            'is_failed': agent_id in self.failed_agents
        }
    
    def get_all_agents_status(self) -> Dict[str, Any]:
        """Get status of all registered agents"""
        return {
            agent_id: self.get_agent_status(agent_id)
            for agent_id in self.registered_agents.keys()
        }