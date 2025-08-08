from typing import Dict, Any, List
import time
from ....logs.intelligence_logger import IntelligenceLogger

class SystemConfidence:
    def __init__(self, config: Dict[str, Any], logger: IntelligenceLogger):
        self.config = config
        self.logger = logger
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        
    async def calculate_system_confidence(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall system confidence based on agent performance."""
        try:
            confidence_score = self._calculate_confidence_score(system_data)
            confidence_result = {
                "system_id": system_data.get("system_id", "trading_system"),
                "confidence_score": confidence_score,
                "confidence_level": self._get_confidence_level(confidence_score),
                "factors": self._analyze_confidence_factors(system_data),
                "timestamp": int(time.time())
            }
            
            self.logger.log_info(f"Calculated system confidence: {confidence_result['confidence_level']}")
            return confidence_result
            
        except Exception as e:
            self.logger.log_error(f"Error in confidence calculation: {e}")
            return {"error": str(e)}
            
    def _calculate_confidence_score(self, system_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on system metrics."""
        # Mock implementation: Replace with actual confidence calculation
        agent_count = system_data.get("agent_count", 0)
        success_rate = system_data.get("success_rate", 0.8)
        error_rate = system_data.get("error_rate", 0.1)
        uptime = system_data.get("uptime", 0.95)
        
        # Weighted scoring based on multiple factors
        score = (success_rate * 0.4) + (uptime * 0.3) + ((1 - error_rate) * 0.3)
        return max(0.0, min(1.0, score))
        
    def _get_confidence_level(self, score: float) -> str:
        """Convert confidence score to level."""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"
            
    def _analyze_confidence_factors(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze factors contributing to confidence."""
        factors = {
            "agent_performance": system_data.get("agent_performance", {}),
            "system_stability": system_data.get("system_stability", 0.8),
            "data_quality": system_data.get("data_quality", 0.9),
            "communication_health": system_data.get("communication_health", 0.85)
        }
        return factors
