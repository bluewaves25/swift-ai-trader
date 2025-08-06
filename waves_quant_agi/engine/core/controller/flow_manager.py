from typing import Dict, Any, Optional
from ..interfaces.trade_model import TradeCommand
from ..interfaces.agent_io import AgentIO
from ..logs.core_agent_logger import CoreAgentLogger

class FlowManager:
    def __init__(self, agent_io: AgentIO):
        self.agent_io = agent_io
        self.logger = CoreAgentLogger("flow_manager")
        self.risk_params = {"max_exposure": 100000.0, "max_loss_pct": 0.02}

    def check_risk_compliance(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Check if signal complies with risk parameters."""
        try:
            exposure = signal.get("params", {}).get("amount", 0.0) * signal.get("params", {}).get("price", 1.0)
            if exposure > self.risk_params["max_exposure"]:
                self.logger.log_action("risk_check", {"result": "failed", "reason": "Exposure limit exceeded"})
                return {"passed": False, "reason": "Exposure limit exceeded"}
            self.logger.log_action("risk_check", {"result": "passed"})
            return {"passed": True}
        except Exception as e:
            self.logger.log_action("risk_check", {"result": "failed", "reason": str(e)})
            return {"passed": False, "reason": str(e)}

    def route_to_execution(self, trade_command: TradeCommand) -> bool:
        """Route trade command to execution agent."""
        try:
            self.agent_io.send_to_execution(trade_command.to_dict())
            self.logger.log_action("route_execution", {"trade_command": trade_command.to_dict()})
            return True
        except Exception as e:
            self.logger.log_action("route_execution", {"trade_command": trade_command.to_dict(), "error": str(e)})
            return False

    def coordinate_agents(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Coordinate signal processing across agents."""
        self.logger.log_action("coordinate_agents", {"signal": signal})
        strategy_response = self.agent_io.send_to_strategy(signal)
        if not strategy_response or not strategy_response.get("approved"):
            self.logger.log_action("strategy_rejected", {"reason": strategy_response.get("reason", "Unknown")})
            return None
        return strategy_response