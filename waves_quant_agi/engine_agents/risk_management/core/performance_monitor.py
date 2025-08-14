#!/usr/bin/env python3
"""
Performance Monitor - Risk Management Performance Tracking
Provides comprehensive performance monitoring and alerting for risk management operations.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from enum import Enum
from ...shared_utils import get_shared_logger

class MetricType(Enum):
    """Types of performance metrics."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"

class PerformanceAlert:
    """Performance alert with severity and details."""
    
    def __init__(self, alert_type: str, message: str, severity: str = "warning", 
                 threshold: float = 0.0, current_value: float = 0.0):
        self.alert_type = alert_type
        self.message = message
        self.severity = severity
        self.threshold = threshold
        self.current_value = current_value
        self.timestamp = time.time()
        self.acknowledged = False

class PerformanceMetric:
    """Individual performance metric with history."""
    
    def __init__(self, name: str, metric_type: MetricType, unit: str = ""):
        self.name = name
        self.metric_type = metric_type
        self.unit = unit
        self.values = []
        self.timestamps = []
        self.count = 0
        self.sum = 0.0
        self.min_value = float('inf')
        self.max_value = float('-inf')
        self.last_update = time.time()
    
    def add_value(self, value: float):
        """Add a new value to the metric."""
        current_time = time.time()
        
        self.values.append(value)
        self.timestamps.append(current_time)
        self.count += 1
        self.sum += value
        self.min_value = min(self.min_value, value)
        self.max_value = max(self.max_value, value)
        self.last_update = current_time
        
        # Keep only last 1000 values to prevent memory bloat
        if len(self.values) > 1000:
            self.values.pop(0)
            self.timestamps.pop(0)
    
    def get_average(self) -> float:
        """Get average value."""
        return self.sum / self.count if self.count > 0 else 0.0
    
    def get_recent_average(self, window_seconds: int = 60) -> float:
        """Get average value over recent time window."""
        current_time = time.time()
        recent_values = [
            value for value, timestamp in zip(self.values, self.timestamps)
            if current_time - timestamp <= window_seconds
        ]
        return sum(recent_values) / len(recent_values) if recent_values else 0.0

class PerformanceMonitor:
    """Performance monitoring system for risk management operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("risk_management", "performance_monitor")
        
        # Performance metrics
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.alerts: List[PerformanceAlert] = []
        
        # Configuration
        self.alert_thresholds = config.get("performance_thresholds", {
            "latency_critical": 1000.0,  # ms
            "latency_warning": 500.0,    # ms
            "error_rate_critical": 0.1,  # 10%
            "error_rate_warning": 0.05,  # 5%
            "memory_critical": 0.9,      # 90%
            "memory_warning": 0.8,       # 80%
        })
        
        # Initialize default metrics
        self._initialize_default_metrics()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None
        
        self.logger.info("Performance Monitor initialized")
    
    def _initialize_default_metrics(self):
        """Initialize default performance metrics."""
        default_metrics = [
            ("risk_calculation_latency", MetricType.LATENCY, "ms"),
            ("risk_validation_latency", MetricType.LATENCY, "ms"),
            ("risk_operations_per_second", MetricType.THROUGHPUT, "ops/sec"),
            ("risk_validation_error_rate", MetricType.ERROR_RATE, "%"),
            ("risk_calculation_error_rate", MetricType.ERROR_RATE, "%"),
            ("memory_usage", MetricType.MEMORY_USAGE, "%"),
            ("cpu_usage", MetricType.CPU_USAGE, "%"),
        ]
        
        for name, metric_type, unit in default_metrics:
            self.metrics[name] = PerformanceMetric(name, metric_type, unit)
    
    async def start_monitoring(self):
        """Start performance monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring."""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Check for alerts
                await self._check_performance_alerts()
                
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _check_performance_alerts(self):
        """Check for performance alerts based on thresholds."""
        try:
            for metric_name, metric in self.metrics.items():
                current_value = metric.get_recent_average(60)  # 1 minute window
                
                if metric.metric_type == MetricType.LATENCY:
                    if current_value > self.alert_thresholds["latency_critical"]:
                        await self._create_alert(metric_name, "critical", current_value, 
                                               self.alert_thresholds["latency_critical"])
                    elif current_value > self.alert_thresholds["latency_warning"]:
                        await self._create_alert(metric_name, "warning", current_value, 
                                               self.alert_thresholds["latency_warning"])
                
                elif metric.metric_type == MetricType.ERROR_RATE:
                    if current_value > self.alert_thresholds["error_rate_critical"]:
                        await self._create_alert(metric_name, "critical", current_value, 
                                               self.alert_thresholds["error_rate_critical"])
                    elif current_value > self.alert_thresholds["error_rate_warning"]:
                        await self._create_alert(metric_name, "warning", current_value, 
                                               self.alert_thresholds["error_rate_warning"])
                
                elif metric.metric_type == MetricType.MEMORY_USAGE:
                    if current_value > self.alert_thresholds["memory_critical"]:
                        await self._create_alert(metric_name, "critical", current_value, 
                                               self.alert_thresholds["memory_critical"])
                    elif current_value > self.alert_thresholds["memory_warning"]:
                        await self._create_alert(metric_name, "warning", current_value, 
                                               self.alert_thresholds["memory_warning"])
        
        except Exception as e:
            self.logger.error(f"Error checking performance alerts: {e}")
    
    async def _create_alert(self, metric_name: str, severity: str, current_value: float, threshold: float):
        """Create a new performance alert."""
        try:
            # Check if similar alert already exists
            existing_alert = next(
                (alert for alert in self.alerts 
                 if alert.alert_type == metric_name and not alert.acknowledged), None
            )
            
            if not existing_alert:
                message = f"{metric_name} exceeded {severity} threshold: {current_value:.2f} > {threshold:.2f}"
                alert = PerformanceAlert(
                    alert_type=metric_name,
                    message=message,
                    severity=severity,
                    threshold=threshold,
                    current_value=current_value
                )
                self.alerts.append(alert)
                self.logger.warning(f"Performance alert: {message}")
        
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
    
    async def _cleanup_old_alerts(self):
        """Clean up old acknowledged alerts."""
        try:
            current_time = time.time()
            self.alerts = [
                alert for alert in self.alerts
                if not alert.acknowledged or (current_time - alert.timestamp) < 3600  # Keep for 1 hour
            ]
        except Exception as e:
            self.logger.error(f"Error cleaning up old alerts: {e}")
    
    def record_metric(self, metric_name: str, value: float):
        """Record a performance metric value."""
        try:
            if metric_name in self.metrics:
                self.metrics[metric_name].add_value(value)
            else:
                # Create new metric if it doesn't exist
                self.metrics[metric_name] = PerformanceMetric(metric_name, MetricType.LATENCY)
                self.metrics[metric_name].add_value(value)
        
        except Exception as e:
            self.logger.error(f"Error recording metric {metric_name}: {e}")
    
    def record_latency(self, operation_name: str, latency_ms: float):
        """Record operation latency."""
        metric_name = f"{operation_name}_latency"
        self.record_metric(metric_name, latency_ms)
    
    def record_throughput(self, operation_name: str, operations_per_second: float):
        """Record operation throughput."""
        metric_name = f"{operation_name}_throughput"
        self.record_metric(metric_name, operations_per_second)
    
    def record_error_rate(self, operation_name: str, error_rate: float):
        """Record operation error rate."""
        metric_name = f"{operation_name}_error_rate"
        self.record_metric(metric_name, error_rate)
    
    def get_metric_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        try:
            summary = {}
            for metric_name, metric in self.metrics.items():
                summary[metric_name] = {
                    "current": metric.get_recent_average(60),
                    "average": metric.get_average(),
                    "min": metric.min_value if metric.min_value != float('inf') else 0.0,
                    "max": metric.max_value if metric.max_value != float('-inf') else 0.0,
                    "count": metric.count,
                    "unit": metric.unit
                }
            return summary
        
        except Exception as e:
            self.logger.error(f"Error getting metric summary: {e}")
            return {}
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active (unacknowledged) alerts."""
        try:
            return [
                {
                    "alert_type": alert.alert_type,
                    "message": alert.message,
                    "severity": alert.severity,
                    "threshold": alert.threshold,
                    "current_value": alert.current_value,
                    "timestamp": alert.timestamp
                }
                for alert in self.alerts if not alert.acknowledged
            ]
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_type: str):
        """Acknowledge an alert."""
        try:
            for alert in self.alerts:
                if alert.alert_type == alert_type and not alert.acknowledged:
                    alert.acknowledged = True
                    self.logger.info(f"Alert acknowledged: {alert_type}")
                    break
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            await self.stop_monitoring()
            self.logger.info("Performance Monitor cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
