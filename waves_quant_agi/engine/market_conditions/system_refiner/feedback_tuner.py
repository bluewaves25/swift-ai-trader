from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class FeedbackTuner:
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
        self.feedback_threshold = config.get("feedback_threshold", 0.2)  # 20% performance deviation

    async def tune_feedback(self, agent_feedback: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Refine feedback to strategy agents for real-time alignment."""
        try:
            feedback_adjustments = []
            for feedback in agent_feedback:
                agent = feedback.get("agent", "unknown")
                performance_score = float(feedback.get("performance_score", 0.5))
                target_score = float(self.redis_client.get(f"market_conditions:target_score:{agent}") or 0.5)

                if abs(performance_score - target_score) > self.feedback_threshold:
                    adjustment = {
                        "type": "feedback_adjustment",
                        "agent": agent,
                        "performance_score": performance_score,
                        "target_score": target_score,
                        "adjustment_factor": self._calculate_adjustment(performance_score, target_score),
                        "timestamp": int(time.time()),
                        "description": f"Feedback adjustment for {agent}: score {performance_score:.2f}, target {target_score:.2f}"
                    }
                    feedback_adjustments.append(adjustment)
                    self.logger.log_issue(adjustment)
                    self.cache.store_incident(adjustment)
                    self.redis_client.set(f"market_conditions:feedback:{agent}", str(adjustment), ex=604800)  # Expire after 7 days

            summary = {
                "type": "feedback_tuner_summary",
                "adjustment_count": len(feedback_adjustments),
                "timestamp": int(time.time()),
                "description": f"Tuned feedback for {len(feedback_adjustments)} agents"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return feedback_adjustments
        except Exception as e:
            self.logger.log(f"Error tuning feedback: {e}")
            self.cache.store_incident({
                "type": "feedback_tuner_error",
                "timestamp": int(time.time()),
                "description": f"Error tuning feedback: {str(e)}"
            })
            return []

    def _calculate_adjustment(self, performance_score: float, target_score: float) -> float:
        """Calculate adjustment factor (placeholder)."""
        return (target_score - performance_score) / target_score if target_score > 0 else 0.0

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of feedback tuning results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))