import time
import asyncio
from typing import Dict, Any, Optional, List
from ..interfaces.trade_model import TradeCommand
from ..interfaces.agent_io import AgentIO
from ..logs.core_agent_logger import CoreAgentLogger

class FlowManager:
    """
    Enhanced flow manager for coordinating agent interactions and managing trading flow.
    Provides comprehensive flow control, risk management, and performance tracking.
    """
    
    def __init__(self, agent_io: AgentIO, config: Dict[str, Any] = None):
        self.agent_io = agent_io
        self.config = config or {}
        self.logger = CoreAgentLogger("flow_manager")
        
        # Flow configuration
        self.flow_config = self.config.get('flow_manager', {})
        self.risk_params = self.flow_config.get('risk_params', {
            "max_exposure": 100000.0, 
            "max_loss_pct": 0.02,
            "max_position_size": 0.1,
            "max_daily_trades": 100
        })
        
        # Flow tracking
        self.flow_stats = {
            'total_flows': 0,
            'successful_flows': 0,
            'failed_flows': 0,
            'risk_rejections': 0,
            'strategy_rejections': 0,
            'execution_failures': 0,
            'avg_flow_duration': 0.0
        }
        
        # Active flows
        self.active_flows = {}
        
    async def process_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Process a signal through the complete flow"""
        try:
            flow_id = signal.get('signal_id', f"flow_{int(time.time())}")
            start_time = time.time()
            
            self.logger.log_flow_management(
                flow_id=flow_id,
                flow_type="signal_processing",
                stage="start",
                status="initiated"
            )
            
            # Step 1: Risk compliance check
            risk_result = await self._check_risk_compliance(signal)
            if not risk_result['passed']:
                self.flow_stats['risk_rejections'] += 1
                self.flow_stats['failed_flows'] += 1
                
                self.logger.log_flow_management(
                    flow_id=flow_id,
                    flow_type="signal_processing",
                    stage="risk_check",
                    status="rejected",
                    metadata={'reason': risk_result['reason']}
                )
                return {"success": False, "reason": risk_result['reason']}
            
            # Step 2: Strategy approval
            strategy_result = await self._get_strategy_approval(signal)
            if not strategy_result['approved']:
                self.flow_stats['strategy_rejections'] += 1
                self.flow_stats['failed_flows'] += 1
                
                self.logger.log_flow_management(
                    flow_id=flow_id,
                    flow_type="signal_processing",
                    stage="strategy_approval",
                    status="rejected",
                    metadata={'reason': strategy_result.get('reason', 'Unknown')}
                )
                return {"success": False, "reason": strategy_result.get('reason', 'Strategy rejected')}
            
            # Step 3: Create trade command
            trade_command = await self._create_trade_command(signal, strategy_result)
            if not trade_command:
                self.flow_stats['failed_flows'] += 1
                
                self.logger.log_flow_management(
                    flow_id=flow_id,
                    flow_type="signal_processing",
                    stage="command_creation",
                    status="failed",
                    metadata={'reason': 'Failed to create trade command'}
                )
                return {"success": False, "reason": "Failed to create trade command"}
            
            # Step 4: Route to execution
            execution_result = await self._route_to_execution(trade_command)
            if not execution_result:
                self.flow_stats['execution_failures'] += 1
                self.flow_stats['failed_flows'] += 1
                
                self.logger.log_flow_management(
                    flow_id=flow_id,
                    flow_type="signal_processing",
                    stage="execution",
                    status="failed",
                    metadata={'reason': 'Execution failed'}
                )
                return {"success": False, "reason": "Execution failed"}
            
            # Success
            duration = time.time() - start_time
            self.flow_stats['successful_flows'] += 1
            self.flow_stats['total_flows'] += 1
            
            # Update average duration
            self._update_avg_duration(duration)
            
            self.logger.log_flow_management(
                flow_id=flow_id,
                flow_type="signal_processing",
                stage="completed",
                status="success",
                duration=duration
            )
            
            return {"success": True, "trade_command": trade_command.to_dict()}
            
        except Exception as e:
            self.flow_stats['failed_flows'] += 1
            self.logger.log_error("Flow processing failed", str(e), "FlowManager")
            return {"success": False, "reason": f"Flow error: {str(e)}"}
    
    async def _check_risk_compliance(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Check if signal complies with risk parameters"""
        try:
            # Calculate exposure
            amount = signal.get("params", {}).get("amount", 0.0)
            price = signal.get("params", {}).get("price", 1.0)
            exposure = amount * price
            
            # Check exposure limit
            if exposure > self.risk_params["max_exposure"]:
                return {
                    "passed": False, 
                    "reason": f"Exposure {exposure:.2f} exceeds limit {self.risk_params['max_exposure']}"
                }
            
            # Check position size
            if amount > self.risk_params["max_position_size"]:
                return {
                    "passed": False,
                    "reason": f"Position size {amount:.2f} exceeds limit {self.risk_params['max_position_size']}"
                }
            
            # Check daily trade limit
            daily_trades = self.flow_stats['total_flows']
            if daily_trades >= self.risk_params["max_daily_trades"]:
                return {
                    "passed": False,
                    "reason": f"Daily trade limit {self.risk_params['max_daily_trades']} reached"
                }
            
            self.logger.log_flow_management(
                flow_id=signal.get('signal_id', 'unknown'),
                flow_type="risk_check",
                stage="compliance",
                status="passed",
                metadata={'exposure': exposure, 'amount': amount}
            )
            
            return {"passed": True}
            
        except Exception as e:
            self.logger.log_error("Risk compliance check failed", str(e), "FlowManager")
            return {"passed": False, "reason": f"Risk check error: {str(e)}"}
    
    async def _get_strategy_approval(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Get strategy approval for the signal"""
        try:
            strategy_response = await self.agent_io.send_to_strategy(signal)
            
            if strategy_response and strategy_response.get("approved"):
                self.logger.log_flow_management(
                    flow_id=signal.get('signal_id', 'unknown'),
                    flow_type="strategy_approval",
                    stage="approval",
                    status="approved",
                    metadata=strategy_response
                )
                return strategy_response
            else:
                reason = strategy_response.get("reason", "Strategy rejected") if strategy_response else "No response from strategy"
                return {"approved": False, "reason": reason}
                
        except Exception as e:
            self.logger.log_error("Strategy approval failed", str(e), "FlowManager")
            return {"approved": False, "reason": f"Strategy error: {str(e)}"}
    
    async def _create_trade_command(self, signal: Dict[str, Any], strategy_result: Dict[str, Any]) -> Optional[TradeCommand]:
        """Create trade command from signal and strategy result"""
        try:
            # Extract signal parameters
            symbol = signal.get("symbol", "")
            action = signal.get("action", "")
            amount = signal.get("params", {}).get("amount", 0.0)
            price = signal.get("params", {}).get("price", 0.0)
            
            # Create trade command
            command = TradeCommand(
                symbol=symbol,
                action=action,
                amount=amount,
                price=price,
                signal_id=signal.get("signal_id"),
                strategy_id=strategy_result.get("strategy_id"),
                timestamp=int(time.time())
            )
            
            self.logger.log_trade_command(
                command_id=command.command_id,
                command_type="trade_command",
                symbol=symbol,
                action=action,
                status="created",
                metadata=command.to_dict()
            )
            
            return command
            
        except Exception as e:
            self.logger.log_error("Trade command creation failed", str(e), "FlowManager")
            return None
    
    async def _route_to_execution(self, trade_command: TradeCommand) -> bool:
        """Route trade command to execution agent"""
        try:
            result = await self.agent_io.send_to_execution(trade_command.to_dict())
            
            if result:
                self.logger.log_trade_command(
                    command_id=trade_command.command_id,
                    command_type="trade_command",
                    symbol=trade_command.symbol,
                    action=trade_command.action,
                    status="routed",
                    metadata=trade_command.to_dict()
                )
            
            return result
            
        except Exception as e:
            self.logger.log_error("Execution routing failed", str(e), "FlowManager")
            return False
    
    def _update_avg_duration(self, duration: float):
        """Update average flow duration"""
        try:
            total_flows = self.flow_stats['successful_flows']
            current_avg = self.flow_stats['avg_flow_duration']
            
            # Calculate new average
            new_avg = ((current_avg * (total_flows - 1)) + duration) / total_flows
            self.flow_stats['avg_flow_duration'] = new_avg
            
        except Exception as e:
            self.logger.log_error("Failed to update average duration", str(e), "FlowManager")
    
    async def coordinate_agents(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Coordinate signal processing across agents"""
        try:
            signal_id = signal.get('signal_id', f"coord_{int(time.time())}")
            
            self.logger.log_agent_coordination(
                agent_type="all",
                action="coordinate",
                signal_id=signal_id,
                status="initiated"
            )
            
            # Send to strategy first
            strategy_response = await self.agent_io.send_to_strategy(signal)
            if not strategy_response or not strategy_response.get("approved"):
                self.logger.log_agent_coordination(
                    agent_type="strategy",
                    action="rejected",
                    signal_id=signal_id,
                    status="rejected",
                    response=strategy_response
                )
                return None
            
            # Send to risk management
            risk_response = await self.agent_io.send_to_risk(signal)
            if not risk_response or not risk_response.get("passed"):
                self.logger.log_agent_coordination(
                    agent_type="risk",
                    action="rejected",
                    signal_id=signal_id,
                    status="rejected",
                    response=risk_response
                )
                return None
            
            # Send to intelligence for analysis
            intel_response = await self.agent_io.send_to_intelligence({
                'signal': signal,
                'strategy_response': strategy_response,
                'risk_response': risk_response
            })
            
            # Combine all responses
            coordinated_response = {
                'signal_id': signal_id,
                'strategy_approved': strategy_response.get('approved', False),
                'risk_passed': risk_response.get('passed', False),
                'intelligence_analysis': intel_response,
                'timestamp': int(time.time())
            }
            
            self.logger.log_agent_coordination(
                agent_type="all",
                action="completed",
                signal_id=signal_id,
                status="success",
                response=coordinated_response
            )
            
            return coordinated_response
            
        except Exception as e:
            self.logger.log_error("Agent coordination failed", str(e), "FlowManager")
            return None
    
    def get_flow_stats(self) -> Dict[str, Any]:
        """Get flow management statistics"""
        try:
            stats = self.flow_stats.copy()
            
            # Calculate success rate
            if stats['total_flows'] > 0:
                stats['success_rate'] = stats['successful_flows'] / stats['total_flows']
            else:
                stats['success_rate'] = 0.0
            
            # Add risk parameters
            stats['risk_params'] = self.risk_params
            
            return stats
            
        except Exception as e:
            self.logger.log_error("Failed to get flow stats", str(e), "FlowManager")
            return {'error': str(e)}
    
    def reset_stats(self):
        """Reset flow statistics"""
        try:
            self.flow_stats = {
                'total_flows': 0,
                'successful_flows': 0,
                'failed_flows': 0,
                'risk_rejections': 0,
                'strategy_rejections': 0,
                'execution_failures': 0,
                'avg_flow_duration': 0.0
            }
            
            self.logger.log_system_operation(
                operation="reset_stats",
                component="flow_manager",
                status="completed"
            )
            
        except Exception as e:
            self.logger.log_error("Failed to reset flow stats", str(e), "FlowManager")
    
    def is_connected(self) -> bool:
        """Check if flow manager is connected"""
        try:
            return self.agent_io.is_connected()
        except:
            return False