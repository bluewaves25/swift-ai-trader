#!/usr/bin/env python3
"""
Enhanced Core Agent - SINGLE SOURCE OF TRUTH FOR SYSTEM COORDINATION
Consolidates all health monitoring, timing coordination, system-wide coordination, and system monitoring.
Eliminates duplicate functionality from other agents.
Handles ALL system health, performance, and monitoring responsibilities.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedCoreAgent(BaseAgent):
    """Enhanced core agent - single source of truth for system coordination."""
    
    def _initialize_agent_components(self):
        """Initialize core agent specific components."""
        # Initialize core agent components
        self.signal_router = None
        self.agent_coordinator = None
        self.learning_coordinator = None
        
        # System-wide coordination state
        self.system_state = {
            "overall_health_score": 1.0,
            "agent_status": {},
            "system_timing": {
                "ultra_hft_cycle": 0,
                "fast_cycle": 0,
                "tactical_cycle": 0,
                "strategic_cycle": 0
            },
            "last_coordination_time": time.time(),
            "last_timing_update": time.time(),
            "timing_cycles_processed": 0
        }
        
        # Pipeline orchestration state
        self.pipeline_state = {
            "current_phase": "initialization",
            "pipeline_health": 1.0,
            "signal_queue": [],
            "execution_queue": [],
            "pipeline_metrics": {
                "signals_processed": 0,
                "orders_executed": 0,
                "avg_signal_latency": 0.0,
                "avg_execution_time": 0.0,
                "data_quality_score": 100.0
            }
        }
        
        # Signal tracking system
        self.signal_tracker = {
            "active_signals": {},
            "signal_history": [],
            "signal_performance": {},
            "correlation_map": {}
        }
        
        # Execution tracking system
        self.execution_tracker = {
            "active_orders": {},
            "order_history": [],
            "execution_performance": {},
            "broker_status": {}
        }
        
        # Timing coordination for 4-tier architecture
        self.timing_coordinator = {
            "ultra_hft": {"interval": 0.001, "last_run": 0, "active": True},
            "fast": {"interval": 0.1, "last_run": 0, "active": True},
            "tactical": {"interval": 30.0, "last_run": 0, "active": True},
            "strategic": {"interval": 300.0, "last_run": 0, "active": True}
        }
        
        # Health monitoring registry (comprehensive system monitoring)
        self.health_registry = {}
        self.system_performance_registry = {}
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Core agent specific startup logic."""
        try:
            # Initialize system-wide coordination
            await self._initialize_system_coordination()
            
            # Start timing coordination
            await self._start_timing_coordination()
            
            # Initialize comprehensive health and system monitoring
            await self._initialize_health_monitoring()
            await self._initialize_system_performance_monitoring()
            
            self.logger.info("✅ Core Agent: System coordination initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error in core agent startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Core agent specific shutdown logic."""
        try:
            # Stop all timing coordination
            await self._stop_timing_coordination()
            
            # Cleanup health monitoring
            await self._cleanup_health_monitoring()
            
            # Cleanup system performance monitoring
            await self._cleanup_system_performance_monitoring()
            
            self.logger.info("✅ Core Agent: System coordination shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in core agent shutdown: {e}")
    
    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._timing_coordination_loop, "Timing Coordination", "fast"),
            (self._health_monitoring_loop, "Health Monitoring", "tactical"),
            (self._system_coordination_loop, "System Coordination", "strategic"),
            (self._signal_routing_loop, "Signal Routing", "fast"),
            (self._pipeline_orchestration_loop, "Pipeline Orchestration", "fast")
        ]
    
    # ============= SYSTEM COORDINATION INITIALIZATION =============
    
    async def _initialize_system_coordination(self):
        """Initialize system-wide coordination systems."""
        try:
            # Initialize Redis pub/sub for system coordination
            self.coordination_channels = {
                "system_health": "system:health",
                "timing_signals": "system:timing",
                "agent_status": "system:agent_status",
                "coordination_commands": "system:commands"
            }
            
            # Set up Redis pub/sub
            self.redis_pubsub = self.redis_conn.pubsub()
            if self.redis_pubsub:
                self.redis_pubsub.subscribe(*self.coordination_channels.values())
            
            self.logger.info("✅ System coordination channels established")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing system coordination: {e}")
            raise
    
    async def _start_timing_coordination(self):
        """Start timing coordination for 4-tier architecture."""
        try:
            # Initialize timing state
            current_time = time.time()
            for tier in self.timing_coordinator:
                self.timing_coordinator[tier]["last_run"] = current_time
            
            self.logger.info("✅ Timing coordination initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting timing coordination: {e}")
            raise
    
    async def _initialize_health_monitoring(self):
        """Initialize system-wide health monitoring."""
        try:
            # Initialize health monitoring state
            self.health_registry = {
                "agents": {},
                "system_components": {},
                "external_connections": {},
                "last_health_check": time.time()
            }
            
            self.logger.info("✅ Health monitoring initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing health monitoring: {e}")
            raise
    
    async def _initialize_system_performance_monitoring(self):
        """Initialize comprehensive system performance monitoring."""
        try:
            # Initialize system performance monitoring state
            self.system_performance_registry = {
                "cpu_usage": {},
                "memory_usage": {},
                "disk_usage": {},
                "network_latency": {},
                "error_rates": {},
                "last_performance_check": time.time()
            }
            
            self.logger.info("✅ System performance monitoring initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing system performance monitoring: {e}")
            raise
    
    # ============= SYSTEM COORDINATION LOOP =============
    
    async def _system_coordination_loop(self):
        """Main system coordination loop (30s intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Coordinate system-wide operations
                await self._coordinate_system_operations()
                
                # Update system state
                self._update_system_state()
                
                # Publish system status
                await self._publish_system_status()
                
                # Record operation
                duration_ms = (time.time() - start_time) * 1000
                if hasattr(self, 'status_monitor') and self.status_monitor:
                    self.status_monitor.record_operation(duration_ms, True)
                
                await asyncio.sleep(30)  # 30s coordination cycle
                
            except Exception as e:
                self.logger.error(f"Error in system coordination loop: {e}")
                await asyncio.sleep(30)
    
    async def _coordinate_system_operations(self):
        """Coordinate all system-wide operations."""
        try:
            # Coordinate agent operations
            await self._coordinate_agent_operations()
            
            # Coordinate system timing
            await self._coordinate_system_timing()
            
            # Coordinate health monitoring
            await self._coordinate_health_monitoring()
            
        except Exception as e:
            self.logger.error(f"Error coordinating system operations: {e}")
    
    # ============= TIMING COORDINATION LOOP =============
    
    async def _timing_coordination_loop(self):
        """Timing coordination loop for 4-tier architecture (100ms intervals)."""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Check and trigger timing cycles
                await self._check_and_trigger_timing_cycles(current_time)
                
                # Update timing state
                await self._update_timing_state(current_time)
                
                await asyncio.sleep(0.1)  # 100ms timing check
                
            except Exception as e:
                self.logger.error(f"Error in timing coordination loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _check_and_trigger_timing_cycles(self, current_time: float):
        """Check and trigger appropriate timing cycles."""
        try:
            for tier, config in self.timing_coordinator.items():
                if config["active"] and (current_time - config["last_run"]) >= config["interval"]:
                    # Trigger timing cycle
                    await self._trigger_timing_cycle(tier, current_time)
                    config["last_run"] = current_time
                    
        except Exception as e:
            self.logger.error(f"Error checking timing cycles: {e}")
    
    async def _trigger_timing_cycle(self, tier: str, current_time: float):
        """Trigger a specific timing cycle."""
        try:
            # Publish timing signal to Redis
            timing_signal = {
                "tier": tier,
                "timestamp": current_time,
                "cycle_id": f"{tier}_{int(current_time)}"
            }
            
            await self.redis_conn.publish_async(
                self.coordination_channels["timing_signals"],
                json.dumps(timing_signal)
            )
            
            # Update system timing state
            self.system_state["system_timing"][f"{tier}_cycle"] += 1
            
        except Exception as e:
            self.logger.error(f"Error triggering {tier} timing cycle: {e}")
    
    # ============= HEALTH MONITORING LOOP =============
    
    async def _health_monitoring_loop(self):
        """System-wide health monitoring loop (30s intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Check all agent health
                await self._check_all_agent_health()
                
                # Check system component health
                await self._check_system_component_health()
                
                # Check external connection health
                await self._check_external_connection_health()
                
                # Calculate overall system health
                self._calculate_overall_system_health()
                
                # Publish health status
                await self._publish_health_status()
                
                # Record operation
                duration_ms = (time.time() - start_time) * 1000
                if hasattr(self, 'status_monitor') and self.status_monitor:
                    self.status_monitor.record_operation(duration_ms, True)
                
                await asyncio.sleep(30)  # 30s health check cycle
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _check_all_agent_health(self):
        """Check health of all registered agents."""
        try:
            # Get all registered agents from Redis
            agent_keys = await self.redis_conn.keys_async("agent:*")
            
            for agent_key in agent_keys:
                agent_data = await self.redis_conn.hgetall_async(agent_key)
                if agent_data:
                    agent_name = agent_key.replace("agent:", "")
                    self.health_registry["agents"][agent_name] = {
                        "status": agent_data.get("status", "unknown"),
                        "last_heartbeat": float(agent_data.get("last_heartbeat", 0)),
                        "health_score": float(agent_data.get("health_score", 0.0))
                    }
                    
        except Exception as e:
            self.logger.error(f"Error checking agent health: {e}")
    
    async def _check_system_component_health(self):
        """Check health of system components."""
        try:
            # Check Redis connection health
            redis_health = await self._check_redis_health()
            self.health_registry["system_components"]["redis"] = redis_health
            
            # Check timing coordination health
            timing_health = self._check_timing_coordination_health()
            self.health_registry["system_components"]["timing"] = timing_health
            
        except Exception as e:
            self.logger.error(f"Error checking system component health: {e}")
    
    async def _check_external_connection_health(self):
        """Check health of external connections."""
        try:
            # This will be populated by other agents reporting their connection status
            # For now, initialize with default values
            self.health_registry["external_connections"] = {
                "mt5": {"status": "unknown", "last_check": time.time()},
                "brokers": {"status": "unknown", "last_check": time.time()}
            }
            
        except Exception as e:
            self.logger.error(f"Error checking external connection health: {e}")
    
    def _calculate_overall_system_health(self):
        """Calculate overall system health score."""
        try:
            total_score = 0.0
            component_count = 0
            
            # Calculate agent health average
            if self.health_registry["agents"]:
                agent_scores = [agent["health_score"] for agent in self.health_registry["agents"].values()]
                total_score += sum(agent_scores)
                component_count += len(agent_scores)
            
            # Calculate system component health average
            if self.health_registry["system_components"]:
                component_scores = [comp["health_score"] for comp in self.health_registry["system_components"].values()]
                total_score += sum(component_scores)
                component_count += len(component_scores)
            
            # Calculate overall health
            if component_count > 0:
                self.system_state["overall_health_score"] = total_score / component_count
            else:
                self.system_state["overall_health_score"] = 1.0
                
        except Exception as e:
            self.logger.error(f"Error calculating system health: {e}")
            self.system_state["overall_health_score"] = 0.0
    
    # ============= SIGNAL ROUTING LOOP =============
    
    async def _signal_routing_loop(self):
        """Real-time signal routing loop (1ms intervals)."""
        while self.is_running:
            try:
                # Process routing requests from message handlers
                await self._process_routing_requests()
                
                await asyncio.sleep(0.001)  # 1ms for real-time responsiveness
                
            except Exception as e:
                self.logger.error(f"Error in signal routing loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_routing_requests(self):
        """Process pending routing requests."""
        try:
            # Check for new routing requests in Redis
            routing_requests = await self.redis_conn.lrange_async("routing:requests", 0, 9)
            
            for request in routing_requests:
                try:
                    request_data = json.loads(request)
                    await self._route_signal(request_data)
                    
                    # Remove processed request
                    await self.redis_conn.lrem_async("routing:requests", 1, request)
                    
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid routing request format: {request}")
                except Exception as e:
                    self.logger.error(f"Error processing routing request: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error processing routing requests: {e}")
    
    # ============= UTILITY METHODS =============
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connection health."""
        try:
            start_time = time.time()
            await self.redis_conn.ping_async()
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "health_score": 1.0,
                "last_check": time.time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "health_score": 0.0,
                "last_check": time.time()
            }
    
    def _check_timing_coordination_health(self) -> Dict[str, Any]:
        """Check timing coordination health."""
        try:
            current_time = time.time()
            timing_issues = []
            
            for tier, config in self.timing_coordinator.items():
                if config["active"]:
                    time_since_last = current_time - config["last_run"]
                    if time_since_last > config["interval"] * 2:
                        timing_issues.append(f"{tier}_delayed")
            
            health_score = 1.0 if not timing_issues else 0.5
            
            return {
                "status": "healthy" if not timing_issues else "degraded",
                "issues": timing_issues,
                "health_score": health_score,
                "last_check": current_time
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "health_score": 0.0,
                "last_check": time.time()
            }
    
    async def _publish_system_status(self):
        """Publish system status to Redis."""
        try:
            status_data = {
                "timestamp": time.time(),
                "overall_health": self.system_state["overall_health_score"],
                "system_timing": self.system_state["system_timing"],
                "agent_count": len(self.health_registry["agents"])
            }
            
            await self.redis_conn.publish_async(
                self.coordination_channels["system_health"],
                json.dumps(status_data)
            )
            
        except Exception as e:
            self.logger.error(f"Error publishing system status: {e}")
    
    async def _publish_health_status(self):
        """Publish health status to Redis."""
        try:
            health_data = {
                "timestamp": time.time(),
                "overall_health": self.system_state["overall_health_score"],
                "agents": self.health_registry["agents"],
                "system_components": self.health_registry["system_components"],
                "external_connections": self.health_registry["external_connections"]
            }
            
            await self.redis_conn.publish_async(
                self.coordination_channels["agent_status"],
                json.dumps(health_data)
            )
            
        except Exception as e:
            self.logger.error(f"Error publishing health status: {e}")
    
    async def _route_signal(self, signal_data: Dict[str, Any]):
        """Route a signal to appropriate destination."""
        try:
            signal_type = signal_data.get("type", "unknown")
            destination = signal_data.get("destination", "unknown")
            
            # Route signal based on type and destination
            if signal_type == "trading_signal":
                await self._route_trading_signal(signal_data)
            elif signal_type == "system_command":
                await self._route_system_command(signal_data)
            elif signal_type == "health_update":
                await self._route_health_update(signal_data)
            else:
                self.logger.warning(f"Unknown signal type: {signal_type}")
                
        except Exception as e:
            self.logger.error(f"Error routing signal: {e}")
    
    async def _route_trading_signal(self, signal_data: Dict[str, Any]):
        """Route trading signal to appropriate agent."""
        try:
            # Publish to trading signals channel
            await self.redis_conn.publish_async("trading:signals", json.dumps(signal_data))
            
        except Exception as e:
            self.logger.error(f"Error routing trading signal: {e}")
    
    async def _route_execution_order(self, order_data: Dict[str, Any]):
        """Route execution order to execution agent."""
        try:
            # Publish to execution orders channel
            await self.redis_conn.publish_async("execution:orders", json.dumps(order_data))
            
        except Exception as e:
            self.logger.error(f"Error routing execution order: {e}")
    
    async def _route_system_command(self, command_data: Dict[str, Any]):
        """Route system command to appropriate destination."""
        try:
            # Publish to system commands channel
            await self.redis_conn.publish_async("system:commands", json.dumps(command_data))
            
        except Exception as e:
            self.logger.error(f"Error routing system command: {e}")
    
    async def _route_health_update(self, health_data: Dict[str, Any]):
        """Route health update to health monitoring system."""
        try:
            # Update local health registry
            agent_name = health_data.get("agent_name", "unknown")
            if agent_name != "unknown":
                self.health_registry["agents"][agent_name] = health_data
            
            # Publish to health channel
            await self.redis_conn.publish_async("system:health", json.dumps(health_data))
            
        except Exception as e:
            self.logger.error(f"Error routing health update: {e}")
    
    # ============= SHUTDOWN METHODS =============
    
    async def _stop_timing_coordination(self):
        """Stop timing coordination."""
        try:
            # Deactivate all timing tiers
            for tier in self.timing_coordinator:
                self.timing_coordinator[tier]["active"] = False
            
            self.logger.info("✅ Timing coordination stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping timing coordination: {e}")
    
    async def _cleanup_health_monitoring(self):
        """Cleanup health monitoring resources."""
        try:
            # Clear health registry
            self.health_registry.clear()
            
            # Unsubscribe from Redis channels if pubsub exists
            if hasattr(self, 'redis_pubsub') and self.redis_pubsub:
                try:
                    await self.redis_pubsub.unsubscribe()
                    await self.redis_pubsub.close()
                except Exception as e:
                    self.logger.warning(f"Warning during Redis pubsub cleanup: {e}")
            
            self.logger.info("✅ Health monitoring cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up health monitoring: {e}")
    
    async def _cleanup_system_performance_monitoring(self):
        """Cleanup system performance monitoring resources."""
        try:
            # Clear system performance registry
            self.system_performance_registry.clear()
            
            self.logger.info("✅ System performance monitoring cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up system performance monitoring: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status."""
        return {
            "overall_health": self.system_state["overall_health_score"],
            "agents": self.health_registry["agents"],
            "system_components": self.health_registry["system_components"],
            "external_connections": self.health_registry["external_connections"],
            "last_update": time.time()
        }
    
    async def get_timing_status(self) -> Dict[str, Any]:
        """Get current timing coordination status."""
        return {
            "timing_coordinator": self.timing_coordinator,
            "system_timing": self.system_state["system_timing"],
            "last_update": time.time()
        }
    
    async def trigger_timing_cycle(self, tier: str) -> bool:
        """Manually trigger a timing cycle."""
        try:
            if tier in self.timing_coordinator:
                await self._trigger_timing_cycle(tier, time.time())
                return True
            else:
                self.logger.warning(f"Unknown timing tier: {tier}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error triggering timing cycle: {e}")
            return False
    
    # ============= PIPELINE ORCHESTRATION =============
    
    async def _pipeline_orchestration_loop(self):
        """Main pipeline orchestration loop."""
        while self.is_running:
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
                self.logger.error(f"Error in pipeline orchestration: {e}")
                await asyncio.sleep(1.0)
    
    async def _update_pipeline_phase(self):
        """Update current pipeline phase based on system state."""
        try:
            # Determine current phase based on agent statuses
            all_agents_ready = all(
                status.get("status") == "ready" 
                for status in self.system_state["agent_status"].values()
            )
            
            if all_agents_ready and self.pipeline_state["current_phase"] == "initialization":
                self.pipeline_state["current_phase"] = "operational"
                self.logger.info("🚀 Pipeline phase changed to: operational")
            
            # Update pipeline health based on agent health scores
            health_scores = [
                status.get("health_score", 0.0) 
                for status in self.system_state["agent_status"].values()
            ]
            
            if health_scores:
                self.pipeline_state["pipeline_health"] = sum(health_scores) / len(health_scores)
                
        except Exception as e:
            self.logger.error(f"Error updating pipeline phase: {e}")
    
    async def _process_signal_queue(self):
        """Process signals in the pipeline signal queue."""
        try:
            for signal in self.pipeline_state["signal_queue"][:10]:  # Process up to 10 at a time
                # Track signal in signal tracker
                await self._track_signal(signal)
                
                # Route signal to appropriate destination
                await self._route_trading_signal(signal)
                
                # Remove processed signal
                self.pipeline_state["signal_queue"].remove(signal)
                
        except Exception as e:
            self.logger.error(f"Error processing signal queue: {e}")
    
    async def _process_execution_queue(self):
        """Process orders in the pipeline execution queue."""
        try:
            for order in self.pipeline_state["execution_queue"][:5]:  # Process up to 5 at a time
                # Track order in execution tracker
                await self._track_execution(order)
                
                # Route order to execution agent
                await self._route_execution_order(order)
                
                # Remove processed order
                self.pipeline_state["execution_queue"].remove(order)
                
        except Exception as e:
            self.logger.error(f"Error processing execution queue: {e}")
    
    async def _update_pipeline_metrics(self):
        """Update pipeline performance metrics."""
        try:
            # Calculate average signal latency
            if self.signal_tracker["signal_history"]:
                latencies = [
                    signal.get("processing_time", 0.0) 
                    for signal in self.signal_tracker["signal_history"][-100:]  # Last 100 signals
                ]
                if latencies:
                    self.pipeline_state["pipeline_metrics"]["avg_signal_latency"] = sum(latencies) / len(latencies)
            
            # Calculate average execution time
            if self.execution_tracker["order_history"]:
                execution_times = [
                    order.get("execution_time", 0.0) 
                    for order in self.execution_tracker["order_history"][-100:]  # Last 100 orders
                ]
                if execution_times:
                    self.pipeline_state["pipeline_metrics"]["avg_execution_time"] = sum(execution_times) / len(execution_times)
                    
        except Exception as e:
            self.logger.error(f"Error updating pipeline metrics: {e}")
    
    async def _publish_pipeline_status(self):
        """Publish current pipeline status to Redis."""
        try:
            pipeline_status = {
                "timestamp": time.time(),
                "phase": self.pipeline_state["current_phase"],
                "health": self.pipeline_state["pipeline_health"],
                "metrics": self.pipeline_state["pipeline_metrics"],
                "queue_sizes": {
                    "signals": len(self.pipeline_state["signal_queue"]),
                    "executions": len(self.pipeline_state["execution_queue"])
                }
            }
            
            await self.redis_conn.publish_async("pipeline:flow", json.dumps(pipeline_status))
            
        except Exception as e:
            self.logger.error(f"Error publishing pipeline status: {e}")
    
    # ============= SIGNAL TRACKING =============
    
    async def _signal_tracking_loop(self):
        """Main signal tracking loop."""
        while self.is_running:
            try:
                # Update signal performance metrics
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
            
            # Add to active signals
            self.signal_tracker["active_signals"][signal_id] = {
                **signal_data,
                "tracking_start": time.time(),
                "status": "active",
                "processing_time": 0.0
            }
            
            # Add to signal history
            self.signal_tracker["signal_history"].append({
                **signal_data,
                "tracking_start": time.time(),
                "status": "created"
            })
            
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
                if signal["status"] == "active":
                    signal["processing_time"] = current_time - signal["tracking_start"]
                
                # Update performance metrics
                if signal_id not in self.signal_tracker["signal_performance"]:
                    self.signal_tracker["signal_performance"][signal_id] = {
                        "total_processing_time": 0.0,
                        "status_changes": 0,
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
    
    async def _publish_signal_tracking(self):
        """Publish signal tracking updates to Redis."""
        try:
            tracking_update = {
                "timestamp": time.time(),
                "active_signals": len(self.signal_tracker["active_signals"]),
                "total_signals": len(self.signal_tracker["signal_history"]),
                "performance_summary": {
                    signal_id: {
                        "processing_time": perf.get("total_processing_time", 0.0),
                        "status_changes": perf.get("status_changes", 0)
                    }
                    for signal_id, perf in self.signal_tracker["signal_performance"].items()
                }
            }
            
            await self.redis_conn.publish_async("signals:tracking", json.dumps(tracking_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing signal tracking: {e}")
    
    # ============= EXECUTION TRACKING =============
    
    async def _execution_tracking_loop(self):
        """Main execution tracking loop."""
        while self.is_running:
            try:
                # Update execution performance metrics
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
            
            # Add to active orders
            self.execution_tracker["active_orders"][order_id] = {
                **order_data,
                "tracking_start": time.time(),
                "status": "created",
                "execution_time": 0.0
            }
            
            # Add to order history
            self.execution_tracker["order_history"].append({
                **order_data,
                "tracking_start": time.time(),
                "status": "created"
            })
            
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
                        "status_changes": 0,
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
    
    async def _publish_execution_tracking(self):
        """Publish execution tracking updates to Redis."""
        try:
            tracking_update = {
                "timestamp": time.time(),
                "active_orders": len(self.execution_tracker["active_orders"]),
                "total_orders": len(self.execution_tracker["order_history"]),
                "performance_summary": {
                    order_id: {
                        "execution_time": perf.get("total_execution_time", 0.0),
                        "status_changes": perf.get("status_changes", 0)
                    }
                    for order_id, perf in self.execution_tracker["execution_performance"].items()
                }
            }
            
            await self.redis_conn.publish_async("execution:tracking", json.dumps(tracking_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing execution tracking: {e}")
    
    # ============= PUBLIC PIPELINE INTERFACE =============
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            "phase": self.pipeline_state["current_phase"],
            "health": self.pipeline_state["pipeline_health"],
            "metrics": self.pipeline_state["pipeline_metrics"],
            "queue_sizes": {
                "signals": len(self.pipeline_state["signal_queue"]),
                "executions": len(self.pipeline_state["execution_queue"])
            },
            "last_update": time.time()
        }
    
    async def get_signal_tracking(self) -> Dict[str, Any]:
        """Get current signal tracking status."""
        return {
            "active_signals": len(self.signal_tracker["active_signals"]),
            "total_signals": len(self.signal_tracker["signal_history"]),
            "performance_summary": self.signal_tracker["signal_performance"],
            "last_update": time.time()
        }
    
    async def get_execution_tracking(self) -> Dict[str, Any]:
        """Get current execution tracking status."""
        return {
            "active_orders": len(self.execution_tracker["active_orders"]),
            "total_orders": len(self.execution_tracker["order_history"]),
            "performance_summary": self.execution_tracker["execution_performance"],
            "last_update": time.time()
        }
    
    async def submit_signal(self, signal_data: Dict[str, Any]) -> str:
        """Submit a signal to the pipeline."""
        try:
            signal_id = signal_data.get("signal_id", f"signal_{int(time.time() * 1000)}")
            
            # Add to signal queue
            self.pipeline_state["signal_queue"].append({
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
            self.pipeline_state["execution_queue"].append({
                **order_data,
                "order_id": order_id,
                "submission_time": time.time()
            })
            
            self.logger.info(f"Order submitted to pipeline: {order_id}")
            return order_id
            
        except Exception as e:
            self.logger.error(f"Error submitting order: {e}")
            return None
    
    # ============= MISSING METHODS =============
    
    async def _coordinate_system_operations(self):
        """Coordinate system-wide operations."""
        try:
            # Placeholder for system coordination logic
            pass
        except Exception as e:
            self.logger.error(f"Error coordinating system operations: {e}")
    
    def _update_system_state(self):
        """Update system state."""
        try:
            # Placeholder for system state update logic
            pass
        except Exception as e:
            self.logger.error(f"Error updating system state: {e}")
    
    async def _publish_system_status(self):
        """Publish system status to Redis."""
        try:
            # Placeholder for system status publishing
            pass
        except Exception as e:
            self.logger.error(f"Error publishing system status: {e}")
    
    async def _update_timing_state(self, current_time: float):
        """Update timing state."""
        try:
            # Update timing state with current time
            self.system_state["last_timing_update"] = current_time
            self.system_state["timing_cycles_processed"] += 1
        except Exception as e:
            self.logger.error(f"Error updating timing state: {e}")
    
    async def _route_trading_signal(self, signal: Dict[str, Any]):
        """Route trading signal to appropriate destination."""
        try:
            # Placeholder for signal routing logic
            pass
        except Exception as e:
            self.logger.error(f"Error routing trading signal: {e}")
    
    async def _get_pending_signals(self):
        """Get pending signals from Redis."""
        try:
            # Placeholder for getting pending signals
            return []
        except Exception as e:
            self.logger.error(f"Error getting pending signals: {e}")
            return []
