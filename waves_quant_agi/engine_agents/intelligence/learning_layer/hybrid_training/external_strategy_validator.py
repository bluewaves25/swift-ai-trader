from typing import Dict, Any, List
import time
from ...logs.intelligence_logger import IntelligenceLogger

class ExternalStrategyValidator:
    def __init__(self, config: Dict[str, Any], logger: IntelligenceLogger):
        self.config = config
        self.logger = logger
        self.validation_threshold = config.get("validation_threshold", 0.7)
        
    async def validate_external_strategy(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate external strategy against internal standards."""
        try:
            validation_result = {
                "strategy_id": strategy_data.get("strategy_id", "unknown"),
                "validation_score": self._calculate_validation_score(strategy_data),
                "validation_status": self._get_validation_status(strategy_data),
                "issues": self._identify_issues(strategy_data),
                "recommendations": self._generate_recommendations(strategy_data),
                "timestamp": int(time.time())
            }
            
            self.logger.log_info(f"Validated external strategy {validation_result['strategy_id']}: {validation_result['validation_status']}")
            return validation_result
            
        except Exception as e:
            self.logger.log_error(f"Error in external strategy validation: {e}")
            return {"error": str(e)}
            
    def _calculate_validation_score(self, strategy_data: Dict[str, Any]) -> float:
        """Calculate validation score based on multiple criteria."""
        criteria_scores = {
            "risk_assessment": self._validate_risk_assessment(strategy_data),
            "performance_history": self._validate_performance_history(strategy_data),
            "strategy_logic": self._validate_strategy_logic(strategy_data),
            "market_compatibility": self._validate_market_compatibility(strategy_data)
        }
        
        # Weighted average of criteria scores
        weights = {"risk_assessment": 0.3, "performance_history": 0.3, 
                  "strategy_logic": 0.2, "market_compatibility": 0.2}
        
        total_score = 0
        total_weight = 0
        
        for criterion, score in criteria_scores.items():
            weight = weights.get(criterion, 0.25)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
        
    def _validate_risk_assessment(self, strategy_data: Dict[str, Any]) -> float:
        """Validate risk assessment of the strategy."""
        risk_score = strategy_data.get("risk_score", 0.5)
        max_drawdown = strategy_data.get("max_drawdown", 0.1)
        volatility = strategy_data.get("volatility", 0.2)
        
        # Score based on risk metrics
        risk_penalty = (risk_score * 0.4) + (max_drawdown * 0.3) + (volatility * 0.3)
        return max(0.0, 1.0 - risk_penalty)
        
    def _validate_performance_history(self, strategy_data: Dict[str, Any]) -> float:
        """Validate performance history of the strategy."""
        sharpe_ratio = strategy_data.get("sharpe_ratio", 1.0)
        total_return = strategy_data.get("total_return", 0.1)
        consistency = strategy_data.get("consistency", 0.8)
        
        # Score based on performance metrics
        performance_score = (sharpe_ratio * 0.4) + (total_return * 0.3) + (consistency * 0.3)
        return min(1.0, performance_score)
        
    def _validate_strategy_logic(self, strategy_data: Dict[str, Any]) -> float:
        """Validate the logic and structure of the strategy."""
        logic_complexity = strategy_data.get("logic_complexity", 0.5)
        parameter_count = strategy_data.get("parameter_count", 10)
        backtest_period = strategy_data.get("backtest_period_days", 365)
        
        # Score based on logic quality
        logic_score = 1.0 - (logic_complexity * 0.3)  # Simpler is better
        parameter_score = 1.0 - min(1.0, parameter_count / 50)  # Fewer parameters is better
        backtest_score = min(1.0, backtest_period / 730)  # Longer backtest is better
        
        return (logic_score * 0.4) + (parameter_score * 0.3) + (backtest_score * 0.3)
        
    def _validate_market_compatibility(self, strategy_data: Dict[str, Any]) -> float:
        """Validate market compatibility of the strategy."""
        market_conditions = strategy_data.get("market_conditions", [])
        asset_classes = strategy_data.get("asset_classes", [])
        timeframes = strategy_data.get("timeframes", [])
        
        # Score based on market compatibility
        condition_score = min(1.0, len(market_conditions) / 5)
        asset_score = min(1.0, len(asset_classes) / 3)
        timeframe_score = min(1.0, len(timeframes) / 2)
        
        return (condition_score * 0.4) + (asset_score * 0.3) + (timeframe_score * 0.3)
        
    def _get_validation_status(self, strategy_data: Dict[str, Any]) -> str:
        """Get validation status based on score."""
        score = self._calculate_validation_score(strategy_data)
        
        if score >= 0.8:
            return "approved"
        elif score >= 0.6:
            return "conditional_approval"
        else:
            return "rejected"
            
    def _identify_issues(self, strategy_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify issues with the strategy."""
        issues = []
        
        # Check for common issues
        if strategy_data.get("risk_score", 0) > 0.7:
            issues.append({"type": "high_risk", "severity": "high", "description": "Strategy has high risk score"})
            
        if strategy_data.get("max_drawdown", 0) > 0.2:
            issues.append({"type": "high_drawdown", "severity": "medium", "description": "Strategy has high maximum drawdown"})
            
        if strategy_data.get("parameter_count", 0) > 20:
            issues.append({"type": "over_parameterized", "severity": "medium", "description": "Strategy has too many parameters"})
            
        if strategy_data.get("backtest_period_days", 0) < 180:
            issues.append({"type": "short_backtest", "severity": "low", "description": "Strategy has short backtest period"})
            
        return issues
        
    def _generate_recommendations(self, strategy_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for strategy improvement."""
        recommendations = []
        
        # Generate recommendations based on validation results
        if strategy_data.get("risk_score", 0) > 0.6:
            recommendations.append({
                "type": "risk_reduction",
                "priority": "high",
                "description": "Consider implementing additional risk controls"
            })
            
        if strategy_data.get("parameter_count", 0) > 15:
            recommendations.append({
                "type": "simplification",
                "priority": "medium",
                "description": "Consider reducing the number of parameters"
            })
            
        if strategy_data.get("backtest_period_days", 0) < 365:
            recommendations.append({
                "type": "extended_backtest",
                "priority": "medium",
                "description": "Extend backtest period to at least one year"
            })
            
        return recommendations
