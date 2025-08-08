from typing import Dict, Any, List
import time
from ....logs.intelligence_logger import IntelligenceLogger

class AgentFusionEngine:
    def __init__(self, config: Dict[str, Any], logger: IntelligenceLogger):
        self.config = config
        self.logger = logger
        self.fusion_threshold = config.get("fusion_threshold", 0.6)
        
    async def fuse_agent_intelligence(self, agent_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fuse intelligence from multiple agents into unified insights."""
        try:
            fused_intelligence = {
                "fusion_id": f"fusion_{int(time.time())}",
                "agent_count": len(agent_data_list),
                "fused_insights": self._generate_fused_insights(agent_data_list),
                "confidence": self._calculate_fusion_confidence(agent_data_list),
                "timestamp": int(time.time())
            }
            
            self.logger.log_info(f"Fused intelligence from {fused_intelligence['agent_count']} agents")
            return fused_intelligence
            
        except Exception as e:
            self.logger.log_error(f"Error in agent fusion: {e}")
            return {"error": str(e)}
            
    def _generate_fused_insights(self, agent_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fused insights from multiple agents."""
        insights = {
            "market_sentiment": self._fuse_market_sentiment(agent_data_list),
            "risk_assessment": self._fuse_risk_assessment(agent_data_list),
            "performance_metrics": self._fuse_performance_metrics(agent_data_list)
        }
        return insights
        
    def _fuse_market_sentiment(self, agent_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fuse market sentiment from multiple agents."""
        sentiments = []
        for agent_data in agent_data_list:
            if "sentiment" in agent_data:
                sentiments.append(agent_data["sentiment"])
        
        if not sentiments:
            return {"fused_sentiment": "neutral", "confidence": 0.5}
            
        avg_sentiment = sum(sentiments) / len(sentiments)
        return {
            "fused_sentiment": "positive" if avg_sentiment > 0.6 else "negative" if avg_sentiment < 0.4 else "neutral",
            "confidence": min(1.0, len(sentiments) / 10),
            "agent_count": len(sentiments)
        }
        
    def _fuse_risk_assessment(self, agent_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fuse risk assessments from multiple agents."""
        risk_scores = []
        for agent_data in agent_data_list:
            if "risk_score" in agent_data:
                risk_scores.append(agent_data["risk_score"])
        
        if not risk_scores:
            return {"fused_risk": "medium", "confidence": 0.5}
            
        avg_risk = sum(risk_scores) / len(risk_scores)
        return {
            "fused_risk": "high" if avg_risk > 0.7 else "low" if avg_risk < 0.3 else "medium",
            "average_risk": avg_risk,
            "confidence": min(1.0, len(risk_scores) / 10)
        }
        
    def _fuse_performance_metrics(self, agent_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fuse performance metrics from multiple agents."""
        metrics = {"success_rate": [], "error_rate": []}
        
        for agent_data in agent_data_list:
            if "performance" in agent_data:
                perf = agent_data["performance"]
                if "success_rate" in perf:
                    metrics["success_rate"].append(perf["success_rate"])
                if "error_rate" in perf:
                    metrics["error_rate"].append(perf["error_rate"])
        
        fused_metrics = {}
        for metric_name, values in metrics.items():
            if values:
                fused_metrics[metric_name] = sum(values) / len(values)
        
        return fused_metrics
        
    def _calculate_fusion_confidence(self, agent_data_list: List[Dict[str, Any]]) -> float:
        """Calculate confidence in fused intelligence."""
        if not agent_data_list:
            return 0.0
            
        confidences = []
        for agent_data in agent_data_list:
            if "confidence" in agent_data:
                confidences.append(agent_data["confidence"])
        
        if not confidences:
            return 0.5
            
        avg_confidence = sum(confidences) / len(confidences)
        agent_factor = min(1.0, len(agent_data_list) / 10)
        
        return avg_confidence * agent_factor
