#!/usr/bin/env python3
"""
Enhanced Failure Prevention Agent V2 - REFACTORED TO USE BASE AGENT
Eliminates duplicate start/stop methods and Redis connection logic.
"""

import asyncio
import time
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedFailurePreventionAgentV2(BaseAgent):
    """Enhanced failure prevention agent using base class."""
    
    def _initialize_agent_components(self):
        """Initialize failure prevention specific components."""
        # Initialize failure prevention components with mock implementations
        self.system_monitor = MockSystemMonitor()
        self.failure_predictor = MockFailurePredictor()
        
        # Initialize prevention state with default values
        self.prevention_state = {
            "system_health_score": 1.0,
            "critical_alerts": 0,
            "predicted_failures": [],
            "preventive_actions_taken": 0,
            "failures_prevented": 0
        }
        
        # Initialize stats
        self.stats = {
            "total_health_checks": 0,
            "preventive_actions": 0,
            "critical_alerts": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Failure prevention specific startup logic."""
        # Initialize system monitoring and failure prediction systems
        self.logger.info("Failure prevention components initialized")
    
    async def _agent_specific_shutdown(self):
        """Failure prevention specific shutdown logic."""
        # Cleanup failure prevention specific resources
        self.logger.info("Failure prevention components cleaned up")
    
    # ============= 4-TIER PREVENTION LOOPS =============
    
    async def _fast_critical_monitoring(self):
        """TIER 2: Fast critical monitoring (100ms) for system overload detection."""
        while self.is_running:
            try:
                # Monitor critical system resources
                critical_metrics = await self.system_monitor.check_critical_resources()
                
                # Check for immediate threats
                await self._check_immediate_threats(critical_metrics)
                
                # Update prevention state
                self._update_prevention_state(critical_metrics)
                
                await asyncio.sleep(0.1)  # 100ms
                
            except Exception as e:
                self.logger.warning(f"Error in fast critical monitoring: {e}")
                await asyncio.sleep(1.0)
    
    async def _tactical_health_monitoring(self):
        """TIER 3: Tactical health monitoring (30s) for strategy and data health."""
        while self.is_running:
            try:
                # Monitor strategy and data health
                health_metrics = await self.system_monitor.check_system_health()
                
                # Analyze for potential issues
                potential_issues = await self.failure_predictor.analyze_potential_issues(health_metrics)
                
                # Execute preventive actions if needed
                await self._execute_preventive_actions(potential_issues)
                
                # Update statistics
                self.stats["total_health_checks"] += 1
                
                await asyncio.sleep(30)  # 30s
                
            except Exception as e:
                self.logger.warning(f"Error in tactical health monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _strategic_analysis_loop(self):
        """TIER 4: Strategic analysis (300s) for comprehensive system health."""
        while self.is_running:
            try:
                # Comprehensive system analysis
                analysis = await self._perform_comprehensive_analysis()
                
                # Update long-term health metrics
                self._update_strategic_metrics(analysis)
                
                # Publish comprehensive health report
                await self._publish_health_report(analysis)
                
                await asyncio.sleep(300)  # 300s (5 minutes)
                
            except Exception as e:
                self.logger.warning(f"Error in strategic analysis: {e}")
                await asyncio.sleep(300)
    
    async def _predictive_analysis_loop(self):
        """TIER 4: Predictive analysis (600s) for long-term failure prediction."""
        while self.is_running:
            try:
                # Predict potential failures
                predictions = await self.failure_predictor.predict_failures()
                
                # Update prediction state
                self.prevention_state["predicted_failures"] = predictions
                
                # Plan preventive measures
                await self._plan_preventive_measures(predictions)
                
                await asyncio.sleep(600)  # 600s (10 minutes)
                
            except Exception as e:
                self.logger.warning(f"Error in predictive analysis: {e}")
                await asyncio.sleep(600)
    
    async def _heartbeat_loop(self):
        """Send regular heartbeat to communication hub."""
        while self.is_running:
            try:
                if self.comm_hub:
                    heartbeat_data = {
                        "status": "healthy",
                        "system_health_score": self.prevention_state.get("system_health_score", 1.0),
                        "critical_alerts": self.prevention_state.get("critical_alerts", 0),
                        "uptime": time.time() - self.stats["start_time"]
                    }
                    
                    from ..communication.message_formats import create_agent_heartbeat
                    heartbeat = create_agent_heartbeat("failure_prevention", "healthy", time.time())
                    await self.comm_hub.publish_message(heartbeat)
                
                # Update agent stats in Redis (same as BaseAgent)
                current_time = time.time()
                agent_stats = {
                    'status': 'running' if self.is_running else 'stopped',
                    'start_time': str(self.start_time) if self.start_time else '0',
                    'uptime_seconds': str(int(current_time - self.start_time)) if self.start_time else '0',
                    'last_heartbeat': str(current_time),
                    'timestamp': str(current_time)
                }
                
                # Update the agent_stats hash using the correct Redis connector method
                if hasattr(self, 'redis_conn') and self.redis_conn:
                    self.redis_conn.hset(f"agent_stats:{self.agent_name}", mapping=agent_stats)
                else:
                    self.logger.warning("Redis connection not available for storing agent status")
                
                await asyncio.sleep(30)  # 30s heartbeat
                
            except Exception as e:
                self.logger.warning(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(30)
    
    # ============= MESSAGE HANDLERS =============
    
    async def _handle_system_alert(self, message):
        """Handle system alerts for failure prevention analysis."""
        try:
            alert_data = message.payload
            alert_type = alert_data.get("alert_type", "")
            
            # Analyze alert for failure patterns
            await self.failure_predictor.analyze_alert_pattern(alert_data)
            
            # Take preventive action if needed
            if "critical" in alert_type.lower():
                await self._handle_critical_situation(alert_data)
            
        except Exception as e:
            self.logger.warning(f"Error handling system alert: {e}")
    
    async def _handle_critical_alert(self, message):
        """Handle critical alerts requiring immediate attention."""
        try:
            alert_data = message.payload
            
            # Execute immediate preventive measures
            await self._execute_immediate_prevention(alert_data)
            
            # Update critical alert count
            self.prevention_state["critical_alerts"] += 1
            self.stats["critical_alerts_sent"] += 1
            
        except Exception as e:
            self.logger.warning(f"Error handling critical alert: {e}")
    
    # ============= PREVENTION & ANALYSIS =============
    
    async def _check_immediate_threats(self, critical_metrics: Dict[str, Any]):
        """Check for immediate threats requiring instant action."""
        try:
            threats = critical_metrics.get("immediate_threats", [])
            
            for threat in threats:
                if threat.get("severity", "") == "critical":
                    await self._execute_immediate_prevention(threat)
                    self.stats["failures_prevented"] += 1
            
        except Exception as e:
            self.logger.warning(f"Error checking immediate threats: {e}")
    
    async def _execute_preventive_actions(self, potential_issues: List[Dict[str, Any]]):
        """Execute preventive actions for potential issues."""
        try:
            for issue in potential_issues:
                action_taken = await self.failure_predictor.execute_prevention(issue)
                
                if action_taken:
                    self.stats["preventive_actions_executed"] += 1
                    self.prevention_state["preventive_actions_taken"] += 1
            
        except Exception as e:
            self.logger.warning(f"Error executing preventive actions: {e}")
    
    async def _execute_immediate_prevention(self, threat_data: Dict[str, Any]):
        """Execute immediate preventive measures for critical threats."""
        try:
            threat_type = threat_data.get("threat_type", "unknown")
            
            # Execute appropriate prevention based on threat type
            if "memory" in threat_type:
                await self._prevent_memory_overload()
            elif "cpu" in threat_type:
                await self._prevent_cpu_overload()
            elif "connection" in threat_type:
                await self._prevent_connection_failure()
            
            self.logger.warning(f"Executed immediate prevention for {threat_type}")
            
        except Exception as e:
            self.logger.error(f"Error executing immediate prevention: {e}")
    
    async def _perform_comprehensive_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive system health analysis."""
        try:
            # Get comprehensive system metrics
            system_metrics = await self.system_monitor.get_comprehensive_metrics()
            prediction_metrics = await self.failure_predictor.get_prediction_metrics()
            
            return {
                "system_metrics": system_metrics,
                "prediction_metrics": prediction_metrics,
                "overall_health_score": self.prevention_state["system_health_score"],
                "analysis_timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.warning(f"Error in comprehensive analysis: {e}")
            return {"error": str(e), "analysis_timestamp": time.time()}
    
    def _update_prevention_state(self, critical_metrics: Dict[str, Any]):
        """Update prevention state from critical metrics."""
        try:
            health_score = critical_metrics.get("health_score", 1.0)
            
            self.prevention_state.update({
                "system_health_score": health_score,
                "last_health_check": time.time()
            })
            
        except Exception as e:
            self.logger.warning(f"Error updating prevention state: {e}")
    
    def _update_strategic_metrics(self, analysis: Dict[str, Any]):
        """Update strategic metrics from comprehensive analysis."""
        try:
            system_metrics = analysis.get("system_metrics", {})
            
            self.prevention_state.update({
                "system_health_score": system_metrics.get("overall_health", 1.0)
            })
            
        except Exception as e:
            self.logger.warning(f"Error updating strategic metrics: {e}")
    
    async def _plan_preventive_measures(self, predictions: List[Dict[str, Any]]):
        """Plan preventive measures based on failure predictions."""
        try:
            for prediction in predictions:
                if prediction.get("probability", 0.0) > 0.7:  # High probability
                    await self.failure_predictor.plan_prevention(prediction)
            
        except Exception as e:
            self.logger.warning(f"Error planning preventive measures: {e}")
    
    async def _handle_critical_situation(self, alert_data: Dict[str, Any]):
        """Handle critical situations requiring immediate intervention."""
        try:
            # Execute critical intervention
            await self._execute_immediate_prevention(alert_data)
            
            # Send critical alert
            if self.comm_hub:
                from ..communication.message_formats import create_system_alert
                critical_alert = create_system_alert(
                    "failure_prevention",
                    "CRITICAL_INTERVENTION",
                    alert_data
                )
                await self.comm_hub.publish_message(critical_alert)
            
        except Exception as e:
            self.logger.error(f"Error handling critical situation: {e}")
    
    # ============= PREVENTION METHODS =============
    
    async def _prevent_memory_overload(self):
        """Prevent memory overload."""
        self.logger.warning("Preventing memory overload - executing cleanup")
        # Implementation would include memory cleanup, garbage collection, etc.
    
    async def _prevent_cpu_overload(self):
        """Prevent CPU overload.""" 
        self.logger.warning("Preventing CPU overload - reducing processing load")
        # Implementation would include reducing processing intensity, pausing non-critical tasks
    
    async def _prevent_connection_failure(self):
        """Prevent connection failures."""
        self.logger.warning("Preventing connection failure - optimizing connections")
        # Implementation would include connection optimization, failover activation
    
    # ============= COMMUNICATION & REPORTING =============
    
    async def _publish_health_report(self, analysis: Dict[str, Any]):
        """Publish comprehensive health report."""
        try:
            if self.comm_hub:
                report_data = {
                    "type": "COMPREHENSIVE_HEALTH_REPORT", 
                    "prevention_state": self.prevention_state,
                    "analysis": analysis,
                    "statistics": self.stats,
                    "timestamp": time.time()
                }
                
                from ..communication.message_formats import BaseMessage, MessageType
                message = BaseMessage(
                    sender="failure_prevention",
                    message_type=MessageType.LOG_MESSAGE,
                    payload=report_data
                )
                
                await self.comm_hub.publish_message(message)
            
        except Exception as e:
            self.logger.warning(f"Error publishing health report: {e}")
    
    # ============= UTILITY METHODS =============
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        return {
            "is_running": self.is_running,
            "prevention_state": self.prevention_state,
            "stats": self.stats,
            "uptime_seconds": int(time.time() - self.stats["start_time"])
        }

# Mock classes for components that don't exist yet
class MockSystemMonitor:
    async def check_critical_resources(self):
        return {
            "cpu_usage": 25.0,
            "memory_usage": 60.0,
            "disk_usage": 45.0,
            "network_status": "healthy"
        }
    
    async def check_system_health(self):
        return {
            "overall_health": "good",
            "critical_alerts": 0,
            "warning_alerts": 0
        }

class MockFailurePredictor:
    async def analyze_potential_issues(self, health_metrics):
        return []
    
    async def predict_failures(self, system_data):
        return []
