from typing import Dict, Any, List
import time
from ....logs.intelligence_logger import IntelligenceLogger

class SystemPredictor:
    def __init__(self, config: Dict[str, Any], logger: IntelligenceLogger):
        self.config = config
        self.logger = logger
        self.prediction_horizon = config.get("prediction_horizon", 24)  # hours
        
    async def predict_system_behavior(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict future system behavior based on current state."""
        try:
            predictions = {
                "system_id": system_data.get("system_id", "trading_system"),
                "prediction_horizon": self.prediction_horizon,
                "predictions": self._generate_predictions(system_data),
                "confidence": self._calculate_prediction_confidence(system_data),
                "timestamp": int(time.time())
            }
            
            self.logger.log_info(f"Generated system predictions for {predictions['system_id']}")
            return predictions
            
        except Exception as e:
            self.logger.log_error(f"Error in system prediction: {e}")
            return {"error": str(e)}
            
    def _generate_predictions(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate various system predictions."""
        predictions = {
            "performance_trend": self._predict_performance_trend(system_data),
            "resource_usage": self._predict_resource_usage(system_data),
            "error_probability": self._predict_error_probability(system_data),
            "scaling_needs": self._predict_scaling_needs(system_data)
        }
        return predictions
        
    def _predict_performance_trend(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict performance trend over the next period."""
        current_performance = system_data.get("current_performance", 0.8)
        historical_trend = system_data.get("historical_trend", 0.02)
        
        predicted_performance = current_performance + (historical_trend * self.prediction_horizon)
        return {
            "current": current_performance,
            "predicted": max(0.0, min(1.0, predicted_performance)),
            "trend": "improving" if historical_trend > 0 else "declining"
        }
        
    def _predict_resource_usage(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict resource usage patterns."""
        current_cpu = system_data.get("current_cpu_usage", 0.6)
        current_memory = system_data.get("current_memory_usage", 0.7)
        
        # Simple linear prediction
        predicted_cpu = min(1.0, current_cpu * 1.1)
        predicted_memory = min(1.0, current_memory * 1.05)
        
        return {
            "cpu_usage": {"current": current_cpu, "predicted": predicted_cpu},
            "memory_usage": {"current": current_memory, "predicted": predicted_memory}
        }
        
    def _predict_error_probability(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict probability of errors in the next period."""
        current_error_rate = system_data.get("current_error_rate", 0.05)
        system_age = system_data.get("system_age_days", 30)
        
        # Error probability increases with system age and current error rate
        base_probability = current_error_rate
        age_factor = min(0.1, system_age / 365)  # Max 10% increase due to age
        
        predicted_probability = min(0.5, base_probability + age_factor)
        
        return {
            "current_probability": current_error_rate,
            "predicted_probability": predicted_probability,
            "risk_level": "high" if predicted_probability > 0.1 else "medium" if predicted_probability > 0.05 else "low"
        }
        
    def _predict_scaling_needs(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict scaling requirements."""
        current_load = system_data.get("current_load", 0.7)
        growth_rate = system_data.get("growth_rate", 0.1)
        
        predicted_load = current_load * (1 + growth_rate)
        scaling_needed = predicted_load > 0.8
        
        return {
            "current_load": current_load,
            "predicted_load": predicted_load,
            "scaling_needed": scaling_needed,
            "recommended_action": "scale_up" if scaling_needed else "maintain"
        }
        
    def _calculate_prediction_confidence(self, system_data: Dict[str, Any]) -> float:
        """Calculate confidence in predictions."""
        data_quality = system_data.get("data_quality", 0.8)
        historical_data_points = system_data.get("historical_data_points", 100)
        
        # Confidence based on data quality and quantity
        confidence = data_quality * min(1.0, historical_data_points / 1000)
        return max(0.1, min(1.0, confidence))
