from typing import Dict, Any, Optional, List
from ...logs.strategy_engine_logger import StrategyEngineLogger
from ..interfaces.trade_model import TradeCommand
import time

class TradingExecutionPipeline:
    """Trading execution pipeline - consolidated from Core Agent."""
    
    def __init__(self, agent_io=None):
        self.agent_io = agent_io
        self.logger = StrategyEngineLogger("trading_execution_pipeline")
        
    async def initialize(self):
        """Initialize the trading execution pipeline."""
        try:
            self.logger.log_action("initialize", {"status": "started"})
            return True
        except Exception as e:
            self.logger.log_action("initialize_error", {"error": str(e)})
            return False
            
    async def cleanup(self):
        """Clean up the trading execution pipeline."""
        try:
            self.logger.log_action("cleanup", {"status": "started"})
            # Reset state
            self.agent_io = None
            self.logger.log_action("cleanup", {"status": "completed"})
            return True
        except Exception as e:
            self.logger.log_action("cleanup_error", {"error": str(e)})
            return False

    def build_command_package(self, trade_command: TradeCommand) -> Optional[Dict[str, Any]]:
        """Build command package for execution agent."""
        try:
            if not trade_command.validate():
                self.logger.log_action("build_command_package", {
                    "result": "failed", 
                    "reason": "Invalid trade command"
                })
                return None
                
            package = {
                "command": trade_command.to_dict(),
                "timestamp": trade_command.timestamp,
                "priority": trade_command.get_execution_priority(),
                "source": "strategy_engine",
                "execution_metadata": {
                    "risk_score": trade_command.risk_score,
                    "exposure": trade_command.get_exposure(),
                    "risk_adjusted_amount": trade_command.get_risk_adjusted_amount()
                }
            }
            
            self.logger.log_action("build_command_package", {
                "result": "success", 
                "package": package
            })
            return package
            
        except Exception as e:
            self.logger.log_action("build_command_package", {
                "result": "failed", 
                "reason": str(e)
            })
            return None

    async def send_to_execution(self, trade_command: TradeCommand) -> bool:
        """Send command package to execution agent."""
        try:
            package = self.build_command_package(trade_command)
            if not package:
                return False
            
            if self.agent_io:
                success = await self.agent_io.send_to_execution(package)
                self.logger.log_action("send_to_execution", {
                    "package": package, 
                    "result": "success" if success else "failed"
                })
                return success
            else:
                # Fallback: log the command without sending
                self.logger.log_action("send_to_execution", {
                    "package": package, 
                    "result": "skipped",
                    "reason": "No agent IO available"
                })
                return True
                
        except Exception as e:
            self.logger.log_action("send_to_execution", {
                "package": package if 'package' in locals() else None, 
                "result": "failed", 
                "reason": str(e)
            })
            return False

    def validate_execution_package(self, package: Dict[str, Any]) -> bool:
        """Validate execution package before sending."""
        try:
            required_fields = ["command", "timestamp", "priority", "source"]
            
            # Check required fields
            if not all(field in package for field in required_fields):
                self.logger.log_action("validate_execution_package", {
                    "result": "failed",
                    "reason": "Missing required fields"
                })
                return False
            
            # Validate command structure
            command = package.get("command", {})
            if not isinstance(command, dict):
                self.logger.log_action("validate_execution_package", {
                    "result": "failed",
                    "reason": "Invalid command structure"
                })
                return False
            
            # Validate priority
            priority = package.get("priority", 0)
            if not isinstance(priority, int) or priority < 0 or priority > 100:
                self.logger.log_action("validate_execution_package", {
                    "result": "failed",
                    "reason": f"Invalid priority: {priority}"
                })
                return False
            
            # Validate timestamp
            timestamp = package.get("timestamp", 0)
            if not isinstance(timestamp, (int, float)) or timestamp <= 0:
                self.logger.log_action("validate_execution_package", {
                    "result": "failed",
                    "reason": f"Invalid timestamp: {timestamp}"
                })
                return False
            
            self.logger.log_action("validate_execution_package", {"result": "passed"})
            return True
            
        except Exception as e:
            self.logger.log_action("validate_execution_package", {
                "result": "failed",
                "reason": str(e)
            })
            return False

    def create_execution_batch(self, trade_commands: List[TradeCommand]) -> List[Dict[str, Any]]:
        """Create execution batch from multiple trade commands."""
        try:
            execution_batch = []
            
            for command in trade_commands:
                package = self.build_command_package(command)
                if package and self.validate_execution_package(package):
                    execution_batch.append(package)
                else:
                    self.logger.log_action("create_execution_batch", {
                        "result": "skipped",
                        "command_id": command.command_id,
                        "reason": "Invalid command package"
                    })
            
            self.logger.log_action("create_execution_batch", {
                "result": "success",
                "total_commands": len(trade_commands),
                "valid_packages": len(execution_batch)
            })
            
            return execution_batch
            
        except Exception as e:
            self.logger.log_action("create_execution_batch", {
                "result": "failed",
                "error": str(e)
            })
            return []

    async def send_execution_batch(self, execution_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send execution batch to execution agent."""
        try:
            results = {
                "total_packages": len(execution_batch),
                "successful_sends": 0,
                "failed_sends": 0,
                "skipped_packages": 0,
                "errors": []
            }
            
            for package in execution_batch:
                try:
                    if self.agent_io:
                        success = await self.agent_io.send_to_execution(package)
                        if success:
                            results["successful_sends"] += 1
                        else:
                            results["failed_sends"] += 1
                    else:
                        results["skipped_packages"] += 1
                        
                except Exception as e:
                    results["failed_sends"] += 1
                    results["errors"].append({
                        "package": package.get("command", {}).get("command_id", "unknown"),
                        "error": str(e)
                    })
            
            self.logger.log_action("send_execution_batch", {
                "result": "completed",
                "results": results
            })
            
            return results
            
        except Exception as e:
            self.logger.log_action("send_execution_batch", {
                "result": "failed",
                "error": str(e)
            })
            return {"error": str(e)}

    def get_execution_priority_queue(self, trade_commands: List[TradeCommand]) -> List[TradeCommand]:
        """Get trade commands sorted by execution priority."""
        try:
            # Sort by priority (highest first) and then by timestamp (oldest first)
            sorted_commands = sorted(
                trade_commands,
                key=lambda cmd: (cmd.get_execution_priority(), cmd.timestamp),
                reverse=True
            )
            
            self.logger.log_action("get_execution_priority_queue", {
                "result": "success",
                "total_commands": len(sorted_commands),
                "highest_priority": sorted_commands[0].get_execution_priority() if sorted_commands else 0
            })
            
            return sorted_commands
            
        except Exception as e:
            self.logger.log_action("get_execution_priority_queue", {
                "result": "failed",
                "error": str(e)
            })
            return trade_commands  # Return original order on error

    def filter_high_priority_commands(self, trade_commands: List[TradeCommand], 
                                    priority_threshold: int = 70) -> List[TradeCommand]:
        """Filter trade commands by priority threshold."""
        try:
            high_priority_commands = [
                cmd for cmd in trade_commands 
                if cmd.get_execution_priority() >= priority_threshold
            ]
            
            self.logger.log_action("filter_high_priority_commands", {
                "result": "success",
                "total_commands": len(trade_commands),
                "high_priority_count": len(high_priority_commands),
                "priority_threshold": priority_threshold
            })
            
            return high_priority_commands
            
        except Exception as e:
            self.logger.log_action("filter_high_priority_commands", {
                "result": "failed",
                "error": str(e)
            })
            return []

    # ============= PUBLIC INTERFACE METHODS =============
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get trading execution pipeline status."""
        try:
            return {
                "pipeline_type": "trading_execution",
                "status": "active",
                "capabilities": [
                    "command_package_building",
                    "execution_sending",
                    "batch_processing",
                    "priority_queuing"
                ],
                "agent_io_connected": self.agent_io is not None,
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.log_action("get_pipeline_status", {
                "result": "failed",
                "reason": str(e)
            })
            return {"error": str(e)}
    
    def set_agent_io(self, agent_io):
        """Set the agent IO interface."""
        try:
            self.agent_io = agent_io
            self.logger.log_action("set_agent_io", {
                "result": "success",
                "agent_io_type": type(agent_io).__name__
            })
        except Exception as e:
            self.logger.log_action("set_agent_io", {
                "result": "failed",
                "error": str(e)
            })
