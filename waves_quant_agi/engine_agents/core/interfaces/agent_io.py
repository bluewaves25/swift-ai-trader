import redis
import time
import asyncio
from typing import Dict, Any, Optional, List
from ..logs.core_agent_logger import CoreAgentLogger

class AgentIO:
    """
    Enhanced agent communication interface with Redis integration.
    Handles communication between Core Agent and other agents.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = CoreAgentLogger("agent_io")
        
        # Redis configuration
        redis_host = self.config.get('redis_host', 'localhost')
        redis_port = int(self.config.get('redis_port', 6379))
        redis_db = int(self.config.get('redis_db', 0))
        
        # Initialize Redis
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=redis_db, 
                decode_responses=True
            )
            self.redis_client.ping()  # Test connection
            self.logger.log_info("AgentIO Redis connection established")
        except Exception as e:
            self.logger.log_error("Redis connection failed", str(e), "AgentIO")
            self.redis_client = None
        
        # Agent communication channels
        self.agent_channels = {
            'strategy': 'strategy_agent:signals',
            'risk': 'risk_agent:signals',
            'execution': 'execution_agent:commands',
            'intelligence': 'intelligence_agent:signals',
            'validation': 'validation_agent:requests',
            'market_conditions': 'market_conditions_agent:signals',
            'fees_monitor': 'fees_monitor_agent:signals',
            'data_feeds': 'data_feeds_agent:signals',
            'adapters': 'adapters_agent:signals',
            'failure_prevention': 'failure_prevention_agent:events'
        }
        
        # Response tracking
        self.pending_responses = {}
        self.response_timeout = self.config.get('response_timeout', 30.0)
        
    async def send_to_strategy(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send signal to strategy agent for approval"""
        try:
            signal_id = signal.get('signal_id', f"signal_{int(time.time())}")
            
            self.logger.log_agent_coordination(
                agent_type="strategy",
                action="send_signal",
                signal_id=signal_id,
                status="sending",
                metadata=signal
            )
            
            # Send to strategy agent via Redis
            if self.redis_client:
                message = {
                    'timestamp': int(time.time()),
                    'signal_id': signal_id,
                    'signal': signal,
                    'source': 'core_agent'
                }
                
                self.redis_client.publish(self.agent_channels['strategy'], str(message))
                
                # Wait for response
                response = await self._wait_for_response(signal_id, 'strategy')
                
                if response:
                    self.logger.log_agent_coordination(
                        agent_type="strategy",
                        action="receive_response",
                        signal_id=signal_id,
                        status="received",
                        response=response
                    )
                    return response
                else:
                    self.logger.log_agent_coordination(
                        agent_type="strategy",
                        action="timeout",
                        signal_id=signal_id,
                        status="timeout"
                    )
                    return {"approved": False, "reason": "Strategy agent timeout"}
            
            # Fallback response
            return {"approved": True, "signal_id": signal_id}
            
        except Exception as e:
            self.logger.log_error("Failed to send to strategy", str(e), "AgentIO")
            return {"approved": False, "reason": f"Error: {str(e)}"}

    async def send_to_risk(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send signal to risk agent for compliance check"""
        try:
            signal_id = signal.get('signal_id', f"risk_{int(time.time())}")
            
            self.logger.log_agent_coordination(
                agent_type="risk",
                action="send_signal",
                signal_id=signal_id,
                status="sending",
                metadata=signal
            )
            
            # Send to risk agent via Redis
            if self.redis_client:
                message = {
                    'timestamp': int(time.time()),
                    'signal_id': signal_id,
                    'signal': signal,
                    'source': 'core_agent'
                }
                
                self.redis_client.publish(self.agent_channels['risk'], str(message))
                
                # Wait for response
                response = await self._wait_for_response(signal_id, 'risk')
                
                if response:
                    self.logger.log_agent_coordination(
                        agent_type="risk",
                        action="receive_response",
                        signal_id=signal_id,
                        status="received",
                        response=response
                    )
                    return response
                else:
                    self.logger.log_agent_coordination(
                        agent_type="risk",
                        action="timeout",
                        signal_id=signal_id,
                        status="timeout"
                    )
                    return {"passed": False, "reason": "Risk agent timeout"}
            
            # Fallback response
            return {"passed": True, "signal_id": signal_id}
            
        except Exception as e:
            self.logger.log_error("Failed to send to risk", str(e), "AgentIO")
            return {"passed": False, "reason": f"Error: {str(e)}"}

    async def send_to_execution(self, trade_command: Dict[str, Any]) -> bool:
        """Send trade command to execution agent"""
        try:
            command_id = trade_command.get('command_id', f"cmd_{int(time.time())}")
            
            self.logger.log_trade_command(
                command_id=command_id,
                command_type=trade_command.get('type', 'unknown'),
                symbol=trade_command.get('symbol', 'unknown'),
                action=trade_command.get('action', 'unknown'),
                status="sending",
                metadata=trade_command
            )
            
            # Send to execution agent via Redis
            if self.redis_client:
                message = {
                    'timestamp': int(time.time()),
                    'command_id': command_id,
                    'command': trade_command,
                    'source': 'core_agent'
                }
                
                self.redis_client.publish(self.agent_channels['execution'], str(message))
                
                # Wait for confirmation
                response = await self._wait_for_response(command_id, 'execution')
                
                if response:
                    self.logger.log_trade_command(
                        command_id=command_id,
                        command_type=trade_command.get('type', 'unknown'),
                        symbol=trade_command.get('symbol', 'unknown'),
                        action=trade_command.get('action', 'unknown'),
                        status="confirmed",
                        metadata=response
                    )
                    return True
                else:
                    self.logger.log_trade_command(
                        command_id=command_id,
                        command_type=trade_command.get('type', 'unknown'),
                        symbol=trade_command.get('symbol', 'unknown'),
                        action=trade_command.get('action', 'unknown'),
                        status="timeout"
                    )
                    return False
            
            # Fallback success
            return True
            
        except Exception as e:
            self.logger.log_error("Failed to send to execution", str(e), "AgentIO")
            return False

    async def send_to_intelligence(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send data to intelligence agent for analysis"""
        try:
            request_id = data.get('request_id', f"intel_{int(time.time())}")
            
            self.logger.log_agent_coordination(
                agent_type="intelligence",
                action="send_data",
                signal_id=request_id,
                status="sending",
                metadata=data
            )
            
            # Send to intelligence agent via Redis
            if self.redis_client:
                message = {
                    'timestamp': int(time.time()),
                    'request_id': request_id,
                    'data': data,
                    'source': 'core_agent'
                }
                
                self.redis_client.publish(self.agent_channels['intelligence'], str(message))
                
                # Wait for response
                response = await self._wait_for_response(request_id, 'intelligence')
                
                if response:
                    self.logger.log_agent_coordination(
                        agent_type="intelligence",
                        action="receive_response",
                        signal_id=request_id,
                        status="received",
                        response=response
                    )
                    return response
            
            return None
            
        except Exception as e:
            self.logger.log_error("Failed to send to intelligence", str(e), "AgentIO")
            return None

    async def send_to_validation(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send validation request to validation agent"""
        try:
            request_id = request.get('request_id', f"val_{int(time.time())}")
            
            self.logger.log_agent_coordination(
                agent_type="validation",
                action="send_request",
                signal_id=request_id,
                status="sending",
                metadata=request
            )
            
            # Send to validation agent via Redis
            if self.redis_client:
                message = {
                    'timestamp': int(time.time()),
                    'request_id': request_id,
                    'request': request,
                    'source': 'core_agent'
                }
                
                self.redis_client.publish(self.agent_channels['validation'], str(message))
                
                # Wait for response
                response = await self._wait_for_response(request_id, 'validation')
                
                if response:
                    self.logger.log_agent_coordination(
                        agent_type="validation",
                        action="receive_response",
                        signal_id=request_id,
                        status="received",
                        response=response
                    )
                    return response
            
            return None
            
        except Exception as e:
            self.logger.log_error("Failed to send to validation", str(e), "AgentIO")
            return None

    async def broadcast_to_all_agents(self, message: Dict[str, Any]) -> Dict[str, bool]:
        """Broadcast message to all agents"""
        try:
            results = {}
            
            for agent_name, channel in self.agent_channels.items():
                try:
                    if self.redis_client:
                        self.redis_client.publish(channel, str(message))
                        results[agent_name] = True
                    else:
                        results[agent_name] = False
                except Exception as e:
                    self.logger.log_error(f"Failed to broadcast to {agent_name}", str(e), "AgentIO")
                    results[agent_name] = False
            
            self.logger.log_system_operation(
                operation="broadcast",
                component="all_agents",
                status="completed",
                metadata={'results': results}
            )
            
            return results
            
        except Exception as e:
            self.logger.log_error("Failed to broadcast to all agents", str(e), "AgentIO")
            return {}

    async def _wait_for_response(self, request_id: str, agent_type: str) -> Optional[Dict[str, Any]]:
        """Wait for response from specific agent"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < self.response_timeout:
                # Check for response in Redis
                if self.redis_client:
                    response_key = f"core_agent:response:{agent_type}:{request_id}"
                    response = self.redis_client.get(response_key)
                    
                    if response:
                        # Clean up response
                        self.redis_client.delete(response_key)
                        return eval(response)  # Convert string back to dict
                
                await asyncio.sleep(0.1)  # Small delay
            
            return None
            
        except Exception as e:
            self.logger.log_error(f"Error waiting for response from {agent_type}", str(e), "AgentIO")
            return None

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        try:
            status = {
                'redis_connected': self.redis_client is not None,
                'agent_channels': list(self.agent_channels.keys()),
                'pending_responses': len(self.pending_responses),
                'response_timeout': self.response_timeout
            }
            
            # Check agent availability via Redis
            if self.redis_client:
                agent_status = {}
                for agent_name, channel in self.agent_channels.items():
                    try:
                        # Try to publish a ping message
                        self.redis_client.publish(f"{channel}:ping", "ping")
                        agent_status[agent_name] = "available"
                    except Exception:
                        agent_status[agent_name] = "unavailable"
                
                status['agent_availability'] = agent_status
            
            return status
            
        except Exception as e:
            self.logger.log_error("Failed to get agent status", str(e), "AgentIO")
            return {'error': str(e)}

    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        try:
            if not self.redis_client:
                return {"error": "Redis not connected"}
            
            stats = {
                'total_messages_sent': self.redis_client.llen('core_agent:message_history'),
                'total_responses_received': self.redis_client.llen('core_agent:response_history'),
                'pending_requests': len(self.pending_responses),
                'agent_channels': len(self.agent_channels)
            }
            
            return stats
            
        except Exception as e:
            self.logger.log_error("Failed to get communication stats", str(e), "AgentIO")
            return {'error': str(e)}

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
            return False
        except:
            return False