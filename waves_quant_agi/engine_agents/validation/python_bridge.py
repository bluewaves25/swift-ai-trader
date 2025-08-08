#!/usr/bin/env python3
"""
Python Bridge for Validation Agent
Integrates Python learning layer with Rust validation core
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import redis
import pandas as pd
from .learning_layer.hybrid_training.external_strategy_validator import ExternalStrategyValidator
from .learning_layer.internal.validation_learning import ValidationLearning
from .logs.validations_logger import ValidationsLogger

class ValidationBridge:
    """Bridge between Rust validation agent and Python learning layer."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = self._init_redis()
        self.logger = ValidationsLogger("validation_bridge", self.redis_client)
        
        # Initialize learning components
        self.external_validator = ExternalStrategyValidator(config.get("external_validation", {}))
        self.validation_learning = ValidationLearning(config.get("learning", {}))
        
        self.stats = {
            "validations_processed": 0,
            "learning_updates": 0,
            "external_validations": 0,
            "errors": 0,
            "start_time": time.time()
        }
        self.is_running = False

    def _init_redis(self) -> redis.Redis:
        """Initialize Redis connection."""
        try:
            redis_url = self.config.get("redis_url", "redis://localhost:6379")
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            self.logger.log("Redis connection established", "info")
            return client
        except Exception as e:
            self.logger.log_error(f"Failed to connect to Redis: {e}")
            raise

    async def start(self):
        """Start the validation bridge."""
        self.is_running = True
        self.logger.log("Validation bridge started", "info")
        
        # Start background tasks
        asyncio.create_task(self._validation_processing_loop())
        asyncio.create_task(self._learning_update_loop())
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

    async def _learning_update_loop(self):
        """Update learning models based on validation results."""
        while self.is_running:
            try:
                # Get validation data for learning
                validation_data = await self._get_validation_data()
                
                if validation_data:
                    await self._update_learning_models(validation_data)
                    self.stats["learning_updates"] += 1
                
                await asyncio.sleep(5)  # 5 second intervals
                
            except Exception as e:
                self.logger.log_error(f"Error in learning update loop: {e}")
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
            
            # Send to learning layer if validation failed
            if status != "valid":
                await self._send_to_learning(result)
            
        except Exception as e:
            self.logger.log_error(f"Error processing validation result: {e}")

    async def _get_validation_data(self) -> List[Dict[str, Any]]:
        """Get validation data for learning."""
        try:
            # Get validation data from Redis
            data = []
            raw_data = self.redis_client.lrange("validation:learning_data", 0, 99)  # Get last 100 entries
            
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

    async def _update_learning_models(self, validation_data: List[Dict[str, Any]]):
        """Update learning models with validation data."""
        try:
            if not validation_data:
                return
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(validation_data)
            
            # Update learning models
            await self.validation_learning.update_models(df)
            
            # Log learning update
            self.logger.log_learning(
                "model_update",
                {
                    "data_points": len(validation_data),
                    "models_updated": True,
                    "timestamp": time.time()
                }
            )
            
        except Exception as e:
            self.logger.log_error(f"Error updating learning models: {e}")

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

    async def _send_to_learning(self, validation_result: Dict[str, Any]):
        """Send validation result to learning layer."""
        try:
            # Add to learning data queue
            self.redis_client.lpush(
                "validation:learning_data",
                json.dumps(validation_result)
            )
            
            # Keep only last 1000 entries
            self.redis_client.ltrim("validation:learning_data", 0, 999)
            
        except Exception as e:
            self.logger.log_error(f"Error sending to learning: {e}")

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
        "learning": {
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
