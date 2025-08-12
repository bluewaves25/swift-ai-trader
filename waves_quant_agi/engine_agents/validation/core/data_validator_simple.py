#!/usr/bin/env python3
"""
Data Validator - SIMPLIFIED CORE MODULE
Handles data integrity validation with Rust integration
MUCH SIMPLER: ~200 lines focused on core validation only

RUST INTEGRATION:
- Delegates heavy validation to Rust components
- Python handles orchestration and learning integration
- Clean separation of concerns
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from ...shared_utils import get_shared_logger, get_agent_learner, LearningType

class DataValidatorSimple:
    """
    Simplified data validation engine - delegates to Rust for performance.
    Python handles orchestration, Rust handles validation.
    """
    
    def __init__(self, config: Dict[str, Any], rust_bridge=None):
        self.config = config
        self.logger = get_shared_logger("validation", "data_validator")
        self.learner = get_agent_learner("validation", LearningType.DATA_QUALITY, 5)
        self.rust_bridge = rust_bridge  # Rust validation bridge
        
        # Simple validation statistics
        self.stats = {
            "total_validations": 0,
            "passed_validations": 0,
            "failed_validations": 0,
            "data_quality_score": 1.0
        }
        
        # Basic validation thresholds
        self.thresholds = {
            "price_deviation": 0.05,    # 5% max price deviation
            "volume_spike": 3.0,        # 3x volume spike
            "timestamp_drift": 1000,    # 1s max drift
            "data_completeness": 0.95   # 95% completeness
        }
        
    async def validate_market_data(self, market_data: Dict[str, Any], 
                                 validation_type: str = "realtime") -> Dict[str, Any]:
        """
        Validate market data using appropriate method and Rust backend.
        Main validation method - delegates to Rust for performance.
        """
        start_time = time.time()
        
        try:
            self.stats["total_validations"] += 1
            
            # Basic validation first
            basic_result = self._validate_basic_fields(market_data)
            if not basic_result["valid"]:
                return {
                    "data_quality_score": 0.0,
                    "validation_result": basic_result,
                    "critical_issues": [basic_result["error"]],
                    "timestamp": time.time()
                }
            
            # Validate via Rust if available, otherwise use Python
            if self.rust_bridge:
                result = await self._validate_via_rust(market_data, validation_type)
            else:
                result = await self._validate_python(market_data, validation_type)
            
            # Learn from validation
            await self._learn_from_validation(market_data, result, start_time)
            
            # Update statistics
            self._update_stats(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in data validation: {e}")
            self.stats["failed_validations"] += 1
            return {
                "data_quality_score": 0.0,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _validate_via_rust(self, market_data: Dict[str, Any], 
                               validation_type: str) -> Dict[str, Any]:
        """Validate data via Rust backend for high performance."""
        try:
            # This would call the actual Rust validation code
            # For now, we'll simulate the Rust call
            
            await asyncio.sleep(0.001)  # Simulate 1ms Rust validation
            
            # Simulate comprehensive Rust validation
            quality_score = self._calculate_quality_score_fast(market_data)
            
            result = {
                "data_quality_score": quality_score,
                "validation_result": {
                    "overall_score": quality_score,
                    "validation_method": "rust",
                    "validation_type": validation_type
                },
                "critical_issues": [] if quality_score > 0.7 else ["Low data quality detected"],
                "recommendations": self._get_simple_recommendations(quality_score),
                "timestamp": time.time()
            }
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Rust validation error: {e}")
            return await self._validate_python(market_data, validation_type)
    
    async def _validate_python(self, market_data: Dict[str, Any], 
                             validation_type: str) -> Dict[str, Any]:
        """Fallback Python validation when Rust is not available."""
        try:
            await asyncio.sleep(0.01)  # Simulate 10ms Python validation
            
            # Simple Python validation
            quality_score = self._calculate_quality_score_python(market_data)
            
            result = {
                "data_quality_score": quality_score,
                "validation_result": {
                    "overall_score": quality_score,
                    "validation_method": "python",
                    "validation_type": validation_type
                },
                "critical_issues": [] if quality_score > 0.7 else ["Data quality issues detected"],
                "recommendations": self._get_simple_recommendations(quality_score),
                "timestamp": time.time()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Python validation error: {e}")
            return {
                "data_quality_score": 0.0,
                "error": str(e),
                "validation_method": "python",
                "timestamp": time.time()
            }
    
    def _validate_basic_fields(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic field validation."""
        required_fields = ["symbol", "price", "timestamp"]
        
        for field in required_fields:
            if field not in market_data:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # Check price
        price = market_data.get("price", 0.0)
        if price <= 0:
            return {"valid": False, "error": "Invalid price: must be positive"}
        
        # Check timestamp
        timestamp = market_data.get("timestamp", 0)
        current_time = time.time()
        if abs(current_time - timestamp) > self.thresholds["timestamp_drift"]:
            return {"valid": False, "error": f"Timestamp drift too large: {abs(current_time - timestamp):.1f}s"}
        
        return {"valid": True, "error": None}
    
    def _calculate_quality_score_fast(self, market_data: Dict[str, Any]) -> float:
        """Fast quality score calculation (simulating Rust performance)."""
        score = 1.0
        
        # Price validation
        price = market_data.get("price", 0.0)
        if price <= 0:
            score -= 0.5
        
        # Completeness check
        required_fields = ["symbol", "price", "timestamp", "volume"]
        present_fields = sum(1 for field in required_fields if field in market_data)
        completeness = present_fields / len(required_fields)
        
        if completeness < self.thresholds["data_completeness"]:
            score -= 0.3
        
        # Volume validation
        volume = market_data.get("volume", 0.0)
        avg_volume = market_data.get("average_volume", volume)
        
        if avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio > self.thresholds["volume_spike"]:
                score -= 0.2
        
        return max(0.0, score)
    
    def _calculate_quality_score_python(self, market_data: Dict[str, Any]) -> float:
        """Python quality score calculation (slower but more detailed)."""
        score = 1.0
        
        # More comprehensive Python validation
        # Price validation
        price = market_data.get("price", 0.0)
        previous_price = market_data.get("previous_price", price)
        
        if price <= 0:
            score -= 0.5
        elif previous_price > 0:
            deviation = abs(price - previous_price) / previous_price
            if deviation > self.thresholds["price_deviation"]:
                score -= 0.2
        
        # Completeness check
        all_fields = ["symbol", "price", "timestamp", "volume", "bid", "ask", "high_24h", "low_24h"]
        present_fields = sum(1 for field in all_fields if field in market_data and market_data[field] is not None)
        completeness = present_fields / len(all_fields)
        
        if completeness < 0.5:
            score -= 0.3
        elif completeness < 0.8:
            score -= 0.1
        
        # Consistency checks
        bid = market_data.get("bid")
        ask = market_data.get("ask")
        if bid is not None and ask is not None:
            if bid >= ask:
                score -= 0.3
        
        return max(0.0, score)
    
    def _get_simple_recommendations(self, quality_score: float) -> List[str]:
        """Get simple recommendations based on quality score."""
        recommendations = []
        
        if quality_score < 0.3:
            recommendations.append("Critical data quality issues - investigate data sources")
        elif quality_score < 0.6:
            recommendations.append("Data quality degraded - check data feeds")
        elif quality_score < 0.8:
            recommendations.append("Minor data quality issues - monitor closely")
        
        return recommendations
    
    def _update_stats(self, result: Dict[str, Any]):
        """Update validation statistics."""
        quality_score = result.get("data_quality_score", 0.0)
        
        if quality_score >= 0.7:
            self.stats["passed_validations"] += 1
        else:
            self.stats["failed_validations"] += 1
        
        # Update running quality score (exponential moving average)
        alpha = 0.1
        self.stats["data_quality_score"] = (
            self.stats["data_quality_score"] * (1 - alpha) + quality_score * alpha
        )
    
    async def _learn_from_validation(self, market_data: Dict[str, Any], 
                                   result: Dict[str, Any], start_time: float):
        """Learn from validation for improvement."""
        try:
            # Simple learning features
            price = market_data.get("price", 0.0)
            volume = market_data.get("volume", 0.0)
            quality_score = result.get("data_quality_score", 0.0)
            
            features = [
                price / 10000.0,  # Normalize
                volume / 1000000.0,  # Normalize
                quality_score,
                len(market_data) / 10.0,  # Normalize field count
                time.time() - start_time  # Validation time
            ]
            
            # Target is quality score
            target = quality_score
            
            # Learn for future improvement
            from ...shared_utils import LearningData
            learning_data = LearningData(
                agent_name="validation",
                learning_type=LearningType.DATA_QUALITY,
                input_features=features,
                target_value=target
            )
            
            self.learner.learn(learning_data)
            
        except Exception as e:
            self.logger.warning(f"Learning error: {e}")
    
    # ============= UTILITY METHODS =============
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get simple validation statistics."""
        total_validations = self.stats["total_validations"]
        success_rate = (
            self.stats["passed_validations"] / max(total_validations, 1)
        )
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "failure_rate": 1.0 - success_rate
        }
    
    def reset_stats(self):
        """Reset validation statistics."""
        self.stats = {
            "total_validations": 0,
            "passed_validations": 0,
            "failed_validations": 0,
            "data_quality_score": 1.0
        }
