# failure_prevention/monitor/system_watcher.py
"""
System Watcher - Monitors CPU, memory, async queues, and system health
"""

import asyncio
import psutil
import time
from typing import Dict, Any, Optional
from datetime import datetime
from ..logs.failure_agent_logger import FailureLogger
from .. import FailureType, AlertLevel

class SystemWatcher:
    """Monitors system resources and performance metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = FailureLogger("SystemWatcher")
        self.is_running = False
        
        # Thresholds
        self.cpu_threshold = config.get('cpu_threshold', 80.0)
        self.memory_threshold = config.get('memory_threshold', 85.0)
        self.queue_lag_threshold = config.get('queue_lag_threshold', 100)
        
        # Monitoring intervals
        self.check_interval = config.get('check_interval', 10)  # seconds
        
        # Performance tracking
        self.performance_history = []
        self.last_heartbeat = time.time()
        
    async def start(self):
        """Start system monitoring"""
        self.is_running = True
        self.logger.info("System monitoring started")
        
        # Start monitoring tasks
        await asyncio.gather(
            self._monitor_resources(),
            self._monitor_heartbeat(),
            self._monitor_async_health()
        )
    
    async def stop(self):
        """Stop system monitoring"""
        self.is_running = False
        self.logger.info("System monitoring stopped")
    
    async def _monitor_resources(self):
        """Monitor CPU and memory usage"""
        while self.is_running:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Check thresholds
                if cpu_percent > self.cpu_threshold:
                    await self._report_issue(
                        FailureType.SYSTEM_LAG,
                        AlertLevel.HIGH if cpu_percent > 90 else AlertLevel.MEDIUM,
                        f"High CPU usage: {cpu_percent}%"
                    )
                
                if memory.percent > self.memory_threshold:
                    await self._report_issue(
                        FailureType.MEMORY_LEAK,
                        AlertLevel.HIGH if memory.percent > 95 else AlertLevel.MEDIUM,
                        f"High memory usage: {memory.percent}%"
                    )
                
                # Store performance data
                self.performance_history.append({
                    'timestamp': datetime.now(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available': memory.available
                })
                
                # Limit history size
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-500:]
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error monitoring resources: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _monitor_heartbeat(self):
        """Monitor system heartbeat and responsiveness"""
        while self.is_running:
            try:
                current_time = time.time()
                time_since_heartbeat = current_time - self.last_heartbeat
                
                if time_since_heartbeat > 30:  # 30 seconds without heartbeat
                    await self._report_issue(
                        FailureType.SYSTEM_LAG,
                        AlertLevel.CRITICAL,
                        f"System unresponsive for {time_since_heartbeat} seconds"
                    )
                
                self.last_heartbeat = current_time
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring heartbeat: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_async_health(self):
        """Monitor asyncio event loop health"""
        while self.is_running:
            try:
                loop = asyncio.get_event_loop()
                
                # Check if event loop is overloaded
                start_time = time.time()
                await asyncio.sleep(0.1)  # Small delay
                actual_delay = time.time() - start_time
                
                if actual_delay > 0.5:  # If 0.1s sleep took > 0.5s
                    await self._report_issue(
                        FailureType.SYSTEM_LAG,
                        AlertLevel.HIGH,
                        f"Event loop lag detected: {actual_delay:.2f}s"
                    )
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring async health: {e}")
                await asyncio.sleep(10)
    
    async def _report_issue(self, failure_type: FailureType, alert_level: AlertLevel, description: str):
        """Report a detected issue"""
        self.logger.warning(f"System issue detected: {description}")
        
        # In a real implementation, this would integrate with the main agent
        # For now, we'll log and potentially trigger callbacks
        issue_data = {
            'type': failure_type.value,
            'level': alert_level.value,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'source': 'SystemWatcher'
        }
        
        await self.logger.log_failure(issue_data)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters()._asdict(),
                'process_count': len(psutil.pids()),
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return {}
    
    def get_performance_history(self, hours: int = 1) -> list:
        """Get performance history for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            entry for entry in self.performance_history 
            if entry['timestamp'] > cutoff_time
        ]

