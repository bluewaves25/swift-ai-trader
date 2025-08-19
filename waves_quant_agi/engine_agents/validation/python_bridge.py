#!/usr/bin/env python3
"""
Python Bridge for Validation Agent
Integrates Python learning layer with Rust validation core
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import pandas as pd
from engine_agents.shared_utils import (
    get_shared_redis,
    get_shared_logger,
    get_agent_learner,
    LearningType
)

class ValidationBridge:
    """Bridge between Rust validation agent and Python learning layer."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize shared utilities (eliminates duplication)
        self.redis_client = get_shared_redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0)
        )
        self.logger = get_shared_logger("validation", "bridge")
        # Removed learning functionality - now handled by Strategy Engine
        
        self.stats = {
            "validations_processed": 0,
            "validation_improvements": 0,
            "external_validations": 0,
            "errors": 0,
            "start_time": time.time()
        }
        self.is_running = False

    # _init_redis method removed - now using shared Redis connection from shared_utils

    async def start(self):
        """Start the validation bridge."""
        self.is_running = True
        self.logger.log("Validation bridge started", "info")
        
        # Start background tasks
        asyncio.create_task(self._validation_processing_loop())
        asyncio.create_task(self._validation_improvement_loop())
        asyncio.create_task(self._external_validation_loop())
        asyncio.create_task(self._stats_reporting_loop())

    async def stop(self):
        """Stop the validation bridge."""
        self.is_running = False
        self.logger.log("Validation bridge stopped", "info")

    async def _validation_processing_loop(self):
        """Process validation results from Rust core."""
        while self.is_running:
            try:
                # Get validation results from Redis
                validation_results = await self._get_validation_results()
                
                for result in validation_results:
                    await self._process_validation_result(result)
                    self.stats["validations_processed"] += 1
                
                await asyncio.sleep(0.1)  # 100ms polling
                
            except Exception as e:
                self.logger.log_error(f"Error in validation processing loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(1)

    async def _validation_improvement_loop(self):
        """Improve validation rules based on validation results."""
        while self.is_running:
            try:
                # Get validation data for improvement
                validation_data = await self._get_validation_data()
                
                if validation_data:
                    await self._improve_validation_rules(validation_data)
                    self.stats["validation_improvements"] += 1
                
                await asyncio.sleep(5)  # 5 second intervals
                
            except Exception as e:
                self.logger.log_error(f"Error in validation improvement loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(5)

    async def _external_validation_loop(self):
        """Process external validation requests."""
        while self.is_running:
            try:
                # Get external validation requests
                external_requests = await self._get_external_validation_requests()
                
                for request in external_requests:
                    await self._process_external_validation(request)
                    self.stats["external_validations"] += 1
                
                await asyncio.sleep(1)  # 1 second polling
                
            except Exception as e:
                self.logger.log_error(f"Error in external validation loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(5)

    async def _stats_reporting_loop(self):
        """Report statistics to Redis."""
        while self.is_running:
            try:
                await self._report_stats()
                await asyncio.sleep(30)  # Report every 30 seconds
            except Exception as e:
                self.logger.log_error(f"Error in stats reporting loop: {e}")
                await asyncio.sleep(30)

    async def _get_validation_results(self) -> List[Dict[str, Any]]:
        """Get validation results from Redis."""
        try:
            # Get results from validation_output channel
            results = []
            raw_results = self.redis_client.lrange("validation:results", 0, 9)  # Get last 10 results
            
            for raw_result in raw_results:
                try:
                    result = json.loads(raw_result)
                    results.append(result)
                except json.JSONDecodeError:
                    continue
            
            return results
        except Exception as e:
            self.logger.log_error(f"Error getting validation results: {e}")
            return []

    async def _process_validation_result(self, result: Dict[str, Any]):
        """Process a validation result."""
        try:
            validation_type = result.get("type", "unknown")
            status = result.get("status", "unknown")
            
            # Log validation result
            self.logger.log_validation_summary(
                "validation_result",
                {
                    "type": validation_type,
                    "status": status,
                    "details": result.get("details", {}),
                    "timestamp": time.time()
                }
            )
            
            # Store validation result for improvement analysis
            if status != "valid":
                await self._store_validation_result(result)
            
        except Exception as e:
            self.logger.log_error(f"Error processing validation result: {e}")

    async def _get_validation_data(self) -> List[Dict[str, Any]]:
        """Get validation data for improvement analysis."""
        try:
            # Get validation data from Redis
            data = []
            raw_data = self.redis_client.lrange("validation:improvement_data", 0, 99)  # Get last 100 entries
            
            for raw_entry in raw_data:
                try:
                    entry = json.loads(raw_entry)
                    data.append(entry)
                except json.JSONDecodeError:
                    continue
            
            return data
        except Exception as e:
            self.logger.log_error(f"Error getting validation data: {e}")
            return []

    async def _improve_validation_rules(self, validation_data: List[Dict[str, Any]]):
        """Improve validation rules based on validation data."""
        try:
            if not validation_data:
                return
            
            # Analyze validation data for improvement opportunities
            failed_validations = [d for d in validation_data if d.get("status") != "valid"]
            
            if failed_validations:
                # Identify common failure patterns
                failure_patterns = await self._analyze_failure_patterns(failed_validations)
                
                # Apply validation rule improvements
                await self._apply_validation_improvements(failure_patterns)
                
                # Log validation improvement
                self.logger.log_validation_summary(
                    "validation_improvement",
                    {
                        "failed_validations": len(failed_validations),
                        "patterns_identified": len(failure_patterns),
                        "improvements_applied": True,
                        "timestamp": time.time()
                    }
                )
            
        except Exception as e:
            self.logger.log_error(f"Error improving validation rules: {e}")
    
    async def _analyze_failure_patterns(self, failed_validations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze failed validations to identify common patterns."""
        try:
            patterns = []
            
            # Group failures by type
            failure_types = {}
            for validation in failed_validations:
                failure_type = validation.get("failure_type", "unknown")
                if failure_type not in failure_types:
                    failure_types[failure_type] = []
                failure_types[failure_type].append(validation)
            
            # Identify patterns in each failure type
            for failure_type, validations in failure_types.items():
                if len(validations) >= 3:  # Minimum threshold for pattern
                    pattern = {
                        "failure_type": failure_type,
                        "frequency": len(validations),
                        "common_attributes": self._extract_common_attributes(validations),
                        "suggested_improvement": self._suggest_improvement(failure_type)
                    }
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.log_error(f"Error analyzing failure patterns: {e}")
            return []
    
    async def _apply_validation_improvements(self, failure_patterns: List[Dict[str, Any]]):
        """Apply validation rule improvements based on failure patterns."""
        try:
            for pattern in failure_patterns:
                improvement_type = pattern.get("suggested_improvement", {}).get("type")
                
                if improvement_type == "threshold_adjustment":
                    await self._adjust_validation_threshold(pattern)
                elif improvement_type == "rule_addition":
                    await self._add_validation_rule(pattern)
                elif improvement_type == "rule_modification":
                    await self._modify_validation_rule(pattern)
            
        except Exception as e:
            self.logger.log_error(f"Error applying validation improvements: {e}")
    
    def _extract_common_attributes(self, validations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common attributes from failed validations."""
        try:
            if not validations:
                return {}
            
            # Analyze common fields
            common_attrs = {}
            for field in ["data_type", "source", "size", "format"]:
                values = [v.get(field) for v in validations if v.get(field)]
                if values:
                    # Find most common value
                    from collections import Counter
                    counter = Counter(values)
                    common_attrs[field] = counter.most_common(1)[0][0]
            
            return common_attrs
            
        except Exception as e:
            self.logger.log_error(f"Error extracting common attributes: {e}")
            return {}
    
    def _suggest_improvement(self, failure_type: str) -> Dict[str, Any]:
        """Suggest improvement based on failure type."""
        try:
            improvements = {
                "data_quality": {
                    "type": "threshold_adjustment",
                    "description": "Adjust data quality thresholds"
                },
                "format_validation": {
                    "type": "rule_addition",
                    "description": "Add format validation rules"
                },
                "size_validation": {
                    "type": "rule_modification",
                    "description": "Modify size validation rules"
                }
            }
            
            return improvements.get(failure_type, {
                "type": "general_improvement",
                "description": "General validation improvement"
            })
            
        except Exception as e:
            self.logger.log_error(f"Error suggesting improvement: {e}")
            return {"type": "unknown", "description": "Unknown improvement"}
    
    async def _adjust_validation_threshold(self, pattern: Dict[str, Any]):
        """Adjust validation threshold based on pattern."""
        try:
            # Implementation for threshold adjustment
            self.logger.log_validation_summary("threshold_adjusted", pattern)
        except Exception as e:
            self.logger.log_error(f"Error adjusting validation threshold: {e}")
    
    async def _add_validation_rule(self, pattern: Dict[str, Any]):
        """Add new validation rule based on pattern."""
        try:
            # Implementation for adding validation rule
            self.logger.log_validation_summary("rule_added", pattern)
        except Exception as e:
            self.logger.log_error(f"Error adding validation rule: {e}")
    
    async def _modify_validation_rule(self, pattern: Dict[str, Any]):
        """Modify existing validation rule based on pattern."""
        try:
            # Implementation for modifying validation rule
            self.logger.log_validation_summary("rule_modified", pattern)
        except Exception as e:
            self.logger.log_error(f"Error modifying validation rule: {e}")

    async def _get_external_validation_requests(self) -> List[Dict[str, Any]]:
        """Get external validation requests from Redis."""
        try:
            requests = []
            raw_requests = self.redis_client.lrange("validation:external_requests", 0, 9)  # Get last 10 requests
            
            for raw_request in raw_requests:
                try:
                    request = json.loads(raw_request)
                    requests.append(request)
                except json.JSONDecodeError:
                    continue
            
            return requests
        except Exception as e:
            self.logger.log_error(f"Error getting external validation requests: {e}")
            return []

    async def _process_external_validation(self, request: Dict[str, Any]):
        """Process external validation request."""
        try:
            strategy_id = request.get("strategy_id")
            strategy_data = request.get("strategy_data", {})
            
            # Perform external validation
            validation_result = await self.external_validator.validate_strategy(
                strategy_id, strategy_data
            )
            
            # Store result in Redis
            result_key = f"validation:external:{strategy_id}"
            self.redis_client.setex(
                result_key, 
                3600,  # 1 hour TTL
                json.dumps(validation_result)
            )
            
            # Log external validation
            self.logger.log_strategy_validation(
                strategy_id,
                {
                    "type": "external",
                    "result": validation_result,
                    "timestamp": time.time()
                }
            )
            
        except Exception as e:
            self.logger.log_error(f"Error processing external validation: {e}")

    async def _store_validation_result(self, validation_result: Dict[str, Any]):
        """Store validation result for improvement analysis."""
        try:
            # Add to improvement data queue
            self.redis_client.lpush(
                "validation:improvement_data",
                json.dumps(validation_result)
            )
            
            # Keep only last 1000 entries
            self.redis_client.ltrim("validation:improvement_data", 0, 999)
            
        except Exception as e:
            self.logger.log_error(f"Error storing validation result: {e}")

    async def _report_stats(self):
        """Report bridge statistics to Redis."""
        try:
            stats = {
                **self.stats,
                "uptime": time.time() - self.stats["start_time"],
                "timestamp": time.time()
            }
            
            # Store stats in Redis
            self.redis_client.hset("validation:bridge:stats", mapping=stats)
            
            # Log stats
            self.logger.log_metric("bridge_stats", len(stats), {"component": "validation_bridge"})
            
        except Exception as e:
            self.logger.log_error(f"Error reporting stats: {e}")

    async def get_bridge_status(self) -> Dict[str, Any]:
        """Get bridge status."""
        return {
            "is_running": self.is_running,
            "stats": self.stats,
            "redis_connected": self.redis_client.ping(),
            "uptime": time.time() - self.stats["start_time"]
        }

    async def send_validation_request(self, request: Dict[str, Any]) -> bool:
        """Send validation request to Rust core."""
        try:
            # Send to validation input queue
            self.redis_client.lpush(
                "validation:input",
                json.dumps(request)
            )
            
            self.logger.log_validation_summary(
                "request_sent",
                {
                    "request_type": request.get("type", "unknown"),
                    "timestamp": time.time()
                }
            )
            
            return True
        except Exception as e:
            self.logger.log_error(f"Error sending validation request: {e}")
            return False

if __name__ == "__main__":
    # Test the validation bridge
    config = {
        "redis_url": "redis://localhost:6379",
        "external_validation": {
            "enabled": True,
            "timeout": 30
        },
        "improvement": {
            "enabled": True,
            "update_interval": 5
        }
    }
    
    async def test_bridge():
        bridge = ValidationBridge(config)
        await bridge.start()
        
        # Test for 10 seconds
        await asyncio.sleep(10)
        
        status = await bridge.get_bridge_status()
        print(f"Bridge status: {status}")
        
        await bridge.stop()
    
    asyncio.run(test_bridge())
