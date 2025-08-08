#!/usr/bin/env python3
"""
Validation Learning Module
Handles learning from validation results and model updates
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from ...logs.validations_logger import ValidationsLogger

class ValidationLearning:
    """Learning module for validation results and model optimization."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = ValidationsLogger("validation_learning")
        
        # Learning parameters
        self.min_samples = config.get("min_samples", 100)
        self.learning_rate = config.get("learning_rate", 0.01)
        self.update_threshold = config.get("update_threshold", 0.1)
        
        # Model state
        self.validation_patterns = {}
        self.error_patterns = {}
        self.success_patterns = {}
        self.model_performance = {}
        
        # Statistics
        self.stats = {
            "models_updated": 0,
            "patterns_learned": 0,
            "errors_analyzed": 0,
            "last_update": time.time()
        }

    async def update_models(self, validation_data: pd.DataFrame):
        """Update learning models with new validation data."""
        try:
            if len(validation_data) < self.min_samples:
                self.logger.log_learning(
                    "insufficient_data",
                    {
                        "current_samples": len(validation_data),
                        "required_samples": self.min_samples
                    }
                )
                return
            
            # Analyze validation patterns
            await self._analyze_validation_patterns(validation_data)
            
            # Update error patterns
            await self._update_error_patterns(validation_data)
            
            # Update success patterns
            await self._update_success_patterns(validation_data)
            
            # Update model performance
            await self._update_model_performance(validation_data)
            
            # Generate insights
            insights = await self._generate_learning_insights()
            
            # Log learning update
            self.logger.log_learning(
                "model_update",
                {
                    "data_points": len(validation_data),
                    "patterns_learned": len(self.validation_patterns),
                    "insights": insights,
                    "timestamp": time.time()
                }
            )
            
            self.stats["models_updated"] += 1
            self.stats["last_update"] = time.time()
            
        except Exception as e:
            self.logger.log_error(f"Error updating models: {e}")

    async def _analyze_validation_patterns(self, data: pd.DataFrame):
        """Analyze patterns in validation data."""
        try:
            # Group by validation type
            for validation_type in data.get("type", []).unique():
                type_data = data[data["type"] == validation_type]
                
                # Calculate success rate
                success_rate = (type_data["status"] == "valid").mean()
                
                # Calculate average processing time if available
                avg_time = type_data.get("processing_time", pd.Series([0])).mean()
                
                # Store pattern
                self.validation_patterns[validation_type] = {
                    "success_rate": success_rate,
                    "avg_processing_time": avg_time,
                    "total_validations": len(type_data),
                    "last_updated": time.time()
                }
                
                self.stats["patterns_learned"] += 1
                
        except Exception as e:
            self.logger.log_error(f"Error analyzing validation patterns: {e}")

    async def _update_error_patterns(self, data: pd.DataFrame):
        """Update error pattern analysis."""
        try:
            # Filter failed validations
            failed_data = data[data["status"] != "valid"]
            
            if len(failed_data) == 0:
                return
            
            # Analyze error types
            error_counts = failed_data.get("reason", []).value_counts()
            
            for error_type, count in error_counts.items():
                if error_type not in self.error_patterns:
                    self.error_patterns[error_type] = {
                        "count": 0,
                        "first_seen": time.time(),
                        "last_seen": time.time()
                    }
                
                self.error_patterns[error_type]["count"] += count
                self.error_patterns[error_type]["last_seen"] = time.time()
            
            self.stats["errors_analyzed"] += len(failed_data)
            
        except Exception as e:
            self.logger.log_error(f"Error updating error patterns: {e}")

    async def _update_success_patterns(self, data: pd.DataFrame):
        """Update success pattern analysis."""
        try:
            # Filter successful validations
            success_data = data[data["status"] == "valid"]
            
            if len(success_data) == 0:
                return
            
            # Analyze successful validation characteristics
            for validation_type in success_data.get("type", []).unique():
                type_success_data = success_data[success_data["type"] == validation_type]
                
                if validation_type not in self.success_patterns:
                    self.success_patterns[validation_type] = {
                        "total_successes": 0,
                        "avg_processing_time": 0,
                        "common_characteristics": {}
                    }
                
                # Update success count
                self.success_patterns[validation_type]["total_successes"] += len(type_success_data)
                
                # Update average processing time
                current_avg = self.success_patterns[validation_type]["avg_processing_time"]
                new_avg = type_success_data.get("processing_time", pd.Series([0])).mean()
                
                # Weighted average
                total_successes = self.success_patterns[validation_type]["total_successes"]
                self.success_patterns[validation_type]["avg_processing_time"] = (
                    (current_avg * (total_successes - len(type_success_data)) + new_avg * len(type_success_data)) / total_successes
                )
                
        except Exception as e:
            self.logger.log_error(f"Error updating success patterns: {e}")

    async def _update_model_performance(self, data: pd.DataFrame):
        """Update model performance metrics."""
        try:
            # Calculate overall performance metrics
            total_validations = len(data)
            successful_validations = len(data[data["status"] == "valid"])
            failed_validations = total_validations - successful_validations
            
            # Update performance metrics
            self.model_performance = {
                "total_validations": total_validations,
                "successful_validations": successful_validations,
                "failed_validations": failed_validations,
                "success_rate": successful_validations / total_validations if total_validations > 0 else 0,
                "error_rate": failed_validations / total_validations if total_validations > 0 else 0,
                "last_updated": time.time()
            }
            
        except Exception as e:
            self.logger.log_error(f"Error updating model performance: {e}")

    async def _generate_learning_insights(self) -> Dict[str, Any]:
        """Generate insights from learning data."""
        try:
            insights = {
                "top_error_patterns": [],
                "most_successful_types": [],
                "performance_trends": {},
                "recommendations": []
            }
            
            # Top error patterns
            if self.error_patterns:
                sorted_errors = sorted(
                    self.error_patterns.items(),
                    key=lambda x: x[1]["count"],
                    reverse=True
                )
                insights["top_error_patterns"] = [
                    {"error_type": error_type, "count": data["count"]}
                    for error_type, data in sorted_errors[:5]
                ]
            
            # Most successful validation types
            if self.success_patterns:
                sorted_successes = sorted(
                    self.success_patterns.items(),
                    key=lambda x: x[1]["total_successes"],
                    reverse=True
                )
                insights["most_successful_types"] = [
                    {"type": val_type, "successes": data["total_successes"]}
                    for val_type, data in sorted_successes[:5]
                ]
            
            # Performance trends
            if self.model_performance:
                insights["performance_trends"] = {
                    "success_rate": self.model_performance["success_rate"],
                    "error_rate": self.model_performance["error_rate"],
                    "total_validations": self.model_performance["total_validations"]
                }
            
            # Generate recommendations
            insights["recommendations"] = await self._generate_recommendations()
            
            return insights
            
        except Exception as e:
            self.logger.log_error(f"Error generating insights: {e}")
            return {}

    async def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on learning data."""
        recommendations = []
        
        try:
            # Check error patterns
            if self.error_patterns:
                most_common_error = max(self.error_patterns.items(), key=lambda x: x[1]["count"])
                if most_common_error[1]["count"] > 10:
                    recommendations.append(f"Focus on reducing {most_common_error[0]} errors")
            
            # Check success patterns
            if self.success_patterns:
                least_successful = min(self.success_patterns.items(), key=lambda x: x[1]["total_successes"])
                if least_successful[1]["total_successes"] < 5:
                    recommendations.append(f"Improve validation success rate for {least_successful[0]}")
            
            # Check overall performance
            if self.model_performance:
                if self.model_performance["success_rate"] < 0.8:
                    recommendations.append("Overall validation success rate needs improvement")
                elif self.model_performance["success_rate"] > 0.95:
                    recommendations.append("Validation performance is excellent")
            
        except Exception as e:
            self.logger.log_error(f"Error generating recommendations: {e}")
        
        return recommendations

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        return {
            **self.stats,
            "validation_patterns": len(self.validation_patterns),
            "error_patterns": len(self.error_patterns),
            "success_patterns": len(self.success_patterns),
            "model_performance": self.model_performance
        }

    def get_validation_patterns(self) -> Dict[str, Any]:
        """Get learned validation patterns."""
        return self.validation_patterns

    def get_error_patterns(self) -> Dict[str, Any]:
        """Get learned error patterns."""
        return self.error_patterns

    def get_success_patterns(self) -> Dict[str, Any]:
        """Get learned success patterns."""
        return self.success_patterns

    def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance metrics."""
        return self.model_performance

    async def reset_learning(self):
        """Reset all learning data."""
        try:
            self.validation_patterns = {}
            self.error_patterns = {}
            self.success_patterns = {}
            self.model_performance = {}
            
            self.stats = {
                "models_updated": 0,
                "patterns_learned": 0,
                "errors_analyzed": 0,
                "last_update": time.time()
            }
            
            self.logger.log_learning(
                "reset",
                {
                    "timestamp": time.time(),
                    "message": "Learning data reset"
                }
            )
            
        except Exception as e:
            self.logger.log_error(f"Error resetting learning: {e}")

if __name__ == "__main__":
    # Test the validation learning module
    config = {
        "min_samples": 10,
        "learning_rate": 0.01,
        "update_threshold": 0.1
    }
    
    async def test_learning():
        learning = ValidationLearning(config)
        
        # Create test data
        test_data = pd.DataFrame({
            "type": ["strategy", "risk", "market", "strategy", "risk"],
            "status": ["valid", "invalid", "valid", "valid", "invalid"],
            "reason": ["", "insufficient_capital", "", "", "risk_limit_exceeded"],
            "processing_time": [0.1, 0.2, 0.15, 0.12, 0.18]
        })
        
        # Update models
        await learning.update_models(test_data)
        
        # Get stats
        stats = learning.get_learning_stats()
        print(f"Learning stats: {stats}")
        
        # Get patterns
        patterns = learning.get_validation_patterns()
        print(f"Validation patterns: {patterns}")
    
    asyncio.run(test_learning())
