import redis
import time
import asyncio
from typing import Dict, Any, Optional, List
from ..logs.core_agent_logger import CoreAgentLogger

class SystemCoordinationIO:
    """
    System coordination communication interface with Redis integration.
    Handles communication between Core Agent and other agents for system coordination ONLY.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = CoreAgentLogger("system_coordination_io")
        
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
            self.logger.log_info("SystemCoordinationIO Redis connection established")
        except Exception as e:
            self.logger.log_error("Redis connection failed", str(e), "SystemCoordinationIO")
            self.redis_client = None
        
        # System coordination communication channels
        self.coordination_channels = {
            'system_health': 'system:health',
            'timing_sync': 'system:timing',
            'agent_status': 'system:agent_status',
            'system_commands': 'system:commands',
            'coordination_events': 'system:coordination'
        }
        
        # Response tracking for coordination requests
        self.pending_coordination_responses = {}
        self.response_timeout = self.config.get('response_timeout', 30.0)
        
    async def send_health_check_request(self, target_agent: str, health_type: str = "general") -> Optional[Dict[str, Any]]:
        """Send health check request to specific agent"""
        try:
            request_id = f"health_{target_agent}_{int(time.time())}"
            
            self.logger.log_agent_coordination(
                agent_type=target_agent,
                action="send_health_check",
                request_id=request_id,
                status="sending",
                metadata={"health_type": health_type}
            )
            
            # Send health check request via Redis
            if self.redis_client:
                message = {
                    'timestamp': int(time.time()),
                    'request_id': request_id,
                    'request_type': 'health_check',
                    'health_type': health_type,
                    'source': 'core_agent'
                }
                
                self.redis_client.publish(self.coordination_channels['system_health'], str(message))
                
                # Wait for response
                response = await self._wait_for_coordination_response(request_id, target_agent)
                
                if response:
                    self.logger.log_agent_coordination(
                        agent_type=target_agent,
                        action="receive_health_response",
                        request_id=request_id,
                        status="received",
                        response=response
                    )
                    return response
                else:
                    self.logger.log_agent_coordination(
                        agent_type=target_agent,
                        action="health_check_timeout",
                        request_id=request_id,
                        status="timeout"
                    )
                    return {"success": False, "reason": f"{target_agent} health check timeout"}
            
            # Fallback response
            return {"success": True, "request_id": request_id, "health_status": "unknown"}
            
        except Exception as e:
            self.logger.log_error("Error sending health check request", str(e), "SystemCoordinationIO")
            return {"success": False, "reason": f"System error: {str(e)}"}
    
    async def send_timing_sync_request(self, target_agent: str, timing_type: str = "sync") -> Optional[Dict[str, Any]]:
        """Send timing synchronization request to specific agent"""
        try:
            request_id = f"timing_{target_agent}_{int(time.time())}"
            
            self.logger.log_agent_coordination(
                agent_type=target_agent,
                action="send_timing_sync",
                request_id=request_id,
                status="sending",
                metadata={"timing_type": timing_type}
            )
            
            # Send timing sync request via Redis
            if self.redis_client:
                message = {
                    'timestamp': int(time.time()),
                    'request_id': request_id,
                    'request_type': 'timing_sync',
                    'timing_type': timing_type,
                    'source': 'core_agent'
                }
                
                self.redis_client.publish(self.coordination_channels['timing_sync'], str(message))
                
                # Wait for response
                response = await self._wait_for_coordination_response(request_id, target_agent)
                
                if response:
                    self.logger.log_agent_coordination(
                        agent_type=target_agent,
                        action="receive_timing_response",
                        request_id=request_id,
                        status="received",
                        response=response
                    )
                    return response
                else:
                    self.logger.log_agent_coordination(
                        agent_type=target_agent,
                        action="timing_sync_timeout",
                        request_id=request_id,
                        status="timeout"
                    )
                    return {"success": False, "reason": f"{target_agent} timing sync timeout"}
            
            # Fallback response
            return {"success": True, "request_id": request_id, "timing_synced": True}
            
        except Exception as e:
            self.logger.log_error("Error sending timing sync request", str(e), "SystemCoordinationIO")
            return {"success": False, "reason": f"System error: {str(e)}"}
    
    async def send_agent_status_request(self, target_agent: str, status_type: str = "update") -> Optional[Dict[str, Any]]:
        """Send agent status request to specific agent"""
        try:
            request_id = f"status_{target_agent}_{int(time.time())}"
            
            self.logger.log_agent_coordination(
                agent_type=target_agent,
                action="send_status_request",
                request_id=request_id,
                status="sending",
                metadata={"status_type": status_type}
            )
            
            # Send status request via Redis
            if self.redis_client:
                message = {
                    'timestamp': int(time.time()),
                    'request_id': request_id,
                    'request_type': 'agent_status',
                    'status_type': status_type,
                    'source': 'core_agent'
                }
                
                self.redis_client.publish(self.coordination_channels['agent_status'], str(message))
                
                # Wait for response
                response = await self._wait_for_coordination_response(request_id, target_agent)
                
                if response:
                    self.logger.log_agent_coordination(
                        agent_type=target_agent,
                        action="receive_status_response",
                        request_id=request_id,
                        status="received",
                        response=response
                    )
                    return response
                else:
                    self.logger.log_agent_coordination(
                        agent_type=target_agent,
                        action="status_request_timeout",
                        request_id=request_id,
                        status="timeout"
                    )
                    return {"success": False, "reason": f"{target_agent} status request timeout"}
            
            # Fallback response
            return {"success": True, "request_id": request_id, "status_updated": True}
            
        except Exception as e:
            self.logger.log_error("Error sending agent status request", str(e), "SystemCoordinationIO")
            return {"success": False, "reason": f"System error: {str(e)}"}
    
    async def broadcast_system_command(self, command: Dict[str, Any]) -> bool:
        """Broadcast system command to all agents"""
        try:
            if not self.redis_client:
                return False
            
            message = {
                'timestamp': int(time.time()),
                'command': command,
                'source': 'core_agent'
            }
            
            # Broadcast to system commands channel
            self.redis_client.publish(self.coordination_channels['system_commands'], str(message))
            
            self.logger.log_agent_coordination(
                agent_type="all",
                action="broadcast_system_command",
                request_id=command.get('command_id', 'unknown'),
                status="sent",
                metadata=command
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error("Error broadcasting system command", str(e), "SystemCoordinationIO")
            return False
    
    async def publish_coordination_event(self, event: Dict[str, Any]) -> bool:
        """Publish coordination event to coordination channel"""
        try:
            if not self.redis_client:
                return False
            
            message = {
                'timestamp': int(time.time()),
                'event': event,
                'source': 'core_agent'
            }
            
            # Publish to coordination events channel
            self.redis_client.publish(self.coordination_channels['coordination_events'], str(message))
            
            self.logger.log_agent_coordination(
                agent_type="system",
                action="publish_coordination_event",
                request_id=event.get('event_id', 'unknown'),
                status="published",
                metadata=event
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error("Error publishing coordination event", str(e), "SystemCoordinationIO")
            return False
    
    # ============= PRIVATE METHODS =============
    
    async def _wait_for_coordination_response(self, request_id: str, target_agent: str) -> Optional[Dict[str, Any]]:
        """Wait for coordination response from target agent"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < self.response_timeout:
                # Check if response is available
                if request_id in self.pending_coordination_responses:
                    response = self.pending_coordination_responses.pop(request_id)
                    return response
                
                await asyncio.sleep(0.1)  # 100ms polling interval
            
            return None
            
        except Exception as e:
            self.logger.log_error(f"Error waiting for coordination response: {str(e)}", str(e), "SystemCoordinationIO")
            return None
    
    def _store_coordination_response(self, request_id: str, response: Dict[str, Any]):
        """Store coordination response for waiting requests"""
        try:
            self.pending_coordination_responses[request_id] = response
        except Exception as e:
            self.logger.log_error(f"Error storing coordination response: {str(e)}", str(e), "SystemCoordinationIO")
    
    # ============= PUBLIC INTERFACE METHODS =============
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get system coordination communication status"""
        try:
            return {
                "redis_connected": self.redis_client is not None,
                "active_channels": len(self.coordination_channels),
                "pending_responses": len(self.pending_coordination_responses),
                "response_timeout": self.response_timeout,
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.log_error("Error getting coordination status", str(e), "SystemCoordinationIO")
            return {"error": str(e)}
    
    def is_connected(self) -> bool:
        """Check if system coordination IO is connected"""
        try:
            return self.redis_client is not None and self.redis_client.ping()
        except:
            return False
    
    def cleanup_pending_responses(self):
        """Cleanup expired pending responses"""
        try:
            current_time = time.time()
            expired_requests = []
            
            for request_id, response in self.pending_coordination_responses.items():
                if current_time - response.get('timestamp', 0) > self.response_timeout:
                    expired_requests.append(request_id)
            
            for request_id in expired_requests:
                self.pending_coordination_responses.pop(request_id, None)
                
        except Exception as e:
            self.logger.log_error("Error cleaning up pending responses", str(e), "SystemCoordinationIO")