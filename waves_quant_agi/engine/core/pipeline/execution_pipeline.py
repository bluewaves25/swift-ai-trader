from typing import Dict, Any, Optional
from ..interfaces.trade_model import TradeCommand
from ..interfaces.agent_io import AgentIO
from ..logs.core_agent_logger import CoreAgentLogger

class ExecutionPipeline:
    def __init__(self, agent_io: AgentIO):
        self.agent_io = agent_io
        self.logger = CoreAgentLogger("execution_pipeline")

    def build_command_package(self, trade_command: TradeCommand) -> Optional[Dict[str, Any]]:
        """Build command package for execution agent."""
        try:
            if not trade_command.validate():
                self.logger.log_action("build_package", {"result": "failed", "reason": "Invalid trade command"})
                return None
            package = {
                "command": trade_command.to_dict(),
                "timestamp": trade_command.metadata.get("timestamp"),
                "priority": 1.0  # Placeholder for dynamic priority
            }
            self.logger.log_action("build_package", {"result": "success", "package": package})
            return package
        except Exception as e:
            self.logger.log_action("build_package", {"result": "failed", "reason": str(e)})
            return None

    def send_to_execution(self, trade_command: TradeCommand) -> bool:
        """Send command package to execution agent."""
        package = self.build_command_package(trade_command)
        if not package:
            return False
        try:
            success = self.agent_io.send_to_execution(package)
            self.logger.log_action("send_to_execution", {"package": package, "result": "success" if success else "failed"})
            return success
        except Exception as e:
            self.logger.log_action("send_to_execution", {"package": package, "result": "failed", "reason": str(e)})
            return False