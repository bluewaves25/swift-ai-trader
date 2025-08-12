"""
Complete Trading Engine with 4-Tier Architecture

This module implements a comprehensive trading engine with:
- TIER 1: Ultra-HFT (1ms cycles) for arbitrage
- TIER 2: Fast (100ms cycles) for market making and strategy signals
- TIER 3: Tactical (30s cycles) for market analysis
- TIER 4: Strategic (5min cycles) for portfolio optimization

Features:
- Complete position management lifecycle
- Strategy-specific signal handling
- Risk management integration
- Real-time monitoring and control
- Redis-based inter-agent communication
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

# Import shared utilities
from .shared_utils import get_shared_redis, get_shared_logger, get_timing_coordinator
from .shared_utils.base_agent import BaseAgent
from .shared_utils.simplified_timing import SimplifiedTimingCoordinator
from .communication.communication_hub import get_communication_hub

# Trading state enums
class TradingState(Enum):
    """Trading engine states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

class PositionStatus(Enum):
    """Position status values."""
    OPENING = "opening"
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"
    ERROR = "error"

class TradingEngine:
    """Complete trading engine with 4-tier architecture."""
    
    def __init__(self):
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("trading_engine")
        
        # Initialize placeholders
        self.redis_conn = get_shared_redis()
        self.timing_coordinator = None
        
        self.state = TradingState.STOPPED
        self.is_running = False
        self.start_time = time.time()
        
        # Add communication hub
        self.comm_hub = get_communication_hub()
        
        # Position management
        self.active_positions: Dict[str, Dict[str, Any]] = {}
        self.position_history: List[Dict[str, Any]] = []
        
        # Trading statistics
        self.stats = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "ultra_hft_cycles": 0,
            "fast_cycles": 0,
            "tactical_cycles": 0,
            "strategic_cycles": 0,
            "positions_opened": 0,
            "positions_closed": 0,
            "total_pnl": 0.0,
            "start_time": self.start_time
        }
        
        # Cycle tasks
        self.cycle_tasks: List[asyncio.Task] = []
        
        # Heartbeat task
        self.heartbeat_task: Optional[asyncio.Task] = None
    
    async def start_trading_engine(self):
        """Start the complete trading engine."""
        try:
            self.logger.info("🚀 Starting Complete Trading Engine...")
            self.state = TradingState.STARTING
            self.is_running = True
            
            # Try to start communication hub if available, otherwise skip
            if self.comm_hub is not None:
                try:
                    await self.comm_hub.start()
                    self.logger.info("✅ Communication hub started")
                except Exception as e:
                    self.logger.warning(f"⚠️ Communication hub start failed: {e}")
                    self.comm_hub = None
            else:
                self.logger.info("ℹ️ No communication hub available, using direct Redis communication")
            
            # Initialize shared utilities (with fallback)
            try:
                self.redis_conn = get_shared_redis()
            except Exception as e:
                self.logger.warning(f"⚠️ Could not initialize Redis connection: {e}")
                self.redis_conn = None
                
            try:
                self.timing_coordinator = get_timing_coordinator()
            except Exception as e:
                self.logger.warning(f"⚠️ Could not initialize timing coordinator: {e}")
                self.timing_coordinator = SimplifiedTimingCoordinator()
            
            # Register with communication hub if available
            if self.comm_hub is not None:
                try:
                    self.comm_hub.register_agent("trading_engine", {
                        "class": "TradingEngine",
                        "business_focus": "Complete trading system with 4-tier architecture",
                        "capabilities": ["position_management", "strategy_execution", "risk_management"]
                    })
                    self.logger.info("✅ Registered with communication hub")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to register with communication hub: {e}")
            else:
                self.logger.info("ℹ️ No communication hub to register with")
            
            # Start all 4 tiers
            self.cycle_tasks = [
                asyncio.create_task(self._ultra_hft_cycle(), name="ultra_hft"),
                asyncio.create_task(self._fast_cycle(), name="fast"),
                asyncio.create_task(self._tactical_cycle(), name="tactical"),
                asyncio.create_task(self._strategic_cycle(), name="strategic"),
                asyncio.create_task(self._position_manager(), name="position_manager"),
                asyncio.create_task(self._command_processor(), name="command_processor"),
                asyncio.create_task(self._status_reporter(), name="status_reporter"),
                asyncio.create_task(self._system_health_check(), name="system_health_check")
            ]
            
            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self._heartbeat_updater())
            
            self.state = TradingState.RUNNING
            self.logger.info("✅ Trading Engine started with 4-tier architecture")
            
            # Signal that trading engine is ready for execution engine
            if self.redis_conn:
                try:
                    self.redis_conn.set('trading_engine_ready', 'true', ex=3600)  # 1 hour expiry
                    self.logger.info("✅ Trading engine ready signal sent to execution engine")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not send ready signal: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start trading engine: {e}")
            self.state = TradingState.ERROR
            return False
    
    async def stop_trading_engine(self):
        """Stop the trading engine gracefully."""
        try:
            self.logger.info("🛑 Stopping Trading Engine...")
            self.is_running = False
            self.state = TradingState.STOPPED
            
            # Cancel all cycle tasks
            for task in self.cycle_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            self.cycle_tasks.clear()
            
            # Cancel heartbeat task
            if self.heartbeat_task and not self.heartbeat_task.done():
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            # Close all open positions
            await self._close_all_positions()
            
            self.logger.info("✅ Trading Engine stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping trading engine: {e}")
    
    async def _ultra_hft_cycle(self):
        """TIER 1: Ultra-HFT cycle - 1ms execution for arbitrage."""
        while self.is_running:
            try:
                cycle_start = time.time()
                
                # Process ultra-fast opportunities
                await self._process_ultra_hft_signals()
                
                # Update stats
                self.stats["ultra_hft_cycles"] += 1
                self.stats["total_cycles"] += 1
                self.stats["successful_cycles"] += 1
                
                # Maintain 1ms timing
                elapsed = (time.time() - cycle_start) * 1000
                if elapsed < 1:
                    await asyncio.sleep((1 - elapsed) / 1000)
                
            except Exception as e:
                self.logger.error(f"❌ Ultra-HFT cycle error: {e}")
                self.stats["failed_cycles"] += 1
                await asyncio.sleep(0.001)
    
    async def _fast_cycle(self):
        """TIER 2: Fast cycle - 100ms for dynamic strategy signals."""
        while self.is_running:
            try:
                cycle_start = time.time()
                
                # Process fast trading signals
                await self._process_fast_signals()
                
                # Update stats
                self.stats["fast_cycles"] += 1
                self.stats["total_cycles"] += 1
                self.stats["successful_cycles"] += 1
                
                # Maintain 100ms timing
                elapsed = time.time() - cycle_start
                if elapsed < 0.1:
                    await asyncio.sleep(0.1 - elapsed)
                
            except Exception as e:
                self.logger.error(f"❌ Fast cycle error: {e}")
                self.stats["failed_cycles"] += 1
                await asyncio.sleep(0.1)
    
    async def _tactical_cycle(self):
        """TIER 3: Tactical cycle - 30s for market analysis."""
        while self.is_running:
            try:
                cycle_start = time.time()
                
                # Market analysis and coordination
                await self._process_tactical_analysis()
                
                # Update stats
                self.stats["tactical_cycles"] += 1
                self.stats["total_cycles"] += 1
                self.stats["successful_cycles"] += 1
                
                # 30 second cycle
                elapsed = time.time() - cycle_start
                if elapsed < 30:
                    await asyncio.sleep(30 - elapsed)
                
            except Exception as e:
                self.logger.error(f"❌ Tactical cycle error: {e}")
                self.stats["failed_cycles"] += 1
                await asyncio.sleep(30)
    
    async def _strategic_cycle(self):
        """TIER 4: Strategic cycle - 5min for portfolio optimization."""
        while self.is_running:
            try:
                cycle_start = time.time()
                
                # Portfolio optimization and strategy review
                await self._process_strategic_planning()
                
                # Update stats
                self.stats["strategic_cycles"] += 1
                self.stats["total_cycles"] += 1
                self.stats["successful_cycles"] += 1
                
                # 5 minute cycle
                elapsed = time.time() - cycle_start
                if elapsed < 300:
                    await asyncio.sleep(300 - elapsed)
                
            except Exception as e:
                self.logger.error(f"❌ Strategic cycle error: {e}")
                self.stats["failed_cycles"] += 1
                await asyncio.sleep(300)
    
    async def _check_position_health(self):
        """Check the health of all active positions."""
        try:
            for position_id, position in list(self.active_positions.items()):
                # Check if position has been open too long
                if "created_at" in position:
                    age = time.time() - position["created_at"]
                    if age > 3600:  # 1 hour
                        self.logger.warning(f"⚠️ Position {position_id} has been open for {age:.0f}s")
                
                # Check position status
                if position.get("status") == PositionStatus.ERROR.value:
                    self.logger.error(f"❌ Position {position_id} has error status")
                    
        except Exception as e:
            self.logger.error(f"❌ Error checking position health: {e}")

    async def _position_manager(self):
        """Position management loop - monitors and manages all positions."""
        while self.is_running:
            try:
                # Check position health
                await self._check_position_health()
                
                # Process position updates
                await self._process_position_updates()
                
                # Update position statistics
                await self._update_position_stats()
                
                # Sleep for 1 second
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ Position manager error: {e}")
                await asyncio.sleep(1)
    
    async def _process_ultra_hft_signals(self):
        """Process ultra-HFT signals from Redis."""
        try:
            if not self.redis_conn:
                return
                
            # Get signals from Redis
            signals = self.redis_conn.lrange("hft_signals", 0, 9)  # Last 10 signals
            
            for signal_data in signals:
                try:
                    signal = json.loads(signal_data)
                    await self._handle_hft_signals(signal)
                except Exception as e:
                    self.logger.error(f"❌ Error processing HFT signal: {e}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error in ultra-HFT signal processing: {e}")

    async def _process_fast_signals(self):
        """Process fast signals from Redis."""
        try:
            if not self.redis_conn:
                return
                
            # Get signals from Redis
            signals = self.redis_conn.lrange("fast_signals", 0, 9)  # Last 10 signals
            
            for signal_data in signals:
                try:
                    signal = json.loads(signal_data)
                    await self._handle_fast_signals(signal)
                except Exception as e:
                    self.logger.error(f"❌ Error processing fast signal: {e}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error in fast signal processing: {e}")

    async def _process_tactical_analysis(self):
        """Process tactical analysis from Redis."""
        try:
            if not self.redis_conn:
                return
                
            # Get tactical signals from Redis
            signals = self.redis_conn.lrange("tactical_signals", 0, 9)  # Last 10 signals
            
            for signal_data in signals:
                try:
                    signal = json.loads(signal_data)
                    await self._handle_tactical_signals(signal)
                except Exception as e:
                    self.logger.error(f"❌ Error processing tactical signal: {e}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error in tactical analysis: {e}")
    
    async def _process_strategic_planning(self):
        """Process strategic planning and optimization."""
        try:
            # Portfolio optimization
            await self._optimize_portfolio()
            
            # Strategy performance review
            await self._review_strategy_performance()
            
            # System health check
            await self._system_health_check()
            
            # Update strategic stats
            if self.redis_conn:
                self.redis_conn.hset("trading_stats", {"last_strategic_cycle": str(time.time())})
                
        except Exception as e:
            self.logger.error(f"❌ Strategic planning error: {e}")
    
    async def _analyze_market_conditions(self):
        """Analyze current market conditions."""
        try:
            # Request market analysis from market conditions agent
            if self.redis_conn:
                analysis_request = {
                    "type": "market_analysis",
                    "timestamp": time.time()
                }
                self.redis_conn.lpush("market_analysis_requests", json.dumps(analysis_request))
                
        except Exception as e:
            self.logger.error(f"❌ Market analysis error: {e}")
    
    async def _coordinate_agents(self):
        """Coordinate activities between agents."""
        try:
            # Check agent health and coordination
            if self.redis_conn:
                coordination_message = {
                    "type": "health_check",
                    "timestamp": time.time()
                }
                self.redis_conn.lpush("coordination_messages", json.dumps(coordination_message))
                
        except Exception as e:
            self.logger.error(f"❌ Agent coordination error: {e}")
    
    async def _assess_portfolio_risk(self):
        """Assess current portfolio risk."""
        try:
            # Request risk assessment from risk management agent
            if self.redis_conn:
                risk_request = {
                    "type": "portfolio_risk_assessment",
                    "timestamp": time.time()
                }
                self.redis_conn.lpush("risk_assessment_requests", json.dumps(risk_request))
                
        except Exception as e:
            self.logger.error(f"❌ Risk assessment error: {e}")
    
    async def _optimize_portfolio(self):
        """Optimize portfolio allocation."""
        try:
            # Request portfolio optimization
            if self.redis_conn:
                optimization_request = {
                    "type": "portfolio_optimization",
                    "timestamp": time.time()
                }
                self.redis_conn.lpush("optimization_requests", json.dumps(optimization_request))
                
        except Exception as e:
            self.logger.error(f"❌ Portfolio optimization error: {e}")
    
    async def _review_strategy_performance(self):
        """Review and analyze strategy performance."""
        try:
            # Get performance data and analyze
            if self.redis_conn:
                performance_data = self.redis_conn.hgetall("strategy_performance")
                
                # Log performance summary
                if performance_data:
                    self.logger.info(f"📊 Strategy Performance Review: {len(performance_data)} metrics")
                
        except Exception as e:
            self.logger.error(f"❌ Performance review error: {e}")
    
    async def _system_health_check(self):
        """Perform comprehensive system health check."""
        while self.is_running:
            try:
                # Check all agents are healthy using agent_stats keys (Redis hashes)
                if self.redis_conn:
                    agent_count = 0
                    healthy_agents = 0
                    
                    agent_names = [
                        "communication_hub", "data_feeds", "adapters", "strategy_engine",
                        "risk_management", "execution", "validation", "intelligence",
                        "market_conditions", "core", "fees_monitor", "failure_prevention",
                        "trading_engine"
                    ]
                    
                    for agent in agent_names:
                        agent_count += 1
                        # Check agent_stats key (Redis hash) first
                        agent_stats = self.redis_conn.hgetall(f"agent_stats:{agent}")
                        if agent_stats:
                            try:
                                # Check if agent is running and has recent heartbeat
                                status = agent_stats.get('status', '')  # Fixed: use string key, not bytes
                                last_heartbeat = float(agent_stats.get('last_heartbeat', 0)) if agent_stats.get('last_heartbeat') else 0  # Fixed: use string key, not bytes
                                current_time = time.time()
                                
                                self.logger.info(f"Agent {agent}: status={status}, last_heartbeat={last_heartbeat}, time_diff={current_time - last_heartbeat}")
                                
                                if status == 'running' and (current_time - last_heartbeat) < 300:  # 5 minutes
                                    healthy_agents += 1
                                    self.logger.info(f"✅ {agent} healthy")
                                else:
                                    self.logger.info(f"❌ {agent} not healthy: status={status}, heartbeat_age={current_time - last_heartbeat:.1f}s")
                            except (ValueError, AttributeError) as e:
                                self.logger.error(f"Error parsing {agent} stats: {e}")
                                # Fallback to heartbeat check if agent_stats parsing fails
                                heartbeat = self.redis_conn.get(f"heartbeat:{agent}")
                                if heartbeat and (time.time() - float(heartbeat)) < 300:
                                    healthy_agents += 1
                                    self.logger.info(f"✅ {agent} healthy via heartbeat fallback")
                        else:
                            self.logger.warning(f"No agent_stats found for {agent}")
                            # Fallback to heartbeat check if no agent_stats
                            heartbeat = self.redis_conn.get(f"heartbeat:{agent}")
                            if heartbeat and (time.time() - float(heartbeat)) < 300:
                                healthy_agents += 1
                                self.logger.info(f"✅ {agent} healthy via heartbeat fallback")
                            else:
                                self.logger.warning(f"❌ {agent} not healthy via heartbeat")
                    
                    health_percentage = (healthy_agents / agent_count) * 100 if agent_count > 0 else 0
                    
                    self.logger.info(f"📊 Health Check Summary: agent_count={agent_count}, healthy_agents={healthy_agents}, health_percentage={health_percentage:.1f}%")
                    
                    # Update system health stats
                    self.redis_conn.hset("system_health", {
                        "total_agents": str(agent_count),
                        "healthy_agents": str(healthy_agents),
                        "health_percentage": str(health_percentage),
                        "last_check": str(time.time())
                    })
                    
                    self.logger.info(f"🏥 System Health: {healthy_agents}/{agent_count} agents healthy ({health_percentage:.1f}%)")
                
                # Run health check every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"❌ System health check error: {e}")
                await asyncio.sleep(30)
    
    async def _heartbeat_updater(self):
        """Update trading engine heartbeat regularly."""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Update heartbeat in Redis
                if self.redis_conn:
                    self.redis_conn.set(f"heartbeat:trading_engine", current_time)
                    
                    # Update agent_stats like other agents do
                    agent_stats = {
                        'status': 'running' if self.is_running else 'stopped',
                        'start_time': str(self.stats.get("start_time", current_time)),
                        'uptime_seconds': str(int(current_time - self.stats.get("start_time", current_time))),
                        'last_heartbeat': str(current_time),
                        'timestamp': str(current_time)
                    }
                    self.redis_conn.hset(f"agent_stats:trading_engine", mapping=agent_stats)
                
                # Update heartbeat through communication hub if available
                if self.comm_hub is not None:
                    try:
                        self.comm_hub.update_heartbeat("trading_engine")
                    except Exception as e:
                        self.logger.debug(f"Heartbeat update failed: {e}")
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Heartbeat updater error: {e}")
                await asyncio.sleep(30)
    
    async def _command_processor(self):
        """Process commands from the API."""
        while self.is_running:
            try:
                if self.redis_conn:
                    # Check for new commands
                    command_data = self.redis_conn.rpop("trading_commands")
                    
                    if command_data:
                        try:
                            command = json.loads(command_data)
                            await self._execute_command(command)
                        except json.JSONDecodeError:
                            pass
                
                await asyncio.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                self.logger.error(f"❌ Command processor error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_command(self, command: Dict[str, Any]):
        """Execute a trading command."""
        try:
            action = command.get("action")
            target = command.get("target")
            
            self.logger.info(f"🎯 Executing command: {action} on {target}")
            
            if action == "stop" and target == "trading":
                await self.stop_trading_engine()
            elif action == "pause" and target == "trading":
                self.state = TradingState.PAUSED
            elif action == "resume" and target == "trading":
                self.state = TradingState.RUNNING
            
            # Log command execution
            if self.redis_conn:
                self.redis_conn.lpush("command_history", json.dumps({
                    "command": command,
                    "executed_at": time.time(),
                    "status": "completed"
                }))
                
        except Exception as e:
            self.logger.error(f"❌ Command execution error: {e}")
    
    async def _status_reporter(self):
        """Report trading engine status regularly."""
        while self.is_running:
            try:
                # Calculate performance metrics
                uptime = time.time() - self.stats["start_time"]
                success_rate = (self.stats["successful_cycles"] / max(self.stats["total_cycles"], 1)) * 100
                
                # Update status in Redis
                if self.redis_conn:
                    status_data = {
                        "state": self.state.value,
                        "uptime": uptime,
                        "total_cycles": self.stats["total_cycles"],
                        "successful_cycles": self.stats["successful_cycles"],
                        "failed_cycles": self.stats["failed_cycles"],
                        "success_rate": success_rate,
                        "ultra_hft_cycles": self.stats["ultra_hft_cycles"],
                        "fast_cycles": self.stats["fast_cycles"],
                        "tactical_cycles": self.stats["tactical_cycles"],
                        "strategic_cycles": self.stats["strategic_cycles"],
                        "positions_opened": self.stats["positions_opened"],
                        "positions_closed": self.stats["positions_closed"],
                        "total_pnl": self.stats["total_pnl"],
                        "active_positions": len(self.active_positions),
                        "last_update": time.time()
                    }
                    
                    for key, value in status_data.items():
                        self.redis_conn.hset("trading_stats", {key: str(value)})
                
                # Log status every 5 minutes
                if int(uptime) % 300 == 0:
                    self.logger.info(f"📊 Trading Engine Status: {self.stats['total_cycles']} cycles, {success_rate:.1f}% success rate, {len(self.active_positions)} active positions")
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Status reporter error: {e}")
                await asyncio.sleep(10)
    
    async def _process_position_updates(self):
        """Process position updates from execution agent."""
        try:
            if self.redis_conn:
                # Get position updates
                updates = self.redis_conn.lrange("position_updates", 0, 9)
                
                for update_data in updates:
                    try:
                        update = json.loads(update_data)
                        position_id = update.get("position_id")
                        
                        if position_id in self.active_positions:
                            # Update position
                            self.active_positions[position_id].update(update.get("updates", {}))
                            
                            # Remove processed update
                            self.redis_conn.lrem("position_updates", 1, update_data)
                            
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            self.logger.error(f"❌ Position update processing error: {e}")
    
    async def _update_position_stats(self):
        """Update position statistics."""
        try:
            if self.redis_conn:
                # Calculate position stats
                total_positions = len(self.active_positions)
                long_positions = len([p for p in self.active_positions.values() if p["direction"] == "long"])
                short_positions = total_positions - long_positions
                
                # Update Redis
                self.redis_conn.hset("position_stats", {
                    "total_positions": str(total_positions),
                    "long_positions": str(long_positions),
                    "short_positions": str(short_positions),
                    "last_update": str(time.time())
                })
                
        except Exception as e:
            self.logger.error(f"❌ Position stats update error: {e}")
    
    async def _execute_arbitrage(self, signal: Dict[str, Any]):
        """Execute arbitrage opportunity."""
        try:
            # Send to execution agent via Redis
            if self.redis_conn:
                execution_order = {
                    "type": "arbitrage",
                    "signal": signal,
                    "timestamp": time.time(),
                    "priority": "ultra_high"
                }
                self.redis_conn.lpush("execution_orders", json.dumps(execution_order))
                
        except Exception as e:
            self.logger.error(f"❌ Arbitrage execution error: {e}")
    
    async def _execute_market_making(self, signal: Dict[str, Any]):
        """Execute market making strategy."""
        try:
            # Send to execution agent via Redis
            if self.redis_conn:
                execution_order = {
                    "type": "market_making",
                    "signal": signal,
                    "timestamp": time.time(),
                    "priority": "high"
                }
                self.redis_conn.lpush("execution_orders", json.dumps(execution_order))
                
        except Exception as e:
            self.logger.error(f"❌ Market making execution error: {e}")
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive trading engine status."""
        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "uptime": time.time() - self.start_time,
            "stats": self.stats,
            "active_positions": len(self.active_positions),
            "position_history": len(self.position_history),
            "total_pnl": self.stats["total_pnl"]
        }
    
    def is_redis_available(self) -> bool:
        """Check if Redis connection is available."""
        return self.redis_conn is not None
    
    def get_redis_status(self) -> Dict[str, Any]:
        """Get Redis connection status."""
        return {
            "available": self.is_redis_available(),
            "connection_type": "redis" if self.is_redis_available() else "none"
        }

    async def _start_communication_system(self):
        """Start the communication system for agent integration."""
        try:
            # Initialize Redis channel manager
            from .communication.redis_channel_manager import RedisChannelManager
            from .communication.message_formats import MessageType, MessagePriority
            
            # Create channel manager
            redis_config = {
                "host": "localhost",
                "port": 6379,
                "db": 0
            }
            
            self.channel_manager = RedisChannelManager(redis_config)
            await self.channel_manager.initialize()
            await self.channel_manager.start()
            
            # Subscribe to agent channels
            await self.channel_manager.subscribe_to_channel(
                "hft_signals", 
                self._handle_hft_signals
            )
            await self.channel_manager.subscribe_to_channel(
                "fast_signals", 
                self._handle_fast_signals
            )
            await self.channel_manager.subscribe_to_channel(
                "tactical_signals", 
                self._handle_tactical_signals
            )
            
            self.logger.info("✅ Communication system started")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start communication system: {e}")
            return False

    async def _handle_hft_signals(self, message: Dict[str, Any]):
        """Handle ultra-HFT signals from agents."""
        try:
            # Process HFT signal immediately
            signal_type = message.get("action")
            if signal_type == "arbitrage":
                await self._execute_arbitrage(message)
            elif signal_type == "market_making":
                await self._execute_market_making(message)
            
            self.logger.info(f"🚀 Processed HFT signal: {signal_type}")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing HFT signal: {e}")

    async def _handle_fast_signals(self, message: Dict[str, Any]):
        """Handle fast execution signals from agents."""
        try:
            # Process fast signal
            strategy = message.get("strategy")
            action = message.get("action")
            
            if action in ["buy", "sell"]:
                # Create position
                position = {
                    "symbol": message.get("symbol", "UNKNOWN"),
                    "action": action,
                    "direction": action,  # Direction for closing positions
                    "entry_price": message.get("entry_price"),
                    "stop_loss": message.get("stop_loss"),
                    "take_profit": message.get("take_profit"),
                    "quantity": message.get("quantity", 0.01),  # Default to 0.01 lot size
                    "strategy": strategy,
                    "confidence": message.get("confidence", 0.5),
                    "timestamp": time.time()
                }
                
                await self._open_position(position)
                self.logger.info(f"📈 Opened {action} position for {strategy}")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing fast signal: {e}")

    async def _handle_tactical_signals(self, message: Dict[str, Any]):
        """Handle tactical signals from agents."""
        try:
            # Process tactical signal
            signal_type = message.get("action")
            
            if signal_type == "market_anomaly":
                await self._handle_market_anomaly(message)
            elif signal_type == "regime_change":
                await self._handle_regime_change(message)
            
            self.logger.info(f"📊 Processed tactical signal: {signal_type}")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing tactical signal: {e}")

    async def _handle_market_anomaly(self, message: Dict[str, Any]):
        """Handle market anomaly signals."""
        try:
            anomaly_type = message.get("anomaly_type")
            severity = message.get("severity", "medium")
            
            if severity == "high":
                # Close all positions immediately
                await self._close_all_positions()
                self.logger.warning(f"🚨 High severity anomaly: {anomaly_type}")
            else:
                # Reduce position sizes
                self.logger.info(f"⚠️ Market anomaly detected: {anomaly_type}")
                
        except Exception as e:
            self.logger.error(f"❌ Error handling market anomaly: {e}")

    async def _handle_regime_change(self, message: Dict[str, Any]):
        """Handle market regime change signals."""
        try:
            new_regime = message.get("new_regime")
            confidence = message.get("confidence", 0.5)
            
            if confidence > 0.7:
                # Adjust strategy parameters
                self.logger.info(f"🔄 Market regime change: {new_regime}")
            else:
                # Monitor closely
                self.logger.info(f"👀 Potential regime change: {new_regime}")
                
        except Exception as e:
            self.logger.error(f"❌ Error handling regime change: {e}")

    async def _open_position(self, position: Dict[str, Any]):
        """Open a new trading position."""
        try:
            position_id = f"pos_{int(time.time() * 1000)}"
            position["id"] = position_id
            position["status"] = PositionStatus.OPENING.value
            position["opened_at"] = time.time()
            
            # Add to active positions
            self.active_positions[position_id] = position
            
            # Send order to execution agent
            if self.redis_conn:
                execution_order = {
                    "action": position.get("action", "buy"),
                    "symbol": position.get("symbol"),
                    "quantity": position.get("quantity", 0.01),
                    "price": position.get("entry_price"),
                    "stop_loss": position.get("stop_loss"),
                    "take_profit": position.get("take_profit"),
                    "strategy": position.get("strategy", "unknown"),
                    "position_id": position_id,
                    "timestamp": time.time()
                }
                self.redis_conn.lpush("execution_orders", json.dumps(execution_order))
            
            # Update statistics
            self.stats["positions_opened"] += 1
            
            self.logger.info(f"📈 Opening position {position_id}: {position.get('action')} {position.get('symbol')}")
            
        except Exception as e:
            self.logger.error(f"❌ Error opening position: {e}")
    
    async def _close_position(self, position_id: str, reason: str = "manual"):
        """Close a specific trading position."""
        try:
            if position_id not in self.active_positions:
                self.logger.warning(f"⚠️ Position {position_id} not found in active positions")
                return
            
            position = self.active_positions[position_id]
            position["status"] = PositionStatus.CLOSING.value
            position["closed_at"] = time.time()
            position["close_reason"] = reason
            
            # Send close order to execution agent
            if self.redis_conn:
                close_order = {
                    "action": "close",
                    "position_id": position_id,
                    "symbol": position.get("symbol"),
                    "direction": position.get("direction"),
                    "quantity": position.get("quantity"),
                    "reason": reason,
                    "timestamp": time.time()
                }
                self.redis_conn.lpush("execution_orders", json.dumps(close_order))
            
            # Move to position history
            self.position_history[position_id] = position
            del self.active_positions[position_id]
            
            # Update statistics
            self.stats["positions_closed"] += 1
            
            self.logger.info(f"📉 Closed position {position_id}: {reason}")
            
        except Exception as e:
            self.logger.error(f"❌ Error closing position {position_id}: {e}")
    
    async def _close_all_positions(self):
        """Close all active positions immediately."""
        try:
            if not self.active_positions:
                self.logger.info("ℹ️ No active positions to close")
                return
            
            self.logger.warning(f"🚨 Closing all {len(self.active_positions)} active positions")
            
            for position_id, position in list(self.active_positions.items()):
                try:
                    # Mark position as closing
                    position["status"] = PositionStatus.CLOSING.value
                    position["closed_at"] = time.time()
                    
                    # Send close order to execution agent
                    if self.redis_conn:
                        close_order = {
                            "action": "close",
                            "position_id": position_id,
                            "symbol": position.get("symbol"),
                            "direction": position.get("direction"),
                            "quantity": position.get("quantity"),
                            "reason": "emergency_close",
                            "timestamp": time.time()
                        }
                        self.redis_conn.lpush("execution_orders", json.dumps(close_order))
                    
                    # Move to position history
                    self.position_history[position_id] = position
                    del self.active_positions[position_id]
                    
                    self.logger.info(f"✅ Closed position {position_id}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Error closing position {position_id}: {e}")
            
            self.logger.info(f"✅ All positions closed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error in _close_all_positions: {e}")


# Global trading engine instance
trading_engine = TradingEngine()

# Main execution block
if __name__ == "__main__":
    import asyncio
    
    async def test_trading_engine():
        """Test the trading engine functionality."""
        print("🧪 Testing Trading Engine...")
        
        # Test instantiation
        print(f"✅ Engine state: {trading_engine.state.value}")
        print(f"✅ Redis available: {trading_engine.is_redis_available()}")
        print(f"✅ Active positions: {len(trading_engine.active_positions)}")
        
        # Test starting
        print("\n🚀 Starting Trading Engine...")
        success = await trading_engine.start_trading_engine()
        
        if success:
            print("✅ Trading Engine started successfully")
            
            # Run for a few seconds to test
            print("⏱️ Running for 5 seconds...")
            await asyncio.sleep(5)
            
            # Get status
            status = trading_engine.get_engine_status()
            print(f"📊 Status: {status['state']}, Cycles: {status['stats']['total_cycles']}")
            
            # Stop
            print("\n🛑 Stopping Trading Engine...")
            await trading_engine.stop_trading_engine()
            print("✅ Trading Engine stopped")
        else:
            print("❌ Failed to start Trading Engine")
    
    async def main():
        """Main execution function."""
        try:
            # Run test first
            await test_trading_engine()
            
            # Then start normal operation
            print("\n🚀 Starting Normal Trading Engine Operation...")
            success = await trading_engine.start_trading_engine()
            
            if success:
                print("✅ Trading Engine started successfully")
                
                # Keep running until interrupted
                try:
                    while trading_engine.is_running:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down Trading Engine...")
                    await trading_engine.stop_trading_engine()
                    print("✅ Trading Engine stopped")
            else:
                print("❌ Failed to start Trading Engine")
                
        except Exception as e:
            print(f"❌ Error in main execution: {e}")
            await trading_engine.stop_trading_engine()
    
    # Run the main function
    asyncio.run(main())
