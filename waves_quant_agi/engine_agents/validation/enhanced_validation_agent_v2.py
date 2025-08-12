#!/usr/bin/env python3
"""
Enhanced Validation Agent V2 - REFACTORED TO USE BASE AGENT
Eliminates duplicate start/stop methods and Redis connection logic.
"""

import asyncio
import time
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedValidationAgentV2(BaseAgent):
    """Enhanced validation agent using base class."""
    
    def _initialize_agent_components(self):
        """Initialize validation specific components."""
        # Initialize validation components with mock implementations
        self.data_validator = MockDataValidator()
        self.system_validator = MockSystemValidator()
        self.validation_queue = {}
        
        # Initialize validation state
        self.current_validation_state = {
            "last_validation_time": time.time(),
            "system_health_score": 1.0,
            "data_quality_score": 1.0,
            "validation_status": "initializing"
        }
        
        # Initialize stats
        self.stats = {
            "data_validations": 0,
            "system_validations": 0,
            "comprehensive_validations": 0,
            "validation_failures": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Validation specific startup logic."""
        # Initialize validation systems
        self.logger.info("Validation systems initialized")
    
    async def _agent_specific_shutdown(self):
        """Validation specific shutdown logic."""
        # Cleanup validation specific resources
        self.logger.info("Validation systems cleaned up")
    
    # ============= TIER 2: FAST DATA VALIDATION LOOP (100ms) =============
    
    async def _fast_data_validation_loop(self):
        """TIER 2: Fast data integrity validation for critical data (100ms)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Process fast data validation queue
                data_validations = await self._process_fast_data_validations()
                
                # Update validation state if needed
                if data_validations > 0:
                    self._update_validation_state_fast()
                    self.stats["data_validations"] += data_validations
                
                # Record operation for monitoring
                duration_ms = (time.time() - start_time) * 1000
                self.status_monitor.record_operation(duration_ms, data_validations > 0)
                
                # TIER 2 timing: 100ms for fast data validation
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in fast data validation loop: {e}")
                await asyncio.sleep(0.1)
    
    # ============= TIER 3: TACTICAL SYSTEM VALIDATION LOOP (30s) =============
    
    async def _tactical_system_validation_loop(self):
        """TIER 3: Tactical system health validation (30s)."""
        while self.is_running:
            try:
                # Perform basic system health check (simplified)
                system_validation = await self._perform_basic_system_check()
                
                # Update validation state
                self._update_validation_state_from_system_health(system_validation)
                
                # Publish system health alerts if needed
                await self._publish_system_health_alerts(system_validation)
                
                # TIER 3 timing: 30s for tactical system validation
                await asyncio.sleep(30.0)
                
            except Exception as e:
                self.logger.error(f"Error in tactical system validation loop: {e}")
                await asyncio.sleep(30.0)
    
    # ============= TIER 4: STRATEGIC COMPREHENSIVE VALIDATION LOOP (300s) =============
    
    async def _strategic_comprehensive_validation_loop(self):
        """TIER 4: Strategic comprehensive validation and audit (300s)."""
        while self.is_running:
            try:
                # Perform comprehensive validation audit
                audit_results = await self._perform_comprehensive_validation_audit()
                
                # Publish comprehensive validation report
                await self._publish_comprehensive_validation_report(audit_results)
                
                # Update comprehensive stats
                self._update_comprehensive_stats()
                
                # TIER 4 timing: 300s for strategic comprehensive validation
                await asyncio.sleep(300.0)
                
            except Exception as e:
                self.logger.error(f"Error in strategic comprehensive validation loop: {e}")
                await asyncio.sleep(300.0)
    
    # ============= TIER 4: HEARTBEAT LOOP (60s) =============
    
    async def _heartbeat_loop(self):
        """TIER 4: Communication heartbeat and status reporting (60s)."""
        while self.is_running:
            try:
                # Send heartbeat to communication hub
                if self.comm_hub:
                    await self._send_heartbeat()
                
                # Update agent stats in Redis (same as BaseAgent)
                current_time = time.time()
                agent_stats = {
                    'status': 'running' if self.is_running else 'stopped',
                    'start_time': str(self.start_time) if self.start_time else '0',
                    'uptime_seconds': str(int(current_time - self.start_time)) if self.start_time else '0',
                    'last_heartbeat': str(current_time),
                    'timestamp': str(current_time)
                }
                
                # Update the agent_stats hash using the correct Redis connector method
                if hasattr(self, 'redis_conn') and self.redis_conn:
                    self.redis_conn.hset(f"agent_stats:{self.agent_name}", mapping=agent_stats)
                else:
                    self.logger.warning("Redis connection not available for storing agent status")
                
                # TIER 4 timing: 60s for heartbeat
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(60)
    
    # ============= HELPER METHODS =============
    
    async def _process_fast_data_validations(self) -> int:
        """Process fast data validations from queue."""
        validations_processed = 0
        
        try:
            # Get pending data validation requests
            pending_validations = self._get_pending_data_validations()
            
            for validation_request in pending_validations:
                try:
                    start_time = time.time()
                    
                    # Validate market data
                    validation_result = await self.data_validator.validate_market_data(
                        validation_request["data"],
                        validation_request.get("validation_type", "realtime")
                    )
                    
                    # Send validation response
                    await self._send_data_validation_response(validation_request, validation_result)
                    
                    validations_processed += 1
                    
                    # Update stats
                    if validation_result.get("data_quality_score", 0.0) < 0.7:
                        self.stats["validation_failures"] += 1
                    
                except Exception as e:
                    self.logger.warning(f"Error processing data validation: {e}")
            
        except Exception as e:
            self.logger.error(f"Error in fast data validation processing: {e}")
        
        return validations_processed
    
    def _get_pending_data_validations(self) -> List[Dict[str, Any]]:
        """Get pending data validation requests."""
        try:
            # Safety check for Redis connection
            if not hasattr(self, 'redis_conn') or not self.redis_conn:
                self.logger.warning("Redis connection not available, returning empty list")
                return []
            
            # Check if the method exists
            if not hasattr(self.redis_conn, 'get_queue_items'):
                self.logger.warning(f"Redis connector missing get_queue_items method. Available methods: {[m for m in dir(self.redis_conn) if not m.startswith('_')]}")
                return []
            
            # Get from Redis queue or return simulated data for testing
            validations = self.redis_conn.get_queue_items("data_validations_fast")
            return validations if validations else []
            
        except Exception as e:
            self.logger.warning(f"Error getting pending data validations: {e}")
            return []
    
    async def _send_data_validation_response(self, validation_request: Dict[str, Any], 
                                           validation_result: Dict[str, Any]):
        """Send data validation response back to requester."""
        try:
            response = {
                "type": "DATA_VALIDATION_RESPONSE",
                "request_id": validation_request.get("request_id"),
                "validation_result": validation_result,
                "timestamp": time.time(),
                "source": "validation"
            }
            
            if self.comm_hub:
                await self.comm_hub.publish_message(response)
                
        except Exception as e:
            self.logger.error(f"Error sending data validation response: {e}")
    
    def _update_validation_state_fast(self):
        """Update validation state from fast operations."""
        self.current_validation_state["last_validation_time"] = time.time()
    
    def _update_validation_state_from_system_health(self, system_validation: Dict[str, Any]):
        """Update validation state from system health validation."""
        try:
            system_health_score = system_validation.get("system_health_score", 1.0)
            
            self.current_validation_state.update({
                "system_health_score": system_health_score,
                "last_validation_time": time.time()
            })
            
        except Exception as e:
            self.logger.warning(f"Error updating validation state: {e}")
    
    async def _perform_basic_system_check(self) -> Dict[str, Any]:
        """Perform basic system health check (simplified)."""
        try:
            import psutil
            
            # Basic system metrics
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            # Simple health assessment
            system_health_score = 1.0
            critical_issues = []
            
            if cpu_usage > 85:
                system_health_score -= 0.3
                critical_issues.append(f"High CPU usage: {cpu_usage:.1f}%")
            
            if memory_usage > 90:
                system_health_score -= 0.4
                critical_issues.append(f"High memory usage: {memory_usage:.1f}%")
            
            return {
                "system_health_score": max(0.0, system_health_score),
                "critical_issues": critical_issues,
                "recommendations": ["Monitor system resources"] if critical_issues else [],
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.warning(f"Error in basic system check: {e}")
            return {
                "system_health_score": 0.8,  # Default to reasonable health
                "critical_issues": [],
                "recommendations": [],
                "timestamp": time.time()
            }
    
    async def _simple_system_health_monitoring(self):
        """Simple system health monitoring (placeholder)."""
        try:
            # Basic monitoring - could be expanded later
            self.current_validation_state["last_validation_time"] = time.time()
            
        except Exception as e:
            self.logger.warning(f"Error in simple system health monitoring: {e}")
    
    async def _publish_system_health_alerts(self, system_validation: Dict[str, Any]):
        """Publish system health alerts if critical issues are found."""
        try:
            critical_issues = system_validation.get("critical_issues", [])
            
            if critical_issues:
                alert_message = {
                    "type": "SYSTEM_HEALTH_ALERT",
                    "critical_issues": critical_issues,
                    "system_health_score": system_validation.get("system_health_score", 0.0),
                    "recommendations": system_validation.get("recommendations", []),
                    "timestamp": time.time(),
                    "source": "validation"
                }
                
                if self.comm_hub:
                    await self.comm_hub.publish_message(alert_message)
                
        except Exception as e:
            self.logger.error(f"Error publishing system health alerts: {e}")
    
    async def _perform_comprehensive_validation_audit(self) -> Dict[str, Any]:
        """Perform comprehensive validation audit across all systems."""
        try:
            # Simplified comprehensive validation
            
            # Perform both data and basic system validation
            data_validation = await self.data_validator.validate_market_data({
                "symbol": "AUDIT_CHECK",
                "price": 30000.0,
                "timestamp": time.time()
            }, "comprehensive")
            
            system_validation = await self._perform_basic_system_check()
            
            # Update current validation state
            self.current_validation_state.update({
                "data_quality_score": data_validation.get("data_quality_score", 1.0),
                "system_health_score": system_validation.get("system_health_score", 1.0),
                "last_validation_time": time.time()
            })
            
            return {
                "data_validation_result": data_validation,
                "system_validation_result": system_validation
            }
            
        except Exception as e:
            self.logger.warning(f"Error in comprehensive validation audit: {e}")
            return {}
    

    
    async def _publish_comprehensive_validation_report(self, audit_results: Dict[str, Any]):
        """Publish comprehensive validation report."""
        try:
            validation_report = {
                "type": "COMPREHENSIVE_VALIDATION_REPORT",
                "current_validation_state": self.current_validation_state,
                "data_validator_stats": audit_results.get("data_validation_result", {}).get("validation_stats", {}),
                "system_validator_stats": audit_results.get("system_validation_result", {}).get("validation_stats", {}),
                "timestamp": time.time(),
                "source": "validation"
            }
            
            if self.comm_hub:
                await self.comm_hub.publish_message(validation_report)
                
        except Exception as e:
            self.logger.error(f"Error publishing comprehensive validation report: {e}")
    
    def _update_comprehensive_stats(self):
        """Update comprehensive statistics."""
        # The original code had data_validator.get_validation_stats() here,
        # but data_validator is not initialized in the new BaseAgent structure.
        # This method will need to be refactored or removed if comprehensive stats
        # are no longer tracked by the data validator.
        # For now, keeping the structure but noting the potential issue.
        pass
    
    async def _send_heartbeat(self):
        """Send heartbeat to communication hub."""
        try:
            heartbeat_data = {
                "agent": "validation",
                "status": "healthy",
                "stats": self.stats,
                "current_validation_state": self.current_validation_state,
                "timestamp": time.time()
            }
            
            if hasattr(self.comm_hub, 'publish_message'):
                await self.comm_hub.publish_message({
                    "type": "AGENT_HEARTBEAT",
                    "data": heartbeat_data
                })
                
        except Exception as e:
            self.logger.warning(f"Error sending heartbeat: {e}")
    
    # ============= MESSAGE HANDLERS =============
    
    async def _handle_data_validation_request(self, message):
        """Handle data validation requests."""
        try:
            data = message.get("data", {})
            validation_type = message.get("validation_type", "realtime")
            
            # Validate data
            validation_result = await self.data_validator.validate_market_data(data, validation_type)
            
            # Send response back through communication hub
            if self.comm_hub:
                response = {
                    "type": "DATA_VALIDATION_RESPONSE",
                    "request_id": message.get("request_id"),
                    "validation_result": validation_result,
                    "timestamp": time.time()
                }
                await self.comm_hub.publish_message(response)
                
        except Exception as e:
            self.logger.error(f"Error handling data validation request: {e}")
    
    async def _handle_system_validation_request(self, message):
        """Handle system validation requests."""
        try:
            # Perform system health validation
            system_validation = await self.system_validator.validate_system_health()
            
            # Send response back through communication hub
            if self.comm_hub:
                response = {
                    "type": "SYSTEM_VALIDATION_RESPONSE",
                    "request_id": message.get("request_id"),
                    "system_validation": system_validation,
                    "timestamp": time.time()
                }
                await self.comm_hub.publish_message(response)
                
        except Exception as e:
            self.logger.error(f"Error handling system validation request: {e}")
    
    async def _handle_validation_status_request(self, message):
        """Handle validation status requests."""
        try:
            # Get current validation status
            validation_status = {
                "current_state": self.current_validation_state,
                "agent_stats": self.stats,
                "data_validator_stats": self.data_validator.get_validation_stats() if self.data_validator else {},
                "system_validator_stats": self.system_validator.get_system_validation_stats() if self.system_validator else {}
            }
            
            # Send response back through communication hub
            if self.comm_hub:
                response = {
                    "type": "VALIDATION_STATUS_RESPONSE",
                    "request_id": message.get("request_id"),
                    "validation_status": validation_status,
                    "timestamp": time.time()
                }
                await self.comm_hub.publish_message(response)
                
        except Exception as e:
            self.logger.error(f"Error handling validation status request: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        return {
            "is_running": self.is_running,
            "stats": self.stats,
            "current_validation_state": self.current_validation_state,
            "data_validator_stats": self.data_validator.get_validation_stats() if self.data_validator else {},
            "uptime_seconds": int(time.time() - self.stats["start_time"])
        }

# Mock classes for components that don't exist yet
class MockDataValidator:
    async def validate_market_data(self, data, validation_type):
        return {
            "data_quality_score": 0.95,
            "is_valid": True,
            "validation_type": validation_type,
            "timestamp": time.time()
        }

class MockSystemValidator:
    async def validate_system_health(self):
        return {
            "system_health_score": 0.9,
            "is_healthy": True,
            "timestamp": time.time()
        }
