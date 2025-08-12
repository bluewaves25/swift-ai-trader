#!/usr/bin/env python3
"""
System Monitor - SIMPLIFIED CORE MODULE
Handles system health monitoring and resource tracking
SIMPLE: ~120 lines focused on monitoring only
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from ...shared_utils import get_shared_logger

class SystemMonitor:
    """
    Simplified system monitoring engine.
    Focuses on essential system health monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("failure_prevention", "system_monitor")
        
        # Monitoring thresholds
        self.thresholds = {
            "cpu_critical": 0.9,      # 90% CPU usage
            "memory_critical": 0.85,  # 85% memory usage
            "disk_critical": 0.9,     # 90% disk usage
            "latency_critical": 1000,  # 1000ms latency
            "error_rate_critical": 0.05  # 5% error rate
        }
        
        # Health tracking
        self.health_history = []
        self.current_metrics = {}
    
    async def check_critical_resources(self) -> Dict[str, Any]:
        """Check critical system resources (fast check)."""
        try:
            # Get current system metrics
            metrics = await self._get_system_metrics()
            
            # Check for immediate threats
            immediate_threats = []
            
            # CPU check
            if metrics["cpu_usage"] > self.thresholds["cpu_critical"]:
                immediate_threats.append({
                    "threat_type": "cpu_overload",
                    "severity": "critical",
                    "value": metrics["cpu_usage"],
                    "threshold": self.thresholds["cpu_critical"]
                })
            
            # Memory check
            if metrics["memory_usage"] > self.thresholds["memory_critical"]:
                immediate_threats.append({
                    "threat_type": "memory_overload",
                    "severity": "critical",
                    "value": metrics["memory_usage"],
                    "threshold": self.thresholds["memory_critical"]
                })
            
            # Calculate health score
            health_score = self._calculate_health_score(metrics)
            
            result = {
                "timestamp": time.time(),
                "metrics": metrics,
                "immediate_threats": immediate_threats,
                "health_score": health_score,
                "critical_alerts": len(immediate_threats)
            }
            
            # Update current metrics
            self.current_metrics = metrics
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Error checking critical resources: {e}")
            return {
                "error": str(e),
                "timestamp": time.time(),
                "immediate_threats": [],
                "health_score": 0.5
            }
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check comprehensive system health (tactical check)."""
        try:
            # Get detailed system metrics
            detailed_metrics = await self._get_detailed_metrics()
            
            # Analyze health trends
            health_trends = self._analyze_health_trends()
            
            # Check for potential issues
            potential_issues = self._identify_potential_issues(detailed_metrics)
            
            result = {
                "timestamp": time.time(),
                "detailed_metrics": detailed_metrics,
                "health_trends": health_trends,
                "potential_issues": potential_issues,
                "overall_health": self._calculate_overall_health(detailed_metrics),
                "recommendations": self._generate_recommendations(potential_issues)
            }
            
            # Update health history
            self._update_health_history(result)
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Error checking system health: {e}")
            return {
                "error": str(e),
                "timestamp": time.time(),
                "overall_health": 0.5
            }
    
    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        try:
            # Comprehensive metrics including historical data
            return {
                "current_metrics": self.current_metrics,
                "health_history": self.health_history[-10:],  # Last 10 entries
                "overall_health": self._calculate_overall_health(self.current_metrics),
                "system_uptime": self._get_system_uptime(),
                "performance_trends": self._get_performance_trends(),
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting comprehensive metrics: {e}")
            return {"error": str(e), "timestamp": time.time()}
    
    # ============= PRIVATE MONITORING METHODS =============
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            # Simulate system metrics (in production, would use psutil)
            import random
            
            metrics = {
                "cpu_usage": random.uniform(0.1, 0.8),      # 10-80% CPU
                "memory_usage": random.uniform(0.3, 0.7),   # 30-70% memory
                "disk_usage": random.uniform(0.4, 0.8),     # 40-80% disk
                "network_latency": random.uniform(10, 100), # 10-100ms latency
                "active_connections": random.randint(5, 50),
                "error_rate": random.uniform(0.0, 0.02),    # 0-2% error rate
                "timestamp": time.time()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"Error getting system metrics: {e}")
            return {
                "cpu_usage": 0.5,
                "memory_usage": 0.5,
                "disk_usage": 0.5,
                "error_rate": 0.0,
                "timestamp": time.time()
            }
    
    async def _get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed system metrics."""
        try:
            basic_metrics = await self._get_system_metrics()
            
            # Add detailed metrics
            detailed_metrics = {
                **basic_metrics,
                "process_count": 25,
                "thread_count": 150,
                "file_descriptors": 200,
                "swap_usage": 0.1,
                "load_average": [1.2, 1.1, 1.0],
                "network_io": {"bytes_sent": 1000000, "bytes_recv": 2000000},
                "disk_io": {"read_bytes": 500000, "write_bytes": 300000}
            }
            
            return detailed_metrics
            
        except Exception as e:
            self.logger.warning(f"Error getting detailed metrics: {e}")
            return await self._get_system_metrics()
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall health score from metrics."""
        try:
            # Simple health score calculation
            cpu_score = max(0.0, 1.0 - metrics.get("cpu_usage", 0.5))
            memory_score = max(0.0, 1.0 - metrics.get("memory_usage", 0.5))
            disk_score = max(0.0, 1.0 - metrics.get("disk_usage", 0.5))
            error_score = max(0.0, 1.0 - (metrics.get("error_rate", 0.0) * 20))  # Scale error rate
            
            # Weighted average
            health_score = (cpu_score * 0.3 + memory_score * 0.3 + 
                          disk_score * 0.2 + error_score * 0.2)
            
            return min(1.0, max(0.0, health_score))
            
        except Exception as e:
            self.logger.warning(f"Error calculating health score: {e}")
            return 0.5
    
    def _analyze_health_trends(self) -> Dict[str, Any]:
        """Analyze health trends from history."""
        try:
            if len(self.health_history) < 2:
                return {"trend": "stable", "change": 0.0}
            
            # Simple trend analysis
            recent_health = self.health_history[-1].get("overall_health", 0.5)
            previous_health = self.health_history[-2].get("overall_health", 0.5)
            
            change = recent_health - previous_health
            
            if change > 0.1:
                trend = "improving"
            elif change < -0.1:
                trend = "degrading"
            else:
                trend = "stable"
            
            return {
                "trend": trend,
                "change": change,
                "recent_health": recent_health,
                "previous_health": previous_health
            }
            
        except Exception as e:
            self.logger.warning(f"Error analyzing health trends: {e}")
            return {"trend": "unknown", "change": 0.0}
    
    def _identify_potential_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential issues from metrics."""
        try:
            issues = []
            
            # Check for warning-level issues
            cpu_usage = metrics.get("cpu_usage", 0.0)
            if cpu_usage > 0.7:  # 70% warning threshold
                issues.append({
                    "issue_type": "high_cpu_usage",
                    "severity": "warning",
                    "value": cpu_usage,
                    "recommendation": "Monitor CPU usage and consider optimization"
                })
            
            memory_usage = metrics.get("memory_usage", 0.0)
            if memory_usage > 0.6:  # 60% warning threshold
                issues.append({
                    "issue_type": "high_memory_usage",
                    "severity": "warning",
                    "value": memory_usage,
                    "recommendation": "Monitor memory usage and consider cleanup"
                })
            
            error_rate = metrics.get("error_rate", 0.0)
            if error_rate > 0.01:  # 1% warning threshold
                issues.append({
                    "issue_type": "elevated_error_rate",
                    "severity": "warning",
                    "value": error_rate,
                    "recommendation": "Investigate error sources"
                })
            
            return issues
            
        except Exception as e:
            self.logger.warning(f"Error identifying potential issues: {e}")
            return []
    
    def _calculate_overall_health(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall system health."""
        return self._calculate_health_score(metrics)
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []
        
        for issue in issues:
            recommendation = issue.get("recommendation", "Monitor system health")
            if recommendation not in recommendations:
                recommendations.append(recommendation)
        
        return recommendations
    
    def _update_health_history(self, health_data: Dict[str, Any]):
        """Update health history."""
        try:
            self.health_history.append({
                "timestamp": health_data.get("timestamp", time.time()),
                "overall_health": health_data.get("overall_health", 0.5),
                "issues_count": len(health_data.get("potential_issues", []))
            })
            
            # Keep only last 50 entries
            if len(self.health_history) > 50:
                self.health_history = self.health_history[-50:]
                
        except Exception as e:
            self.logger.warning(f"Error updating health history: {e}")
    
    def _get_system_uptime(self) -> float:
        """Get system uptime in seconds."""
        # Simulate uptime
        return time.time() % 86400  # Uptime within a day
    
    def _get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends."""
        try:
            if len(self.health_history) < 5:
                return {"trend": "insufficient_data"}
            
            # Simple trend calculation
            recent_avg = sum(h["overall_health"] for h in self.health_history[-5:]) / 5
            older_avg = sum(h["overall_health"] for h in self.health_history[-10:-5]) / 5 if len(self.health_history) >= 10 else recent_avg
            
            return {
                "recent_average_health": recent_avg,
                "older_average_health": older_avg,
                "trend_direction": "improving" if recent_avg > older_avg else "stable" if recent_avg == older_avg else "declining"
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting performance trends: {e}")
            return {"trend": "unknown"}
    
    # ============= UTILITY METHODS =============
    
    def get_current_health(self) -> Dict[str, Any]:
        """Get current health summary."""
        return {
            "current_metrics": self.current_metrics,
            "health_score": self._calculate_health_score(self.current_metrics),
            "last_update": self.current_metrics.get("timestamp", 0)
        }
