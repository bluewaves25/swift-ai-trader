#!/usr/bin/env python3
"""
Enhanced Validation Agent V2 - ROLE CONSOLIDATED: DATA VALIDATION ONLY
Removed system health validation functionality - now handled by Core Agent.
Focuses exclusively on data validation and quality monitoring.
"""

import asyncio
import time
import json
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedValidationAgentV2(BaseAgent):
    """Enhanced validation agent - focused solely on data validation."""
    
    def _initialize_agent_components(self):
        """Initialize validation specific components."""
        # Initialize validation components
        self.data_validator = None
        self.validation_queue = {}
        self.data_quality_monitor = None
        
        # Data validation state
        self.validation_state = {
            "last_validation_time": time.time(),
            "data_quality_score": 1.0,
            "validation_status": "initializing",
            "active_validations": {},
            "validation_history": []
        }
        
        # Data validation statistics
        self.stats = {
            "data_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "data_quality_issues": 0,
            "validation_timeouts": 0,
            "comprehensive_validations": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Validation specific startup logic."""
        try:
            # Initialize data validation components
            await self._initialize_validation_components()
            
            # Initialize data quality monitoring
            await self._initialize_data_quality_monitoring()
            
            self.logger.info("✅ Validation Agent: Data validation systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in validation startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Validation specific shutdown logic."""
        try:
            # Cleanup validation resources
            await self._cleanup_validation_components()
            
            self.logger.info("✅ Validation Agent: Data validation systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in validation shutdown: {e}")
    
    # ============= BACKGROUND TASKS =============
    
    async def _quality_monitoring_loop(self):
        """Quality monitoring loop."""
        while self.is_running:
            try:
                # Monitor data quality
                await self._monitor_data_quality()
                
                await asyncio.sleep(5.0)  # 5 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in quality monitoring loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _validation_reporting_loop(self):
        """Validation reporting loop."""
        while self.is_running:
            try:
                # Generate validation reports
                await self._generate_validation_report()
                
                await asyncio.sleep(30.0)  # 30 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in validation reporting loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _comprehensive_validation_loop(self):
        """Comprehensive validation loop."""
        while self.is_running:
            try:
                # Perform comprehensive validation
                await self._perform_comprehensive_validation()
                
                await asyncio.sleep(10.0)  # 10 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in comprehensive validation loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _monitor_data_quality(self):
        """Monitor data quality."""
        try:
            # Placeholder for data quality monitoring
            pass
        except Exception as e:
            self.logger.error(f"Error monitoring data quality: {e}")
    
    async def _generate_validation_report(self):
        """Generate validation report."""
        try:
            # Placeholder for validation report generation
            pass
        except Exception as e:
            self.logger.error(f"Error generating validation report: {e}")
    
    async def _perform_comprehensive_validation(self):
        """Perform comprehensive validation."""
        try:
            # Placeholder for comprehensive validation
            pass
        except Exception as e:
            self.logger.error(f"Error performing comprehensive validation: {e}")

    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._data_validation_loop, "Data Validation", "fast"),
            (self._quality_monitoring_loop, "Quality Monitoring", "tactical"),
            (self._validation_reporting_loop, "Validation Reporting", "strategic"),
            (self._comprehensive_validation_loop, "Comprehensive Validation", "tactical")
        ]
    
    # ============= VALIDATION COMPONENT INITIALIZATION =============
    
    async def _initialize_validation_components(self):
        """Initialize data validation components."""
        try:
            # Initialize data validator
            from .core.data_validator_simple import DataValidatorSimple as DataValidator
            self.data_validator = DataValidator(self.config)
            
            # Initialize validation queue
            self.validation_queue = {
                "high_priority": [],
                "normal_priority": [],
                "low_priority": []
            }
            
            self.logger.info("✅ Data validation components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing validation components: {e}")
            raise
    
    async def _initialize_data_quality_monitoring(self):
        """Initialize data quality monitoring."""
        try:
            # Initialize data quality monitor
            from .core.data_quality_monitor import DataQualityMonitor
            self.data_quality_monitor = DataQualityMonitor(self.config)
            
            self.logger.info("✅ Data quality monitoring initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing data quality monitoring: {e}")
            raise
    
    # ============= DATA VALIDATION LOOP =============
    
    async def _data_validation_loop(self):
        """Main data validation loop (100ms intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Process validation queue
                validations_processed = await self._process_validation_queue()
                
                # Update validation state
                if validations_processed > 0:
                    self._update_validation_state()
                    self.stats["data_validations"] += validations_processed
                
                # Record operation
                duration_ms = (time.time() - start_time) * 1000
                if hasattr(self, 'status_monitor') and self.status_monitor:
                    self.status_monitor.record_operation(duration_ms, validations_processed > 0)
                
                await asyncio.sleep(0.1)  # 100ms validation cycle
                
            except Exception as e:
                self.logger.error(f"Error in data validation loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_validation_queue(self) -> int:
        """Process validation queue and return number of validations processed."""
        try:
            validations_processed = 0
            
            # Process high priority validations first
            if self.validation_queue["high_priority"]:
                validations_processed += await self._process_priority_queue("high_priority")
            
            # Process normal priority validations
            if self.validation_queue["normal_priority"]:
                validations_processed += await self._process_priority_queue("normal_priority")
            
            # Process low priority validations (if time permits)
            if self.validation_queue["low_priority"] and validations_processed < 5:
                validations_processed += await self._process_priority_queue("low_priority")
            
            return validations_processed
            
        except Exception as e:
            self.logger.error(f"Error processing validation queue: {e}")
            return 0
    
    async def _process_priority_queue(self, priority: str) -> int:
        """Process a specific priority queue."""
        try:
            validations_processed = 0
            queue = self.validation_queue[priority]
            
            # Process up to 10 validations per cycle
            max_validations = min(10, len(queue))
            
            for _ in range(max_validations):
                if not queue:
                    break
                
                validation_request = queue.pop(0)
                if await self._process_validation_request(validation_request):
                    validations_processed += 1
            
            return validations_processed
            
        except Exception as e:
            self.logger.error(f"Error processing {priority} queue: {e}")
            return 0
    
    async def _process_validation_request(self, validation_request: Dict[str, Any]) -> bool:
        """Process a single validation request."""
        try:
            request_id = validation_request.get("request_id")
            data_type = validation_request.get("data_type")
            data = validation_request.get("data")
            priority = validation_request.get("priority", "normal")
            
            # Add to active validations
            self.validation_state["active_validations"][request_id] = {
                "data_type": data_type,
                "priority": priority,
                "start_time": time.time(),
                "status": "processing"
            }
            
            # Perform validation
            validation_result = await self._validate_data(data_type, data)
            
            # Update validation state
            self.validation_state["active_validations"][request_id]["status"] = "completed"
            self.validation_state["active_validations"][request_id]["result"] = validation_result
            
            # Add to validation history
            self.validation_state["validation_history"].append({
                "request_id": request_id,
                "data_type": data_type,
                "priority": priority,
                "result": validation_result,
                "timestamp": time.time()
            })
            
            # Update statistics
            if validation_result.get("valid", False):
                self.stats["successful_validations"] += 1
            else:
                self.stats["failed_validations"] += 1
            
            # Publish validation result
            await self._publish_validation_result(request_id, validation_result)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing validation request: {e}")
            return False
    
    async def _validate_data(self, data_type: str, data: Any) -> Dict[str, Any]:
        """Validate data based on type."""
        try:
            if not self.data_validator:
                return await self._fallback_validation(data_type, data)
            
            # Use data validator for validation
            validation_result = await self.data_validator.validate(data_type, data)
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
            return {
                "valid": False,
                "error": str(e),
                "data_type": data_type,
                "timestamp": time.time()
            }
    
    async def _fallback_validation(self, data_type: str, data: Any) -> Dict[str, Any]:
        """Fallback validation when data validator is not available."""
        try:
            # Basic validation checks
            if data is None:
                return {
                    "valid": False,
                    "error": "Data is None",
                    "data_type": data_type,
                    "timestamp": time.time()
                }
            
            # Type-specific validation
            if data_type == "price_data":
                return await self._validate_price_data(data)
            elif data_type == "order_data":
                return await self._validate_order_data(data)
            elif data_type == "market_data":
                return await self._validate_market_data(data)
            else:
                return {
                    "valid": True,
                    "data_type": data_type,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            self.logger.error(f"Error in fallback validation: {e}")
            return {
                "valid": False,
                "error": str(e),
                "data_type": data_type,
                "timestamp": time.time()
            }
    
    async def _validate_price_data(self, data: Any) -> Dict[str, Any]:
        """Validate price data."""
        try:
            if not isinstance(data, dict):
                return {
                    "valid": False,
                    "error": "Price data must be a dictionary",
                    "timestamp": time.time()
                }
            
            required_fields = ["symbol", "price", "timestamp"]
            for field in required_fields:
                if field not in data:
                    return {
                        "valid": False,
                        "error": f"Missing required field: {field}",
                        "timestamp": time.time()
                    }
            
            # Validate price is numeric and positive
            if not isinstance(data["price"], (int, float)) or data["price"] <= 0:
                return {
                    "valid": False,
                    "error": "Price must be a positive number",
                    "timestamp": time.time()
                }
            
            return {
                "valid": True,
                "data_type": "price_data",
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _validate_order_data(self, data: Any) -> Dict[str, Any]:
        """Validate order data."""
        try:
            if not isinstance(data, dict):
                return {
                    "valid": False,
                    "error": "Order data must be a dictionary",
                    "timestamp": time.time()
                }
            
            required_fields = ["symbol", "side", "volume", "order_type"]
            for field in required_fields:
                if field not in data:
                    return {
                        "valid": False,
                        "error": f"Missing required field: {field}",
                        "timestamp": time.time()
                    }
            
            # Validate side
            if data["side"] not in ["buy", "sell"]:
                return {
                    "valid": False,
                    "error": "Side must be 'buy' or 'sell'",
                    "timestamp": time.time()
                }
            
            # Validate volume
            if not isinstance(data["volume"], (int, float)) or data["volume"] <= 0:
                return {
                    "valid": False,
                    "error": "Volume must be a positive number",
                    "timestamp": time.time()
                }
            
            return {
                "valid": True,
                "data_type": "order_data",
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _validate_market_data(self, data: Any) -> Dict[str, Any]:
        """Validate market data."""
        try:
            if not isinstance(data, dict):
                return {
                    "valid": False,
                    "error": "Market data must be a dictionary",
                    "timestamp": time.time()
                }
            
            # Basic market data validation
            if "symbol" not in data:
                return {
                    "valid": False,
                    "error": "Missing symbol field",
                    "timestamp": time.time()
                }
            
            return {
                "valid": True,
                "data_type": "market_data",
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    # ============= DATA QUALITY MONITORING LOOP =============
    
    async def _data_quality_monitoring_loop(self):
        """Data quality monitoring loop (30s intervals)."""
        while self.is_running:
            try:
                if self.data_quality_monitor:
                    # Monitor data quality
                    quality_metrics = await self.data_quality_monitor.get_quality_metrics()
                    
                    # Update validation state
                    self.validation_state["data_quality_score"] = quality_metrics.get("overall_score", 1.0)
                    
                    # Check for quality issues
                    await self._check_data_quality_issues(quality_metrics)
                    
                    # Publish quality update
                    await self._publish_quality_update(quality_metrics)
                
                await asyncio.sleep(30)  # 30s quality monitoring cycle
                
            except Exception as e:
                self.logger.error(f"Error in data quality monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _check_data_quality_issues(self, quality_metrics: Dict[str, Any]):
        """Check for data quality issues."""
        try:
            overall_score = quality_metrics.get("overall_score", 1.0)
            
            if overall_score < 0.8:
                self.stats["data_quality_issues"] += 1
                self.logger.warning(f"Data quality degraded: {overall_score}")
                
                # Publish quality alert
                await self._publish_quality_alert(quality_metrics)
                
        except Exception as e:
            self.logger.error(f"Error checking data quality issues: {e}")
    
    # ============= VALIDATION AUDIT LOOP =============
    
    async def _validation_audit_loop(self):
        """Validation audit loop (5min intervals)."""
        while self.is_running:
            try:
                # Perform validation audit
                audit_results = await self._perform_validation_audit()
                
                # Publish audit report
                await self._publish_validation_audit(audit_results)
                
                # Update comprehensive stats
                self._update_comprehensive_stats()
                
                await asyncio.sleep(300)  # 5min audit cycle
                
            except Exception as e:
                self.logger.error(f"Error in validation audit loop: {e}")
                await asyncio.sleep(300)
    
    async def _perform_validation_audit(self) -> Dict[str, Any]:
        """Perform comprehensive validation audit."""
        try:
            audit_results = {
                "timestamp": time.time(),
                "total_validations": self.stats["data_validations"],
                "success_rate": self.stats["successful_validations"] / max(self.stats["data_validations"], 1),
                "data_quality_score": self.validation_state["data_quality_score"],
                "active_validations": len(self.validation_state["active_validations"]),
                "validation_history_size": len(self.validation_state["validation_history"])
            }
            
            return audit_results
            
        except Exception as e:
            self.logger.error(f"Error performing validation audit: {e}")
            return {"error": str(e), "timestamp": time.time()}
    
    # ============= UTILITY METHODS =============
    
    def _update_validation_state(self):
        """Update validation state with current information."""
        try:
            # Update validation timestamp
            self.validation_state["last_validation_time"] = time.time()
            
            # Clean up old validation history (keep last 1000)
            if len(self.validation_state["validation_history"]) > 1000:
                self.validation_state["validation_history"] = self.validation_state["validation_history"][-1000:]
                
        except Exception as e:
            self.logger.error(f"Error updating validation state: {e}")
    
    def _update_comprehensive_stats(self):
        """Update comprehensive validation statistics."""
        try:
            # Update comprehensive validation count
            self.stats["comprehensive_validations"] += 1
            
        except Exception as e:
            self.logger.error(f"Error updating comprehensive stats: {e}")
    
    async def _cleanup_validation_components(self):
        """Cleanup validation components."""
        try:
            # Cleanup data validator
            if self.data_validator:
                await self.data_validator.cleanup()
            
            # Cleanup data quality monitor
            if self.data_quality_monitor:
                await self.data_quality_monitor.cleanup()
            
            self.logger.info("✅ Validation components cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up validation components: {e}")
    
    # ============= PUBLISHING METHODS =============
    
    async def _publish_validation_result(self, request_id: str, result: Dict[str, Any]):
        """Publish validation result."""
        try:
            validation_update = {
                "request_id": request_id,
                "result": result,
                "timestamp": time.time()
            }
            
            await self.redis_conn.publish_async("validation:results", json.dumps(validation_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing validation result: {e}")
    
    async def _publish_quality_update(self, quality_metrics: Dict[str, Any]):
        """Publish data quality update."""
        try:
            quality_update = {
                "quality_metrics": quality_metrics,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("validation:quality_updates", json.dumps(quality_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing quality update: {e}")
    
    async def _publish_quality_alert(self, quality_metrics: Dict[str, Any]):
        """Publish data quality alert."""
        try:
            quality_alert = {
                "alert_type": "data_quality_degraded",
                "quality_metrics": quality_metrics,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("validation:quality_alerts", json.dumps(quality_alert))
            
        except Exception as e:
            self.logger.error(f"Error publishing quality alert: {e}")
    
    async def _publish_validation_audit(self, audit_results: Dict[str, Any]):
        """Publish validation audit report."""
        try:
            audit_report = {
                "audit_results": audit_results,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("validation:audit_reports", json.dumps(audit_report))
            
        except Exception as e:
            self.logger.error(f"Error publishing validation audit: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def submit_validation_request(self, data_type: str, data: Any, priority: str = "normal") -> str:
        """Submit a validation request."""
        try:
            request_id = f"val_{int(time.time() * 1000)}_{len(self.validation_state['validation_history'])}"
            
            validation_request = {
                "request_id": request_id,
                "data_type": data_type,
                "data": data,
                "priority": priority,
                "timestamp": time.time()
            }
            
            # Add to appropriate priority queue
            if priority == "high":
                self.validation_queue["high_priority"].append(validation_request)
            elif priority == "low":
                self.validation_queue["low_priority"].append(validation_request)
            else:
                self.validation_queue["normal_priority"].append(validation_request)
            
            self.logger.info(f"Validation request submitted: {request_id} ({priority} priority)")
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error submitting validation request: {e}")
            return ""
    
    async def get_validation_status(self, request_id: str) -> Dict[str, Any]:
        """Get validation status for a specific request."""
        try:
            if request_id in self.validation_state["active_validations"]:
                return self.validation_state["active_validations"][request_id]
            else:
                # Check validation history
                for validation in self.validation_state["validation_history"]:
                    if validation["request_id"] == request_id:
                        return validation
                
                return {"error": "Request not found"}
                
        except Exception as e:
            self.logger.error(f"Error getting validation status: {e}")
            return {"error": str(e)}
    
    async def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return {
            "stats": self.stats,
            "validation_state": self.validation_state,
            "queue_status": {
                "high_priority": len(self.validation_queue["high_priority"]),
                "normal_priority": len(self.validation_queue["normal_priority"]),
                "low_priority": len(self.validation_queue["low_priority"])
            },
            "last_update": time.time()
        }
