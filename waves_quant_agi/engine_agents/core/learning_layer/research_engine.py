from typing import Dict, Any, List
from ..memory.recent_context import SystemCoordinationContext
from ..logs.core_agent_logger import CoreAgentLogger
import time

class SystemCoordinationResearchEngine:
    """System coordination research engine - focused ONLY on system coordination research."""
    
    def __init__(self, context: SystemCoordinationContext):
        self.context = context
        self.logger = CoreAgentLogger("system_coordination_research")

    def analyze_coordination_behavior(self) -> Dict[str, Any]:
        """Analyze system coordination behavior based on recent context."""
        try:
            health_checks = self.context.get_recent_health_checks()
            timing_syncs = self.context.get_recent_timing_syncs()
            agent_status_updates = self.context.get_recent_agent_status_updates()
            coordination_events = self.context.get_recent_coordination_events()
            
            # Analyze health check patterns
            health_analysis = self._analyze_health_patterns(health_checks)
            
            # Analyze timing synchronization patterns
            timing_analysis = self._analyze_timing_patterns(timing_syncs)
            
            # Analyze agent status patterns
            status_analysis = self._analyze_status_patterns(agent_status_updates)
            
            # Analyze coordination event patterns
            event_analysis = self._analyze_event_patterns(coordination_events)
            
            analysis = {
                "health_patterns": health_analysis,
                "timing_patterns": timing_analysis,
                "status_patterns": status_analysis,
                "event_patterns": event_analysis,
                "total_health_checks": len(health_checks),
                "total_timing_syncs": len(timing_syncs),
                "total_agent_status_updates": len(agent_status_updates),
                "total_coordination_events": len(coordination_events)
            }
            
            self.logger.log_action("analyze_coordination_behavior", analysis)
            return analysis
            
        except Exception as e:
            self.logger.log_action("analyze_coordination_behavior_error", {"error": str(e)})
            return {"error": str(e)}

    def collect_system_metrics(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and process system metrics for coordination research."""
        try:
            processed_metrics = {
                "system_health": external_data.get("system_health", {}),
                "agent_performance": external_data.get("agent_performance", {}),
                "coordination_latency": external_data.get("coordination_latency", {}),
                "timestamp": external_data.get("timestamp"),
                "source": "system_coordination_research"
            }
            
            self.logger.log_action("collect_system_metrics", {"metrics": processed_metrics})
            return processed_metrics
            
        except Exception as e:
            self.logger.log_action("collect_system_metrics_error", {"error": str(e)})
            return {"error": str(e)}
    
    # ============= PRIVATE ANALYSIS METHODS =============
    
    def _analyze_health_patterns(self, health_checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze health check patterns."""
        try:
            if not health_checks:
                return {"status": "no_data"}
            
            # Count health statuses
            status_counts = {}
            agent_health = {}
            
            for check in health_checks:
                status = check.get("health_status", "unknown")
                agent = check.get("agent_name", "unknown")
                
                status_counts[status] = status_counts.get(status, 0) + 1
                
                if agent not in agent_health:
                    agent_health[agent] = []
                agent_health[agent].append(check)
            
            return {
                "status_distribution": status_counts,
                "agent_health_summary": {
                    agent: len(checks) for agent, checks in agent_health.items()
                },
                "total_checks": len(health_checks)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_timing_patterns(self, timing_syncs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze timing synchronization patterns."""
        try:
            if not timing_syncs:
                return {"status": "no_data"}
            
            # Count sync statuses
            sync_status_counts = {}
            agent_timing = {}
            
            for sync in timing_syncs:
                status = sync.get("sync_status", "unknown")
                agent = sync.get("agent_name", "unknown")
                
                sync_status_counts[status] = sync_status_counts.get(status, 0) + 1
                
                if agent not in agent_timing:
                    agent_timing[agent] = []
                agent_timing[agent].append(sync)
            
            return {
                "sync_status_distribution": sync_status_counts,
                "agent_timing_summary": {
                    agent: len(syncs) for agent, syncs in agent_timing.items()
                },
                "total_syncs": len(timing_syncs)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_status_patterns(self, status_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze agent status update patterns."""
        try:
            if not status_updates:
                return {"status": "no_data"}
            
            # Count status types
            status_type_counts = {}
            agent_status_summary = {}
            
            for update in status_updates:
                status_type = update.get("status", "unknown")
                agent = update.get("agent_name", "unknown")
                
                status_type_counts[status_type] = status_type_counts.get(status_type, 0) + 1
                
                if agent not in agent_status_summary:
                    agent_status_summary[agent] = []
                agent_status_summary[agent].append(update)
            
            return {
                "status_type_distribution": status_type_counts,
                "agent_status_summary": {
                    agent: len(updates) for agent, updates in agent_status_summary.items()
                },
                "total_updates": len(status_updates)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_event_patterns(self, coordination_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze coordination event patterns."""
        try:
            if not coordination_events:
                return {"status": "no_data"}
            
            # Count event types
            event_type_counts = {}
            
            for event in coordination_events:
                event_type = event.get("event_type", "unknown")
                event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
            
            return {
                "event_type_distribution": event_type_counts,
                "total_events": len(coordination_events)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    # ============= PUBLIC INTERFACE METHODS =============
    
    def get_research_summary(self) -> Dict[str, Any]:
        """Get system coordination research summary."""
        try:
            return {
                "research_engine_type": "system_coordination",
                "capabilities": [
                    "coordination_behavior_analysis",
                    "system_metrics_collection",
                    "pattern_analysis"
                ],
                "status": "active",
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": str(e)}