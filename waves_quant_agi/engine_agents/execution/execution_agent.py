#!/usr/bin/env python3
"""
Execution Agent
Main entry point for the execution module that coordinates Rust execution with Python learning.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import redis
from .python_bridge import ExecutionBridge
from .logs.execution_logger import ExecutionLogger

class ExecutionAgent:
    """Main execution agent that coordinates Rust execution with Python learning layer."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = self._init_redis()
        self.logger = ExecutionLogger("execution_agent", self.redis_client)
        
        # Initialize Python bridge
        self.bridge = ExecutionBridge(config)
        
        # Agent state
        self.is_running = False
        self.start_time = time.time()
        
        # Performance tracking
        self.stats = {
            "total_signals_processed": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "learning_updates": 0
        }

    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            return redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0),
                decode_responses=True
            )
        except Exception as e:
            print(f"Failed to initialize Redis: {e}")
            return None

    async def start(self):
        """Start the execution agent."""
        try:
            self.logger.log("Starting Execution Agent...")
            self.is_running = True
            
            # Start the Python bridge
            await self.bridge.start()
            
            # Start monitoring loop
            await self._monitoring_loop()
            
        except Exception as e:
            self.logger.log_error(f"Error starting execution agent: {e}")
            await self.stop()

    async def stop(self):
        """Stop the execution agent gracefully."""
        self.logger.log("Stopping Execution Agent...")
        self.is_running = False
        await self.bridge.stop()

    async def _monitoring_loop(self):
        """Main monitoring loop for the execution agent."""
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
            self.stats["total_signals_processed"] = bridge_status.get("stats", {}).get("total_signals_processed", 0)
            self.stats["successful_executions"] = bridge_status.get("stats", {}).get("successful_executions", 0)
            self.stats["failed_executions"] = bridge_status.get("stats", {}).get("failed_executions", 0)
            self.stats["learning_updates"] = bridge_status.get("stats", {}).get("learning_updates", 0)

    async def _report_agent_status(self):
        """Report agent status to Redis."""
        try:
            uptime = time.time() - self.start_time
            
            status_report = {
                "agent_type": "execution_agent",
                "is_running": self.is_running,
                "uptime_seconds": uptime,
                "stats": self.stats,
                "redis_connected": self.redis_client is not None,
                "bridge_running": self.bridge.is_running,
                "timestamp": time.time()
            }
            
            # Store status in Redis
            if self.redis_client:
                self.redis_client.hset("execution:agent_status", mapping=status_report)
            
            # Log status
            self.logger.log_execution("agent_status", status_report)
            
        except Exception as e:
            self.logger.log_error(f"Error reporting agent status: {e}")

    async def send_signal(self, signal: Dict[str, Any]) -> bool:
        """Send a trading signal to the execution system."""
        try:
            return await self.bridge.send_signal(signal)
        except Exception as e:
            self.logger.log_error(f"Error sending signal: {e}")
            return False

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        uptime = time.time() - self.start_time
        
        return {
            "agent_type": "execution_agent",
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "stats": self.stats,
            "redis_connected": self.redis_client is not None,
            "bridge_running": self.bridge.is_running,
            "timestamp": time.time()
        }

    async def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "total_signals_processed": self.stats["total_signals_processed"],
            "successful_executions": self.stats["successful_executions"],
            "failed_executions": self.stats["failed_executions"],
            "learning_updates": self.stats["learning_updates"],
            "success_rate": self.stats["successful_executions"] / max(self.stats["total_signals_processed"], 1),
            "timestamp": time.time()
        }
