#!/usr/bin/env python3
"""
Enhanced Failure Prevention Agent V2 - ROLE CONSOLIDATED: FAILURE PREVENTION ONLY
Removed health monitoring functionality - now handled by Core Agent.
Removed system monitoring functionality - now handled by Core Agent.
Focuses exclusively on failure prediction and preventive actions.
"""

import asyncio
import time
import json
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedFailurePreventionAgentV2(BaseAgent):
    """Enhanced failure prevention agent - focused solely on failure prevention."""
    
    def _initialize_agent_components(self):
        """Initialize failure prevention specific components."""
        # Initialize failure prevention components
        self.failure_predictor = None
        self.preventive_action_executor = None
        self.failure_pattern_analyzer = None
        
        # Failure prevention state
        self.prevention_state = {
            "critical_alerts": 0,
            "predicted_failures": [],
            "preventive_actions_taken": 0,
            "failures_prevented": 0,
            "active_preventive_measures": {},
            "failure_patterns": {}
        }
        
        # Failure prevention statistics
        self.stats = {
            "total_failure_checks": 0,
            "preventive_actions": 0,
            "critical_alerts": 0,
            "failures_prevented": 0,
            "false_positives": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Failure prevention specific startup logic."""
        try:
            # Initialize failure prevention components
            await self._initialize_prevention_components()
            
            # Initialize failure prediction systems
            await self._initialize_failure_prediction()
            
            self.logger.info("✅ Failure Prevention Agent: Failure prevention systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in failure prevention startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Failure prevention specific shutdown logic."""
        try:
            # Cleanup failure prevention resources
            await self._cleanup_prevention_components()
            
            self.logger.info("✅ Failure Prevention Agent: Failure prevention systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in failure prevention shutdown: {e}")
    
    # ============= BACKGROUND TASKS =============
    
    async def _prevention_measures_loop(self):
        """Prevention measures loop."""
        while self.is_running:
            try:
                # Implement prevention measures
                await self._implement_prevention_measures()
                
                await asyncio.sleep(5.0)  # 5 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in prevention measures loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _system_health_monitoring_loop(self):
        """System health monitoring loop."""
        while self.is_running:
            try:
                # Monitor system health
                await self._monitor_system_health()
                
                await asyncio.sleep(2.0)  # 2 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in system health monitoring loop: {e}")
                await asyncio.sleep(2.0)
    
    async def _failure_reporting_loop(self):
        """Failure reporting loop."""
        while self.is_running:
            try:
                # Report failures
                await self._report_failures()
                
                await asyncio.sleep(30.0)  # 30 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in failure reporting loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _implement_prevention_measures(self):
        """Implement prevention measures."""
        try:
            # Placeholder for prevention measures
            pass
        except Exception as e:
            self.logger.error(f"Error implementing prevention measures: {e}")
    
    async def _monitor_system_health(self):
        """Monitor system health."""
        try:
            # Placeholder for system health monitoring
            pass
        except Exception as e:
            self.logger.error(f"Error monitoring system health: {e}")
    
    async def _report_failures(self):
        """Report failures."""
        try:
            # Placeholder for failure reporting
            pass
        except Exception as e:
            self.logger.error(f"Error reporting failures: {e}")

    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._failure_prediction_loop, "Failure Prediction", "fast"),
            (self._prevention_measures_loop, "Prevention Measures", "tactical"),
            (self._system_health_monitoring_loop, "System Health Monitoring", "tactical"),
            (self._failure_reporting_loop, "Failure Reporting", "strategic")
        ]
    
    # ============= PREVENTION COMPONENT INITIALIZATION =============
    
    async def _initialize_prevention_components(self):
        """Initialize failure prevention components."""
        try:
            # Initialize failure predictor
            from .core.failure_predictor import FailurePredictor
            self.failure_predictor = FailurePredictor(self.config)
            
            # Initialize preventive action executor
            from .core.preventive_action_executor import PreventiveActionExecutor
            self.preventive_action_executor = PreventiveActionExecutor(self.config)
            
            # Initialize failure pattern analyzer
            from .core.failure_pattern_analyzer import FailurePatternAnalyzer
            self.failure_pattern_analyzer = FailurePatternAnalyzer(self.config)
            
            self.logger.info("✅ Failure prevention components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing prevention components: {e}")
            raise
    
    async def _initialize_failure_prediction(self):
        """Initialize failure prediction systems."""
        try:
            # Set up failure prediction models
            await self.failure_predictor.initialize_models()
            
            # Set up preventive action templates
            await self.preventive_action_executor.initialize_actions()
            
            # Set up pattern analysis
            await self.failure_pattern_analyzer.initialize_analysis()
            
            self.logger.info("✅ Failure prediction systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing failure prediction: {e}")
            raise
    
    # ============= FAILURE PREDICTION LOOP =============
    
    async def _failure_prediction_loop(self):
        """Main failure prediction loop (30s intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Analyze system for potential failures
                potential_failures = await self._analyze_potential_failures()
                
                # Update prediction state
                if potential_failures:
                    self.prevention_state["predicted_failures"] = potential_failures
                    await self._handle_predicted_failures(potential_failures)
                
                # Update statistics
                self.stats["total_failure_checks"] += 1
                
                # Record operation
                duration_ms = (time.time() - start_time) * 1000
                if hasattr(self, 'status_monitor') and self.status_monitor:
                    self.status_monitor.record_operation(duration_ms, len(potential_failures) > 0)
                
                await asyncio.sleep(30)  # 30s failure prediction cycle
                
            except Exception as e:
                self.logger.error(f"Error in failure prediction loop: {e}")
                await asyncio.sleep(30)
    
    async def _analyze_potential_failures(self) -> List[Dict[str, Any]]:
        """Analyze system for potential failures."""
        try:
            if not self.failure_predictor:
                return []
            
            # Get system metrics from Core Agent (no duplicate health monitoring - Core Agent handles all system health)
            system_metrics = await self._get_system_metrics_from_core()
            
            # Analyze for potential failures
            potential_failures = await self.failure_predictor.analyze_potential_issues(system_metrics)
            
            return potential_failures
            
        except Exception as e:
            self.logger.error(f"Error analyzing potential failures: {e}")
            return []
    
    async def _get_system_metrics_from_core(self) -> Dict[str, Any]:
        """Get system metrics from Core Agent (no duplicate health monitoring)."""
        try:
            # Get system health from Core Agent via Redis
            health_data = await self.redis_conn.get("system:health:latest")
            
            if health_data:
                return json.loads(health_data)
            else:
                # Fallback to basic metrics
                return {
                    "overall_health": 1.0,
                    "agent_status": {},
                    "system_timing": {},
                    "timestamp": time.time()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting system metrics from core: {e}")
            return {"overall_health": 1.0, "timestamp": time.time()}
    
    async def _handle_predicted_failures(self, potential_failures: List[Dict[str, Any]]):
        """Handle predicted failures."""
        try:
            for failure in potential_failures:
                failure_type = failure.get("type", "unknown")
                severity = failure.get("severity", "low")
                
                # Log the predicted failure
                self.logger.warning(f"Predicted failure: {failure_type} (severity: {severity})")
                
                # Trigger preventive actions if severity is high
                if severity in ["high", "critical"]:
                    await self._trigger_preventive_actions(failure)
                    
                    # Update statistics
                    self.stats["critical_alerts"] += 1
                
        except Exception as e:
            self.logger.error(f"Error handling predicted failures: {e}")
    
    # ============= PREVENTIVE ACTION LOOP =============
    
    async def _preventive_action_loop(self):
        """Preventive action execution loop (100ms intervals)."""
        while self.is_running:
            try:
                # Execute pending preventive actions
                actions_executed = await self._execute_pending_preventive_actions()
                
                # Update prevention state
                if actions_executed > 0:
                    self._update_prevention_state()
                
                await asyncio.sleep(0.1)  # 100ms preventive action cycle
                
            except Exception as e:
                self.logger.error(f"Error in preventive action loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _trigger_preventive_actions(self, failure: Dict[str, Any]):
        """Trigger preventive actions for a predicted failure."""
        try:
            if not self.preventive_action_executor:
                return
            
            # Get appropriate preventive actions for this failure type
            preventive_actions = await self.preventive_action_executor.get_actions_for_failure(failure)
            
            # Execute preventive actions
            for action in preventive_actions:
                action_id = await self._execute_preventive_action(action, failure)
                
                if action_id:
                    # Track active preventive measures
                    self.prevention_state["active_preventive_measures"][action_id] = {
                        "action": action,
                        "failure": failure,
                        "start_time": time.time(),
                        "status": "executing"
                    }
                    
                    # Update statistics
                    self.stats["preventive_actions"] += 1
            
        except Exception as e:
            self.logger.error(f"Error triggering preventive actions: {e}")
    
    async def _execute_preventive_action(self, action: Dict[str, Any], failure: Dict[str, Any]) -> str:
        """Execute a single preventive action."""
        try:
            action_id = f"prev_{int(time.time() * 1000)}_{len(self.prevention_state['active_preventive_measures'])}"
            
            # Execute the action
            success = await self.preventive_action_executor.execute_action(action, failure)
            
            if success:
                self.logger.info(f"Preventive action executed successfully: {action.get('name', 'unknown')}")
                return action_id
            else:
                self.logger.warning(f"Preventive action failed: {action.get('name', 'unknown')}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error executing preventive action: {e}")
            return ""
    
    async def _execute_pending_preventive_actions(self) -> int:
        """Execute pending preventive actions."""
        try:
            actions_executed = 0
            
            # Check for actions that need execution
            for action_id, action_data in list(self.prevention_state["active_preventive_measures"].items()):
                if action_data["status"] == "executing":
                    # Check if action is complete
                    if await self._check_action_completion(action_id, action_data):
                        actions_executed += 1
                        
                        # Update action status
                        action_data["status"] = "completed"
                        action_data["completion_time"] = time.time()
                        
                        # Check if failure was prevented
                        if await self._check_failure_prevention(action_data):
                            self.stats["failures_prevented"] += 1
                        else:
                            self.stats["false_positives"] += 1
            
            return actions_executed
            
        except Exception as e:
            self.logger.error(f"Error executing pending preventive actions: {e}")
            return 0
    
    async def _check_action_completion(self, action_id: str, action_data: Dict[str, Any]) -> bool:
        """Check if a preventive action is complete."""
        try:
            # Check action completion status
            if self.preventive_action_executor:
                return await self.preventive_action_executor.check_action_status(action_id)
            
            # Fallback: assume action completes after 5 seconds
            action_duration = time.time() - action_data["start_time"]
            return action_duration > 5.0
            
        except Exception as e:
            self.logger.error(f"Error checking action completion: {e}")
            return False
    
    async def _check_failure_prevention(self, action_data: Dict[str, Any]) -> bool:
        """Check if a failure was successfully prevented."""
        try:
            failure = action_data.get("failure", {})
            failure_type = failure.get("type", "unknown")
            
            # Check if the failure condition still exists
            current_metrics = await self._get_system_metrics_from_core()
            
            # Simple check: if overall health improved, assume prevention was successful
            current_health = current_metrics.get("overall_health", 1.0)
            return current_health > 0.8  # Threshold for considering prevention successful
            
        except Exception as e:
            self.logger.error(f"Error checking failure prevention: {e}")
            return False
    
    # ============= PATTERN ANALYSIS LOOP =============
    
    async def _pattern_analysis_loop(self):
        """Failure pattern analysis loop (5min intervals)."""
        while self.is_running:
            try:
                # Analyze failure patterns
                patterns = await self._analyze_failure_patterns()
                
                # Update pattern state
                if patterns:
                    self.prevention_state["failure_patterns"] = patterns
                    
                    # Publish pattern analysis
                    await self._publish_pattern_analysis(patterns)
                
                await asyncio.sleep(300)  # 5min pattern analysis cycle
                
            except Exception as e:
                self.logger.error(f"Error in pattern analysis loop: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_failure_patterns(self) -> Dict[str, Any]:
        """Analyze failure patterns for system improvement."""
        try:
            if not self.failure_pattern_analyzer:
                return {}
            
            # Get failure history
            failure_history = self.prevention_state.get("predicted_failures", [])
            
            # Analyze patterns
            patterns = await self.failure_pattern_analyzer.analyze_patterns(failure_history)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing failure patterns: {e}")
            return {}
    
    # ============= UTILITY METHODS =============
    
    def _update_prevention_state(self):
        """Update prevention state with current information."""
        try:
            # Update active preventive measures count
            active_measures = len([m for m in self.prevention_state["active_preventive_measures"].values() 
                                 if m["status"] == "executing"])
            
            # Clean up completed measures older than 1 hour
            current_time = time.time()
            for action_id, action_data in list(self.prevention_state["active_preventive_measures"].items()):
                if (action_data["status"] == "completed" and 
                    current_time - action_data.get("completion_time", 0) > 3600):
                    del self.prevention_state["active_preventive_measures"][action_id]
                    
        except Exception as e:
            self.logger.error(f"Error updating prevention state: {e}")
    
    async def _cleanup_prevention_components(self):
        """Cleanup failure prevention components."""
        try:
            # Cleanup failure predictor
            if self.failure_predictor:
                await self.failure_predictor.cleanup()
            
            # Cleanup preventive action executor
            if self.preventive_action_executor:
                await self.preventive_action_executor.cleanup()
            
            # Cleanup pattern analyzer
            if self.failure_pattern_analyzer:
                await self.failure_pattern_analyzer.cleanup()
            
            self.logger.info("✅ Failure prevention components cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up prevention components: {e}")
    
    # ============= PUBLISHING METHODS =============
    
    async def _publish_pattern_analysis(self, patterns: Dict[str, Any]):
        """Publish failure pattern analysis."""
        try:
            pattern_report = {
                "patterns": patterns,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("failure_prevention:pattern_analysis", json.dumps(pattern_report))
            
        except Exception as e:
            self.logger.error(f"Error publishing pattern analysis: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_prevention_status(self) -> Dict[str, Any]:
        """Get current failure prevention status."""
        return {
            "prevention_state": self.prevention_state,
            "stats": self.stats,
            "active_measures": len(self.prevention_state["active_preventive_measures"]),
            "last_update": time.time()
        }
    
    async def get_predicted_failures(self) -> List[Dict[str, Any]]:
        """Get currently predicted failures."""
        return self.prevention_state.get("predicted_failures", [])
    
    async def get_preventive_actions(self) -> Dict[str, Any]:
        """Get active preventive actions."""
        return self.prevention_state.get("active_preventive_measures", {})
    
    async def trigger_manual_prevention(self, failure_type: str, severity: str = "medium") -> bool:
        """Manually trigger prevention for a specific failure type."""
        try:
            # Create manual failure prediction
            manual_failure = {
                "type": failure_type,
                "severity": severity,
                "source": "manual",
                "timestamp": time.time()
            }
            
            # Handle the manual failure
            await self._handle_predicted_failures([manual_failure])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error triggering manual prevention: {e}")
            return False
