#!/usr/bin/env python3
"""
Trading Retraining Loop - Trading Model Retraining Component
Handles periodic retraining of trading models based on performance and market conditions.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque

@dataclass
class RetrainingEvent:
    """A retraining event."""
    event_id: str
    strategy_id: str
    trigger_type: str  # scheduled, performance_based, market_change
    trigger_data: Dict[str, Any]
    status: str = "pending"
    created_at: float = None
    priority: int = 5
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class RetrainingResult:
    """Result of a retraining session."""
    result_id: str
    event_id: str
    strategy_id: str
    trigger_type: str
    original_performance: Dict[str, float]
    new_performance: Dict[str, float]
    improvement: float
    retraining_duration: float
    timestamp: float
    success: bool

class TradingRetrainingLoop:
    """Handles periodic retraining of trading models."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.retraining_queue: deque = deque(maxlen=100)
        self.retraining_results: Dict[str, List[RetrainingResult]] = {}
        self.retraining_history: deque = deque(maxlen=1000)
        self.active_retraining: Dict[str, Dict[str, Any]] = {}
        
        # Retraining settings
        self.retraining_settings = {
            "max_concurrent_retraining": 2,
            "retraining_timeout": 3600,  # 1 hour
            "scheduled_interval": 86400,  # 24 hours
            "performance_threshold": 0.6,
            "improvement_threshold": 0.05,  # 5% improvement required
            "max_retraining_attempts": 3
        }
        
        # Retraining statistics
        self.retraining_stats = {
            "total_retraining": 0,
            "successful_retraining": 0,
            "failed_retraining": 0,
            "average_improvement": 0.0,
            "scheduled_retraining": 0,
            "performance_based_retraining": 0,
            "market_change_retraining": 0
        }
        
        # Training module reference
        self.training_module = None
        
    async def initialize(self):
        """Initialize the trading retraining loop."""
        try:
            # Initialize training module reference
            await self._initialize_training_module()
            
            # Initialize retraining tracking
            await self._initialize_retraining_tracking()
            
            print("✅ Trading Retraining Loop initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Trading Retraining Loop: {e}")
            raise
    
    async def _initialize_training_module(self):
        """Initialize reference to training module."""
        try:
            # Import training module
            from .trading_training_module import TradingTrainingModule
            
            self.training_module = TradingTrainingModule(self.config)
            await self.training_module.initialize()
            
            print("✅ Training module reference initialized")
            
        except Exception as e:
            print(f"❌ Error initializing training module reference: {e}")
            raise
    
    async def _initialize_retraining_tracking(self):
        """Initialize retraining tracking systems."""
        try:
            # Reset retraining statistics
            for key in self.retraining_stats:
                if isinstance(self.retraining_stats[key], (int, float)):
                    self.retraining_stats[key] = 0
            
            print("✅ Retraining tracking initialized")
            
        except Exception as e:
            print(f"❌ Error initializing retraining tracking: {e}")
    
    async def add_retraining_event(self, strategy_id: str, trigger_type: str, 
                                 trigger_data: Dict[str, Any]) -> str:
        """Add a new retraining event to the queue."""
        try:
            # Validate retraining event
            validation_result = await self._validate_retraining_event(strategy_id, trigger_type, trigger_data)
            if not validation_result["valid"]:
                print(f"❌ Retraining event validation failed: {validation_result['error']}")
                return None
            
            # Generate event ID
            event_id = f"retrain_{strategy_id}_{int(time.time())}"
            
            # Create retraining event
            retraining_event = RetrainingEvent(
                event_id=event_id,
                strategy_id=strategy_id,
                trigger_type=trigger_type,
                trigger_data=trigger_data,
                priority=self._calculate_retraining_priority(strategy_id, trigger_type, trigger_data)
            )
            
            # Add to queue
            self.retraining_queue.append(retraining_event)
            
            # Update statistics
            self.retraining_stats["total_retraining"] += 1
            
            if trigger_type == "scheduled":
                self.retraining_stats["scheduled_retraining"] += 1
            elif trigger_type == "performance_based":
                self.retraining_stats["performance_based_retraining"] += 1
            elif trigger_type == "market_change":
                self.retraining_stats["market_change_retraining"] += 1
            
            print(f"✅ Retraining event {event_id} added to queue")
            return event_id
            
        except Exception as e:
            print(f"❌ Error adding retraining event: {e}")
            return None
    
    async def _validate_retraining_event(self, strategy_id: str, trigger_type: str, 
                                       trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate retraining event parameters."""
        try:
            errors = []
            
            # Check strategy ID
            if not strategy_id:
                errors.append("Strategy ID is required")
            
            # Check trigger type
            valid_trigger_types = ["scheduled", "performance_based", "market_change"]
            if trigger_type not in valid_trigger_types:
                errors.append(f"Invalid trigger type: {trigger_type}")
            
            # Check trigger data based on type
            if trigger_type == "performance_based":
                if "performance_metrics" not in trigger_data:
                    errors.append("Performance metrics required for performance-based retraining")
            
            elif trigger_type == "market_change":
                if "market_conditions" not in trigger_data:
                    errors.append("Market conditions required for market-change retraining")
            
            # Check concurrent retraining limit
            if len(self.active_retraining) >= self.retraining_settings["max_concurrent_retraining"]:
                errors.append("Maximum concurrent retraining limit reached")
            
            return {
                "valid": len(errors) == 0,
                "error": "; ".join(errors) if errors else None
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {e}"
            }
    
    def _calculate_retraining_priority(self, strategy_id: str, trigger_type: str, 
                                     trigger_data: Dict[str, Any]) -> int:
        """Calculate priority for retraining event."""
        try:
            # Base priority
            priority = 5
            
            # Trigger type priority
            if trigger_type == "performance_based":
                priority += 3  # Performance issues get highest priority
            elif trigger_type == "market_change":
                priority += 2  # Market changes get high priority
            elif trigger_type == "scheduled":
                priority += 1  # Scheduled retraining gets normal priority
            
            # Performance-based priority adjustments
            if trigger_type == "performance_based" and "performance_metrics" in trigger_data:
                performance = trigger_data["performance_metrics"]
                if performance.get("win_rate", 0.5) < self.retraining_settings["performance_threshold"]:
                    priority += 2  # Poor performance gets higher priority
            
            # Market change priority adjustments
            if trigger_type == "market_change" and "market_conditions" in trigger_data:
                market_conditions = trigger_data["market_conditions"]
                if market_conditions.get("volatility", 0) > 0.8:
                    priority += 1  # High volatility gets higher priority
            
            return max(1, min(10, priority))  # Clamp between 1 and 10
            
        except Exception as e:
            print(f"❌ Error calculating retraining priority: {e}")
            return 5
    
    async def process_retraining_queue(self):
        """Process the retraining queue."""
        try:
            if not self.retraining_queue:
                return
            
            # Sort queue by priority
            sorted_queue = sorted(self.retraining_queue, key=lambda x: x.priority, reverse=True)
            
            # Process events that can be started
            for event in sorted_queue[:3]:  # Process top 3 events
                if event.status == "pending" and len(self.active_retraining) < self.retraining_settings["max_concurrent_retraining"]:
                    await self._execute_retraining(event)
            
        except Exception as e:
            print(f"❌ Error processing retraining queue: {e}")
    
    async def _execute_retraining(self, event: RetrainingEvent):
        """Execute a single retraining event."""
        try:
            event_id = event.event_id
            strategy_id = event.strategy_id
            
            print(f"🔄 Starting retraining {event_id} for strategy {strategy_id}")
            
            # Update event status
            event.status = "running"
            self.active_retraining[event_id] = {
                "event": event,
                "started_at": time.time(),
                "status": "running"
            }
            
            # Execute retraining
            start_time = time.time()
            retraining_result = await self._execute_retraining_process(event)
            retraining_duration = time.time() - start_time
            
            if retraining_result and retraining_result.get("success"):
                # Create retraining result record
                result = RetrainingResult(
                    result_id=f"result_{event_id}_{int(time.time())}",
                    event_id=event_id,
                    strategy_id=strategy_id,
                    trigger_type=event.trigger_type,
                    original_performance=retraining_result.get("original_performance", {}),
                    new_performance=retraining_result.get("new_performance", {}),
                    improvement=retraining_result.get("improvement", 0.0),
                    retraining_duration=retraining_duration,
                    timestamp=time.time(),
                    success=True
                )
                
                # Store result
                if strategy_id not in self.retraining_results:
                    self.retraining_results[strategy_id] = []
                self.retraining_results[strategy_id].append(result)
                
                # Add to history
                self.retraining_history.append(result)
                
                # Update event status
                event.status = "completed"
                
                # Update statistics
                self.retraining_stats["successful_retraining"] += 1
                self._update_average_improvement(retraining_result.get("improvement", 0.0))
                
                print(f"✅ Retraining {event_id} completed successfully with {retraining_result.get('improvement', 0.0):.2%} improvement")
                
            else:
                # Retraining failed
                error_msg = retraining_result.get("error", "Unknown retraining error") if retraining_result else "No retraining result"
                print(f"❌ Retraining {event_id} failed: {error_msg}")
                
                event.status = "failed"
                self.retraining_stats["failed_retraining"] += 1
            
            # Remove from active retraining
            if event_id in self.active_retraining:
                del self.active_retraining[event_id]
            
        except Exception as e:
            print(f"❌ Error executing retraining: {e}")
            if "event_id" in locals():
                event.status = "failed"
                if event_id in self.active_retraining:
                    del self.active_retraining[event_id]
    
    async def _execute_retraining_process(self, event: RetrainingEvent) -> Optional[Dict[str, Any]]:
        """Execute the actual retraining process."""
        try:
            strategy_id = event.strategy_id
            trigger_type = event.trigger_type
            trigger_data = event.trigger_data
            
            if not self.training_module:
                return {
                    "success": False,
                    "error": "Training module not available"
                }
            
            # Get current performance
            current_performance = await self._get_current_performance(strategy_id)
            
            # Prepare retraining data
            retraining_data = await self._prepare_retraining_data(strategy_id, trigger_data)
            if not retraining_data:
                return {
                    "success": False,
                    "error": "Failed to prepare retraining data"
                }
            
            # Execute retraining
            training_result = await self.training_module.train_trading_model(strategy_id, retraining_data)
            if not training_result:
                return {
                    "success": False,
                    "error": "Training failed"
                }
            
            # Get new performance
            new_performance = await self._get_current_performance(strategy_id)
            
            # Calculate improvement
            improvement = self._calculate_performance_improvement(current_performance, new_performance)
            
            # Check if improvement meets threshold
            if improvement < self.retraining_settings["improvement_threshold"]:
                print(f"⚠️ Retraining improvement {improvement:.2%} below threshold {self.retraining_settings['improvement_threshold']:.2%}")
            
            return {
                "success": True,
                "original_performance": current_performance,
                "new_performance": new_performance,
                "improvement": improvement,
                "training_result": training_result
            }
            
        except Exception as e:
            print(f"❌ Error in retraining process: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_current_performance(self, strategy_id: str) -> Dict[str, float]:
        """Get current performance metrics for a strategy."""
        try:
            # This would typically fetch from trading context or database
            # For now, return simulated performance data
            return {
                "win_rate": 0.6 + (hash(strategy_id) % 20) / 100,  # 0.6-0.8
                "profit_factor": 1.2 + (hash(strategy_id) % 30) / 100,  # 1.2-1.5
                "sharpe_ratio": 1.0 + (hash(strategy_id) % 20) / 100,  # 1.0-1.2
                "max_drawdown": 0.05 - (hash(strategy_id) % 10) / 1000  # 0.04-0.05
            }
            
        except Exception as e:
            print(f"❌ Error getting current performance: {e}")
            return {}
    
    async def _prepare_retraining_data(self, strategy_id: str, trigger_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Prepare data for retraining."""
        try:
            # This would typically fetch actual trading data
            # For now, return simulated data
            retraining_data = {
                "trades": [
                    {"action": "buy", "amount": 1000, "price": 100.0, "pnl": 50.0, "timestamp": time.time() - 3600},
                    {"action": "sell", "amount": 1000, "price": 101.0, "pnl": 100.0, "timestamp": time.time() - 1800}
                ],
                "signals": [
                    {"action": "buy", "confidence": 0.8, "timestamp": time.time() - 3600},
                    {"action": "sell", "confidence": 0.7, "timestamp": time.time() - 1800}
                ],
                "market_data": {
                    "volatility": 0.02,
                    "trend_strength": 0.6,
                    "volume": 1000000,
                    "market_regime": 0.5
                }
            }
            
            # Add trigger-specific data
            if "performance_metrics" in trigger_data:
                retraining_data["performance_metrics"] = trigger_data["performance_metrics"]
            
            if "market_conditions" in trigger_data:
                retraining_data["market_conditions"] = trigger_data["market_conditions"]
            
            return retraining_data
            
        except Exception as e:
            print(f"❌ Error preparing retraining data: {e}")
            return None
    
    def _calculate_performance_improvement(self, original: Dict[str, float], new: Dict[str, float]) -> float:
        """Calculate performance improvement between original and new metrics."""
        try:
            if not original or not new:
                return 0.0
            
            # Calculate weighted improvement across multiple metrics
            improvements = []
            weights = {
                "win_rate": 0.4,
                "profit_factor": 0.3,
                "sharpe_ratio": 0.2,
                "max_drawdown": 0.1
            }
            
            for metric, weight in weights.items():
                if metric in original and metric in new:
                    if metric == "max_drawdown":
                        # Lower drawdown is better
                        improvement = (original[metric] - new[metric]) / max(original[metric], 0.001)
                    else:
                        # Higher values are better
                        improvement = (new[metric] - original[metric]) / max(original[metric], 0.001)
                    
                    improvements.append(improvement * weight)
            
            # Return weighted average improvement
            return sum(improvements) if improvements else 0.0
            
        except Exception as e:
            print(f"❌ Error calculating performance improvement: {e}")
            return 0.0
    
    def _update_average_improvement(self, improvement: float):
        """Update average improvement statistics."""
        try:
            current_avg = self.retraining_stats["average_improvement"]
            successful_retraining = self.retraining_stats["successful_retraining"]
            
            if successful_retraining > 0:
                new_avg = (current_avg * (successful_retraining - 1) + improvement) / successful_retraining
                self.retraining_stats["average_improvement"] = new_avg
            
        except Exception as e:
            print(f"❌ Error updating average improvement: {e}")
    
    async def get_retraining_status(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a retraining event."""
        try:
            # Check active retraining
            if event_id in self.active_retraining:
                return self.active_retraining[event_id]
            
            # Check queue
            for event in self.retraining_queue:
                if event.event_id == event_id:
                    return {
                        "event_id": event.event_id,
                        "strategy_id": event.strategy_id,
                        "trigger_type": event.trigger_type,
                        "status": event.status,
                        "created_at": event.created_at,
                        "priority": event.priority
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting retraining status: {e}")
            return None
    
    async def get_retraining_results(self, strategy_id: str) -> List[RetrainingResult]:
        """Get retraining results for a strategy."""
        try:
            return self.retraining_results.get(strategy_id, [])
            
        except Exception as e:
            print(f"❌ Error getting retraining results: {e}")
            return []
    
    async def get_retraining_summary(self) -> Dict[str, Any]:
        """Get summary of all retraining activities."""
        try:
            return {
                "retraining_statistics": self.retraining_stats.copy(),
                "queue_size": len(self.retraining_queue),
                "active_retraining": len(self.active_retraining),
                "retraining_history_size": len(self.retraining_history)
            }
            
        except Exception as e:
            print(f"❌ Error getting retraining summary: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            # Cancel all active retraining
            for event_id in list(self.active_retraining.keys()):
                retraining_info = self.active_retraining[event_id]
                retraining_info["status"] = "cancelled"
            
            # Cleanup training module
            if self.training_module:
                await self.training_module.cleanup()
            
            print("✅ Trading Retraining Loop cleanup completed")
            
        except Exception as e:
            print(f"❌ Error in Trading Retraining Loop cleanup: {e}")
