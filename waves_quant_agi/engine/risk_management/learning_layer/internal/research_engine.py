from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class ResearchEngine:
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
        self.failure_threshold = config.get("failure_threshold", 0.1)  # 10% failure rate threshold

    async def analyze_failures(self, incident_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze failure patterns for risk model improvement."""
        try:
            failure_patterns = []
            for risk_type in incident_data["type"].unique():
                type_data = incident_data[incident_data["type"] == risk_type]
                failure_rate = len(type_data[type_data["description"].str.contains("denied|failed")]) / len(type_data) if len(type_data) > 0 else 0.0

                if failure_rate > self.failure_threshold:
                    pattern = {
                        "type": "failure_pattern",
                        "risk_type": risk_type,
                        "failure_rate": failure_rate,
                        "timestamp": int(time.time()),
                        "description": f"High failure rate detected for {risk_type}: Failure rate {failure_rate:.2%}"
                    }
                    failure_patterns.append(pattern)
                    self.logger.log_issue(pattern)
                    self.cache.store_incident(pattern)
                    self.redis_client.set(f"risk_management:failure_pattern:{risk_type}", str(pattern), ex=604800)
                    await self.notify_retraining(pattern)

            summary = {
                "type": "failure_analysis_summary",
                "pattern_count": len(failure_patterns),
                "timestamp": int(time.time()),
                "description": f"Analyzed {len(failure_patterns)} failure patterns"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return failure_patterns
        except Exception as e:
            self.logger.log(f"Error analyzing failure patterns: {e}")
            self.cache.store_incident({
                "type": "research_engine_error",
                "timestamp": int(time.time()),
                "description": f"Error analyzing failure patterns: {str(e)}"
            })
            return []

    async def notify_retraining(self, pattern: Dict[str, Any]):
        """Notify retraining module of detected failure patterns."""
        self.logger.log(f"Notifying Retraining Module: {pattern.get('description', 'unknown')}")
        self.redis_client.publish("retraining_module", str(pattern))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of failure analysis results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))