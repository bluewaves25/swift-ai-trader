#!/usr/bin/env python3
"""
Python Bridge for Rust Execution Agent
Integrates Rust-based execution with Python learning layer and other agents.
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

class ExecutionBridge:
    """Bridge between Rust execution agent and Python learning layer."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize shared utilities (eliminates duplication)
        self.redis_client = get_shared_redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0)
        )
        self.logger = get_shared_logger("execution", "bridge")
        self.learner = get_agent_learner("execution", LearningType.EXECUTION_OPTIMIZATION, 5)
        
        # Performance tracking
        self.stats = {
            "total_signals_processed": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "learning_updates": 0,
            "start_time": time.time()
        }
        
        # Signal processing state
        self.is_running = False



    async def start(self):
        """Start the execution bridge."""
        try:
            self.logger.info("Starting Execution Bridge...")
            self.is_running = True
            
            # Start signal processing loop
            await self._signal_processing_loop()
            
        except Exception as e:
            self.logger.error(f"Error starting execution bridge: {e}")
            await self.stop()

    async def stop(self):
        """Stop the execution bridge gracefully."""
        self.logger.info("Stopping Execution Bridge...")
        self.is_running = False

    async def _signal_processing_loop(self):
        """Main loop for processing trading signals."""
        while self.is_running:
            try:
                # Get signals from Redis
                signals = await self._get_pending_signals()
                
                for signal in signals:
                    await self._process_signal(signal)
                
                # Update learning models periodically
                await self._update_learning_models()
                
                # Report statistics
                await self._report_stats()
                
                await asyncio.sleep(self.config.get("signal_processing_interval", 1))
                
            except Exception as e:
                self.logger.log_error(f"Error in signal processing loop: {e}")
                await asyncio.sleep(5)

    async def _get_pending_signals(self) -> List[Dict[str, Any]]:
        """Get pending trading signals from Redis."""
        try:
            if not self.redis_client:
                return []
            
            # Get signals from Redis queue
            signals = []
            for _ in range(10):  # Process up to 10 signals per cycle
                signal_data = self.redis_client.lpop("execution:signals")
                if signal_data:
                    try:
                        signal = json.loads(signal_data)
                        signals.append(signal)
                    except json.JSONDecodeError as e:
                        self.logger.log_error(f"Invalid signal format: {e}")
                        continue
                else:
                    break
            
            return signals
            
        except Exception as e:
            self.logger.log_error(f"Error getting pending signals: {e}")
            return []

    async def _process_signal(self, signal: Dict[str, Any]):
        """Process a single trading signal."""
        try:
            self.stats["total_signals_processed"] += 1
            
            # Extract signal data
            symbol = signal.get("symbol", "")
            signal_type = signal.get("signal", "")
            size = signal.get("size", 0.0)
            expected_price = signal.get("expected_price", 0.0)
            
            # Validate signal
            if not self._validate_signal(signal):
                self.logger.log_error(f"Invalid signal: {signal}")
                return
            
            # Send to Rust execution agent via Redis
            execution_request = {
                "symbol": symbol,
                "signal": signal_type,
                "size": size,
                "expected_price": expected_price,
                "timestamp": time.time(),
                "source": "python_bridge"
            }
            
            # Publish to Rust execution agent
            if self.redis_client:
                self.redis_client.publish("rust_execution:signals", json.dumps(execution_request))
            
            self.logger.log_execution("signal_processed", {
                "symbol": symbol,
                "signal": signal_type,
                "size": size,
                "description": f"Signal sent to Rust execution agent"
            })
            
        except Exception as e:
            self.logger.log_error(f"Error processing signal: {e}")

    def _validate_signal(self, signal: Dict[str, Any]) -> bool:
        """Validate trading signal."""
        required_fields = ["symbol", "signal", "size"]
        
        for field in required_fields:
            if field not in signal:
                return False
        
        if signal["signal"] not in ["BUY", "SELL"]:
            return False
        
        if signal["size"] <= 0:
            return False
        
        if not signal["symbol"]:
            return False
        
        return True

    async def _update_learning_models(self):
        """Update learning models with execution data."""
        try:
            # Get execution data from Redis
            execution_data = await self._get_execution_data()
            
            if execution_data and len(execution_data) > 0:
                # Convert to DataFrame for training
                df = pd.DataFrame(execution_data)
                
                # Train models
                models = await self.training_module.train_execution_model(df)
                
                if models:
                    self.stats["learning_updates"] += 1
                    self.logger.log_execution("model_training", {
                        "models_trained": len(models),
                        "description": f"Updated {len(models)} execution models"
                    })
                    
                    # Send model updates to Rust agent
                    await self._send_model_updates(models)
            
        except Exception as e:
            self.logger.log_error(f"Error updating learning models: {e}")

    async def _get_execution_data(self) -> List[Dict[str, Any]]:
        """Get execution data from Redis for training."""
        try:
            if not self.redis_client:
                return []
            
            # Get recent execution results
            execution_keys = self.redis_client.keys("execution:orders:*")
            execution_data = []
            
            for key in execution_keys[:100]:  # Limit to 100 recent executions
                try:
                    data = self.redis_client.hgetall(key)
                    if data:
                        # Parse execution data
                        execution_record = {
                            "symbol": data.get("symbol", ""),
                            "signal": data.get("signal", ""),
                            "size": float(data.get("size", 0)),
                            "latency_ms": float(data.get("latency_ms", 0)),
                            "success": data.get("success", "false").lower() == "true",
                            "timestamp": int(data.get("timestamp", 0))
                        }
                        execution_data.append(execution_record)
                except Exception as e:
                    self.logger.log_error(f"Error parsing execution data: {e}")
                    continue
            
            return execution_data
            
        except Exception as e:
            self.logger.log_error(f"Error getting execution data: {e}")
            return []

    async def _send_model_updates(self, models: List[Dict[str, Any]]):
        """Send model updates to Rust execution agent."""
        try:
            if not self.redis_client:
                return
            
            for model in models:
                # Send model parameters to Rust agent
                model_update = {
                    "type": "model_update",
                    "symbol": model.get("symbol", ""),
                    "accuracy": model.get("accuracy", 0),
                    "model_version": model.get("model_version", ""),
                    "timestamp": time.time()
                }
                
                self.redis_client.publish("rust_execution:model_updates", json.dumps(model_update))
            
            self.logger.log_execution("model_update", {
                "models_sent": len(models),
                "description": f"Sent {len(models)} model updates to Rust agent"
            })
            
        except Exception as e:
            self.logger.log_error(f"Error sending model updates: {e}")

    async def _report_stats(self):
        """Report bridge statistics."""
        try:
            uptime = time.time() - self.stats["start_time"]
            
            stats_report = {
                "uptime_seconds": uptime,
                "total_signals_processed": self.stats["total_signals_processed"],
                "successful_executions": self.stats["successful_executions"],
                "failed_executions": self.stats["failed_executions"],
                "learning_updates": self.stats["learning_updates"],
                "signals_per_second": self.stats["total_signals_processed"] / max(uptime, 1),
                "timestamp": time.time()
            }
            
            # Store stats in Redis
            if self.redis_client:
                self.redis_client.hset("execution:bridge_stats", mapping=stats_report)
            
            # Log metrics
            self.logger.log_metric("signals_processed", self.stats["total_signals_processed"])
            self.logger.log_metric("learning_updates", self.stats["learning_updates"])
            
        except Exception as e:
            self.logger.log_error(f"Error reporting stats: {e}")

    async def get_bridge_status(self) -> Dict[str, Any]:
        """Get current bridge status."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "stats": self.stats,
            "redis_connected": self.redis_client is not None
        }

    async def send_signal(self, signal: Dict[str, Any]) -> bool:
        """Send a trading signal to the execution system."""
        try:
            if not self._validate_signal(signal):
                self.logger.log_error(f"Invalid signal format: {signal}")
                return False
            
            # Add to Redis queue
            if self.redis_client:
                self.redis_client.rpush("execution:signals", json.dumps(signal))
                self.logger.log_execution("signal_sent", {
                    "symbol": signal.get("symbol", ""),
                    "signal": signal.get("signal", ""),
                    "description": "Signal added to execution queue"
                })
                return True
            
            return False
            
        except Exception as e:
            self.logger.log_error(f"Error sending signal: {e}")
            return False 