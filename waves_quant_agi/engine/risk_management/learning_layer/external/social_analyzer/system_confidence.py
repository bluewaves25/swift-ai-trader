from typing import Dict, Any, List
import redis
import pandas as pd
from .....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from .....market_conditions.memory.incident_cache import IncidentCache

class SystemConfidence:
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
        self.confidence_threshold = config.get("confidence_threshold", 0.8)  # 80% confidence threshold

    async def assess_confidence(self, system_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Assess system-wide confidence for risk decisions."""
        try:
            confidence_results = []
            for _, row in system_data.iterrows():
                component = row.get("component", "unknown")
                confidence_score = float(row.get("confidence_score", 0.0))

                if confidence_score < self.confidence_threshold:
                    result = {
                        "type": "system_confidence",
                        "component": component,
                        "confidence_score": confidence_score,
                        "timestamp": int(time.time()),
                        "description": f"Low system confidence for {component}: Score {confidence_score:.2f}"
                    }
                    confidence_results.append(result)
                    self.logger.log_issue(result)
                    self.cache.store_incident(result)
                    self.redis_client.set(f"risk_management:system_confidence:{component}", str(result), ex=3600)
                    await self.notify_execution(result)
                else:
                    result = {
                        "type": "system_confidence",
                        "component": component,
                        "confidence_score": confidence_score,
                        "timestamp": int(time.time()),
                        "description": f"High system confidence for {component}: Score {confidence_score:.2f}"
                    }
                    confidence_results.append(result)
                    self.logger.log_issue(result)
                    self.cache.store_incident(result)

            summary = {
                "type": "system_confidence_summary",
                "result_count": len(confidence_results),
                "timestamp": int(time.time()),
                "description": f"Assessed confidence for {len(confidence_results)} components"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return confidence_results
        except Exception as e:
            self.logger.log(f"Error assessing system confidence: {e}")
            self.cache.store_incident({
                "type": "system_confidence_error",
                "timestamp": int(time.time()),
                "description": f"Error assessing system confidence: {str(e)}"
            })
            return []

    async def notify_execution(self, result: Dict[str, Any]):
        """Notify Executions Agent of low confidence signals."""
        self.logger.log(f"Notifying Executions Agent: {result.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of system confidence results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))