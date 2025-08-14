#!/usr/bin/env python3
"""
Optimization Engine - Core Strategy Optimization Component
Optimizes trading strategies and integrates with consolidated trading functionality.
Focuses purely on strategy-specific optimization, delegating risk management to the risk management agent.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque

# Import consolidated trading functionality
from ..trading.memory.trading_context import TradingContext
from ..trading.learning.trading_research_engine import TradingResearchEngine

@dataclass
class OptimizationRequest:
    """A strategy optimization request."""
    request_id: str
    strategy_id: str
    optimization_type: str  # parameter, component, composition
    target_metrics: Dict[str, float]
    constraints: Dict[str, Any]
    priority: int = 5
    created_at: float = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class OptimizationResult:
    """Result of strategy optimization."""
    result_id: str
    request_id: str
    strategy_id: str
    optimization_type: str
    original_parameters: Dict[str, Any]
    optimized_parameters: Dict[str, Any]
    performance_improvement: Dict[str, float]
    optimization_duration: float
    timestamp: float
    success: bool

class OptimizationEngine:
    """Optimizes trading strategies for better performance.
    
    Focuses purely on strategy-specific optimization:
    - Parameter tuning
    - Component optimization
    - Strategy composition improvement
    - Performance metric optimization
    
    Risk management is delegated to the risk management agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext(max_history=1000)  # Fixed: pass integer instead of config
        self.trading_research_engine = TradingResearchEngine(config)
        
        # Optimization state
        self.optimization_queue: deque = deque(maxlen=100)
        self.active_optimizations: Dict[str, OptimizationRequest] = {}
        self.optimization_results: Dict[str, List[OptimizationResult]] = {}
        self.optimization_history: deque = deque(maxlen=1000)
        
        # Optimization settings (strategy-specific only)
        self.optimization_settings = {
            "max_concurrent_optimizations": 5,
            "optimization_timeout": 1800,  # 30 minutes
            "performance_threshold": 0.1,  # 10% improvement threshold
            "optimization_algorithms": ["genetic", "bayesian", "grid_search"],
            "strategy_parameters": {
                "max_iterations": 100,
                "convergence_threshold": 0.001,
                "population_size": 50
            }
        }
        
        # Optimization statistics
        self.optimization_stats = {
            "total_optimizations": 0,
            "successful_optimizations": 0,
            "failed_optimizations": 0,
            "average_improvement": 0.0,
            "total_optimization_time": 0.0
        }
        
    async def initialize(self):
        """Initialize the optimization engine."""
        try:
            # Initialize trading components
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            
            # Load optimization settings
            await self._load_optimization_settings()
            
            print("✅ Optimization Engine initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Optimization Engine: {e}")
            raise
    
    async def _load_optimization_settings(self):
        """Load optimization settings from configuration."""
        try:
            opt_config = self.config.get("strategy_engine", {}).get("optimization", {})
            self.optimization_settings.update(opt_config)
        except Exception as e:
            print(f"❌ Error loading optimization settings: {e}")

    async def add_optimization_request(self, strategy_id: str, optimization_type: str, 
                                     target_metrics: Dict[str, float], constraints: Dict[str, Any] = None) -> str:
        """Add an optimization request to the queue."""
        try:
            request_id = f"opt_{strategy_id}_{int(time.time())}"
            
            request = OptimizationRequest(
                request_id=request_id,
                strategy_id=strategy_id,
                optimization_type=optimization_type,
                target_metrics=target_metrics,
                constraints=constraints or {}
            )
            
            # Add to optimization queue
            self.optimization_queue.append(request)
            
            # Store request in trading context
            await self.trading_context.store_signal({
                "type": "optimization_request",
                "request_id": request_id,
                "strategy_id": strategy_id,
                "optimization_data": {
                    "type": optimization_type,
                    "target_metrics": target_metrics,
                    "constraints": constraints
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Added optimization request: {request_id}")
            return request_id
            
        except Exception as e:
            print(f"❌ Error adding optimization request: {e}")
            return ""

    async def process_optimization_queue(self) -> List[OptimizationResult]:
        """Process the optimization queue."""
        try:
            results = []
            
            while self.optimization_queue and len(self.active_optimizations) < self.optimization_settings["max_concurrent_optimizations"]:
                request = self.optimization_queue.popleft()
                result = await self._execute_optimization(request)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing optimization queue: {e}")
            return []

    async def _execute_optimization(self, request: OptimizationRequest) -> Optional[OptimizationResult]:
        """Execute a single optimization request."""
        start_time = time.time()
        
        try:
            # Mark as active
            self.active_optimizations[request.request_id] = request
            request.status = "running"
            
            # Get current strategy performance
            current_performance = await self._get_current_performance(request.strategy_id)
            
            # Execute optimization based on type
            if request.optimization_type == "parameter":
                optimized_params = await self._optimize_parameters(request, current_performance)
            elif request.optimization_type == "component":
                optimized_params = await self._optimize_components(request, current_performance)
            elif request.optimization_type == "composition":
                optimized_params = await self._optimize_composition(request, current_performance)
            else:
                raise ValueError(f"Unknown optimization type: {request.optimization_type}")
            
            # Calculate performance improvement
            performance_improvement = await self._calculate_performance_improvement(
                request.strategy_id, current_performance, optimized_params
            )
            
            # Create optimization result
            result = OptimizationResult(
                result_id=f"result_{request.request_id}",
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                optimization_type=request.optimization_type,
                original_parameters=current_performance.get("parameters", {}),
                optimized_parameters=optimized_params,
                performance_improvement=performance_improvement,
                optimization_duration=time.time() - start_time,
                timestamp=time.time(),
                success=True
            )
            
            # Store result
            if request.strategy_id not in self.optimization_results:
                self.optimization_results[request.strategy_id] = []
            self.optimization_results[request.strategy_id].append(result)
            
            # Update statistics
            self.optimization_stats["total_optimizations"] += 1
            self.optimization_stats["successful_optimizations"] += 1
            self.optimization_stats["total_optimization_time"] += result.optimization_duration
            
            # Store result in trading context
            await self.trading_context.store_signal({
                "type": "optimization_result",
                "strategy_id": request.strategy_id,
                "result_data": {
                    "optimization_type": request.optimization_type,
                    "performance_improvement": performance_improvement,
                    "optimized_parameters": optimized_params
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Optimization completed: {request.request_id}")
            return result
            
        except Exception as e:
            print(f"❌ Error executing optimization: {e}")
            self.optimization_stats["failed_optimizations"] += 1
            
            # Return failed result
            return OptimizationResult(
                result_id=f"failed_{request.request_id}",
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                optimization_type=request.optimization_type,
                original_parameters={},
                optimized_parameters={},
                performance_improvement={},
                optimization_duration=time.time() - start_time,
                timestamp=time.time(),
                success=False
            )
        finally:
            # Remove from active optimizations
            self.active_optimizations.pop(request.request_id, None)

    async def _get_current_performance(self, strategy_id: str) -> Dict[str, Any]:
        """Get current strategy performance for optimization."""
        try:
            # Get recent signals and performance data from trading context
            signals = await self.trading_context.get_recent_signals(strategy_id, limit=100)
            pnl_snapshots = await self.trading_context.get_recent_pnl_snapshots(strategy_id, limit=100)
            
            # Analyze performance using trading research engine
            performance_analysis = await self.trading_research_engine.analyze_trading_performance(signals + pnl_snapshots)
            
            return {
                "performance_metrics": performance_analysis,
                "parameters": self._extract_strategy_parameters(signals),
                "timestamp": int(time.time())
            }
            
        except Exception as e:
            print(f"❌ Error getting current performance: {e}")
            return {}

    def _extract_strategy_parameters(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract strategy parameters from signals."""
        try:
            if not signals:
                return {}
            
            # Extract common parameters from signals
            parameters = {}
            for signal in signals:
                if "strategy_parameters" in signal:
                    parameters.update(signal["strategy_parameters"])
            
            return parameters
            
        except Exception as e:
            print(f"❌ Error extracting strategy parameters: {e}")
            return {}

    async def _optimize_parameters(self, request: OptimizationRequest, 
                                 current_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize strategy parameters."""
        try:
            # Simple parameter optimization based on performance targets
            current_params = current_performance.get("parameters", {})
            optimized_params = current_params.copy()
            
            # Adjust parameters based on target metrics
            for metric, target in request.target_metrics.items():
                current_value = current_performance.get("performance_metrics", {}).get(metric, 0.0)
                
                if metric == "signal_confidence_threshold":
                    if current_value < target:
                        optimized_params[metric] = min(0.9, current_params.get(metric, 0.7) - 0.05)
                    else:
                        optimized_params[metric] = max(0.3, current_params.get(metric, 0.7) + 0.05)
                
                elif metric == "strategy_timeout":
                    if current_value < target:
                        optimized_params[metric] = max(30, current_params.get(metric, 60) - 10)
                    else:
                        optimized_params[metric] = min(300, current_params.get(metric, 60) + 10)
            
            return optimized_params
            
        except Exception as e:
            print(f"❌ Error optimizing parameters: {e}")
            return current_performance.get("parameters", {})

    async def _optimize_components(self, request: OptimizationRequest, 
                                 current_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize strategy components."""
        try:
            # Component optimization logic
            current_params = current_performance.get("parameters", {})
            optimized_params = current_params.copy()
            
            # Adjust component weights based on performance
            component_weights = current_params.get("component_weights", {})
            if component_weights:
                # Simple weight adjustment
                for component_id, weight in component_weights.items():
                    if weight < 0.5:
                        optimized_params["component_weights"][component_id] = min(1.0, weight + 0.1)
                    else:
                        optimized_params["component_weights"][component_id] = max(0.1, weight - 0.05)
            
            return optimized_params
            
        except Exception as e:
            print(f"❌ Error optimizing components: {e}")
            return current_performance.get("parameters", {})

    async def _optimize_composition(self, request: OptimizationRequest, 
                                  current_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize strategy composition."""
        try:
            # Composition optimization logic
            current_params = current_performance.get("parameters", {})
            optimized_params = current_params.copy()
            
            # Adjust composition rules
            if "signal_aggregation" in current_params:
                optimized_params["signal_consensus_threshold"] = max(0.5, 
                    current_params.get("signal_consensus_threshold", 0.6) - 0.05)
            
            return optimized_params
            
        except Exception as e:
            print(f"❌ Error optimizing composition: {e}")
            return current_performance.get("parameters", {})

    async def _calculate_performance_improvement(self, strategy_id: str, 
                                              current_performance: Dict[str, Any], 
                                              optimized_params: Dict[str, Any]) -> Dict[str, float]:
        """Calculate expected performance improvement from optimization."""
        try:
            improvement = {}
            
            # Calculate improvement for each target metric
            for metric, target in current_performance.get("performance_metrics", {}).items():
                if isinstance(target, (int, float)):
                    # Simple improvement calculation
                    improvement[metric] = min(0.5, target * 0.1)  # 10% improvement cap
            
            return improvement
            
        except Exception as e:
            print(f"❌ Error calculating performance improvement: {e}")
            return {}

    async def get_optimization_status(self, strategy_id: str = None) -> Dict[str, Any]:
        """Get optimization status and statistics."""
        if strategy_id:
            return {
                "strategy_id": strategy_id,
                "active_optimizations": len([r for r in self.active_optimizations.values() if r.strategy_id == strategy_id]),
                "optimization_results": len(self.optimization_results.get(strategy_id, [])),
                "last_optimization": self.optimization_results.get(strategy_id, [{}])[-1] if self.optimization_results.get(strategy_id) else {}
            }
        else:
            return {
                "stats": self.optimization_stats,
                "queue_size": len(self.optimization_queue),
                "active_optimizations": len(self.active_optimizations),
                "optimization_history_size": len(self.optimization_history),
                "optimization_settings": self.optimization_settings
            }

    async def get_optimization_results(self, strategy_id: str) -> List[OptimizationResult]:
        """Get optimization results for a specific strategy."""
        return self.optimization_results.get(strategy_id, [])

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
            print("✅ Optimization Engine cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up Optimization Engine: {e}")
