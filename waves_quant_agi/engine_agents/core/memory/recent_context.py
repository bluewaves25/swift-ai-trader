from typing import Dict, Any, List
from collections import deque
from ..logs.core_agent_logger import CoreAgentLogger
import time

class SystemCoordinationContext:
    """System coordination context - focused ONLY on system coordination."""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.health_checks = deque(maxlen=max_history)
        self.timing_syncs = deque(maxlen=max_history)
        self.agent_status_updates = deque(maxlen=max_history)
        self.coordination_events = deque(maxlen=max_history)
        self.logger = CoreAgentLogger("system_coordination_context")

    def store_health_check(self, health_check: Dict[str, Any]):
        """Store a health check event."""
        self.health_checks.append(health_check)
        self.logger.log_action("store_health_check", {
            "agent_name": health_check.get("agent_name"),
            "health_status": health_check.get("health_status")
        })

    def store_timing_sync(self, timing_sync: Dict[str, Any]):
        """Store a timing synchronization event."""
        self.timing_syncs.append(timing_sync)
        self.logger.log_action("store_timing_sync", {
            "agent_name": timing_sync.get("agent_name"),
            "sync_status": timing_sync.get("sync_status")
        })

    def store_agent_status_update(self, status_update: Dict[str, Any]):
        """Store an agent status update event."""
        self.agent_status_updates.append(status_update)
        self.logger.log_action("store_agent_status_update", {
            "agent_name": status_update.get("agent_name"),
            "status": status_update.get("status")
        })

    def store_coordination_event(self, coordination_event: Dict[str, Any]):
        """Store a system coordination event."""
        self.coordination_events.append(coordination_event)
        self.logger.log_action("store_coordination_event", {
            "event_type": coordination_event.get("event_type"),
            "event_id": coordination_event.get("event_id")
        })

    def get_recent_health_checks(self) -> List[Dict[str, Any]]:
        """Get recent health check events."""
        return list(self.health_checks)

    def get_recent_timing_syncs(self) -> List[Dict[str, Any]]:
        """Get recent timing synchronization events."""
        return list(self.timing_syncs)

    def get_recent_agent_status_updates(self) -> List[Dict[str, Any]]:
        """Get recent agent status update events."""
        return list(self.agent_status_updates)

    def get_recent_coordination_events(self) -> List[Dict[str, Any]]:
        """Get recent system coordination events."""
        return list(self.coordination_events)

    def get_agent_health_summary(self, agent_name: str) -> Dict[str, Any]:
        """Get health summary for a specific agent."""
        try:
            agent_health_checks = [
                hc for hc in self.health_checks 
                if hc.get("agent_name") == agent_name
            ]
            
            if not agent_health_checks:
                return {"agent_name": agent_name, "health_status": "unknown", "last_check": None}
            
            latest_check = max(agent_health_checks, key=lambda x: x.get("timestamp", 0))
            
            return {
                "agent_name": agent_name,
                "health_status": latest_check.get("health_status", "unknown"),
                "last_check": latest_check.get("timestamp"),
                "total_checks": len(agent_health_checks)
            }
            
        except Exception as e:
            self.logger.log_action("get_agent_health_summary_error", {"error": str(e)})
            return {"agent_name": agent_name, "error": str(e)}

    def get_system_coordination_summary(self) -> Dict[str, Any]:
        """Get system coordination summary."""
        try:
            return {
                "total_health_checks": len(self.health_checks),
                "total_timing_syncs": len(self.timing_syncs),
                "total_agent_status_updates": len(self.agent_status_updates),
                "total_coordination_events": len(self.coordination_events),
                "context_size": self.max_history,
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.log_action("get_system_coordination_summary_error", {"error": str(e)})
            return {"error": str(e)}

    def clear_context(self):
        """Clear all stored system coordination context."""
        self.health_checks.clear()
        self.timing_syncs.clear()
        self.agent_status_updates.clear()
        self.coordination_events.clear()
        self.logger.log_action("clear_system_coordination_context", {})