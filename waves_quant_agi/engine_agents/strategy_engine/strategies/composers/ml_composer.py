#!/usr/bin/env python3
"""
ML Composer - Strategy ML Composition Component
Composes new trading strategies using machine learning and integrates with consolidated trading functionality.
Focuses purely on strategy-specific ML composition, delegating risk management to the risk management agent.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque

# Import consolidated trading functionality (updated paths for new structure)
from ...core.memory.trading_context import TradingContext
from ...core.learning.trading_research_engine import TradingResearchEngine
from ...core.learning.trading_training_module import TradingTrainingModule

@dataclass
class MLCompositionRequest:
    """A machine learning composition request."""
    request_id: str
    composition_type: str  # pattern_based, performance_optimized, hybrid
    target_symbols: List[str]
    target_metrics: Dict[str, float]
    constraints: Dict[str, Any]
    priority: int = 5
    created_at: float = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class MLCompositionResult:
    """Result of ML strategy composition."""
    result_id: str
    request_id: str
    composition_type: str
    composed_strategy: Dict[str, Any]
    performance_metrics: Dict[str, float]
    confidence_score: float
    composition_duration: float
    timestamp: float
    success: bool

class MLComposer:
    """Composes new trading strategies using machine learning.
    
    Focuses purely on strategy-specific ML composition:
    - Pattern-based strategy generation
    - Performance-optimized strategy creation
    - Hybrid strategy composition
    - ML model training and validation
    
    Risk management is delegated to the risk management agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext(max_history=1000)
        self.trading_research_engine = TradingResearchEngine(config)
        self.trading_training_module = TradingTrainingModule(config)
        
        # ML composition state
        self.composition_queue: deque = deque(maxlen=100)
        self.active_compositions: Dict[str, MLCompositionRequest] = {}
        self.composition_results: Dict[str, List[MLCompositionResult]] = {}
        self.composition_history: deque = deque(maxlen=1000)
        
        # ML composition settings (strategy-specific only)
        self.composition_settings = {
            "max_concurrent_compositions": 3,
            "composition_timeout": 3600,  # 1 hour
            "min_confidence_threshold": 0.7,
            "ml_models": ["pattern_recognition", "performance_optimization", "hybrid"],
            "strategy_parameters": {
                "max_components": 5,
                "min_data_points": 1000,
                "validation_split": 0.2
            }
        }
        
        # ML composition statistics
        self.composition_stats = {
            "total_compositions": 0,
            "successful_compositions": 0,
            "failed_compositions": 0,
            "total_strategies_generated": 0,
            "average_confidence": 0.0,
            "total_composition_time": 0.0
        }
        
        # Logger
        self.logger = None
        
    def set_logger(self, logger):
        """Set logger for the ML composer."""
        self.logger = logger
        
    async def initialize(self):
        """Initialize the ML composer."""
        try:
            # Initialize trading components
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            await self.trading_training_module.initialize()
            
            # Load composition settings
            await self._load_composition_settings()
            
            print("✅ ML Composer initialized")
            
        except Exception as e:
            print(f"❌ Error initializing ML Composer: {e}")
            raise
    
    async def _load_composition_settings(self):
        """Load ML composition settings from configuration."""
        try:
            ml_config = self.config.get("strategy_engine", {}).get("ml_composition", {})
            self.composition_settings.update(ml_config)
        except Exception as e:
            print(f"❌ Error loading ML composition settings: {e}")

    async def add_composition_request(self, composition_type: str, target_symbols: List[str], 
                                    target_metrics: Dict[str, float], constraints: Dict[str, Any] = None) -> str:
        """Add an ML composition request to the queue."""
        try:
            request_id = f"ml_comp_{composition_type}_{int(time.time())}"
            
            request = MLCompositionRequest(
                request_id=request_id,
                composition_type=composition_type,
                target_symbols=target_symbols,
                target_metrics=target_metrics,
                constraints=constraints or {}
            )
            
            # Add to composition queue
            self.composition_queue.append(request)
            
            # Store request in trading context
            await self.trading_context.store_signal({
                "type": "ml_composition_request",
                "request_id": request_id,
                "composition_data": {
                    "type": composition_type,
                    "target_symbols": target_symbols,
                    "target_metrics": target_metrics,
                    "constraints": constraints
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Added ML composition request: {request_id}")
            return request_id
            
        except Exception as e:
            print(f"❌ Error adding ML composition request: {e}")
            return ""

    async def process_composition_queue(self) -> List[MLCompositionResult]:
        """Process the ML composition queue."""
        try:
            results = []
            
            while self.composition_queue and len(self.active_compositions) < self.composition_settings["max_concurrent_compositions"]:
                request = self.composition_queue.popleft()
                result = await self._execute_ml_composition(request)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing ML composition queue: {e}")
            return []

    async def _execute_ml_composition(self, request: MLCompositionRequest) -> Optional[MLCompositionResult]:
        """Execute a single ML composition request."""
        start_time = time.time()
        
        try:
            # Mark as active
            self.active_compositions[request.request_id] = request
            request.status = "running"
            
            # Execute composition based on type
            if request.composition_type == "pattern_based":
                composed_strategy = await self._compose_pattern_based_strategy(request)
            elif request.composition_type == "performance_optimized":
                composed_strategy = await self._compose_performance_optimized_strategy(request)
            elif request.composition_type == "hybrid":
                composed_strategy = await self._compose_hybrid_strategy(request)
            else:
                raise ValueError(f"Unknown composition type: {request.composition_type}")
            
            if not composed_strategy:
                raise ValueError("Strategy composition failed")
            
            # Calculate performance metrics and confidence
            performance_metrics = await self._calculate_strategy_performance(composed_strategy, request.target_symbols)
            confidence_score = await self._calculate_confidence_score(composed_strategy, performance_metrics)
            
            # Create composition result
            result = MLCompositionResult(
                result_id=f"result_{request.request_id}",
                request_id=request.request_id,
                composition_type=request.composition_type,
                composed_strategy=composed_strategy,
                performance_metrics=performance_metrics,
                confidence_score=confidence_score,
                composition_duration=time.time() - start_time,
                timestamp=time.time(),
                success=True
            )
            
            # Store result
            if request.composition_type not in self.composition_results:
                self.composition_results[request.composition_type] = []
            self.composition_results[request.composition_type].append(result)
            
            # Update statistics
            self.composition_stats["total_compositions"] += 1
            self.composition_stats["successful_compositions"] += 1
            self.composition_stats["total_strategies_generated"] += 1
            self.composition_stats["total_composition_time"] += result.composition_duration
            
            # Store result in trading context
            await self.trading_context.store_signal({
                "type": "ml_composition_result",
                "composition_type": request.composition_type,
                "result_data": {
                    "strategy": composed_strategy,
                    "performance_metrics": performance_metrics,
                    "confidence_score": confidence_score
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ ML composition completed: {request.request_id}")
            return result
            
        except Exception as e:
            print(f"❌ Error executing ML composition: {e}")
            self.composition_stats["failed_compositions"] += 1
            
            # Return failed result
            return MLCompositionResult(
                result_id=f"failed_{request.request_id}",
                request_id=request.request_id,
                composition_type=request.composition_type,
                composed_strategy={},
                performance_metrics={},
                confidence_score=0.0,
                composition_duration=time.time() - start_time,
                timestamp=time.time(),
                success=False
            )
        finally:
            # Remove from active compositions
            self.active_compositions.pop(request.request_id, None)

    async def _compose_pattern_based_strategy(self, request: MLCompositionRequest) -> Optional[Dict[str, Any]]:
        """Compose a pattern-based strategy using ML."""
        try:
            # Get market data for target symbols
            market_data = await self._get_market_data_for_symbols(request.target_symbols)
            
            # Analyze patterns using trading research engine
            pattern_analysis = await self.trading_research_engine.analyze_trading_patterns(market_data)
            
            # Identify key patterns
            key_patterns = self._identify_key_patterns(pattern_analysis)
            
            # Generate strategy components based on patterns
            strategy_components = self._generate_pattern_based_components(key_patterns)
            
            # Compose strategy
            strategy = {
                "strategy_id": f"pattern_{request.request_id}",
                "name": f"Pattern-Based Strategy {request.request_id}",
                "description": "ML-generated pattern-based trading strategy",
                "strategy_type": "pattern_based",
                "symbols": request.target_symbols,
                "components": strategy_components,
                "parameters": self._generate_strategy_parameters(strategy_components),
                "confidence_threshold": 0.7,
                "created_at": time.time()
            }
            
            return strategy
            
        except Exception as e:
            print(f"❌ Error composing pattern-based strategy: {e}")
            return None

    async def _compose_performance_optimized_strategy(self, request: MLCompositionRequest) -> Optional[Dict[str, Any]]:
        """Compose a performance-optimized strategy using ML."""
        try:
            # Get historical performance data
            performance_data = await self._get_historical_performance_data(request.target_symbols)
            
            # Train performance optimization model
            training_result = await self.trading_training_module.train_trading_model({
                "type": "performance_optimization",
                "data": performance_data,
                "target_metrics": request.target_metrics
            })
            
            if not training_result.get("success", False):
                raise ValueError("Model training failed")
            
            # Generate optimized strategy components
            strategy_components = self._generate_performance_optimized_components(training_result)
            
            # Compose strategy
            strategy = {
                "strategy_id": f"perf_opt_{request.request_id}",
                "name": f"Performance-Optimized Strategy {request.request_id}",
                "description": "ML-generated performance-optimized trading strategy",
                "strategy_type": "performance_optimized",
                "symbols": request.target_symbols,
                "components": strategy_components,
                "parameters": self._generate_strategy_parameters(strategy_components),
                "confidence_threshold": 0.8,
                "created_at": time.time()
            }
            
            return strategy
            
        except Exception as e:
            print(f"❌ Error composing performance-optimized strategy: {e}")
            return None

    async def _compose_hybrid_strategy(self, request: MLCompositionRequest) -> Optional[Dict[str, Any]]:
        """Compose a hybrid strategy using ML."""
        try:
            # Combine pattern-based and performance-optimized approaches
            pattern_strategy = await self._compose_pattern_based_strategy(request)
            perf_strategy = await self._compose_performance_optimized_strategy(request)
            
            if not pattern_strategy or not perf_strategy:
                raise ValueError("Failed to compose base strategies")
            
            # Merge strategy components
            hybrid_components = self._merge_strategy_components(
                pattern_strategy["components"], 
                perf_strategy["components"]
            )
            
            # Compose hybrid strategy
            strategy = {
                "strategy_id": f"hybrid_{request.request_id}",
                "name": f"Hybrid ML Strategy {request.request_id}",
                "description": "ML-generated hybrid trading strategy",
                "strategy_type": "hybrid",
                "symbols": request.target_symbols,
                "components": hybrid_components,
                "parameters": self._generate_strategy_parameters(hybrid_components),
                "confidence_threshold": 0.75,
                "created_at": time.time()
            }
            
            return strategy
            
        except Exception as e:
            print(f"❌ Error composing hybrid strategy: {e}")
            return None

    async def _get_market_data_for_symbols(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get market data for target symbols."""
        try:
            market_data = []
            
            for symbol in symbols:
                # Get recent signals and PnL snapshots from trading context
                signals = await self.trading_context.get_recent_signals(symbol, limit=500)
                pnl_snapshots = await self.trading_context.get_recent_pnl_snapshots(symbol, limit=500)
                
                market_data.extend(signals + pnl_snapshots)
            
            return market_data
            
        except Exception as e:
            print(f"❌ Error getting market data: {e}")
            return []

    async def _get_historical_performance_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get historical performance data for target symbols."""
        try:
            performance_data = []
            
            for symbol in symbols:
                # Get historical performance from trading context
                signals = await self.trading_context.get_recent_signals(symbol, limit=1000)
                pnl_snapshots = await self.trading_context.get_recent_pnl_snapshots(symbol, limit=1000)
                
                performance_data.extend(signals + pnl_snapshots)
            
            return performance_data
            
        except Exception as e:
            print(f"❌ Error getting historical performance data: {e}")
            return []

    def _identify_key_patterns(self, pattern_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify key patterns from analysis."""
        try:
            key_patterns = []
            
            # Extract key patterns from analysis
            if "trend_patterns" in pattern_analysis:
                key_patterns.extend(pattern_analysis["trend_patterns"])
            
            if "volatility_patterns" in pattern_analysis:
                key_patterns.extend(pattern_analysis["volatility_patterns"])
            
            if "correlation_patterns" in pattern_analysis:
                key_patterns.extend(pattern_analysis["correlation_patterns"])
            
            # Filter and rank patterns by significance
            significant_patterns = [p for p in key_patterns if p.get("significance", 0.0) > 0.6]
            
            return significant_patterns[:10]  # Return top 10 patterns
            
        except Exception as e:
            print(f"❌ Error identifying key patterns: {e}")
            return []

    def _generate_pattern_based_components(self, key_patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate strategy components based on patterns."""
        try:
            components = []
            
            for pattern in key_patterns:
                component = {
                    "component_id": f"pattern_{pattern.get('id', 'unknown')}",
                    "name": f"Pattern Component {pattern.get('id', 'unknown')}",
                    "component_type": "pattern_recognition",
                    "parameters": {
                        "pattern_type": pattern.get("type", "unknown"),
                        "significance": pattern.get("significance", 0.0),
                        "confidence": pattern.get("confidence", 0.0)
                    },
                    "weight": pattern.get("significance", 0.0)
                }
                components.append(component)
            
            return components
            
        except Exception as e:
            print(f"❌ Error generating pattern-based components: {e}")
            return []

    def _generate_performance_optimized_components(self, training_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate strategy components based on performance optimization."""
        try:
            components = []
            
            # Extract optimized parameters from training result
            optimized_params = training_result.get("optimized_parameters", {})
            
            for param_name, param_value in optimized_params.items():
                component = {
                    "component_id": f"perf_opt_{param_name}",
                    "name": f"Performance Optimized {param_name}",
                    "component_type": "performance_optimization",
                    "parameters": {
                        "parameter": param_name,
                        "optimized_value": param_value,
                        "improvement": training_result.get("improvement", 0.0)
                    },
                    "weight": 1.0
                }
                components.append(component)
            
            return components
            
        except Exception as e:
            print(f"❌ Error generating performance-optimized components: {e}")
            return []

    def _merge_strategy_components(self, pattern_components: List[Dict[str, Any]], 
                                 perf_components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge components from different strategy types."""
        try:
            merged_components = []
            
            # Add pattern components
            merged_components.extend(pattern_components)
            
            # Add performance components
            merged_components.extend(perf_components)
            
            # Adjust weights to balance components
            total_components = len(merged_components)
            for component in merged_components:
                component["weight"] = component["weight"] / total_components
            
            return merged_components
            
        except Exception as e:
            print(f"❌ Error merging strategy components: {e}")
            return []

    def _generate_strategy_parameters(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate strategy parameters from components."""
        try:
            parameters = {
                "confidence_threshold": 0.7,
                "execution_timeout": 60,
                "max_position_size": 100000
            }
            
            # Add component-specific parameters
            for component in components:
                component_params = component.get("parameters", {})
                for param_name, param_value in component_params.items():
                    if param_name not in parameters:
                        parameters[f"{component['component_id']}_{param_name}"] = param_value
            
            return parameters
            
        except Exception as e:
            print(f"❌ Error generating strategy parameters: {e}")
            return {}

    async def _calculate_strategy_performance(self, strategy: Dict[str, Any], 
                                            target_symbols: List[str]) -> Dict[str, float]:
        """Calculate expected performance metrics for the strategy."""
        try:
            # Simple performance calculation based on strategy components
            performance_metrics = {
                "expected_return": 0.0,
                "expected_volatility": 0.0,
                "expected_sharpe_ratio": 0.0,
                "expected_win_rate": 0.0
            }
            
            # Calculate metrics based on component weights and types
            total_weight = 0.0
            weighted_metrics = {"return": 0.0, "volatility": 0.0, "sharpe": 0.0, "win_rate": 0.0}
            
            for component in strategy.get("components", []):
                weight = component.get("weight", 1.0)
                total_weight += weight
                
                # Simple metric calculation based on component type
                if component["component_type"] == "pattern_recognition":
                    weighted_metrics["return"] += weight * 0.05  # 5% expected return
                    weighted_metrics["volatility"] += weight * 0.15  # 15% expected volatility
                    weighted_metrics["sharpe"] += weight * 0.33  # 0.33 expected Sharpe ratio
                    weighted_metrics["win_rate"] += weight * 0.55  # 55% expected win rate
                
                elif component["component_type"] == "performance_optimization":
                    weighted_metrics["return"] += weight * 0.08  # 8% expected return
                    weighted_metrics["volatility"] += weight * 0.12  # 12% expected volatility
                    weighted_metrics["sharpe"] += weight * 0.67  # 0.67 expected Sharpe ratio
                    weighted_metrics["win_rate"] += weight * 0.65  # 65% expected win rate
            
            # Normalize by total weight
            if total_weight > 0:
                performance_metrics["expected_return"] = weighted_metrics["return"] / total_weight
                performance_metrics["expected_volatility"] = weighted_metrics["volatility"] / total_weight
                performance_metrics["expected_sharpe_ratio"] = weighted_metrics["sharpe"] / total_weight
                performance_metrics["expected_win_rate"] = weighted_metrics["win_rate"] / total_weight
            
            return performance_metrics
            
        except Exception as e:
            print(f"❌ Error calculating strategy performance: {e}")
            return {}

    async def _calculate_confidence_score(self, strategy: Dict[str, Any], 
                                        performance_metrics: Dict[str, float]) -> float:
        """Calculate confidence score for the composed strategy."""
        try:
            confidence_score = 0.0
            
            # Base confidence from component quality
            components = strategy.get("components", [])
            if components:
                component_confidence = sum(c.get("weight", 0.0) for c in components)
                confidence_score += component_confidence * 0.4
            
            # Performance-based confidence
            if performance_metrics:
                if performance_metrics.get("expected_sharpe_ratio", 0.0) > 0.5:
                    confidence_score += 0.3
                if performance_metrics.get("expected_win_rate", 0.0) > 0.6:
                    confidence_score += 0.3
            
            return min(1.0, max(0.0, confidence_score))
            
        except Exception as e:
            print(f"❌ Error calculating confidence score: {e}")
            return 0.0

    async def compose_strategy(self, composition_request: Dict[str, Any]) -> Dict[str, Any]:
        """Compose a new trading strategy using ML composition."""
        try:
            start_time = time.time()
            
            # Create composition request
            request = MLCompositionRequest(
                request_id=composition_request.get("request_id", f"ml_comp_{int(time.time())}"),
                composition_type=composition_request.get("composition_type", "pattern_based"),
                target_symbols=composition_request.get("target_symbols", ["BTC", "ETH"]),
                target_metrics=composition_request.get("target_metrics", {}),
                constraints=composition_request.get("constraints", {}),
                priority=composition_request.get("priority", 5)
            )
            
            # Add to composition queue
            self.composition_queue.append(request)
            self.active_compositions[request.request_id] = request
            
            # Compose strategy based on type
            if request.composition_type == "pattern_based":
                strategy = await self._compose_pattern_based_strategy(request)
            elif request.composition_type == "performance_optimized":
                strategy = await self._compose_performance_optimized_strategy(request)
            elif request.composition_type == "hybrid":
                strategy = await self._compose_hybrid_strategy(request)
            else:
                strategy = await self._compose_pattern_based_strategy(request)  # Default
            
            if not strategy:
                return {
                    "success": False,
                    "reason": "Failed to compose strategy"
                }
            
            # Calculate performance metrics
            performance_metrics = await self._calculate_strategy_performance(strategy)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(strategy, performance_metrics)
            
            # Create composition result
            composition_duration = time.time() - start_time
            result = MLCompositionResult(
                result_id=f"result_{request.request_id}",
                request_id=request.request_id,
                composition_type=request.composition_type,
                composed_strategy=strategy,
                performance_metrics=performance_metrics,
                confidence_score=confidence_score,
                composition_duration=composition_duration,
                timestamp=time.time(),
                success=True
            )
            
            # Store result
            if request.composition_type not in self.composition_results:
                self.composition_results[request.composition_type] = []
            self.composition_results[request.composition_type].append(result)
            
            # Update statistics
            self.composition_stats["total_compositions"] += 1
            self.composition_stats["successful_compositions"] += 1
            self.composition_stats["total_strategies_generated"] += 1
            self.composition_stats["total_composition_time"] += composition_duration
            
            # Remove from active compositions
            if request.request_id in self.active_compositions:
                del self.active_compositions[request.request_id]
            
            return {
                "success": True,
                "result_id": result.result_id,
                "composed_strategy": strategy,
                "performance_metrics": performance_metrics,
                "confidence_score": confidence_score,
                "composition_duration": composition_duration
            }
            
        except Exception as e:
            print(f"❌ Error composing strategy: {e}")
            return {
                "success": False,
                "reason": f"Strategy composition error: {str(e)}"
            }

    async def get_composition_status(self, composition_type: str = None) -> Dict[str, Any]:
        """Get ML composition status and statistics."""
        if composition_type:
            return {
                "composition_type": composition_type,
                "active_compositions": len([r for r in self.active_compositions.values() if r.composition_type == composition_type]),
                "composition_results": len(self.composition_results.get(composition_type, [])),
                "last_composition": self.composition_results.get(composition_type, [{}])[-1] if self.composition_results.get(composition_type) else {}
            }
        else:
            # Calculate average confidence
            if self.composition_stats["successful_compositions"] > 0:
                avg_confidence = self.composition_stats["total_composition_time"] / self.composition_stats["successful_compositions"]
            else:
                avg_confidence = 0.0
            
            return {
                "stats": {**self.composition_stats, "average_confidence": avg_confidence},
                "queue_size": len(self.composition_queue),
                "active_compositions": len(self.active_compositions),
                "composition_history_size": len(self.composition_history),
                "composition_settings": self.composition_settings
            }

    async def get_composition_results(self, composition_type: str) -> List[MLCompositionResult]:
        """Get ML composition results for a specific type."""
        return self.composition_results.get(composition_type, [])

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
            await self.trading_training_module.cleanup()
            print("✅ ML Composer cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up ML Composer: {e}")