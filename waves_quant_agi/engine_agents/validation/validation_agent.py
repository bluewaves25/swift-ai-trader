#!/usr/bin/env python3
"""
Validation Agent
Main entry point for the validation module that coordinates Rust validation with Python learning.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import redis
from .python_bridge import ValidationBridge
from .logs.validations_logger import ValidationsLogger

class ValidationAgent:
    """Main validation agent that coordinates Rust validation with Python learning layer."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = self._init_redis()
        self.logger = ValidationsLogger("validation_agent", self.redis_client)
        
        # Initialize Python bridge
        self.bridge = ValidationBridge(config)
        
        # Agent state
        self.is_running = False
        self.start_time = time.time()
        
        # Performance tracking
        self.stats = {
            "validations_processed": 0,
            "learning_updates": 0,
            "external_validations": 0,
            "errors": 0
        }

    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            redis_url = self.config.get("redis_url", "redis://localhost:6379")
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            return client
        except Exception as e:
            print(f"Failed to initialize Redis: {e}")
            return None

    async def start(self):
        """Start the validation agent."""
        try:
            self.logger.log("Starting Validation Agent...", "info")
            self.is_running = True
            
            # Start the Python bridge
            await self.bridge.start()
            
            # Start monitoring loop
            await self._monitoring_loop()
            
        except Exception as e:
            self.logger.log_error(f"Error starting validation agent: {e}")
            await self.stop()

    async def stop(self):
        """Stop the validation agent gracefully."""
        self.logger.log("Stopping Validation Agent...", "info")
        self.is_running = False
        await self.bridge.stop()

    async def _monitoring_loop(self):
        """Main monitoring loop for the validation agent."""
        while self.is_running:
            try:
                # Get bridge status
                bridge_status = await self.bridge.get_bridge_status()
                
                # Update agent statistics
                self._update_stats(bridge_status)
                
                # Report agent status
                await self._report_agent_status()
                
                await asyncio.sleep(self.config.get("monitoring_interval", 5))
                
            except Exception as e:
                self.logger.log_error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)

    def _update_stats(self, bridge_status: Dict[str, Any]):
        """Update agent statistics from bridge status."""
        if bridge_status:
            self.stats["validations_processed"] = bridge_status.get("validations_processed", 0)
            self.stats["learning_updates"] = bridge_status.get("learning_updates", 0)
            self.stats["external_validations"] = bridge_status.get("external_validations", 0)
            self.stats["errors"] = bridge_status.get("errors", 0)

    async def _report_agent_status(self):
        """Report agent status to Redis."""
        try:
            uptime = time.time() - self.start_time
            
            status_report = {
                "agent_type": "validation_agent",
                "is_running": self.is_running,
                "uptime_seconds": uptime,
                "stats": self.stats,
                "redis_connected": self.redis_client is not None,
                "bridge_running": self.bridge.is_running,
                "timestamp": time.time()
            }
            
            # Store status in Redis
            if self.redis_client:
                self.redis_client.hset("validation:agent_status", mapping=status_report)
            
            # Log status
            self.logger.log("agent_status", status_report)
            
        except Exception as e:
            self.logger.log_error(f"Error reporting agent status: {e}")

    async def send_validation_request(self, request: Dict[str, Any]) -> bool:
        """Send a validation request to the validation system."""
        try:
            return await self.bridge.send_validation_request(request)
        except Exception as e:
            self.logger.log_error(f"Error sending validation request: {e}")
            return False

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        uptime = time.time() - self.start_time
        
        return {
            "agent_type": "validation_agent",
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "stats": self.stats,
            "redis_connected": self.redis_client is not None,
            "bridge_running": self.bridge.is_running,
            "timestamp": time.time()
        }

    async def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return {
            "validations_processed": self.stats["validations_processed"],
            "learning_updates": self.stats["learning_updates"],
            "external_validations": self.stats["external_validations"],
            "errors": self.stats["errors"],
            "success_rate": (self.stats["validations_processed"] - self.stats["errors"]) / max(self.stats["validations_processed"], 1),
            "timestamp": time.time()
        }
