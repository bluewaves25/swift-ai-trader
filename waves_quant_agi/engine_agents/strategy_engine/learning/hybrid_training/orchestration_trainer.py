#!/usr/bin/env python3
"""
Orchestration Trainer
Coordinates training across multiple learning components and strategies.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from ....shared_utils import get_shared_logger, get_shared_redis

class OrchestrationTrainer:
    """Coordinates training across multiple learning components."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "orchestration_trainer")
        self.redis_conn = get_shared_redis()
        
        # Training configuration
        self.training_interval = config.get("training_interval", 3600)  # 1 hour
        self.max_concurrent_training = config.get("max_concurrent_training", 3)
        self.min_training_data = config.get("min_training_data", 100)
        self.training_timeout = config.get("training_timeout", 1800)  # 30 minutes
        
        # Training state
        self.active_training_sessions: Dict[str, Dict[str, Any]] = {}
        self.training_queue: List[Dict[str, Any]] = []
        self.training_history: List[Dict[str, Any]] = []
        
        # Training statistics
        self.stats = {
            "training_sessions_started": 0,
            "training_sessions_completed": 0,
            "training_sessions_failed": 0,
            "total_training_time": 0.0,
            "start_time": time.time()
        }

    async def start_orchestration(self):
        """Start the orchestration training process."""
        try:
            self.logger.info("🚀 Starting Orchestration Trainer...")
            
            # Start background training loop
            asyncio.create_task(self._training_orchestration_loop())
            
            # Start training queue processor
            asyncio.create_task(self._process_training_queue())
            
            self.logger.info("✅ Orchestration Trainer started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting orchestration trainer: {e}")

    async def _training_orchestration_loop(self):
        """Main training orchestration loop."""
        while True:
            try:
                # Check for training opportunities
                await self._identify_training_opportunities()
                
                # Schedule training sessions
                await self._schedule_training_sessions()
                
                # Monitor active training sessions
                await self._monitor_training_sessions()
                
                # Wait for next cycle
                await asyncio.sleep(self.training_interval)
                
            except Exception as e:
                self.logger.error(f"Error in training orchestration loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def _identify_training_opportunities(self):
        """Identify strategies and components that need training."""
        try:
            # Get strategy performance data
            performance_data = await self._get_strategy_performance_data()
            
            # Get market condition data
            market_data = await self._get_market_condition_data()
            
            # Identify training candidates
            training_candidates = await self._analyze_training_candidates(performance_data, market_data)
            
            # Add to training queue
            for candidate in training_candidates:
                if candidate not in self.training_queue:
                    self.training_queue.append(candidate)
                    self.logger.info(f"Added training candidate: {candidate['strategy_id']}")
            
        except Exception as e:
            self.logger.error(f"Error identifying training opportunities: {e}")

    async def _analyze_training_candidates(self, performance_data: Dict[str, Any], 
                                        market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze and rank training candidates."""
        try:
            candidates = []
            
            # Check strategy performance
            for strategy_id, performance in performance_data.items():
                if await self._needs_training(strategy_id, performance, market_data):
                    candidate = {
                        "strategy_id": strategy_id,
                        "training_type": "performance_optimization",
                        "priority": self._calculate_training_priority(performance),
                        "estimated_duration": 1800,  # 30 minutes
                        "timestamp": int(time.time())
                    }
                    candidates.append(candidate)
            
            # Sort by priority (highest first)
            candidates.sort(key=lambda x: x["priority"], reverse=True)
            
            return candidates
            
        except Exception as e:
            self.logger.error(f"Error analyzing training candidates: {e}")
            return []

    async def _needs_training(self, strategy_id: str, performance: Dict[str, Any], 
                            market_data: Dict[str, Any]) -> bool:
        """Check if a strategy needs training."""
        try:
            # Check performance metrics
            success_rate = performance.get("success_rate", 0.5)
            avg_pnl = performance.get("avg_pnl", 0.0)
            last_training = performance.get("last_training", 0)
            
            # Check if performance is below threshold
            if success_rate < 0.6 or avg_pnl < 0:
                return True
            
            # Check if training is overdue
            if time.time() - last_training > 86400:  # 24 hours
                return True
            
            # Check market condition changes
            if await self._market_conditions_changed(market_data):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking training need: {e}")
            return False

    def _calculate_training_priority(self, performance: Dict[str, Any]) -> float:
        """Calculate training priority based on performance."""
        try:
            success_rate = performance.get("success_rate", 0.5)
            avg_pnl = performance.get("avg_pnl", 0.0)
            volatility = performance.get("volatility", 0.0)
            
            # Base priority
            priority = 0.5
            
            # Adjust based on success rate
            if success_rate < 0.5:
                priority += 0.3
            elif success_rate < 0.7:
                priority += 0.1
            
            # Adjust based on PnL
            if avg_pnl < 0:
                priority += 0.2
            
            # Adjust based on volatility
            if volatility > 0.05:
                priority += 0.1
            
            return min(1.0, priority)
            
        except Exception as e:
            self.logger.error(f"Error calculating training priority: {e}")
            return 0.5

    async def _market_conditions_changed(self, market_data: Dict[str, Any]) -> bool:
        """Check if market conditions have changed significantly."""
        try:
            # Get previous market conditions
            previous_conditions = await self._get_previous_market_conditions()
            
            if not previous_conditions:
                return False
            
            # Calculate change score
            change_score = self._calculate_market_change_score(previous_conditions, market_data)
            
            return change_score > 0.3  # 30% change threshold
            
        except Exception as e:
            self.logger.error(f"Error checking market conditions: {e}")
            return False

    def _calculate_market_change_score(self, previous: Dict[str, Any], current: Dict[str, Any]) -> float:
        """Calculate market change score."""
        try:
            if not previous or not current:
                return 0.0
            
            change_score = 0.0
            
            # Compare key metrics
            for key in ["volatility", "trend_strength", "volume_profile"]:
                prev_val = previous.get(key, 0.0)
                curr_val = current.get(key, 0.0)
                
                if prev_val != 0:
                    change = abs(curr_val - prev_val) / abs(prev_val)
                    change_score += change
            
            return change_score / 3  # Average change score
            
        except Exception as e:
            self.logger.error(f"Error calculating market change score: {e}")
            return 0.0

    async def _schedule_training_sessions(self):
        """Schedule training sessions from the queue."""
        try:
            # Check if we can start more training sessions
            available_slots = self.max_concurrent_training - len(self.active_training_sessions)
            
            if available_slots <= 0:
                return
            
            # Get top priority candidates
            candidates = sorted(self.training_queue, key=lambda x: x["priority"], reverse=True)
            
            for candidate in candidates[:available_slots]:
                if await self._start_training_session(candidate):
                    # Remove from queue
                    self.training_queue.remove(candidate)
                    
        except Exception as e:
            self.logger.error(f"Error scheduling training sessions: {e}")

    async def _start_training_session(self, candidate: Dict[str, Any]) -> bool:
        """Start a training session for a candidate."""
        try:
            strategy_id = candidate["strategy_id"]
            training_type = candidate["training_type"]
            
            # Check if strategy is already being trained
            if strategy_id in self.active_training_sessions:
                return False
            
            # Start training session
            session_id = f"training_{strategy_id}_{int(time.time())}"
            
            training_session = {
                "session_id": session_id,
                "strategy_id": strategy_id,
                "training_type": training_type,
                "start_time": time.time(),
                "status": "running",
                "progress": 0.0
            }
            
            # Add to active sessions
            self.active_training_sessions[strategy_id] = training_session
            
            # Start training task
            asyncio.create_task(self._execute_training_session(training_session))
            
            # Update statistics
            self.stats["training_sessions_started"] += 1
            
            self.logger.info(f"Started training session {session_id} for strategy {strategy_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting training session: {e}")
            return False

    async def _execute_training_session(self, training_session: Dict[str, Any]):
        """Execute a training session."""
        try:
            strategy_id = training_session["strategy_id"]
            session_id = training_session["session_id"]
            
            self.logger.info(f"Executing training session {session_id}")
            
            # Simulate training process
            for progress in range(0, 101, 10):
                training_session["progress"] = progress / 100.0
                await asyncio.sleep(1)  # Simulate work
            
            # Mark as completed
            training_session["status"] = "completed"
            training_session["end_time"] = time.time()
            training_session["duration"] = training_session["end_time"] - training_session["start_time"]
            
            # Update statistics
            self.stats["training_sessions_completed"] += 1
            self.stats["total_training_time"] += training_session["duration"]
            
            # Store training result
            await self._store_training_result(training_session)
            
            # Remove from active sessions
            del self.active_training_sessions[strategy_id]
            
            self.logger.info(f"Training session {session_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error executing training session: {e}")
            
            # Mark as failed
            training_session["status"] = "failed"
            training_session["error"] = str(e)
            training_session["end_time"] = time.time()
            
            # Update statistics
            self.stats["training_sessions_failed"] += 1
            
            # Remove from active sessions
            strategy_id = training_session["strategy_id"]
            if strategy_id in self.active_training_sessions:
                del self.active_training_sessions[strategy_id]

    async def _monitor_training_sessions(self):
        """Monitor active training sessions."""
        try:
            current_time = time.time()
            
            # Check for timeout sessions
            for strategy_id, session in list(self.active_training_sessions.items()):
                if current_time - session["start_time"] > self.training_timeout:
                    self.logger.warning(f"Training session {session['session_id']} timed out")
                    
                    # Mark as failed
                    session["status"] = "failed"
                    session["error"] = "Training timeout"
                    session["end_time"] = current_time
                    
                    # Update statistics
                    self.stats["training_sessions_failed"] += 1
                    
                    # Remove from active sessions
                    del self.active_training_sessions[strategy_id]
                    
        except Exception as e:
            self.logger.error(f"Error monitoring training sessions: {e}")

    async def _process_training_queue(self):
        """Process the training queue."""
        while True:
            try:
                # Process queue every 5 minutes
                await asyncio.sleep(300)
                
                # Re-prioritize queue based on current conditions
                await self._reprioritize_training_queue()
                
            except Exception as e:
                self.logger.error(f"Error processing training queue: {e}")
                await asyncio.sleep(60)

    async def _reprioritize_training_queue(self):
        """Re-prioritize the training queue."""
        try:
            if not self.training_queue:
                return
            
            # Get current performance data
            performance_data = await self._get_strategy_performance_data()
            
            # Re-calculate priorities
            for candidate in self.training_queue:
                strategy_id = candidate["strategy_id"]
                performance = performance_data.get(strategy_id, {})
                candidate["priority"] = self._calculate_training_priority(performance)
            
            # Re-sort queue
            self.training_queue.sort(key=lambda x: x["priority"], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error re-prioritizing training queue: {e}")

    async def _get_strategy_performance_data(self) -> Dict[str, Any]:
        """Get strategy performance data from Redis."""
        try:
            # Get performance data from Redis
            performance_key = "strategy_engine:performance:overall"
            performance_data = self.redis_conn.get(performance_key)
            
            if performance_data:
                import json
                return json.loads(performance_data)
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting strategy performance data: {e}")
            return {}

    async def _get_market_condition_data(self) -> Dict[str, Any]:
        """Get market condition data from Redis."""
        try:
            # Get market conditions from Redis
            conditions_key = "market_conditions:current"
            conditions = self.redis_conn.get(conditions_key)
            
            if conditions:
                import json
                return json.loads(conditions)
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting market condition data: {e}")
            return {}

    async def _get_previous_market_conditions(self) -> Optional[Dict[str, Any]]:
        """Get previous market conditions from Redis."""
        try:
            # Get previous conditions from Redis
            previous_key = "market_conditions:previous"
            previous = self.redis_conn.get(previous_key)
            
            if previous:
                import json
                return json.loads(previous)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting previous market conditions: {e}")
            return None

    async def _store_training_result(self, training_session: Dict[str, Any]):
        """Store training result in Redis."""
        try:
            # Store training result
            result_key = f"strategy_engine:training_results:{training_session['session_id']}"
            self.redis_conn.set(result_key, str(training_session), ex=604800)  # 7 days
            
            # Add to training history
            self.training_history.append(training_session)
            
            # Limit history size
            if len(self.training_history) > 1000:
                self.training_history = self.training_history[-1000:]
                
        except Exception as e:
            self.logger.error(f"Error storing training result: {e}")

    async def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration statistics."""
        return {
            **self.stats,
            "active_training_sessions": len(self.active_training_sessions),
            "training_queue_size": len(self.training_queue),
            "training_history_size": len(self.training_history),
            "uptime": time.time() - self.stats["start_time"]
        }

    async def get_active_training_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active training sessions."""
        return list(self.active_training_sessions.values())

    async def get_training_queue(self) -> List[Dict[str, Any]]:
        """Get current training queue."""
        return self.training_queue.copy()

    async def force_training(self, strategy_id: str, training_type: str = "forced"):
        """Force training for a specific strategy."""
        try:
            # Create forced training candidate
            candidate = {
                "strategy_id": strategy_id,
                "training_type": training_type,
                "priority": 1.0,  # Highest priority
                "estimated_duration": 1800,  # 30 minutes
                "timestamp": int(time.time())
            }
            
            # Add to front of queue
            self.training_queue.insert(0, candidate)
            
            self.logger.info(f"Forced training scheduled for strategy {strategy_id}")
            
        except Exception as e:
            self.logger.error(f"Error forcing training: {e}")

    async def stop_orchestration(self):
        """Stop the orchestration trainer."""
        try:
            self.logger.info("🛑 Stopping Orchestration Trainer...")
            
            # Cancel all active training sessions
            for strategy_id in list(self.active_training_sessions.keys()):
                session = self.active_training_sessions[strategy_id]
                session["status"] = "cancelled"
                session["end_time"] = time.time()
                
                # Store cancelled session
                await self._store_training_result(session)
                
                # Remove from active sessions
                del self.active_training_sessions[strategy_id]
            
            self.logger.info("✅ Orchestration Trainer stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping orchestration trainer: {e}")