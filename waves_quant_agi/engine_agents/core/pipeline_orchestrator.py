#!/usr/bin/env python3
"""
Pipeline Orchestrator - Coordinates the complete trading pipeline flow
Provides real-time visibility into signal and execution processes
"""

import asyncio
import time
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class PipelineOrchestrator:
    """Orchestrates the complete trading pipeline with full visibility."""
    
    def __init__(self, redis_conn, logger):
        """Initialize the pipeline orchestrator."""
        self.redis_conn = redis_conn
        self.logger = logger
        
        # Pipeline state
        self.pipeline_state = {
            "current_phase": "initialization",
            "pipeline_health": 1.0,
            "start_time": time.time(),
            "last_phase_change": time.time()
        }
        
        # Signal tracking
        self.signal_tracker = {
            "active_signals": {},
            "signal_history": [],
            "signal_performance": {},
            "signal_queue": [],
            "processed_signals": 0
        }
        
        # Execution tracking
        self.execution_tracker = {
            "active_orders": {},
            "order_history": [],
            "execution_performance": {},
            "execution_queue": [],
            "processed_orders": 0
        }
        
        # Pipeline metrics
        self.pipeline_metrics = {
            "signals_per_second": 0.0,
            "orders_per_second": 0.0,
            "avg_signal_latency": 0.0,
            "avg_execution_time": 0.0,
            "data_quality_score": 100.0,
            "system_throughput": 0.0
        }
        
        # Performance tracking
        self.performance_tracker = {
            "signal_timings": [],
            "execution_timings": [],
            "phase_durations": {},
            "bottleneck_analysis": {}
        }
        
        # Circuit breakers
        self.circuit_breakers = {
            "signal_processing": {"active": False, "trigger_count": 0, "last_trigger": 0},
            "order_execution": {"active": False, "trigger_count": 0, "last_trigger": 0},
            "data_flow": {"active": False, "trigger_count": 0, "last_trigger": 0}
        }
        
        # Running state
        self.running = False
        self.tasks = []
    
    async def start(self):
        """Start the pipeline orchestrator."""
        try:
            self.running = True
            self.logger.info("🚀 Pipeline Orchestrator starting...")
            
            # Start background tasks
            self.tasks = [
                asyncio.create_task(self._pipeline_coordination_loop()),
                asyncio.create_task(self._signal_tracking_loop()),
                asyncio.create_task(self._execution_tracking_loop()),
                asyncio.create_task(self._performance_monitoring_loop()),
                asyncio.create_task(self._circuit_breaker_monitoring_loop())
            ]
            
            self.logger.info("✅ Pipeline Orchestrator started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting Pipeline Orchestrator: {e}")
            raise
    
    async def stop(self):
        """Stop the pipeline orchestrator."""
        try:
            self.running = False
            self.logger.info("🛑 Pipeline Orchestrator stopping...")
            
            # Cancel all tasks
            for task in self.tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
            self.logger.info("✅ Pipeline Orchestrator stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping Pipeline Orchestrator: {e}")
    
    # ============= PIPELINE COORDINATION =============
    
    async def _pipeline_coordination_loop(self):
        """Main pipeline coordination loop."""
        while self.running:
            try:
                # Update pipeline phase
                await self._update_pipeline_phase()
                
                # Process signal queue
                await self._process_signal_queue()
                
                # Process execution queue
                await self._process_execution_queue()
                
                # Update pipeline metrics
                await self._update_pipeline_metrics()
                
                # Publish pipeline status
                await self._publish_pipeline_status()
                
                await asyncio.sleep(0.1)  # 100ms cycle
                
            except Exception as e:
                self.logger.error(f"Error in pipeline coordination: {e}")
                await asyncio.sleep(1.0)
    
    async def _update_pipeline_phase(self):
        """Update current pipeline phase based on system state."""
        try:
            # Get system health from Redis
            health_data = await self._get_system_health()
            
            # Determine current phase
            if health_data.get("overall_health", 0.0) >= 0.8:
                if self.pipeline_state["current_phase"] == "initialization":
                    self.pipeline_state["current_phase"] = "operational"
                    self.pipeline_state["last_phase_change"] = time.time()
                    self.logger.info("🚀 Pipeline phase changed to: operational")
            elif health_data.get("overall_health", 0.0) < 0.5:
                if self.pipeline_state["current_phase"] == "operational":
                    self.pipeline_state["current_phase"] = "degraded"
                    self.pipeline_state["last_phase_change"] = time.time()
                    self.logger.warning("⚠️ Pipeline phase changed to: degraded")
            
            # Update pipeline health
            self.pipeline_state["pipeline_health"] = health_data.get("overall_health", 1.0)
            
        except Exception as e:
            self.logger.error(f"Error updating pipeline phase: {e}")
    
    async def _process_signal_queue(self):
        """Process signals in the pipeline signal queue."""
        try:
            # Check circuit breaker
            if self.circuit_breakers["signal_processing"]["active"]:
                return
            
            # Process up to 10 signals at a time
            for signal in self.signal_tracker["signal_queue"][:10]:
                # Track signal
                await self._track_signal(signal)
                
                # Route signal to strategy engine
                await self._route_signal_to_strategy(signal)
                
                # Remove processed signal
                self.signal_tracker["signal_queue"].remove(signal)
                self.signal_tracker["processed_signals"] += 1
                
        except Exception as e:
            self.logger.error(f"Error processing signal queue: {e}")
            await self._trigger_circuit_breaker("signal_processing")
    
    async def _process_execution_queue(self):
        """Process orders in the pipeline execution queue."""
        try:
            # Check circuit breaker
            if self.circuit_breakers["order_execution"]["active"]:
                return
            
            # Process up to 5 orders at a time
            for order in self.execution_tracker["execution_queue"][:5]:
                # Track order
                await self._track_execution(order)
                
                # Route order to execution agent
                await self._route_order_to_execution(order)
                
                # Remove processed order
                self.execution_tracker["execution_queue"].remove(order)
                self.execution_tracker["processed_orders"] += 1
                
        except Exception as e:
            self.logger.error(f"Error processing execution queue: {e}")
            await self._trigger_circuit_breaker("order_execution")
    
    # ============= SIGNAL TRACKING =============
    
    async def _signal_tracking_loop(self):
        """Main signal tracking loop."""
        while self.running:
            try:
                # Update signal performance
                await self._update_signal_performance()
                
                # Clean up expired signals
                await self._cleanup_expired_signals()
                
                # Publish signal tracking updates
                await self._publish_signal_tracking()
                
                await asyncio.sleep(0.001)  # 1ms cycle for ultra-fast tracking
                
            except Exception as e:
                self.logger.error(f"Error in signal tracking: {e}")
                await asyncio.sleep(0.1)
    
    async def _track_signal(self, signal_data: Dict[str, Any]):
        """Track a new signal in the signal tracking system."""
        try:
            signal_id = signal_data.get("signal_id", f"signal_{int(time.time() * 1000)}")
            
            # Create tracking record
            tracking_record = {
                **signal_data,
                "signal_id": signal_id,
                "tracking_start": time.time(),
                "status": "created",
                "processing_time": 0.0,
                "phase": "data_input"
            }
            
            # Add to active signals
            self.signal_tracker["active_signals"][signal_id] = tracking_record
            
            # Add to signal history
            self.signal_tracker["signal_history"].append(tracking_record)
            
            # Limit history size
            if len(self.signal_tracker["signal_history"]) > 10000:
                self.signal_tracker["signal_history"] = self.signal_tracker["signal_history"][-5000:]
            
            self.logger.debug(f"Signal tracked: {signal_id}")
            
        except Exception as e:
            self.logger.error(f"Error tracking signal: {e}")
    
    async def _update_signal_performance(self):
        """Update signal performance metrics."""
        try:
            current_time = time.time()
            
            for signal_id, signal in self.signal_tracker["active_signals"].items():
                # Calculate processing time
                if signal["status"] in ["created", "processing", "validated"]:
                    signal["processing_time"] = current_time - signal["tracking_start"]
                
                # Update performance metrics
                if signal_id not in self.signal_tracker["signal_performance"]:
                    self.signal_tracker["signal_performance"][signal_id] = {
                        "total_processing_time": 0.0,
                        "phase_durations": {},
                        "last_update": current_time
                    }
                
                self.signal_tracker["signal_performance"][signal_id]["last_update"] = current_time
                
        except Exception as e:
            self.logger.error(f"Error updating signal performance: {e}")
    
    async def _cleanup_expired_signals(self):
        """Clean up expired signals from active tracking."""
        try:
            current_time = time.time()
            expired_signals = []
            
            for signal_id, signal in self.signal_tracker["active_signals"].items():
                # Check if signal is expired (older than 1 hour)
                if current_time - signal["tracking_start"] > 3600:
                    expired_signals.append(signal_id)
            
            # Remove expired signals
            for signal_id in expired_signals:
                del self.signal_tracker["active_signals"][signal_id]
                if signal_id in self.signal_tracker["signal_performance"]:
                    del self.signal_tracker["signal_performance"][signal_id]
            
            if expired_signals:
                self.logger.debug(f"Cleaned up {len(expired_signals)} expired signals")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up expired signals: {e}")
    
    # ============= EXECUTION TRACKING =============
    
    async def _execution_tracking_loop(self):
        """Main execution tracking loop."""
        while self.running:
            try:
                # Update execution performance
                await self._update_execution_performance()
                
                # Clean up completed orders
                await self._cleanup_completed_orders()
                
                # Publish execution tracking updates
                await self._publish_execution_tracking()
                
                await asyncio.sleep(0.1)  # 100ms cycle for execution tracking
                
            except Exception as e:
                self.logger.error(f"Error in execution tracking: {e}")
                await asyncio.sleep(1.0)
    
    async def _track_execution(self, order_data: Dict[str, Any]):
        """Track a new order in the execution tracking system."""
        try:
            order_id = order_data.get("order_id", f"order_{int(time.time() * 1000)}")
            
            # Create tracking record
            tracking_record = {
                **order_data,
                "order_id": order_id,
                "tracking_start": time.time(),
                "status": "created",
                "execution_time": 0.0,
                "phase": "order_creation"
            }
            
            # Add to active orders
            self.execution_tracker["active_orders"][order_id] = tracking_record
            
            # Add to order history
            self.execution_tracker["order_history"].append(tracking_record)
            
            # Limit history size
            if len(self.execution_tracker["order_history"]) > 10000:
                self.execution_tracker["order_history"] = self.execution_tracker["order_history"][-5000:]
            
            self.logger.debug(f"Order tracked: {order_id}")
            
        except Exception as e:
            self.logger.error(f"Error tracking order: {e}")
    
    async def _update_execution_performance(self):
        """Update execution performance metrics."""
        try:
            current_time = time.time()
            
            for order_id, order in self.execution_tracker["active_orders"].items():
                # Calculate execution time
                if order["status"] in ["created", "sent", "confirmed"]:
                    order["execution_time"] = current_time - order["tracking_start"]
                
                # Update performance metrics
                if order_id not in self.execution_tracker["execution_performance"]:
                    self.execution_tracker["execution_performance"][order_id] = {
                        "total_execution_time": 0.0,
                        "phase_durations": {},
                        "last_update": current_time
                    }
                
                self.execution_tracker["execution_performance"][order_id]["last_update"] = current_time
                
        except Exception as e:
            self.logger.error(f"Error updating execution performance: {e}")
    
    async def _cleanup_completed_orders(self):
        """Clean up completed orders from active tracking."""
        try:
            completed_orders = []
            
            for order_id, order in self.execution_tracker["active_orders"].items():
                # Check if order is completed
                if order["status"] in ["filled", "cancelled", "rejected"]:
                    completed_orders.append(order_id)
            
            # Remove completed orders
            for order_id in completed_orders:
                del self.execution_tracker["active_orders"][order_id]
                if order_id in self.execution_tracker["execution_performance"]:
                    del self.execution_tracker["execution_performance"][order_id]
            
            if completed_orders:
                self.logger.debug(f"Cleaned up {len(completed_orders)} completed orders")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up completed orders: {e}")
    
    # ============= PERFORMANCE MONITORING =============
    
    async def _performance_monitoring_loop(self):
        """Main performance monitoring loop."""
        while self.running:
            try:
                # Calculate throughput metrics
                await self._calculate_throughput_metrics()
                
                # Analyze bottlenecks
                await self._analyze_bottlenecks()
                
                # Update performance tracker
                await self._update_performance_tracker()
                
                await asyncio.sleep(1.0)  # 1 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(5.0)
    
    async def _calculate_throughput_metrics(self):
        """Calculate system throughput metrics."""
        try:
            current_time = time.time()
            
            # Calculate signals per second
            if self.signal_tracker["processed_signals"] > 0:
                elapsed_time = current_time - self.pipeline_state["start_time"]
                self.pipeline_metrics["signals_per_second"] = self.signal_tracker["processed_signals"] / elapsed_time
            
            # Calculate orders per second
            if self.execution_tracker["processed_orders"] > 0:
                elapsed_time = current_time - self.pipeline_state["start_time"]
                self.pipeline_metrics["orders_per_second"] = self.execution_tracker["processed_orders"] / elapsed_time
            
            # Calculate average signal latency
            if self.signal_tracker["signal_history"]:
                latencies = [
                    signal.get("processing_time", 0.0) 
                    for signal in self.signal_tracker["signal_history"][-100:]
                ]
                if latencies:
                    self.pipeline_metrics["avg_signal_latency"] = sum(latencies) / len(latencies)
            
            # Calculate average execution time
            if self.execution_tracker["order_history"]:
                execution_times = [
                    order.get("execution_time", 0.0) 
                    for order in self.execution_tracker["order_history"][-100:]
                ]
                if execution_times:
                    self.pipeline_metrics["avg_execution_time"] = sum(execution_times) / len(execution_times)
                    
        except Exception as e:
            self.logger.error(f"Error calculating throughput metrics: {e}")
    
    async def _analyze_bottlenecks(self):
        """Analyze system bottlenecks."""
        try:
            # Analyze signal processing bottlenecks
            if self.pipeline_metrics["avg_signal_latency"] > 0.1:  # > 100ms
                self.performance_tracker["bottleneck_analysis"]["signal_processing"] = {
                    "type": "high_latency",
                    "severity": "medium",
                    "description": "Signal processing latency is high",
                    "timestamp": time.time()
                }
            
            # Analyze execution bottlenecks
            if self.pipeline_metrics["avg_execution_time"] > 0.5:  # > 500ms
                self.performance_tracker["bottleneck_analysis"]["order_execution"] = {
                    "type": "high_latency",
                    "severity": "high",
                    "description": "Order execution time is high",
                    "timestamp": time.time()
                }
            
            # Analyze queue bottlenecks
            if len(self.signal_tracker["signal_queue"]) > 100:
                self.performance_tracker["bottleneck_analysis"]["signal_queue"] = {
                    "type": "queue_overflow",
                    "severity": "high",
                    "description": "Signal queue is overflowing",
                    "timestamp": time.time()
                }
            
            if len(self.execution_tracker["execution_queue"]) > 50:
                self.performance_tracker["bottleneck_analysis"]["execution_queue"] = {
                    "type": "queue_overflow",
                    "severity": "high",
                    "description": "Execution queue is overflowing",
                    "timestamp": time.time()
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing bottlenecks: {e}")
    
    async def _update_performance_tracker(self):
        """Update performance tracking data."""
        try:
            current_time = time.time()
            
            # Update signal timings
            if self.signal_tracker["signal_history"]:
                latest_signal = self.signal_tracker["signal_history"][-1]
                if "processing_time" in latest_signal:
                    self.performance_tracker["signal_timings"].append({
                        "timestamp": current_time,
                        "processing_time": latest_signal["processing_time"]
                    })
                    # Keep only last 1000 entries
                    if len(self.performance_tracker["signal_timings"]) > 1000:
                        self.performance_tracker["signal_timings"] = self.performance_tracker["signal_timings"][-1000:]
            
            # Update execution timings
            if self.execution_tracker["order_history"]:
                latest_order = self.execution_tracker["order_history"][-1]
                if "execution_time" in latest_order:
                    self.performance_tracker["execution_timings"].append({
                        "timestamp": current_time,
                        "execution_time": latest_order["execution_time"]
                    })
                    # Keep only last 1000 entries
                    if len(self.performance_tracker["execution_timings"]) > 1000:
                        self.performance_tracker["execution_timings"] = self.performance_tracker["execution_timings"][-1000:]
            
            # Update phase durations
            if self.pipeline_state["current_phase"] != self.pipeline_state.get("last_phase", ""):
                phase_duration = current_time - self.pipeline_state["last_phase_change"]
                self.performance_tracker["phase_durations"][self.pipeline_state.get("last_phase", "unknown")] = phase_duration
                self.pipeline_state["last_phase"] = self.pipeline_state["current_phase"]
                self.pipeline_state["last_phase_change"] = current_time
                
        except Exception as e:
            self.logger.error(f"Error updating performance tracker: {e}")
    
    # ============= CIRCUIT BREAKER MONITORING =============
    
    async def _circuit_breaker_monitoring_loop(self):
        """Monitor and manage circuit breakers."""
        while self.running:
            try:
                # Check circuit breaker timeouts
                await self._check_circuit_breaker_timeouts()
                
                # Attempt circuit breaker recovery
                await self._attempt_circuit_breaker_recovery()
                
                await asyncio.sleep(5.0)  # 5 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in circuit breaker monitoring: {e}")
                await asyncio.sleep(10.0)
    
    async def _trigger_circuit_breaker(self, breaker_name: str):
        """Trigger a circuit breaker."""
        try:
            if breaker_name in self.circuit_breakers:
                self.circuit_breakers[breaker_name]["active"] = True
                self.circuit_breakers[breaker_name]["trigger_count"] += 1
                self.circuit_breakers[breaker_name]["last_trigger"] = time.time()
                
                self.logger.warning(f"⚠️ Circuit breaker triggered: {breaker_name}")
                
        except Exception as e:
            self.logger.error(f"Error triggering circuit breaker: {e}")
    
    async def _check_circuit_breaker_timeouts(self):
        """Check if circuit breakers should timeout."""
        try:
            current_time = time.time()
            
            for breaker_name, breaker in self.circuit_breakers.items():
                if breaker["active"]:
                    # Timeout after 60 seconds
                    if current_time - breaker["last_trigger"] > 60:
                        breaker["active"] = False
                        self.logger.info(f"✅ Circuit breaker timeout: {breaker_name}")
                        
        except Exception as e:
            self.logger.error(f"Error checking circuit breaker timeouts: {e}")
    
    async def _attempt_circuit_breaker_recovery(self):
        """Attempt to recover from circuit breaker state."""
        try:
            for breaker_name, breaker in self.circuit_breakers.items():
                if not breaker["active"] and breaker["trigger_count"] > 0:
                    # Reset trigger count after successful recovery
                    breaker["trigger_count"] = 0
                    self.logger.info(f"✅ Circuit breaker recovered: {breaker_name}")
                    
        except Exception as e:
            self.logger.error(f"Error attempting circuit breaker recovery: {e}")
    
    # ============= ROUTING METHODS =============
    
    async def _route_signal_to_strategy(self, signal_data: Dict[str, Any]):
        """Route signal to strategy engine."""
        try:
            # Publish to strategy signals channel
            await self.redis_conn.publish_async("strategy:signals", json.dumps(signal_data))
            
        except Exception as e:
            self.logger.error(f"Error routing signal to strategy: {e}")
    
    async def _route_order_to_execution(self, order_data: Dict[str, Any]):
        """Route order to execution agent."""
        try:
            # Publish to execution orders channel
            await self.redis_conn.publish_async("execution:orders", json.dumps(order_data))
            
        except Exception as e:
            self.logger.error(f"Error routing order to execution: {e}")
    
    # ============= UTILITY METHODS =============
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health from Redis."""
        try:
            # This would typically get data from Redis
            # For now, return a default health status
            return {
                "overall_health": 0.95,
                "agents": {},
                "system_components": {},
                "external_connections": {}
            }
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return {"overall_health": 0.0}
    
    async def _update_pipeline_metrics(self):
        """Update pipeline performance metrics."""
        try:
            # Update system throughput
            self.pipeline_metrics["system_throughput"] = (
                self.pipeline_metrics["signals_per_second"] + 
                self.pipeline_metrics["orders_per_second"]
            )
            
        except Exception as e:
            self.logger.error(f"Error updating pipeline metrics: {e}")
    
    async def _publish_pipeline_status(self):
        """Publish current pipeline status to Redis."""
        try:
            pipeline_status = {
                "timestamp": time.time(),
                "phase": self.pipeline_state["current_phase"],
                "health": self.pipeline_state["pipeline_health"],
                "metrics": self.pipeline_metrics,
                "queue_sizes": {
                    "signals": len(self.signal_tracker["signal_queue"]),
                    "executions": len(self.execution_tracker["execution_queue"])
                },
                "performance": {
                    "signals_processed": self.signal_tracker["processed_signals"],
                    "orders_processed": self.execution_tracker["processed_orders"],
                    "active_signals": len(self.signal_tracker["active_signals"]),
                    "active_orders": len(self.execution_tracker["active_orders"])
                }
            }
            
            await self.redis_conn.publish_async("pipeline:flow", json.dumps(pipeline_status))
            
        except Exception as e:
            self.logger.error(f"Error publishing pipeline status: {e}")
    
    async def _publish_signal_tracking(self):
        """Publish signal tracking updates to Redis."""
        try:
            tracking_update = {
                "timestamp": time.time(),
                "active_signals": len(self.signal_tracker["active_signals"]),
                "total_signals": len(self.signal_tracker["signal_history"]),
                "processed_signals": self.signal_tracker["processed_signals"],
                "performance_summary": {
                    signal_id: {
                        "processing_time": perf.get("total_processing_time", 0.0),
                        "phase_durations": perf.get("phase_durations", {})
                    }
                    for signal_id, perf in self.signal_tracker["signal_performance"].items()
                }
            }
            
            await self.redis_conn.publish_async("signals:tracking", json.dumps(tracking_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing signal tracking: {e}")
    
    async def _publish_execution_tracking(self):
        """Publish execution tracking updates to Redis."""
        try:
            tracking_update = {
                "timestamp": time.time(),
                "active_orders": len(self.execution_tracker["active_orders"]),
                "total_orders": len(self.execution_tracker["order_history"]),
                "processed_orders": self.execution_tracker["processed_orders"],
                "performance_summary": {
                    order_id: {
                        "execution_time": perf.get("total_execution_time", 0.0),
                        "phase_durations": perf.get("phase_durations", {})
                    }
                    for order_id, perf in self.execution_tracker["execution_performance"].items()
                }
            }
            
            await self.redis_conn.publish_async("execution:tracking", json.dumps(tracking_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing execution tracking: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def submit_signal(self, signal_data: Dict[str, Any]) -> str:
        """Submit a signal to the pipeline."""
        try:
            signal_id = signal_data.get("signal_id", f"signal_{int(time.time() * 1000)}")
            
            # Add to signal queue
            self.signal_tracker["signal_queue"].append({
                **signal_data,
                "signal_id": signal_id,
                "submission_time": time.time()
            })
            
            self.logger.info(f"Signal submitted to pipeline: {signal_id}")
            return signal_id
            
        except Exception as e:
            self.logger.error(f"Error submitting signal: {e}")
            return None
    
    async def submit_execution(self, order_data: Dict[str, Any]) -> str:
        """Submit an order to the pipeline."""
        try:
            order_id = order_data.get("order_id", f"order_{int(time.time() * 1000)}")
            
            # Add to execution queue
            self.execution_tracker["execution_queue"].append({
                **order_data,
                "order_id": order_id,
                "submission_time": time.time()
            })
            
            self.logger.info(f"Order submitted to pipeline: {order_id}")
            return order_id
            
        except Exception as e:
            self.logger.error(f"Error submitting order: {e}")
            return None
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            "phase": self.pipeline_state["current_phase"],
            "health": self.pipeline_state["pipeline_health"],
            "metrics": self.pipeline_metrics,
            "queue_sizes": {
                "signals": len(self.signal_tracker["signal_queue"]),
                "executions": len(self.execution_tracker["execution_queue"])
            },
            "performance": {
                "signals_processed": self.signal_tracker["processed_signals"],
                "orders_processed": self.execution_tracker["processed_orders"],
                "active_signals": len(self.signal_tracker["active_signals"]),
                "active_orders": len(self.execution_tracker["active_orders"])
            },
            "last_update": time.time()
        }
    
    async def get_signal_tracking(self) -> Dict[str, Any]:
        """Get current signal tracking status."""
        return {
            "active_signals": len(self.signal_tracker["active_signals"]),
            "total_signals": len(self.signal_tracker["signal_history"]),
            "processed_signals": self.signal_tracker["processed_signals"],
            "performance_summary": self.signal_tracker["signal_performance"],
            "last_update": time.time()
        }
    
    async def get_execution_tracking(self) -> Dict[str, Any]:
        """Get current execution tracking status."""
        return {
            "active_orders": len(self.execution_tracker["active_orders"]),
            "total_orders": len(self.execution_tracker["order_history"]),
            "processed_orders": self.execution_tracker["processed_orders"],
            "performance_summary": self.execution_tracker["execution_performance"],
            "last_update": time.time()
        }
    
    async def get_performance_analysis(self) -> Dict[str, Any]:
        """Get performance analysis and bottleneck information."""
        return {
            "throughput_metrics": self.pipeline_metrics,
            "bottleneck_analysis": self.performance_tracker["bottleneck_analysis"],
            "circuit_breakers": self.circuit_breakers,
            "last_update": time.time()
        }
