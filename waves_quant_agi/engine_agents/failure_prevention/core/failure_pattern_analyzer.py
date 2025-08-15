#!/usr/bin/env python3
"""
Failure Pattern Analyzer - Analyzes patterns in system failures
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from ...shared_utils import get_shared_logger


class FailurePatternAnalyzer:
    """Analyzes patterns in system failures to predict future issues."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("failure_prevention", "pattern_analyzer")
        
        # Pattern storage
        self.failure_patterns = {
            "agent_failures": deque(maxlen=1000),
            "connection_failures": deque(maxlen=1000),
            "execution_failures": deque(maxlen=1000),
            "data_failures": deque(maxlen=1000)
        }
        
        # Pattern analysis results
        self.pattern_metrics = {
            "common_failure_sequences": [],
            "failure_correlation_score": 0.0,
            "prediction_accuracy": 0.0,
            "pattern_confidence": 0.0
        }
        
        # Analysis thresholds
        self.thresholds = config.get('pattern_thresholds', {
            "min_pattern_occurrences": 3,
            "correlation_threshold": 0.7,
            "prediction_confidence_threshold": 0.8
        })
    
    async def analyze_failure_pattern(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a failure pattern."""
        try:
            failure_type = failure_data.get("type", "unknown")
            timestamp = failure_data.get("timestamp", time.time())
            
            # Store failure pattern
            pattern_entry = {
                "type": failure_type,
                "timestamp": timestamp,
                "component": failure_data.get("component", "unknown"),
                "severity": failure_data.get("severity", "medium"),
                "context": failure_data.get("context", {})
            }
            
            # Add to appropriate pattern queue
            pattern_queue = self.failure_patterns.get(f"{failure_type}_failures", 
                                                    self.failure_patterns["agent_failures"])
            pattern_queue.append(pattern_entry)
            
            # Analyze patterns
            analysis_result = await self._perform_pattern_analysis(failure_type)
            
            self.logger.info(f"Analyzed failure pattern: {failure_type}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing failure pattern: {e}")
            return {"error": str(e)}
    
    async def _perform_pattern_analysis(self, failure_type: str) -> Dict[str, Any]:
        """Perform detailed pattern analysis."""
        try:
            pattern_queue = self.failure_patterns.get(f"{failure_type}_failures", [])
            
            if len(pattern_queue) < self.thresholds["min_pattern_occurrences"]:
                return {
                    "patterns_detected": 0,
                    "confidence": 0.0,
                    "recommendations": []
                }
            
            # Analyze temporal patterns
            temporal_patterns = self._analyze_temporal_patterns(pattern_queue)
            
            # Analyze correlation patterns
            correlation_patterns = self._analyze_correlation_patterns(pattern_queue)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(temporal_patterns, correlation_patterns)
            
            return {
                "patterns_detected": len(temporal_patterns) + len(correlation_patterns),
                "temporal_patterns": temporal_patterns,
                "correlation_patterns": correlation_patterns,
                "confidence": self._calculate_pattern_confidence(temporal_patterns, correlation_patterns),
                "recommendations": recommendations
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error performing pattern analysis: {e}")
            return {"error": str(e)}
    
    def _analyze_temporal_patterns(self, pattern_queue: deque) -> List[Dict[str, Any]]:
        """Analyze temporal patterns in failures."""
        patterns = []
        
        try:
            # Convert to list for analysis
            failures = list(pattern_queue)
            
            # Look for time-based patterns
            if len(failures) >= 3:
                # Check for recurring time intervals
                time_intervals = []
                for i in range(1, len(failures)):
                    interval = failures[i]["timestamp"] - failures[i-1]["timestamp"]
                    time_intervals.append(interval)
                
                # Find common intervals
                if time_intervals:
                    avg_interval = sum(time_intervals) / len(time_intervals)
                    patterns.append({
                        "type": "temporal_recurring",
                        "average_interval_seconds": avg_interval,
                        "occurrences": len(time_intervals)
                    })
            
        except Exception as e:
            self.logger.warning(f"Error analyzing temporal patterns: {e}")
        
        return patterns
    
    def _analyze_correlation_patterns(self, pattern_queue: deque) -> List[Dict[str, Any]]:
        """Analyze correlation patterns in failures."""
        patterns = []
        
        try:
            # Convert to list for analysis
            failures = list(pattern_queue)
            
            # Analyze component correlation
            component_counts = defaultdict(int)
            for failure in failures:
                component_counts[failure["component"]] += 1
            
            # Find highly correlated components
            total_failures = len(failures)
            for component, count in component_counts.items():
                correlation = count / total_failures
                if correlation >= self.thresholds["correlation_threshold"]:
                    patterns.append({
                        "type": "component_correlation",
                        "component": component,
                        "correlation_score": correlation,
                        "occurrences": count
                    })
            
        except Exception as e:
            self.logger.warning(f"Error analyzing correlation patterns: {e}")
        
        return patterns
    
    def _calculate_pattern_confidence(self, temporal_patterns: List, correlation_patterns: List) -> float:
        """Calculate overall pattern confidence."""
        try:
            if not temporal_patterns and not correlation_patterns:
                return 0.0
            
            # Base confidence on pattern strength
            temporal_confidence = min(len(temporal_patterns) * 0.3, 0.6)
            correlation_confidence = min(len(correlation_patterns) * 0.2, 0.4)
            
            return min(temporal_confidence + correlation_confidence, 1.0)
            
        except Exception as e:
            self.logger.warning(f"Error calculating pattern confidence: {e}")
            return 0.0
    
    def _generate_recommendations(self, temporal_patterns: List, correlation_patterns: List) -> List[str]:
        """Generate recommendations based on patterns."""
        recommendations = []
        
        try:
            # Temporal pattern recommendations
            for pattern in temporal_patterns:
                if pattern["type"] == "temporal_recurring":
                    interval = pattern["average_interval_seconds"]
                    if interval < 3600:  # Less than 1 hour
                        recommendations.append(f"Consider implementing circuit breakers - failures recurring every {interval:.0f} seconds")
            
            # Correlation pattern recommendations
            for pattern in correlation_patterns:
                if pattern["type"] == "component_correlation":
                    component = pattern["component"]
                    score = pattern["correlation_score"]
                    recommendations.append(f"Monitor {component} component closely - high failure correlation ({score:.2f})")
            
            # General recommendations
            if len(temporal_patterns) > 2:
                recommendations.append("Consider implementing predictive failure detection")
            
            if len(correlation_patterns) > 1:
                recommendations.append("Review component dependencies and implement redundancy")
            
        except Exception as e:
            self.logger.warning(f"Error generating recommendations: {e}")
        
        return recommendations
    
    async def get_pattern_summary(self) -> Dict[str, Any]:
        """Get summary of all failure patterns."""
        try:
            summary = {
                "total_patterns_analyzed": sum(len(queue) for queue in self.failure_patterns.values()),
                "pattern_categories": {
                    name: len(queue) for name, queue in self.failure_patterns.items()
                },
                "pattern_metrics": self.pattern_metrics.copy(),
                "last_analysis": time.time()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error getting pattern summary: {e}")
            return {"error": str(e)}
    
    async def predict_failure_probability(self, component: str, time_horizon_seconds: int = 3600) -> float:
        """Predict failure probability for a component."""
        try:
            # Simple prediction based on historical patterns
            relevant_failures = []
            current_time = time.time()
            
            # Collect relevant failure data
            for queue in self.failure_patterns.values():
                for failure in queue:
                    if (failure["component"] == component and 
                        current_time - failure["timestamp"] < time_horizon_seconds * 2):
                        relevant_failures.append(failure)
            
            if len(relevant_failures) < 2:
                return 0.1  # Low base probability
            
            # Calculate failure rate
            time_span = max(f["timestamp"] for f in relevant_failures) - min(f["timestamp"] for f in relevant_failures)
            if time_span <= 0:
                return 0.1
            
            failure_rate = len(relevant_failures) / time_span
            probability = min(failure_rate * time_horizon_seconds, 0.9)  # Cap at 90%
            
            return probability
            
        except Exception as e:
            self.logger.error(f"❌ Error predicting failure probability: {e}")
            return 0.0