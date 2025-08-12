#!/usr/bin/env python3
"""
Performance Monitor - Real-time performance tracking and optimization
Monitors system performance metrics and provides optimization recommendations
Implements performance alerts and trend analysis
"""

import time
import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class MetricType(Enum):
    """Types of performance metrics."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    QUEUE_SIZE = "queue_size"

@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    metric_type: MetricType
    value: float
    timestamp: float
    component: str
    metadata: Dict[str, Any]

class PerformanceAlert:
    """Performance alert structure."""
    
    def __init__(self, alert_type: str, message: str, severity: str, 
                 component: str, current_value: float, threshold: float):
        self.alert_type = alert_type
        self.message = message
        self.severity = severity  # low, medium, high, critical
        self.component = component
        self.current_value = current_value
        self.threshold = threshold
        self.timestamp = time.time()
        self.acknowledged = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'alert_type': self.alert_type,
            'message': self.message,
            'severity': self.severity,
            'component': self.component,
            'current_value': self.current_value,
            'threshold': self.threshold,
            'timestamp': self.timestamp,
            'acknowledged': self.acknowledged
        }

class PerformanceMonitor:
    """Comprehensive performance monitoring system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Performance thresholds
        self.thresholds = config.get('performance_thresholds', {
            'max_latency_ms': 100,
            'min_throughput_per_sec': 1000,
            'max_error_rate': 0.01,
            'min_cache_hit_rate': 0.9,
            'max_memory_usage_percent': 80,
            'max_cpu_usage_percent': 80,
            'max_queue_size': 1000
        })
        
        # Metrics storage
        self.metrics: Dict[MetricType, List[PerformanceMetric]] = {
            metric_type: [] for metric_type in MetricType
        }
        
        # Alerts
        self.alerts: List[PerformanceAlert] = []
        self.max_alerts = config.get('max_alerts', 1000)
        
        # Performance tracking
        self.performance_history = []
        self.max_history = config.get('max_history', 10000)
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Statistics
        self.total_metrics_recorded = 0
        self.total_alerts_generated = 0
        
        # Performance trends
        self.trend_analysis_window = config.get('trend_analysis_window', 3600)  # 1 hour
    
    async def record_operation(self, operation_type: str, duration_ms: float, 
                              success: bool, component: str = "unknown", 
                              metadata: Dict[str, Any] = None):
        """Record operation performance metrics."""
        try:
            timestamp = time.time()
            
            # Record latency
            latency_metric = PerformanceMetric(
                metric_type=MetricType.LATENCY,
                value=duration_ms,
                timestamp=timestamp,
                component=component,
                metadata=metadata or {}
            )
            self._add_metric(MetricType.LATENCY, latency_metric)
            
            # Record throughput (operations per second)
            throughput = 1000 / max(duration_ms, 1)  # ops/sec
            throughput_metric = PerformanceMetric(
                metric_type=MetricType.THROUGHPUT,
                value=throughput,
                timestamp=timestamp,
                component=component,
                metadata=metadata or {}
            )
            self._add_metric(MetricType.THROUGHPUT, throughput_metric)
            
            # Record error rate
            error_rate = 0 if success else 1
            error_metric = PerformanceMetric(
                metric_type=MetricType.ERROR_RATE,
                value=error_rate,
                timestamp=timestamp,
                component=component,
                metadata=metadata or {}
            )
            self._add_metric(MetricType.ERROR_RATE, error_metric)
            
            # Update performance history
            self._update_performance_history(operation_type, duration_ms, success, component)
            
            # Check for performance issues
            await self._check_performance_alerts(component)
            
            self.total_metrics_recorded += 1
            
        except Exception as e:
            print(f"Error recording operation: {e}")
    
    def _add_metric(self, metric_type: MetricType, metric: PerformanceMetric):
        """Add metric to storage."""
        self.metrics[metric_type].append(metric)
        
        # Keep only recent metrics
        if len(self.metrics[metric_type]) > self.max_history:
            self.metrics[metric_type] = self.metrics[metric_type][-self.max_history:]
    
    def _update_performance_history(self, operation_type: str, duration_ms: float, 
                                   success: bool, component: str):
        """Update performance history for trend analysis."""
        history_entry = {
            'operation_type': operation_type,
            'duration_ms': duration_ms,
            'success': success,
            'component': component,
            'timestamp': time.time()
        }
        
        self.performance_history.append(history_entry)
        
        # Keep only recent history
        if len(self.performance_history) > self.max_history:
            self.performance_history = self.performance_history[-self.max_history:]
    
    async def _check_performance_alerts(self, component: str):
        """Check for performance issues and generate alerts."""
        try:
            # Check latency
            await self._check_latency_alerts(component)
            
            # Check throughput
            await self._check_throughput_alerts(component)
            
            # Check error rate
            await self._check_error_rate_alerts(component)
            
            # Check cache hit rate
            await self._check_cache_alerts(component)
            
        except Exception as e:
            print(f"Error checking performance alerts: {e}")
    
    async def _check_latency_alerts(self, component: str):
        """Check for latency issues."""
        recent_latencies = self._get_recent_metrics(MetricType.LATENCY, component, 100)
        
        if recent_latencies:
            avg_latency = np.mean([m.value for m in recent_latencies])
            max_threshold = self.thresholds['max_latency_ms']
            
            if avg_latency > max_threshold:
                alert = PerformanceAlert(
                    alert_type="high_latency",
                    message=f"High latency detected for {component}: {avg_latency:.2f}ms > {max_threshold}ms",
                    severity="high" if avg_latency > max_threshold * 1.5 else "medium",
                    component=component,
                    current_value=avg_latency,
                    threshold=max_threshold
                )
                await self._add_alert(alert)
    
    async def _check_throughput_alerts(self, component: str):
        """Check for throughput issues."""
        recent_throughput = self._get_recent_metrics(MetricType.THROUGHPUT, component, 100)
        
        if recent_throughput:
            avg_throughput = np.mean([m.value for m in recent_throughput])
            min_threshold = self.thresholds['min_throughput_per_sec']
            
            if avg_throughput < min_threshold:
                alert = PerformanceAlert(
                    alert_type="low_throughput",
                    message=f"Low throughput detected for {component}: {avg_throughput:.2f}/sec < {min_threshold}/sec",
                    severity="high" if avg_throughput < min_threshold * 0.5 else "medium",
                    component=component,
                    current_value=avg_throughput,
                    threshold=min_threshold
                )
                await self._add_alert(alert)
    
    async def _check_error_rate_alerts(self, component: str):
        """Check for error rate issues."""
        recent_errors = self._get_recent_metrics(MetricType.ERROR_RATE, component, 100)
        
        if recent_errors:
            error_rate = np.mean([m.value for m in recent_errors])
            max_threshold = self.thresholds['max_error_rate']
            
            if error_rate > max_threshold:
                alert = PerformanceAlert(
                    alert_type="high_error_rate",
                    message=f"High error rate detected for {component}: {error_rate:.2%} > {max_threshold:.2%}",
                    severity="critical" if error_rate > max_threshold * 2 else "high",
                    component=component,
                    current_value=error_rate,
                    threshold=max_threshold
                )
                await self._add_alert(alert)
    
    async def _check_cache_alerts(self, component: str):
        """Check for cache performance issues."""
        recent_cache = self._get_recent_metrics(MetricType.CACHE_HIT_RATE, component, 100)
        
        if recent_cache:
            cache_hit_rate = np.mean([m.value for m in recent_cache])
            min_threshold = self.thresholds['min_cache_hit_rate']
            
            if cache_hit_rate < min_threshold:
                alert = PerformanceAlert(
                    alert_type="low_cache_hit_rate",
                    message=f"Low cache hit rate for {component}: {cache_hit_rate:.2%} < {min_threshold:.2%}",
                    severity="medium",
                    component=component,
                    current_value=cache_hit_rate,
                    threshold=min_threshold
                )
                await self._add_alert(alert)
    
    def _get_recent_metrics(self, metric_type: MetricType, component: str, 
                           count: int) -> List[PerformanceMetric]:
        """Get recent metrics for a specific type and component."""
        all_metrics = self.metrics[metric_type]
        
        # Filter by component and get recent ones
        component_metrics = [m for m in all_metrics if m.component == component]
        return component_metrics[-count:] if component_metrics else []
    
    async def _add_alert(self, alert: PerformanceAlert):
        """Add performance alert."""
        self.alerts.append(alert)
        self.total_alerts_generated += 1
        
        # Keep only recent alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        # Trigger alert callbacks
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                print(f"Error in alert callback: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Add callback function for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def get_performance_summary(self, component: str = None, 
                               time_window: float = 3600) -> Dict[str, Any]:
        """Get performance summary for a component and time window."""
        try:
            cutoff_time = time.time() - time_window
            
            summary = {}
            
            for metric_type in MetricType:
                metrics = self.metrics[metric_type]
                
                # Filter by time and component
                if component:
                    filtered_metrics = [m for m in metrics 
                                      if m.timestamp > cutoff_time and m.component == component]
                else:
                    filtered_metrics = [m for m in metrics if m.timestamp > cutoff_time]
                
                if filtered_metrics:
                    values = [m.value for m in filtered_metrics]
                    summary[metric_type.value] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'mean': np.mean(values),
                        'median': np.median(values),
                        'std': np.std(values) if len(values) > 1 else 0
                    }
                else:
                    summary[metric_type.value] = None
            
            return summary
            
        except Exception as e:
            print(f"Error getting performance summary: {e}")
            return {}
    
    def get_performance_trends(self, component: str = None, 
                              time_window: float = 3600) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        try:
            cutoff_time = time.time() - time_window
            
            # Get recent performance history
            recent_history = [h for h in self.performance_history 
                            if h['timestamp'] > cutoff_time]
            
            if component:
                recent_history = [h for h in recent_history if h['component'] == component]
            
            if not recent_history:
                return {'trend': 'insufficient_data', 'message': 'No data available'}
            
            # Analyze trends
            latencies = [h['duration_ms'] for h in recent_history]
            success_rates = [1 if h['success'] else 0 for h in recent_history]
            
            # Calculate trend indicators
            if len(latencies) > 10:
                # Split data into two halves for trend comparison
                mid_point = len(latencies) // 2
                first_half = latencies[:mid_point]
                second_half = latencies[mid_point:]
                
                first_avg = np.mean(first_half)
                second_avg = np.mean(second_half)
                
                if second_avg < first_avg * 0.9:
                    latency_trend = "improving"
                elif second_avg > first_avg * 1.1:
                    latency_trend = "degrading"
                else:
                    latency_trend = "stable"
            else:
                latency_trend = "insufficient_data"
            
            # Success rate trend
            if len(success_rates) > 10:
                mid_point = len(success_rates) // 2
                first_half = success_rates[:mid_point]
                second_half = success_rates[mid_point:]
                
                first_avg = np.mean(first_half)
                second_avg = np.mean(second_half)
                
                if second_avg > first_avg * 1.05:
                    success_trend = "improving"
                elif second_avg < first_avg * 0.95:
                    success_trend = "degrading"
                else:
                    success_trend = "stable"
            else:
                success_trend = "insufficient_data"
            
            return {
                'latency_trend': latency_trend,
                'success_trend': success_trend,
                'overall_trend': self._determine_overall_trend(latency_trend, success_trend),
                'data_points': len(recent_history),
                'time_window': time_window
            }
            
        except Exception as e:
            print(f"Error analyzing performance trends: {e}")
            return {'trend': 'error', 'message': str(e)}
    
    def _determine_overall_trend(self, latency_trend: str, success_trend: str) -> str:
        """Determine overall performance trend."""
        if latency_trend == "improving" and success_trend == "improving":
            return "strongly_improving"
        elif latency_trend == "improving" or success_trend == "improving":
            return "improving"
        elif latency_trend == "degrading" and success_trend == "degrading":
            return "strongly_degrading"
        elif latency_trend == "degrading" or success_trend == "degrading":
            return "degrading"
        else:
            return "stable"
    
    def get_alerts(self, severity: str = None, component: str = None, 
                   acknowledged: bool = None) -> List[PerformanceAlert]:
        """Get performance alerts with optional filtering."""
        filtered_alerts = self.alerts
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
        
        if component:
            filtered_alerts = [a for a in filtered_alerts if a.component == component]
        
        if acknowledged is not None:
            filtered_alerts = [a for a in filtered_alerts if a.acknowledged == acknowledged]
        
        return filtered_alerts
    
    def acknowledge_alert(self, alert_index: int):
        """Acknowledge a performance alert."""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index].acknowledged = True
    
    def get_monitor_stats(self) -> Dict[str, Any]:
        """Get monitor statistics."""
        return {
            'total_metrics_recorded': self.total_metrics_recorded,
            'total_alerts_generated': self.total_alerts_generated,
            'current_alerts': len(self.alerts),
            'unacknowledged_alerts': len([a for a in self.alerts if not a.acknowledged]),
            'metrics_storage': {metric_type.value: len(metrics) for metric_type, metrics in self.metrics.items()},
            'performance_history_size': len(self.performance_history),
            'alert_callbacks': len(self.alert_callbacks),
            'timestamp': time.time()
        }
    
    def clear_metrics(self, metric_type: MetricType = None):
        """Clear metrics storage."""
        if metric_type:
            self.metrics[metric_type].clear()
        else:
            for metrics_list in self.metrics.values():
                metrics_list.clear()
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()
    
    def clear_history(self):
        """Clear performance history."""
        self.performance_history.clear()
