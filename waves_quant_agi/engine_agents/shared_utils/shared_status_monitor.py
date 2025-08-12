#!/usr/bin/env python3
"""
Shared Status Monitor - ELIMINATE 90% OF STATUS MONITORING DUPLICATION
Single status monitoring system for all agents to prevent massive code duplication

ELIMINATES DUPLICATION FROM:
- adapters/status_monitor/ (3 files)
- core/status_monitor/ (2 files)
- data_feeds/status_monitor/ (2 files) 
- strategy_engine/status_monitor/ (3 files)
- risk_management/status_monitor/ (4 files)
- And other identical status monitoring across agents
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from .redis_connector import get_shared_redis
from .shared_logger import get_shared_logger

class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"
    UNKNOWN = "unknown"

@dataclass
class PerformanceMetrics:
    """Performance metrics for an agent."""
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    memory_usage_percent: float = 0.0
    operations_per_second: float = 0.0
    average_response_time_ms: float = 0.0
    error_rate: float = 0.0
    uptime_seconds: int = 0
    last_operation_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage_mb": self.memory_usage_mb,
            "memory_usage_percent": self.memory_usage_percent,
            "operations_per_second": self.operations_per_second,
            "average_response_time_ms": self.average_response_time_ms,
            "error_rate": self.error_rate,
            "uptime_seconds": self.uptime_seconds,
            "last_operation_time": self.last_operation_time
        }

@dataclass
class AgentStatus:
    """Complete status information for an agent."""
    agent_name: str
    health_status: HealthStatus
    is_running: bool
    performance_metrics: PerformanceMetrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)
    start_time: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "health_status": self.health_status.value,
            "is_running": self.is_running,
            "performance_metrics": self.performance_metrics.to_dict(),
            "custom_metrics": self.custom_metrics,
            "alerts": self.alerts,
            "last_updated": self.last_updated,
            "start_time": self.start_time,
            "uptime_seconds": int(time.time() - self.start_time)
        }

class SharedStatusMonitor:
    """
    Shared status monitor for all agents - eliminates massive status monitoring duplication.
    Provides real-time health monitoring, performance tracking, and alerting.
    """
    
    def __init__(self, agent_name: str, monitoring_interval: float = 5.0):
        self.agent_name = agent_name
        self.monitoring_interval = monitoring_interval
        
        # Get shared utilities
        self.redis_conn = get_shared_redis()
        self.logger = get_shared_logger(agent_name, "status_monitor")
        
        # Agent status
        self.status = AgentStatus(
            agent_name=agent_name,
            health_status=HealthStatus.HEALTHY,
            is_running=False,
            performance_metrics=PerformanceMetrics()
        )
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Operation tracking
        self.operation_count = 0
        self.error_count = 0
        self.response_times: List[float] = []
        self.max_response_times = 100  # Keep last 100 response times
        
        # Health thresholds
        self.health_thresholds = {
            "cpu_warning": 70.0,      # CPU usage %
            "cpu_critical": 90.0,
            "memory_warning": 80.0,   # Memory usage %
            "memory_critical": 95.0,
            "error_rate_warning": 0.05,  # 5% error rate
            "error_rate_critical": 0.15, # 15% error rate
            "response_time_warning": 1000.0,  # 1 second
            "response_time_critical": 5000.0   # 5 seconds
        }
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[str, HealthStatus, str], None]] = []
        
        # System info
        self.process = psutil.Process()
        
        self.logger.info(f"Status monitor initialized for {agent_name}")
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.status.is_running = True
        self.status.start_time = time.time()
        
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name=f"{self.agent_name}_status_monitor"
        )
        self.monitoring_thread.start()
        
        self.logger.info(f"Status monitoring started for {self.agent_name}")
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.status.is_running = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        
        self.logger.info(f"Status monitoring stopped for {self.agent_name}")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Update performance metrics
                self._update_performance_metrics()
                
                # Evaluate health status
                self._evaluate_health_status()
                
                # Store status in Redis
                self._store_status()
                
                # Check for alerts
                self._check_alerts()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _update_performance_metrics(self):
        """Update performance metrics."""
        try:
            # CPU usage
            self.status.performance_metrics.cpu_usage = self.process.cpu_percent()
            
            # Memory usage
            memory_info = self.process.memory_info()
            self.status.performance_metrics.memory_usage_mb = memory_info.rss / 1024 / 1024
            
            system_memory = psutil.virtual_memory()
            self.status.performance_metrics.memory_usage_percent = (
                memory_info.rss / system_memory.total * 100
            )
            
            # Operations per second
            current_time = time.time()
            uptime = current_time - self.status.start_time
            if uptime > 0:
                self.status.performance_metrics.operations_per_second = self.operation_count / uptime
            
            # Average response time
            if self.response_times:
                self.status.performance_metrics.average_response_time_ms = sum(self.response_times) / len(self.response_times)
            
            # Error rate
            if self.operation_count > 0:
                self.status.performance_metrics.error_rate = self.error_count / self.operation_count
            
            # Uptime
            self.status.performance_metrics.uptime_seconds = int(uptime)
            self.status.performance_metrics.last_operation_time = current_time
            
            # Update timestamp
            self.status.last_updated = current_time
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    def _evaluate_health_status(self):
        """Evaluate overall health status based on metrics."""
        metrics = self.status.performance_metrics
        issues = []
        
        # Check CPU usage
        if metrics.cpu_usage > self.health_thresholds["cpu_critical"]:
            issues.append(("CPU usage critical", HealthStatus.CRITICAL))
        elif metrics.cpu_usage > self.health_thresholds["cpu_warning"]:
            issues.append(("CPU usage high", HealthStatus.WARNING))
        
        # Check memory usage
        if metrics.memory_usage_percent > self.health_thresholds["memory_critical"]:
            issues.append(("Memory usage critical", HealthStatus.CRITICAL))
        elif metrics.memory_usage_percent > self.health_thresholds["memory_warning"]:
            issues.append(("Memory usage high", HealthStatus.WARNING))
        
        # Check error rate
        if metrics.error_rate > self.health_thresholds["error_rate_critical"]:
            issues.append(("Error rate critical", HealthStatus.CRITICAL))
        elif metrics.error_rate > self.health_thresholds["error_rate_warning"]:
            issues.append(("Error rate high", HealthStatus.WARNING))
        
        # Check response time
        if metrics.average_response_time_ms > self.health_thresholds["response_time_critical"]:
            issues.append(("Response time critical", HealthStatus.CRITICAL))
        elif metrics.average_response_time_ms > self.health_thresholds["response_time_warning"]:
            issues.append(("Response time slow", HealthStatus.WARNING))
        
        # Determine overall health
        if any(issue[1] == HealthStatus.CRITICAL for issue in issues):
            self.status.health_status = HealthStatus.CRITICAL
        elif any(issue[1] == HealthStatus.WARNING for issue in issues):
            self.status.health_status = HealthStatus.WARNING
        else:
            self.status.health_status = HealthStatus.HEALTHY
        
        # Update alerts
        self.status.alerts = [issue[0] for issue in issues]
    
    def _store_status(self):
        """Store current status in Redis."""
        try:
            status_data = self.status.to_dict()
            self.redis_conn.store_agent_status(self.agent_name, status_data)
        except Exception as e:
            self.logger.error(f"Error storing status in Redis: {e}")
    
    def _check_alerts(self):
        """Check for alerts and trigger callbacks."""
        if self.status.alerts and self.alert_callbacks:
            for alert in self.status.alerts:
                for callback in self.alert_callbacks:
                    try:
                        callback(self.agent_name, self.status.health_status, alert)
                    except Exception as e:
                        self.logger.error(f"Error in alert callback: {e}")
    
    # ============= PUBLIC METHODS =============
    
    def record_operation(self, response_time_ms: float, success: bool = True):
        """Record an operation for performance tracking."""
        self.operation_count += 1
        
        if not success:
            self.error_count += 1
        
        # Store response time
        self.response_times.append(response_time_ms)
        if len(self.response_times) > self.max_response_times:
            self.response_times.pop(0)
    
    def add_custom_metric(self, name: str, value: Any):
        """Add a custom metric."""
        self.status.custom_metrics[name] = {
            "value": value,
            "timestamp": time.time()
        }
    
    def add_alert_callback(self, callback: Callable[[str, HealthStatus, str], None]):
        """Add an alert callback function."""
        self.alert_callbacks.append(callback)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return self.status.to_dict()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        return {
            "agent_name": self.agent_name,
            "health_status": self.status.health_status.value,
            "uptime_hours": self.status.performance_metrics.uptime_seconds / 3600,
            "total_operations": self.operation_count,
            "operations_per_second": self.status.performance_metrics.operations_per_second,
            "error_rate_percent": self.status.performance_metrics.error_rate * 100,
            "avg_response_time_ms": self.status.performance_metrics.average_response_time_ms,
            "cpu_usage_percent": self.status.performance_metrics.cpu_usage,
            "memory_usage_mb": self.status.performance_metrics.memory_usage_mb,
            "current_alerts": len(self.status.alerts),
            "is_monitoring": self.is_monitoring
        }
    
    def set_health_thresholds(self, thresholds: Dict[str, float]):
        """Update health thresholds."""
        self.health_thresholds.update(thresholds)
        self.logger.info(f"Updated health thresholds: {thresholds}")
    
    def force_health_check(self):
        """Force an immediate health check."""
        self._update_performance_metrics()
        self._evaluate_health_status()
        self._store_status()
        self._check_alerts()

# ============= GLOBAL STATUS MANAGER =============

class GlobalStatusManager:
    """Manager for all agent status monitors."""
    
    def __init__(self):
        self.monitors: Dict[str, SharedStatusMonitor] = {}
        self.redis_conn = get_shared_redis()
        self.logger = get_shared_logger("global_status_manager", "system")
        
        # Global alerts
        self.global_alert_callbacks: List[Callable[[str, HealthStatus, str], None]] = []
    
    def register_agent(self, agent_name: str, monitoring_interval: float = 5.0) -> SharedStatusMonitor:
        """Register an agent for monitoring."""
        if agent_name in self.monitors:
            return self.monitors[agent_name]
        
        monitor = SharedStatusMonitor(agent_name, monitoring_interval)
        
        # Add global alert callback
        monitor.add_alert_callback(self._global_alert_handler)
        
        self.monitors[agent_name] = monitor
        self.logger.info(f"Registered agent for monitoring: {agent_name}")
        
        return monitor
    
    def start_all_monitoring(self):
        """Start monitoring for all registered agents."""
        for monitor in self.monitors.values():
            monitor.start_monitoring()
        
        self.logger.info(f"Started monitoring for {len(self.monitors)} agents")
    
    def stop_all_monitoring(self):
        """Stop monitoring for all registered agents."""
        for monitor in self.monitors.values():
            monitor.stop_monitoring()
        
        self.logger.info(f"Stopped monitoring for {len(self.monitors)} agents")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        system_status = {
            "total_agents": len(self.monitors),
            "healthy_agents": 0,
            "warning_agents": 0,
            "critical_agents": 0,
            "error_agents": 0,
            "agents": {},
            "system_alerts": [],
            "timestamp": time.time()
        }
        
        for agent_name, monitor in self.monitors.items():
            status = monitor.get_status()
            system_status["agents"][agent_name] = status
            
            # Count by health status
            health = status["health_status"]
            if health == "healthy":
                system_status["healthy_agents"] += 1
            elif health == "warning":
                system_status["warning_agents"] += 1
            elif health == "critical":
                system_status["critical_agents"] += 1
            else:
                system_status["error_agents"] += 1
            
            # Collect system-wide alerts
            if status["alerts"]:
                for alert in status["alerts"]:
                    system_status["system_alerts"].append(f"{agent_name}: {alert}")
        
        return system_status
    
    def get_performance_overview(self) -> Dict[str, Any]:
        """Get performance overview of all agents."""
        overview = {
            "total_agents": len(self.monitors),
            "avg_cpu_usage": 0.0,
            "total_memory_usage_mb": 0.0,
            "avg_response_time_ms": 0.0,
            "total_operations": 0,
            "overall_error_rate": 0.0,
            "agent_summaries": {}
        }
        
        if not self.monitors:
            return overview
        
        cpu_usages = []
        response_times = []
        total_ops = 0
        total_errors = 0
        
        for agent_name, monitor in self.monitors.items():
            summary = monitor.get_performance_summary()
            overview["agent_summaries"][agent_name] = summary
            
            cpu_usages.append(summary["cpu_usage_percent"])
            response_times.append(summary["avg_response_time_ms"])
            total_ops += summary["total_operations"]
            total_errors += summary["total_operations"] * (summary["error_rate_percent"] / 100)
            overview["total_memory_usage_mb"] += summary["memory_usage_mb"]
        
        overview["avg_cpu_usage"] = sum(cpu_usages) / len(cpu_usages)
        overview["avg_response_time_ms"] = sum(response_times) / len(response_times)
        overview["total_operations"] = total_ops
        overview["overall_error_rate"] = (total_errors / total_ops * 100) if total_ops > 0 else 0
        
        return overview
    
    def add_global_alert_callback(self, callback: Callable[[str, HealthStatus, str], None]):
        """Add a global alert callback."""
        self.global_alert_callbacks.append(callback)
    
    def _global_alert_handler(self, agent_name: str, health_status: HealthStatus, alert: str):
        """Handle global alerts."""
        self.logger.warning(f"ALERT from {agent_name}: {alert} (status: {health_status.value})")
        
        # Trigger global alert callbacks
        for callback in self.global_alert_callbacks:
            try:
                callback(agent_name, health_status, alert)
            except Exception as e:
                self.logger.error(f"Error in global alert callback: {e}")

# Global status manager instance
_global_status_manager: Optional[GlobalStatusManager] = None

def get_global_status_manager() -> GlobalStatusManager:
    """Get the global status manager."""
    global _global_status_manager
    
    if _global_status_manager is None:
        _global_status_manager = GlobalStatusManager()
    
    return _global_status_manager

def get_agent_monitor(agent_name: str, monitoring_interval: float = 5.0) -> SharedStatusMonitor:
    """Get status monitor for a specific agent."""
    manager = get_global_status_manager()
    return manager.register_agent(agent_name, monitoring_interval)

# Example usage and testing
if __name__ == "__main__":
    def test_status_monitor():
        """Test the status monitoring system."""
        print("🧪 Testing Shared Status Monitor...")
        
        # Test individual monitor
        monitor = SharedStatusMonitor("test_agent")
        monitor.start_monitoring()
        
        # Simulate some operations
        for i in range(10):
            monitor.record_operation(50.0 + i * 10, success=(i % 5 != 0))
            time.sleep(0.1)
        
        # Add custom metrics
        monitor.add_custom_metric("test_metric", 42.0)
        monitor.add_custom_metric("another_metric", "healthy")
        
        # Get status
        status = monitor.get_status()
        print(f"Agent status: {status}")
        
        performance = monitor.get_performance_summary()
        print(f"Performance summary: {performance}")
        
        # Test global manager
        manager = get_global_status_manager()
        
        # Register multiple agents
        for agent_name in ["agent_1", "agent_2", "agent_3"]:
            agent_monitor = manager.register_agent(agent_name)
            agent_monitor.start_monitoring()
            
            # Simulate operations
            for i in range(5):
                agent_monitor.record_operation(100.0 + i * 20, success=True)
        
        time.sleep(6)  # Wait for monitoring cycle
        
        # Get system status
        system_status = manager.get_system_status()
        print(f"System status: {system_status}")
        
        overview = manager.get_performance_overview()
        print(f"Performance overview: {overview}")
        
        # Cleanup
        monitor.stop_monitoring()
        manager.stop_all_monitoring()
        
        print("✅ Shared Status Monitor tests completed!")
    
    test_status_monitor()
