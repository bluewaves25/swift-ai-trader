from typing import Dict, Any, Optional
from ..interfaces.trade_model import TradeCommand
from ..logs.core_agent_logger import CoreAgentLogger
from ..controller.signal_filter import SignalFilter
from ..controller.flow_manager import FlowManager

class LogicExecutor:
    def __init__(self, signal_filter: SignalFilter, flow_manager: FlowManager):
        self.signal_filter = signal_filter
        self.flow_manager = flow_manager
        self.logger = CoreAgentLogger("logic_executor")

    def execute_logic_tree(self, signal: Dict[str, Any]) -> Optional[TradeCommand]:
        """Execute the logic tree for a trading signal."""
        self.logger.log_action("execute_logic_tree", {"signal": signal})

        # Step 1: Validate signal
        if not self.signal_filter.validate_signal(signal):
            self.logger.log_action("signal_rejected", {"reason": "Invalid signal format"})
            return None

        # Step 2: Check risk compliance
        risk_check = self.flow_manager.check_risk_compliance(signal)
        if not risk_check["passed"]:
            self.logger.log_action("signal_rejected", {"reason": f"Risk violation: {risk_check['reason']}"})
            return None

        # Step 3: Create trade command
        trade_command = TradeCommand(
            signal_id=signal.get("signal_id"),
            strategy=signal.get("strategy"),
            params=signal.get("params"),
            metadata={"timestamp": signal.get("timestamp")}
        )

        # Step 4: Route to execution pipeline
        result = self.flow_manager.route_to_execution(trade_command)
        if result:
            self.logger.log_action("command_routed", {"trade_command": trade_command.to_dict()})
            return trade_command
        else:
            self.logger.log_action("routing_failed", {"trade_command": trade_command.to_dict()})
            return None