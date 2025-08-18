#!/usr/bin/env python3
"""
Strategy Adaptation Engine - Strategy Adaptation Component
Handles dynamic strategy adaptation based on market conditions and performance, integrating with consolidated trading functionality.
Focuses purely on strategy-specific adaptation, delegating risk management to the risk management agent.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque

# Import consolidated trading functionality (updated paths for new structure)
from ..core.memory.trading_context import TradingContext
from ..core.learning.trading_research_engine import TradingResearchEngine
from ..core.learning.trading_training_module import TradingTrainingModule

@dataclass
class AdaptationRequest:
    """A strategy adaptation request."""
    request_id: str
    strategy_id: str
    adaptation_type: str  # parameter, component, structure
    trigger_conditions: Dict[str, Any]
    target_improvements: Dict[str, float]
    priority: int = 5
    created_at: float = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class AdaptationResult:
    """Result of strategy adaptation."""
    result_id: str
    request_id: str
    strategy_id: str
    adaptation_type: str
    original_strategy: Dict[str, Any]
    adapted_strategy: Dict[str, Any]
    improvement_metrics: Dict[str, float]
    adaptation_duration: float
    timestamp: float
    success: bool

class StrategyAdaptationEngine:
    """Handles dynamic strategy adaptation based on market conditions and performance.
    
    Focuses purely on strategy-specific adaptation:
    - Parameter adaptation
    - Component adaptation
    - Structure adaptation
    - Performance-based optimization
    
    Risk management is delegated to the risk management agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext(max_history=1000)
        self.trading_research_engine = TradingResearchEngine(config)
        self.trading_training_module = TradingTrainingModule(config)
        
        # Adaptation state
        self.adaptation_queue: deque = deque(maxlen=100)
        self.active_adaptations: Dict[str, AdaptationRequest] = {}
        self.adaptation_results: Dict[str, List[AdaptationResult]] = {}
        self.adaptation_history: deque = deque(maxlen=1000)
        
        # Adaptation settings (strategy-specific only)
        self.adaptation_settings = {
            "max_concurrent_adaptations": 5,
            "adaptation_timeout": 1800,  # 30 minutes
            "min_improvement_threshold": 0.05,  # 5% minimum improvement
            "adaptation_types": ["parameter", "component", "structure"],
            "strategy_parameters": {
                "adaptation_rate": 0.1,
                "max_adaptations_per_strategy": 10,
                "validation_period": 300
            }
        }
        
        # Adaptation statistics
        self.adaptation_stats = {
            "total_adaptations": 0,
            "successful_adaptations": 0,
            "failed_adaptations": 0,
            "total_improvements": 0.0,
            "average_improvement": 0.0,
            "total_adaptation_time": 0.0
        }
        
        # Logger
        self.logger = None
        
    def set_logger(self, logger):
        """Set logger for the strategy adaptation engine."""
        self.logger = logger
        
    async def initialize(self):
        """Initialize the strategy adaptation engine."""
        try:
            # Initialize trading components
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            await self.trading_training_module.initialize()
            
            # Load adaptation settings
            await self._load_adaptation_settings()
            
            print("✅ Strategy Adaptation Engine initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Strategy Adaptation Engine: {e}")
            raise
    
    async def _load_adaptation_settings(self):
        """Load strategy adaptation settings from configuration."""
        try:
            adapt_config = self.config.get("strategy_engine", {}).get("strategy_adaptation", {})
            self.adaptation_settings.update(adapt_config)
        except Exception as e:
            print(f"❌ Error loading adaptation settings: {e}")

    async def add_adaptation_request(self, strategy_id: str, adaptation_type: str, 
                                   trigger_conditions: Dict[str, Any], target_improvements: Dict[str, float]) -> str:
        """Add a strategy adaptation request to the queue."""
        try:
            request_id = f"adapt_{strategy_id}_{int(time.time())}"
            
            request = AdaptationRequest(
                request_id=request_id,
                strategy_id=strategy_id,
                adaptation_type=adaptation_type,
                trigger_conditions=trigger_conditions,
                target_improvements=target_improvements
            )
            
            # Add to adaptation queue
            self.adaptation_queue.append(request)
            
            # Store request in trading context
            await self.trading_context.store_signal({
                "type": "strategy_adaptation_request",
                "request_id": request_id,
                "strategy_id": strategy_id,
                "adaptation_data": {
                    "type": adaptation_type,
                    "trigger_conditions": trigger_conditions,
                    "target_improvements": target_improvements
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Added adaptation request: {request_id}")
            return request_id
            
        except Exception as e:
            print(f"❌ Error adding adaptation request: {e}")
            return ""

    async def process_adaptation_queue(self) -> List[AdaptationResult]:
        """Process the strategy adaptation queue."""
        try:
            results = []
            
            while self.adaptation_queue and len(self.active_adaptations) < self.adaptation_settings["max_concurrent_adaptations"]:
                request = self.adaptation_queue.popleft()
                result = await self._execute_strategy_adaptation(request)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing adaptation queue: {e}")
            return []

    async def _execute_strategy_adaptation(self, request: AdaptationRequest) -> Optional[AdaptationResult]:
        """Execute a single strategy adaptation request."""
        start_time = time.time()
        
        try:
            # Mark as active
            self.active_adaptations[request.request_id] = request
            request.status = "running"
            
            # Get current strategy state
            original_strategy = await self._get_current_strategy_state(request.strategy_id)
            if not original_strategy:
                raise ValueError("Could not retrieve current strategy state")
            
            # Execute adaptation based on type
            if request.adaptation_type == "parameter":
                adapted_strategy = await self._adapt_strategy_parameters(request, original_strategy)
            elif request.adaptation_type == "component":
                adapted_strategy = await self._adapt_strategy_components(request, original_strategy)
            elif request.adaptation_type == "structure":
                adapted_strategy = await self._adapt_strategy_structure(request, original_strategy)
            else:
                raise ValueError(f"Unknown adaptation type: {request.adaptation_type}")
            
            if not adapted_strategy:
                raise ValueError("Strategy adaptation failed")
            
            # Calculate improvement metrics
            improvement_metrics = await self._calculate_improvement_metrics(original_strategy, adapted_strategy, request.target_improvements)
            
            # Create adaptation result
            result = AdaptationResult(
                result_id=f"result_{request.request_id}",
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                adaptation_type=request.adaptation_type,
                original_strategy=original_strategy,
                adapted_strategy=adapted_strategy,
                improvement_metrics=improvement_metrics,
                adaptation_duration=time.time() - start_time,
                timestamp=time.time(),
                success=True
            )
            
            # Store result
            if request.strategy_id not in self.adaptation_results:
                self.adaptation_results[request.strategy_id] = []
            self.adaptation_results[request.strategy_id].append(result)
            
            # Update statistics
            self.adaptation_stats["total_adaptations"] += 1
            self.adaptation_stats["successful_adaptations"] += 1
            self.adaptation_stats["total_improvements"] += sum(improvement_metrics.values())
            self.adaptation_stats["total_adaptation_time"] += result.adaptation_duration
            
            # Store result in trading context
            await self.trading_context.store_signal({
                "type": "strategy_adaptation_result",
                "strategy_id": request.strategy_id,
                "result_data": {
                    "adaptation_type": request.adaptation_type,
                    "improvement_metrics": improvement_metrics,
                    "adapted_strategy": adapted_strategy
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Strategy adaptation completed: {request.request_id}")
            return result
            
        except Exception as e:
            print(f"❌ Error executing strategy adaptation: {e}")
            self.adaptation_stats["failed_adaptations"] += 1
            
            # Return failed result
            return AdaptationResult(
                result_id=f"failed_{request.request_id}",
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                adaptation_type=request.adaptation_type,
                original_strategy={},
                adapted_strategy={},
                improvement_metrics={},
                adaptation_duration=time.time() - start_time,
                timestamp=time.time(),
                success=False
            )
        finally:
            # Remove from active adaptations
            self.active_adaptations.pop(request.request_id, None)

    async def _get_current_strategy_state(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get current strategy state."""
        try:
            # Get recent strategy data from trading context
            signals = await self.trading_context.get_recent_signals(strategy_id, limit=100)
            pnl_snapshots = await self.trading_context.get_recent_pnl_snapshots(strategy_id, limit=100)
            
            # Analyze current strategy performance
            performance_analysis = await self.trading_research_engine.analyze_trading_performance(signals + pnl_snapshots)
            
            # Construct strategy state
            strategy_state = {
                "strategy_id": strategy_id,
                "current_performance": performance_analysis,
                "recent_signals": signals,
                "recent_pnl": pnl_snapshots,
                "timestamp": int(time.time())
            }
            
            return strategy_state
            
        except Exception as e:
            print(f"❌ Error getting current strategy state: {e}")
            return None

    async def _adapt_strategy_parameters(self, request: AdaptationRequest, 
                                       original_strategy: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Adapt strategy parameters."""
        try:
            adapted_strategy = original_strategy.copy()
            
            # Get current performance metrics
            current_performance = original_strategy.get("current_performance", {})
            
            # Adapt parameters based on target improvements
            adapted_parameters = {}
            for metric, target_improvement in request.target_improvements.items():
                current_value = current_performance.get(metric, 0.0)
                
                # Simple parameter adaptation logic
                if metric == "win_rate":
                    if current_value < target_improvement:
                        adapted_parameters["confidence_threshold"] = max(0.3, current_value - 0.05)
                    else:
                        adapted_parameters["confidence_threshold"] = min(0.9, current_value + 0.05)
                
                elif metric == "sharpe_ratio":
                    if current_value < target_improvement:
                        adapted_parameters["risk_adjustment"] = "conservative"
                    else:
                        adapted_parameters["risk_adjustment"] = "aggressive"
            
            # Update strategy with adapted parameters
            adapted_strategy["adapted_parameters"] = adapted_parameters
            adapted_strategy["adaptation_timestamp"] = int(time.time())
            
            return adapted_strategy
            
        except Exception as e:
            print(f"❌ Error adapting strategy parameters: {e}")
            return None

    async def _adapt_strategy_components(self, request: AdaptationRequest, 
                                       original_strategy: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Adapt strategy components."""
        try:
            adapted_strategy = original_strategy.copy()
            
            # Get current performance metrics
            current_performance = original_strategy.get("current_performance", {})
            
            # Adapt components based on performance
            adapted_components = []
            
            # Analyze component performance
            component_analysis = await self.trading_research_engine.analyze_trading_patterns(
                original_strategy.get("recent_signals", [])
            )
            
            # Generate adapted components
            for component in component_analysis.get("components", []):
                adapted_component = component.copy()
                
                # Adjust component weights based on performance
                if component.get("performance_score", 0.0) < 0.6:
                    adapted_component["weight"] = max(0.1, component.get("weight", 1.0) - 0.1)
                else:
                    adapted_component["weight"] = min(1.0, component.get("weight", 1.0) + 0.1)
                
                adapted_components.append(adapted_component)
            
            # Update strategy with adapted components
            adapted_strategy["adapted_components"] = adapted_components
            adapted_strategy["adaptation_timestamp"] = int(time.time())
            
            return adapted_strategy
            
        except Exception as e:
            print(f"❌ Error adapting strategy components: {e}")
            return None

    async def _adapt_strategy_structure(self, request: AdaptationRequest, 
                                      original_strategy: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Adapt strategy structure."""
        try:
            adapted_strategy = original_strategy.copy()
            
            # Get current performance metrics
            current_performance = original_strategy.get("current_performance", {})
            
            # Analyze market conditions
            market_analysis = await self.trading_research_engine.analyze_trading_patterns(
                original_strategy.get("recent_signals", [])
            )
            
            # Adapt structure based on market conditions and performance
            adapted_structure = {
                "execution_mode": "adaptive",
                "risk_management": "dynamic",
                "position_sizing": "performance_based"
            }
            
            # Adjust structure based on performance
            if current_performance.get("volatility", 0.0) > 0.2:
                adapted_structure["execution_mode"] = "conservative"
                adapted_structure["position_sizing"] = "reduced"
            
            elif current_performance.get("trend_strength", 0.0) > 0.7:
                adapted_structure["execution_mode"] = "aggressive"
                adapted_structure["position_sizing"] = "increased"
            
            # Update strategy with adapted structure
            adapted_strategy["adapted_structure"] = adapted_structure
            adapted_strategy["adaptation_timestamp"] = int(time.time())
            
            return adapted_strategy
            
        except Exception as e:
            print(f"❌ Error adapting strategy structure: {e}")
            return None

    async def _calculate_improvement_metrics(self, original_strategy: Dict[str, Any], 
                                           adapted_strategy: Dict[str, Any], 
                                           target_improvements: Dict[str, float]) -> Dict[str, float]:
        """Calculate improvement metrics from adaptation."""
        try:
            improvement_metrics = {}
            
            # Calculate improvements for each target metric
            for metric, target_improvement in target_improvements.items():
                if metric in original_strategy.get("current_performance", {}):
                    current_value = original_strategy["current_performance"][metric]
                    
                    # Simple improvement calculation
                    if isinstance(current_value, (int, float)) and current_value > 0:
                        improvement = min(target_improvement, current_value * 0.1)  # 10% improvement cap
                    else:
                        improvement = target_improvement * 0.5  # 50% of target
                    
                    improvement_metrics[metric] = improvement
            
            return improvement_metrics
            
        except Exception as e:
            print(f"❌ Error calculating improvement metrics: {e}")
            return {}

    async def adapt_strategy(self, adaptation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt an existing strategy based on performance and market conditions."""
        try:
            start_time = time.time()
            
            # Create adaptation request
            request = AdaptationRequest(
                request_id=adaptation_request.get("request_id", f"adapt_{int(time.time())}"),
                strategy_id=adaptation_request.get("strategy_id", "unknown"),
                adaptation_type=adaptation_request.get("adaptation_type", "parameter"),
                trigger_conditions=adaptation_request.get("trigger_conditions", {}),
                target_improvements=adaptation_request.get("target_improvements", {}),
                priority=adaptation_request.get("priority", 5)
            )
            
            # Add to adaptation queue
            self.adaptation_queue.append(request)
            self.active_adaptations[request.request_id] = request
            
            # Get original strategy (mock for now)
            original_strategy = {
                "strategy_id": request.strategy_id,
                "current_performance": {"volatility": 0.15, "trend_strength": 0.6},
                "recent_signals": []
            }
            
            # Adapt strategy based on type
            if request.adaptation_type == "parameter":
                adapted_strategy = await self._adapt_strategy_parameters(request, original_strategy)
            elif request.adaptation_type == "component":
                adapted_strategy = await self._adapt_strategy_components(request, original_strategy)
            elif request.adaptation_type == "structure":
                adapted_strategy = await self._adapt_strategy_structure(request, original_strategy)
            else:
                adapted_strategy = await self._adapt_strategy_parameters(request, original_strategy)  # Default
            
            if not adapted_strategy:
                return {
                    "success": False,
                    "reason": "Failed to adapt strategy"
                }
            
            # Calculate improvement metrics
            improvement_metrics = await self._calculate_improvement_metrics(
                original_strategy, adapted_strategy, request.target_improvements
            )
            
            # Create adaptation result
            adaptation_duration = time.time() - start_time
            result = AdaptationResult(
                result_id=f"result_{request.request_id}",
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                adaptation_type=request.adaptation_type,
                original_strategy=original_strategy,
                adapted_strategy=adapted_strategy,
                improvement_metrics=improvement_metrics,
                adaptation_duration=adaptation_duration,
                timestamp=time.time(),
                success=True
            )
            
            # Store result
            if request.strategy_id not in self.adaptation_results:
                self.adaptation_results[request.strategy_id] = []
            self.adaptation_results[request.strategy_id].append(result)
            
            # Update statistics
            self.adaptation_stats["total_adaptations"] += 1
            self.adaptation_stats["successful_adaptations"] += 1
            self.adaptation_stats["total_improvements"] += sum(improvement_metrics.values())
            self.adaptation_stats["total_adaptation_time"] += adaptation_duration
            
            # Remove from active adaptations
            if request.request_id in self.active_adaptations:
                del self.active_adaptations[request.request_id]
            
            return {
                "success": True,
                "result_id": result.result_id,
                "adapted_strategy": adapted_strategy,
                "improvement_metrics": improvement_metrics,
                "adaptation_duration": adaptation_duration
            }
            
        except Exception as e:
            print(f"❌ Error adapting strategy: {e}")
            return {
                "success": False,
                "reason": f"Strategy adaptation error: {str(e)}"
            }

    async def get_adaptation_status(self, strategy_id: str = None) -> Dict[str, Any]:
        """Get strategy adaptation status and statistics."""
        if strategy_id:
            return {
                "strategy_id": strategy_id,
                "active_adaptations": len([r for r in self.active_adaptations.values() if r.strategy_id == strategy_id]),
                "adaptation_results": len(self.adaptation_results.get(strategy_id, [])),
                "last_adaptation": self.adaptation_results.get(strategy_id, [{}])[-1] if self.adaptation_results.get(strategy_id) else {}
            }
        else:
            # Calculate average improvement
            if self.adaptation_stats["successful_adaptations"] > 0:
                avg_improvement = self.adaptation_stats["total_improvements"] / self.adaptation_stats["successful_adaptations"]
            else:
                avg_improvement = 0.0
            
            return {
                "stats": {**self.adaptation_stats, "average_improvement": avg_improvement},
                "queue_size": len(self.adaptation_queue),
                "active_adaptations": len(self.active_adaptations),
                "adaptation_history_size": len(self.adaptation_history),
                "adaptation_settings": self.adaptation_settings
            }

    async def get_adaptation_results(self, strategy_id: str) -> List[AdaptationResult]:
        """Get adaptation results for a specific strategy."""
        return self.adaptation_results.get(strategy_id, [])

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
            await self.trading_training_module.cleanup()
            print("✅ Strategy Adaptation Engine cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up Strategy Adaptation Engine: {e}")
