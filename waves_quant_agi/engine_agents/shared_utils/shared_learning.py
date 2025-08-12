#!/usr/bin/env python3
"""
Shared Learning Layer - ELIMINATE 90% OF ML CODE DUPLICATION
Single learning system for all agents to prevent massive code duplication

ELIMINATES DUPLICATION FROM:
- data_feeds/learning_layer/ (4 files)
- strategy_engine/learning_layer/ (8 files)  
- risk_management/learning_layer/ (6 files)
- market_conditions/learning_layer/ (5 files)
- intelligence/learning_layer/ (12 files)
- execution/learning_layer/ (14 files)
- And other identical ML modules across agents
"""

import numpy as np
import time
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import pickle
import base64

class LearningType(Enum):
    """Types of learning for different agent needs."""
    PATTERN_RECOGNITION = "pattern_recognition"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    RISK_ASSESSMENT = "risk_assessment"
    RISK_OPTIMIZATION = "risk_optimization"
    MARKET_PREDICTION = "market_prediction"
    STRATEGY_ADAPTATION = "strategy_adaptation"
    EXECUTION_OPTIMIZATION = "execution_optimization"
    DATA_QUALITY = "data_quality"
    CONNECTIVITY_OPTIMIZATION = "connectivity_optimization"
    COST_OPTIMIZATION = "cost_optimization"
    FAILURE_PREDICTION = "failure_prediction"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"

@dataclass
class LearningData:
    """Standardized learning data structure."""
    agent_name: str
    learning_type: LearningType
    input_features: List[float]
    target_value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class LearningModel:
    """Simple learning model for agent adaptation."""
    agent_name: str
    learning_type: LearningType
    weights: List[float]
    bias: float
    learning_rate: float
    performance_score: float
    update_count: int
    last_updated: float
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = time.time()

class SharedLearningLayer:
    """
    Shared learning layer for all agents - eliminates massive ML code duplication.
    Provides simple yet effective learning capabilities for agent adaptation.
    """
    
    def __init__(self, agent_name: str, learning_type: LearningType, feature_count: int, learning_rate: float = 0.01):
        self.agent_name = agent_name
        self.learning_type = learning_type
        self.feature_count = feature_count
        self.learning_rate = learning_rate
        
        # Initialize simple linear model
        self.model = LearningModel(
            agent_name=agent_name,
            learning_type=learning_type,
            weights=np.random.normal(0, 0.1, feature_count).tolist(),
            bias=0.0,
            learning_rate=learning_rate,
            performance_score=0.0,
            update_count=0,
            last_updated=time.time()
        )
        
        # Learning history and statistics
        self.learning_history: List[LearningData] = []
        self.performance_history: List[float] = []
        self.max_history_size = 1000
        
        # Learning statistics
        self.stats = {
            "total_updates": 0,
            "successful_predictions": 0,
            "total_predictions": 0,
            "average_error": 0.0,
            "learning_efficiency": 0.0,
            "last_learning_session": time.time(),
            "model_stability": 1.0
        }
        
        # Adaptive learning parameters
        self.adaptation_config = {
            "min_learning_rate": 0.001,
            "max_learning_rate": 0.1,
            "performance_threshold": 0.8,
            "stability_threshold": 0.95,
            "adaptation_frequency": 100  # updates
        }
    
    def predict(self, features: List[float]) -> float:
        """Make a prediction using the current model."""
        if len(features) != self.feature_count:
            raise ValueError(f"Expected {self.feature_count} features, got {len(features)}")
        
        # Simple linear prediction: y = w·x + b
        prediction = sum(w * f for w, f in zip(self.model.weights, features)) + self.model.bias
        
        self.stats["total_predictions"] += 1
        return prediction
    
    def learn(self, learning_data: LearningData) -> bool:
        """Learn from new data using gradient descent."""
        try:
            if learning_data.target_value is None:
                return False  # Can't learn without target
            
            features = learning_data.input_features
            target = learning_data.target_value
            
            # Make prediction
            prediction = self.predict(features)
            error = target - prediction
            
            # Update model using gradient descent
            # dw = learning_rate * error * feature
            # db = learning_rate * error
            for i in range(len(self.model.weights)):
                self.model.weights[i] += self.learning_rate * error * features[i]
            
            self.model.bias += self.learning_rate * error
            
            # Update model metadata
            self.model.update_count += 1
            self.model.last_updated = time.time()
            
            # Update statistics
            self.stats["total_updates"] += 1
            self.stats["last_learning_session"] = time.time()
            
            # Track accuracy
            if abs(error) < abs(target) * 0.1:  # Within 10% of target
                self.stats["successful_predictions"] += 1
            
            # Update average error (exponential moving average)
            alpha = 0.1
            self.stats["average_error"] = (1 - alpha) * self.stats["average_error"] + alpha * abs(error)
            
            # Store learning data
            self.learning_history.append(learning_data)
            self.performance_history.append(abs(error))
            
            # Maintain history size
            if len(self.learning_history) > self.max_history_size:
                self.learning_history.pop(0)
                self.performance_history.pop(0)
            
            # Adaptive learning rate adjustment
            if self.model.update_count % self.adaptation_config["adaptation_frequency"] == 0:
                self._adapt_learning_parameters()
            
            return True
            
        except Exception as e:
            print(f"❌ Learning error in {self.agent_name}: {e}")
            return False
    
    def _adapt_learning_parameters(self):
        """Adapt learning parameters based on performance."""
        if len(self.performance_history) < 10:
            return
        
        # Calculate recent performance
        recent_errors = self.performance_history[-10:]
        recent_performance = 1.0 / (1.0 + np.mean(recent_errors))
        
        # Calculate stability (how consistent are recent errors)
        error_std = np.std(recent_errors)
        stability = 1.0 / (1.0 + error_std)
        
        # Update performance score
        self.model.performance_score = recent_performance
        self.stats["learning_efficiency"] = recent_performance
        self.stats["model_stability"] = stability
        
        # Adapt learning rate
        if recent_performance > self.adaptation_config["performance_threshold"]:
            # Good performance, reduce learning rate for stability
            self.learning_rate *= 0.95
        else:
            # Poor performance, increase learning rate for faster adaptation
            self.learning_rate *= 1.05
        
        # Clamp learning rate
        self.learning_rate = max(
            self.adaptation_config["min_learning_rate"],
            min(self.adaptation_config["max_learning_rate"], self.learning_rate)
        )
        
        self.model.learning_rate = self.learning_rate
    
    def get_model_state(self) -> Dict[str, Any]:
        """Get complete model state for persistence."""
        return {
            "model": {
                "agent_name": self.model.agent_name,
                "learning_type": self.model.learning_type.value,
                "weights": self.model.weights,
                "bias": self.model.bias,
                "learning_rate": self.model.learning_rate,
                "performance_score": self.model.performance_score,
                "update_count": self.model.update_count,
                "last_updated": self.model.last_updated
            },
            "stats": self.stats,
            "config": {
                "feature_count": self.feature_count,
                "max_history_size": self.max_history_size,
                "adaptation_config": self.adaptation_config
            }
        }
    
    def load_model_state(self, state: Dict[str, Any]) -> bool:
        """Load model state from persistence."""
        try:
            model_data = state["model"]
            self.model = LearningModel(
                agent_name=model_data["agent_name"],
                learning_type=LearningType(model_data["learning_type"]),
                weights=model_data["weights"],
                bias=model_data["bias"],
                learning_rate=model_data["learning_rate"],
                performance_score=model_data["performance_score"],
                update_count=model_data["update_count"],
                last_updated=model_data["last_updated"]
            )
            
            self.stats = state["stats"]
            self.learning_rate = self.model.learning_rate
            
            if "config" in state:
                config = state["config"]
                self.feature_count = config.get("feature_count", self.feature_count)
                self.max_history_size = config.get("max_history_size", self.max_history_size)
                self.adaptation_config.update(config.get("adaptation_config", {}))
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading model state for {self.agent_name}: {e}")
            return False
    
    # Complex serialization methods removed - use simple JSON instead
    
    def reset_model(self):
        """Reset model to initial state."""
        self.model.weights = np.random.normal(0, 0.1, self.feature_count).tolist()
        self.model.bias = 0.0
        self.model.performance_score = 0.0
        self.model.update_count = 0
        self.model.last_updated = time.time()
        
        self.learning_history.clear()
        self.performance_history.clear()
        
        # Reset statistics
        self.stats = {
            "total_updates": 0,
            "successful_predictions": 0,
            "total_predictions": 0,
            "average_error": 0.0,
            "learning_efficiency": 0.0,
            "last_learning_session": time.time(),
            "model_stability": 1.0
        }
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about the learning process."""
        if self.stats["total_predictions"] == 0:
            accuracy = 0.0
        else:
            accuracy = self.stats["successful_predictions"] / self.stats["total_predictions"]
        
        # Calculate learning trend
        if len(self.performance_history) >= 20:
            recent_errors = self.performance_history[-10:]
            older_errors = self.performance_history[-20:-10]
            trend = "improving" if np.mean(recent_errors) < np.mean(older_errors) else "declining"
        else:
            trend = "insufficient_data"
        
        return {
            "accuracy": accuracy,
            "learning_trend": trend,
            "model_age_hours": (time.time() - self.model.last_updated) / 3600,
            "learning_efficiency": self.stats["learning_efficiency"],
            "model_stability": self.stats["model_stability"],
            "total_learning_sessions": self.stats["total_updates"],
            "average_error": self.stats["average_error"],
            "current_learning_rate": self.learning_rate,
            "performance_score": self.model.performance_score
        }

# Over-engineered learning manager removed - simplified to direct learner creation

def get_agent_learner(agent_name: str, learning_type: LearningType, feature_count: int, learning_rate: float = 0.01) -> SharedLearningLayer:
    """Get or create learner for a specific agent and learning type."""
    # Simplified: create new learner directly
    return SharedLearningLayer(agent_name, learning_type, feature_count, learning_rate)

# Specialized learning functions removed - over-engineered complexity eliminated

# Over-engineered test function removed - complexity eliminated
