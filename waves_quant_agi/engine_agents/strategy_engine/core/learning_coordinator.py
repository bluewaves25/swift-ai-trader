#!/usr/bin/env python3
"""
Learning Coordinator - Core Strategy Learning Component
Coordinates learning activities across all strategies and integrates with consolidated trading functionality.
Focuses purely on strategy-specific learning, delegating risk management to the risk management agent.
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
from ..trading.learning.trading_training_module import TradingTrainingModule

@dataclass
class LearningEvent:
    """A learning event for strategy improvement."""
    event_id: str
    strategy_id: str
    event_type: str  # performance_review, parameter_update, component_analysis
    data: Dict[str, Any]
    priority: int = 5
    created_at: float = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class LearningResult:
    """Result of a learning event."""
    result_id: str
    event_id: str
    strategy_id: str
    event_type: str
    insights: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    learning_duration: float
    timestamp: float
    success: bool

class LearningCoordinator:
    """Coordinates learning activities across all strategies.
    
    Focuses purely on strategy-specific learning:
    - Performance analysis and insights
    - Parameter optimization recommendations
    - Component performance analysis
    - Strategy adaptation suggestions
    
    Risk management is delegated to the risk management agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext(max_history=1000)  # Fixed: pass integer instead of config
        self.trading_research_engine = TradingResearchEngine(config)
        self.trading_training_module = TradingTrainingModule(config)
        
        # Learning state
        self.learning_queue: deque = deque(maxlen=100)
        self.active_learning: Dict[str, LearningEvent] = {}
        self.learning_results: Dict[str, List[LearningResult]] = {}
        self.learning_history: deque = deque(maxlen=1000)
        
        # Learning settings (strategy-specific only)
        self.learning_settings = {
            "max_concurrent_learning": 5,
            "learning_timeout": 900,  # 15 minutes
            "auto_learning": True,
            "learning_threshold": 0.6,
            "strategy_parameters": {
                "min_data_points": 50,
                "learning_rate": 0.01,
                "validation_split": 0.2
            }
        }
        
        # Learning statistics
        self.learning_stats = {
            "total_learning_events": 0,
            "successful_learning": 0,
            "failed_learning": 0,
            "total_insights": 0,
            "total_recommendations": 0,
            "average_learning_time": 0.0
        }
        
    async def initialize(self):
        """Initialize the learning coordinator."""
        try:
            # Initialize trading components
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            await self.trading_training_module.initialize()
            
            # Load learning settings
            await self._load_learning_settings()
            
            print("✅ Learning Coordinator initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Learning Coordinator: {e}")
            raise
    
    async def _load_learning_settings(self):
        """Load learning settings from configuration."""
        try:
            learning_config = self.config.get("strategy_engine", {}).get("learning", {})
            self.learning_settings.update(learning_config)
        except Exception as e:
            print(f"❌ Error loading learning settings: {e}")

    async def add_learning_event(self, strategy_id: str, event_type: str, 
                               data: Dict[str, Any], priority: int = 5) -> str:
        """Add a learning event to the queue."""
        try:
            event_id = f"learn_{strategy_id}_{int(time.time())}"
            
            event = LearningEvent(
                event_id=event_id,
                strategy_id=strategy_id,
                event_type=event_type,
                data=data,
                priority=priority
            )
            
            # Add to learning queue
            self.learning_queue.append(event)
            
            # Store event in trading context
            await self.trading_context.store_signal({
                "type": "learning_event",
                "event_id": event_id,
                "strategy_id": strategy_id,
                "event_data": {
                    "type": event_type,
                    "data": data,
                    "priority": priority
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Added learning event: {event_id}")
            return event_id
            
        except Exception as e:
            print(f"❌ Error adding learning event: {e}")
            return ""

    async def process_learning_queue(self) -> List[LearningResult]:
        """Process the learning queue."""
        try:
            results = []
            
            while self.learning_queue and len(self.active_learning) < self.learning_settings["max_concurrent_learning"]:
                event = self.learning_queue.popleft()
                result = await self._execute_learning(event)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing learning queue: {e}")
            return []

    async def _execute_learning(self, event: LearningEvent) -> Optional[LearningResult]:
        """Execute a single learning event."""
        start_time = time.time()
        
        try:
            # Mark as active
            self.active_learning[event.event_id] = event
            event.status = "running"
            
            # Execute learning based on event type
            if event.event_type == "performance_review":
                insights, recommendations = await self._review_strategy_performance(event)
            elif event.event_type == "parameter_update":
                insights, recommendations = await self._update_strategy_parameters(event)
            elif event.event_type == "component_analysis":
                insights, recommendations = await self._analyze_strategy_components(event)
            else:
                raise ValueError(f"Unknown learning event type: {event.event_type}")
            
            # Create learning result
            result = LearningResult(
                result_id=f"result_{event.event_id}",
                event_id=event.event_id,
                strategy_id=event.strategy_id,
                event_type=event.event_type,
                insights=insights,
                recommendations=recommendations,
                learning_duration=time.time() - start_time,
                timestamp=time.time(),
                success=True
            )
            
            # Store result
            if event.strategy_id not in self.learning_results:
                self.learning_results[event.strategy_id] = []
            self.learning_results[event.strategy_id].append(result)
            
            # Update statistics
            self.learning_stats["total_learning_events"] += 1
            self.learning_stats["successful_learning"] += 1
            self.learning_stats["total_insights"] += len(insights)
            self.learning_stats["total_recommendations"] += len(recommendations)
            
            # Store result in trading context
            await self.trading_context.store_signal({
                "type": "learning_result",
                "strategy_id": event.strategy_id,
                "result_data": {
                    "event_type": event.event_type,
                    "insights": insights,
                    "recommendations": recommendations
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Learning completed: {event.event_id}")
            return result
            
        except Exception as e:
            print(f"❌ Error executing learning: {e}")
            self.learning_stats["failed_learning"] += 1
            
            # Return failed result
            return LearningResult(
                result_id=f"failed_{event.event_id}",
                event_id=event.event_id,
                strategy_id=event.strategy_id,
                event_type=event.event_type,
                insights={},
                recommendations=[],
                learning_duration=time.time() - start_time,
                timestamp=time.time(),
                success=False
            )
        finally:
            # Remove from active learning
            self.active_learning.pop(event.event_id, None)

    async def _review_strategy_performance(self, event: LearningEvent) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Review strategy performance and generate insights."""
        try:
            strategy_id = event.strategy_id
            
            # Get recent performance data from trading context
            signals = await self.trading_context.get_recent_signals(strategy_id, limit=100)
            pnl_snapshots = await self.trading_context.get_recent_pnl_snapshots(strategy_id, limit=100)
            
            # Analyze performance using trading research engine
            performance_analysis = await self.trading_research_engine.analyze_trading_performance(signals + pnl_snapshots)
            
            # Generate insights
            insights = {
                "performance_metrics": performance_analysis,
                "signal_quality": self._analyze_signal_quality(signals),
                "strategy_efficiency": self._calculate_strategy_efficiency(performance_analysis)
            }
            
            # Generate recommendations
            recommendations = self._generate_performance_recommendations(insights)
            
            return insights, recommendations
            
        except Exception as e:
            print(f"❌ Error reviewing strategy performance: {e}")
            return {}, []

    async def _update_strategy_parameters(self, event: LearningEvent) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Update strategy parameters based on learning."""
        try:
            strategy_id = event.strategy_id
            current_params = event.data.get("current_parameters", {})
            
            # Get recent performance data
            signals = await self.trading_context.get_recent_signals(strategy_id, limit=100)
            
            # Analyze parameter effectiveness
            param_analysis = await self._analyze_parameter_effectiveness(current_params, signals)
            
            # Generate insights
            insights = {
                "parameter_analysis": param_analysis,
                "current_parameters": current_params,
                "parameter_effectiveness": self._calculate_parameter_effectiveness(param_analysis)
            }
            
            # Generate parameter recommendations
            recommendations = self._generate_parameter_recommendations(insights)
            
            return insights, recommendations
            
        except Exception as e:
            print(f"❌ Error updating strategy parameters: {e}")
            return {}, []

    async def _analyze_strategy_components(self, event: LearningEvent) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Analyze strategy components for improvement."""
        try:
            strategy_id = event.strategy_id
            
            # Get component performance data
            signals = await self.trading_context.get_recent_signals(strategy_id, limit=100)
            
            # Analyze component performance
            component_analysis = await self._analyze_component_performance(signals)
            
            # Generate insights
            insights = {
                "component_analysis": component_analysis,
                "component_efficiency": self._calculate_component_efficiency(component_analysis)
            }
            
            # Generate component recommendations
            recommendations = self._generate_component_recommendations(insights)
            
            return insights, recommendations
            
        except Exception as e:
            print(f"❌ Error analyzing strategy components: {e}")
            return {}, []

    def _analyze_signal_quality(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze signal quality metrics."""
        try:
            if not signals:
                return {"quality_score": 0.0, "confidence_distribution": {}}
            
            # Calculate signal quality metrics
            confidences = [s.get("confidence", 0.0) for s in signals]
            quality_score = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Confidence distribution
            confidence_distribution = {
                "high": len([c for c in confidences if c > 0.8]),
                "medium": len([c for c in confidences if 0.5 <= c <= 0.8]),
                "low": len([c for c in confidences if c < 0.5])
            }
            
            return {
                "quality_score": quality_score,
                "confidence_distribution": confidence_distribution,
                "total_signals": len(signals)
            }
            
        except Exception as e:
            print(f"❌ Error analyzing signal quality: {e}")
            return {"quality_score": 0.0, "confidence_distribution": {}}

    def _calculate_strategy_efficiency(self, performance_analysis: Dict[str, Any]) -> float:
        """Calculate overall strategy efficiency."""
        try:
            # Simple efficiency calculation based on performance metrics
            efficiency = 0.0
            
            if "win_rate" in performance_analysis:
                efficiency += performance_analysis["win_rate"] * 0.4
            
            if "sharpe_ratio" in performance_analysis:
                efficiency += min(1.0, performance_analysis["sharpe_ratio"] / 2.0) * 0.3
            
            if "profit_factor" in performance_analysis:
                efficiency += min(1.0, performance_analysis["profit_factor"] / 3.0) * 0.3
            
            return efficiency
            
        except Exception as e:
            print(f"❌ Error calculating strategy efficiency: {e}")
            return 0.0

    async def _analyze_parameter_effectiveness(self, parameters: Dict[str, Any], 
                                             signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze parameter effectiveness."""
        try:
            # Simple parameter effectiveness analysis
            effectiveness = {}
            
            for param_name, param_value in parameters.items():
                if isinstance(param_value, (int, float)):
                    # Analyze how parameter affects signal quality
                    effectiveness[param_name] = {
                        "value": param_value,
                        "effectiveness_score": 0.7,  # Placeholder
                        "recommendation": "maintain"
                    }
            
            return effectiveness
            
        except Exception as e:
            print(f"❌ Error analyzing parameter effectiveness: {e}")
            return {}

    def _calculate_parameter_effectiveness(self, param_analysis: Dict[str, Any]) -> float:
        """Calculate overall parameter effectiveness."""
        try:
            if not param_analysis:
                return 0.0
            
            scores = [analysis.get("effectiveness_score", 0.0) for analysis in param_analysis.values()]
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            print(f"❌ Error calculating parameter effectiveness: {e}")
            return 0.0

    async def _analyze_component_performance(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze component performance."""
        try:
            # Simple component performance analysis
            component_performance = {}
            
            # Analyze different signal types as components
            signal_types = {}
            for signal in signals:
                signal_type = signal.get("type", "unknown")
                if signal_type not in signal_types:
                    signal_types[signal_type] = []
                signal_types[signal_type].append(signal)
            
            for component_type, component_signals in signal_types.items():
                if component_signals:
                    confidences = [s.get("confidence", 0.0) for s in component_signals]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                    
                    component_performance[component_type] = {
                        "signal_count": len(component_signals),
                        "average_confidence": avg_confidence,
                        "performance_score": avg_confidence
                    }
            
            return component_performance
            
        except Exception as e:
            print(f"❌ Error analyzing component performance: {e}")
            return {}

    def _calculate_component_efficiency(self, component_analysis: Dict[str, Any]) -> float:
        """Calculate overall component efficiency."""
        try:
            if not component_analysis:
                return 0.0
            
            scores = [comp.get("performance_score", 0.0) for comp in component_analysis.values()]
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            print(f"❌ Error calculating component efficiency: {e}")
            return 0.0

    def _generate_performance_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance improvement recommendations."""
        try:
            recommendations = []
            
            # Generate recommendations based on insights
            if insights.get("strategy_efficiency", 0.0) < 0.6:
                recommendations.append({
                    "type": "parameter_optimization",
                    "priority": "high",
                    "description": "Strategy efficiency is low, consider parameter optimization",
                    "action": "optimize_parameters"
                })
            
            if insights.get("signal_quality", {}).get("quality_score", 0.0) < 0.7:
                recommendations.append({
                    "type": "signal_improvement",
                    "priority": "medium",
                    "description": "Signal quality needs improvement",
                    "action": "improve_signal_generation"
                })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error generating performance recommendations: {e}")
            return []

    def _generate_parameter_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate parameter improvement recommendations."""
        try:
            recommendations = []
            
            # Generate parameter-specific recommendations
            param_analysis = insights.get("parameter_analysis", {})
            for param_name, analysis in param_analysis.items():
                if analysis.get("effectiveness_score", 0.0) < 0.6:
                    recommendations.append({
                        "type": "parameter_tuning",
                        "priority": "medium",
                        "description": f"Parameter {param_name} effectiveness is low",
                        "action": "tune_parameter",
                        "parameter": param_name
                    })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error generating parameter recommendations: {e}")
            return []

    def _generate_component_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate component improvement recommendations."""
        try:
            recommendations = []
            
            # Generate component-specific recommendations
            component_analysis = insights.get("component_analysis", {})
            for component_type, analysis in component_analysis.items():
                if analysis.get("performance_score", 0.0) < 0.6:
                    recommendations.append({
                        "type": "component_improvement",
                        "priority": "medium",
                        "description": f"Component {component_type} performance is low",
                        "action": "improve_component",
                        "component": component_type
                    })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error generating component recommendations: {e}")
            return []

    async def trigger_auto_learning(self, strategy_id: str) -> bool:
        """Trigger automatic learning for a strategy."""
        try:
            if not self.learning_settings["auto_learning"]:
                return False
            
            # Check if learning is needed
            if await self._should_trigger_learning(strategy_id):
                # Add performance review learning event
                await self.add_learning_event(
                    strategy_id=strategy_id,
                    event_type="performance_review",
                    data={"trigger": "auto"},
                    priority=3
                )
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error triggering auto learning: {e}")
            return False

    async def _should_trigger_learning(self, strategy_id: str) -> bool:
        """Check if learning should be triggered for a strategy."""
        try:
            # Get recent learning results
            recent_results = self.learning_results.get(strategy_id, [])
            if not recent_results:
                return True  # No learning history, trigger learning
            
            # Check if enough time has passed since last learning
            last_learning = recent_results[-1].timestamp
            time_since_learning = time.time() - last_learning
            
            # Trigger learning if more than 1 hour has passed
            return time_since_learning > 3600
            
        except Exception as e:
            print(f"❌ Error checking learning trigger: {e}")
            return False

    async def get_learning_status(self, strategy_id: str = None) -> Dict[str, Any]:
        """Get learning status and statistics."""
        if strategy_id:
            return {
                "strategy_id": strategy_id,
                "active_learning": len([e for e in self.active_learning.values() if e.strategy_id == strategy_id]),
                "learning_results": len(self.learning_results.get(strategy_id, [])),
                "last_learning": self.learning_results.get(strategy_id, [{}])[-1] if self.learning_results.get(strategy_id) else {}
            }
        else:
            return {
                "stats": self.learning_stats,
                "queue_size": len(self.learning_queue),
                "active_learning": len(self.active_learning),
                "learning_history_size": len(self.learning_history),
                "learning_settings": self.learning_settings
            }

    async def get_learning_results(self, strategy_id: str) -> List[LearningResult]:
        """Get learning results for a specific strategy."""
        return self.learning_results.get(strategy_id, [])

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
            await self.trading_training_module.cleanup()
            print("✅ Learning Coordinator cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up Learning Coordinator: {e}")
