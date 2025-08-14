import time
from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...logs.incident_cache import IncidentCache

class ShiftPredictorFuser:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.fusion_threshold = config.get("fusion_threshold", 0.7)  # Confidence threshold for fused predictions

    async def fuse_shift_predictions(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fuse shift predictions using real-time adaptive weighting and ensemble methods."""
        try:
            fused_predictions = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                prediction_scores = data.get("prediction_scores", [])
                model_weights = data.get("model_weights", [])
                historical_accuracy = data.get("historical_accuracy", [])
                market_conditions = data.get("market_conditions", {})
                volatility = float(data.get("volatility", 0.0))
                liquidity_ratio = float(data.get("liquidity_ratio", 1.0))
                
                if not prediction_scores or len(prediction_scores) < 2:
                    continue
                
                # Real-time prediction fusion using adaptive weighting
                fused_score = self._calculate_fused_prediction_score(
                    prediction_scores, model_weights, historical_accuracy, 
                    market_conditions, volatility, liquidity_ratio
                )
                
                fusion_confidence = self._calculate_fusion_confidence(
                    prediction_scores, model_weights, historical_accuracy, 
                    market_conditions, volatility, liquidity_ratio
                )
                
                fusion_characteristics = self._extract_fusion_characteristics(
                    prediction_scores, model_weights, historical_accuracy, 
                    market_conditions, volatility, liquidity_ratio
                )
                
                # Update model weights based on performance
                updated_weights = self._update_model_weights(
                    model_weights, historical_accuracy, market_conditions
                )
                
                fused_prediction = {
                    "type": "shift_prediction_fusion",
                    "symbol": symbol,
                    "fused_score": fused_score,
                    "fusion_confidence": fusion_confidence,
                    "fusion_characteristics": fusion_characteristics,
                    "prediction_scores": prediction_scores,
                    "model_weights": updated_weights,
                    "historical_accuracy": historical_accuracy,
                    "market_conditions": market_conditions,
                    "volatility": volatility,
                    "liquidity_ratio": liquidity_ratio,
                    "timestamp": int(time.time()),
                    "description": f"Fused shift prediction for {symbol}: score {fused_score:.2f} (confidence: {fusion_confidence:.2f})"
                }
                
                fused_predictions.append(fused_prediction)
                self.logger.log_issue(fused_prediction)
                self.cache.store_incident(fused_prediction)
                self.redis_client.set(f"market_conditions:fused_prediction:{symbol}", str(fused_prediction), ex=604800)
            
            summary = {
                "type": "shift_prediction_fusion_summary",
                "fused_count": len(fused_predictions),
                "timestamp": int(time.time()),
                "description": f"Fused shift predictions for {len(fused_predictions)} symbols"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return fused_predictions
            
        except Exception as e:
            self.logger.log(f"Error fusing shift predictions: {e}")
            self.cache.store_incident({
                "type": "shift_prediction_fusion_error",
                "timestamp": int(time.time()),
                "description": f"Error fusing shift predictions: {str(e)}"
            })
            return []
    
    def _calculate_fused_prediction_score(self, prediction_scores: List[float], 
                                        model_weights: List[float], 
                                        historical_accuracy: List[float],
                                        market_conditions: Dict[str, Any], 
                                        volatility: float, liquidity_ratio: float) -> float:
        """Calculate fused prediction score using adaptive ensemble methods."""
        try:
            if not prediction_scores or not model_weights:
                return 0.0
            
            # Normalize weights if they don't sum to 1
            total_weight = sum(model_weights)
            if total_weight > 0:
                normalized_weights = [w / total_weight for w in model_weights]
            else:
                normalized_weights = [1.0 / len(model_weights)] * len(model_weights)
            
            # Calculate base weighted average
            base_score = sum(score * weight for score, weight in zip(prediction_scores, normalized_weights))
            
            # Apply market condition adjustments
            volatility_adjustment = self._calculate_volatility_adjustment(volatility)
            liquidity_adjustment = self._calculate_liquidity_adjustment(liquidity_ratio)
            
            # Apply historical accuracy adjustments
            accuracy_adjustment = self._calculate_accuracy_adjustment(historical_accuracy)
            
            # Apply ensemble diversity adjustment
            diversity_adjustment = self._calculate_diversity_adjustment(prediction_scores)
            
            # Combine all adjustments
            adjusted_score = base_score * (
                1.0 + volatility_adjustment + liquidity_adjustment + 
                accuracy_adjustment + diversity_adjustment
            )
            
            return max(-1.0, min(1.0, adjusted_score))  # Clamp to [-1, 1]
            
        except Exception as e:
            self.logger.log_error(f"Error calculating fused prediction score: {e}")
            return 0.0
    
    def _calculate_volatility_adjustment(self, volatility: float) -> float:
        """Calculate volatility-based adjustment factor."""
        try:
            # Higher volatility reduces prediction confidence
            if volatility > 0.08:  # Extreme volatility
                return -0.2
            elif volatility > 0.05:  # High volatility
                return -0.1
            elif volatility > 0.02:  # Medium volatility
                return -0.05
            else:  # Low volatility
                return 0.0
        except Exception as e:
            self.logger.log_error(f"Error calculating volatility adjustment: {e}")
            return 0.0
    
    def _calculate_liquidity_adjustment(self, liquidity_ratio: float) -> float:
        """Calculate liquidity-based adjustment factor."""
        try:
            # Lower liquidity reduces prediction confidence
            if liquidity_ratio < 0.3:  # Critical liquidity shortage
                return -0.15
            elif liquidity_ratio < 0.6:  # Liquidity shortage
                return -0.1
            elif liquidity_ratio < 0.8:  # Adequate liquidity
                return -0.05
            else:  # Abundant liquidity
                return 0.0
        except Exception as e:
            self.logger.log_error(f"Error calculating liquidity adjustment: {e}")
            return 0.0
    
    def _calculate_accuracy_adjustment(self, historical_accuracy: List[float]) -> float:
        """Calculate historical accuracy adjustment factor."""
        try:
            if not historical_accuracy:
                return 0.0
            
            # Calculate average accuracy
            avg_accuracy = sum(historical_accuracy) / len(historical_accuracy)
            
            # Higher accuracy increases prediction confidence
            if avg_accuracy > 0.8:  # High accuracy
                return 0.1
            elif avg_accuracy > 0.6:  # Medium accuracy
                return 0.05
            elif avg_accuracy > 0.4:  # Low accuracy
                return -0.05
            else:  # Very low accuracy
                return -0.1
                
        except Exception as e:
            self.logger.log_error(f"Error calculating accuracy adjustment: {e}")
            return 0.0
    
    def _calculate_diversity_adjustment(self, prediction_scores: List[float]) -> float:
        """Calculate ensemble diversity adjustment factor."""
        try:
            if len(prediction_scores) < 2:
                return 0.0
            
            # Calculate standard deviation of predictions
            mean_score = sum(prediction_scores) / len(prediction_scores)
            variance = sum((score - mean_score) ** 2 for score in prediction_scores) / len(prediction_scores)
            std_dev = variance ** 0.5
            
            # Higher diversity (higher std dev) reduces confidence
            if std_dev > 0.5:  # High diversity
                return -0.1
            elif std_dev > 0.3:  # Medium diversity
                return -0.05
            elif std_dev > 0.1:  # Low diversity
                return 0.0
            else:  # Very low diversity
                return 0.05
                
        except Exception as e:
            self.logger.log_error(f"Error calculating diversity adjustment: {e}")
            return 0.0
    
    def _calculate_fusion_confidence(self, prediction_scores: List[float], 
                                   model_weights: List[float], 
                                   historical_accuracy: List[float],
                                   market_conditions: Dict[str, Any], 
                                   volatility: float, liquidity_ratio: float) -> float:
        """Calculate confidence in the fusion process."""
        try:
            # Base confidence from number of models
            model_confidence = min(1.0, len(prediction_scores) / 5.0)  # Normalize to 5 models
            
            # Weight consistency confidence
            if model_weights:
                weight_variance = sum((w - sum(model_weights)/len(model_weights)) ** 2 for w in model_weights) / len(model_weights)
                weight_confidence = max(0.0, 1.0 - weight_variance)
            else:
                weight_confidence = 0.5
            
            # Historical accuracy confidence
            accuracy_confidence = self._calculate_accuracy_adjustment(historical_accuracy) + 0.5
            
            # Market condition confidence
            volatility_confidence = max(0.0, 1.0 - (volatility / 0.1))  # Normalize to 10% volatility
            liquidity_confidence = liquidity_ratio
            
            # Combined confidence
            confidence = (
                model_confidence * 0.3 +
                weight_confidence * 0.25 +
                accuracy_confidence * 0.2 +
                volatility_confidence * 0.15 +
                liquidity_confidence * 0.1
            )
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.log_error(f"Error calculating fusion confidence: {e}")
            return 0.5
    
    def _update_model_weights(self, current_weights: List[float], 
                             historical_accuracy: List[float], 
                             market_conditions: Dict[str, Any]) -> List[float]:
        """Update model weights based on performance and market conditions."""
        try:
            if not current_weights or not historical_accuracy:
                return current_weights
            
            # Calculate performance-based weight updates
            performance_weights = []
            for accuracy in historical_accuracy:
                # Higher accuracy gets higher weight
                performance_weight = max(0.1, min(2.0, accuracy * 2.0))
                performance_weights.append(performance_weight)
            
            # Normalize performance weights
            total_performance = sum(performance_weights)
            if total_performance > 0:
                normalized_performance = [w / total_performance for w in performance_weights]
            else:
                normalized_performance = [1.0 / len(performance_weights)] * len(performance_weights)
            
            # Apply market condition adjustments
            market_adjustment = self._get_market_adjustment_factor(market_conditions)
            
            # Update weights with learning rate
            learning_rate = 0.1
            updated_weights = []
            for i, (current, performance) in enumerate(zip(current_weights, normalized_performance)):
                new_weight = current + learning_rate * (performance - current) * market_adjustment
                updated_weights.append(max(0.01, new_weight))  # Ensure minimum weight
            
            # Normalize final weights
            total_weight = sum(updated_weights)
            if total_weight > 0:
                final_weights = [w / total_weight for w in updated_weights]
            else:
                final_weights = [1.0 / len(updated_weights)] * len(updated_weights)
            
            return final_weights
            
        except Exception as e:
            self.logger.log_error(f"Error updating model weights: {e}")
            return current_weights
    
    def _get_market_adjustment_factor(self, market_conditions: Dict[str, Any]) -> float:
        """Get market condition adjustment factor for weight updates."""
        try:
            # Extract market condition indicators
            volatility = market_conditions.get("volatility", 0.0)
            regime = market_conditions.get("regime", "stable")
            stress_level = market_conditions.get("stress_level", 0.0)
            
            # Higher stress markets need faster adaptation
            if stress_level > 0.7 or volatility > 0.08:
                return 2.0  # Fast adaptation
            elif stress_level > 0.4 or volatility > 0.05:
                return 1.5  # Medium adaptation
            elif regime == "stable":
                return 0.8  # Slower adaptation
            else:
                return 1.0  # Normal adaptation
                
        except Exception as e:
            self.logger.log_error(f"Error getting market adjustment factor: {e}")
            return 1.0
    
    def _extract_fusion_characteristics(self, prediction_scores: List[float], 
                                      model_weights: List[float], 
                                      historical_accuracy: List[float],
                                      market_conditions: Dict[str, Any], 
                                      volatility: float, liquidity_ratio: float) -> Dict[str, Any]:
        """Extract detailed characteristics of the fusion process."""
        try:
            characteristics = {
                "model_count": len(prediction_scores),
                "weight_distribution": "balanced" if len(set(model_weights)) <= 2 else "imbalanced",
                "prediction_agreement": "high" if max(prediction_scores) - min(prediction_scores) < 0.3 else "medium" if max(prediction_scores) - min(prediction_scores) < 0.6 else "low",
                "historical_performance": "excellent" if sum(historical_accuracy)/len(historical_accuracy) > 0.8 else "good" if sum(historical_accuracy)/len(historical_accuracy) > 0.6 else "poor",
                "market_volatility": "extreme" if volatility > 0.08 else "high" if volatility > 0.05 else "medium" if volatility > 0.02 else "low",
                "liquidity_condition": "critical" if liquidity_ratio < 0.3 else "shortage" if liquidity_ratio < 0.6 else "adequate" if liquidity_ratio < 0.8 else "abundant",
                "ensemble_stability": "stable" if len(prediction_scores) >= 3 else "unstable"
            }
            
            return characteristics
            
        except Exception as e:
            self.logger.log_error(f"Error extracting fusion characteristics: {e}")
            return {"error": "Unable to extract characteristics"}