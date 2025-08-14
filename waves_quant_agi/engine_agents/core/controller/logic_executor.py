from typing import Dict, Any, Optional
from ..logs.core_agent_logger import CoreAgentLogger
from ..controller.signal_filter import SystemSignalFilter
from ..controller.flow_manager import SystemCoordinationFlowManager

class SystemCoordinationLogicExecutor:
    """System coordination logic executor - focused ONLY on system coordination."""
    
    def __init__(self, signal_filter: SystemSignalFilter, flow_manager: SystemCoordinationFlowManager):
        self.signal_filter = signal_filter
        self.flow_manager = flow_manager
        self.logger = CoreAgentLogger("system_coordination_logic")

    def execute_system_coordination_logic(self, coordination_signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute the logic tree for a system coordination signal."""
        self.logger.log_action("execute_system_coordination_logic", {"signal": coordination_signal})

        # Step 1: Validate system coordination signal
        if not self.signal_filter.validate_system_signal(coordination_signal):
            self.logger.log_action("coordination_signal_rejected", {"reason": "Invalid system signal format"})
            return None

        # Step 2: Route to appropriate coordination flow
        signal_type = coordination_signal.get("signal_type")
        
        if signal_type == "health_check":
            return self._execute_health_coordination_logic(coordination_signal)
        elif signal_type == "timing_sync":
            return self._execute_timing_coordination_logic(coordination_signal)
        elif signal_type == "agent_status":
            return self._execute_status_coordination_logic(coordination_signal)
        else:
            self.logger.log_action("coordination_signal_rejected", {"reason": f"Unknown signal type: {signal_type}"})
            return None

    def _execute_health_coordination_logic(self, coordination_signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute health coordination logic."""
        try:
            # Create health coordination request
            health_request = {
                "agent_name": coordination_signal.get("source_agent"),
                "health_type": coordination_signal.get("health_type", "general"),
                "timestamp": coordination_signal.get("timestamp")
            }
            
            # Execute health coordination
            result = self.flow_manager.coordinate_system_health(health_request)
            
            if result and result.get("success"):
                self.logger.log_action("health_coordination_completed", {"result": result})
                return result
            else:
                self.logger.log_action("health_coordination_failed", {"result": result})
                return None
                
        except Exception as e:
            self.logger.log_action("health_coordination_error", {"error": str(e)})
            return None

    def _execute_timing_coordination_logic(self, coordination_signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute timing coordination logic."""
        try:
            # Create timing coordination request
            timing_request = {
                "agent_name": coordination_signal.get("source_agent"),
                "timing_type": coordination_signal.get("timing_type", "sync"),
                "timestamp": coordination_signal.get("timestamp")
            }
            
            # Execute timing coordination
            result = self.flow_manager.coordinate_timing_sync(timing_request)
            
            if result and result.get("success"):
                self.logger.log_action("timing_coordination_completed", {"result": result})
                return result
            else:
                self.logger.log_action("timing_coordination_failed", {"result": result})
                return None
                
        except Exception as e:
            self.logger.log_action("timing_coordination_error", {"error": str(e)})
            return None

    def _execute_status_coordination_logic(self, coordination_signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute status coordination logic."""
        try:
            # Create status coordination request
            status_request = {
                "agent_name": coordination_signal.get("source_agent"),
                "status_type": coordination_signal.get("status_type", "update"),
                "timestamp": coordination_signal.get("timestamp")
            }
            
            # Execute status coordination
            result = self.flow_manager.coordinate_agent_status(status_request)
            
            if result and result.get("success"):
                self.logger.log_action("status_coordination_completed", {"result": result})
                return result
            else:
                self.logger.log_action("status_coordination_failed", {"result": result})
                return None
                
        except Exception as e:
            self.logger.log_action("status_coordination_error", {"error": str(e)})
            return None

    def get_coordination_status(self) -> Dict[str, Any]:
        """Get system coordination status."""
        try:
            return {
                "signal_filter_status": "active",
                "flow_manager_status": "active",
                "coordination_stats": self.flow_manager.get_coordination_stats(),
                "active_coordinations": self.flow_manager.get_active_coordinations()
            }
        except Exception as e:
            self.logger.log_action("get_coordination_status_error", {"error": str(e)})
            return {"error": str(e)}