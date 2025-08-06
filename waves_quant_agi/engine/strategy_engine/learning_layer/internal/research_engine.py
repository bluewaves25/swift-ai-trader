from typing import Dict, Any, List
import redis
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
        self.failure_threshold = config.get("failure_threshold", 0.1)  # 10% failure rate

    async def analyze_failures(self, performance_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze strategy failure patterns for optimization."""
        try:
            failure_patterns = []
            for data in performance_data:
                strategy_id = data.get("strategy_id", "unknown")
                symbol = data.get("symbol", "unknown")
                failure_rate = float(data.get("failure_rate", 0.0))

                if failure_rate > self.failure_threshold:
                    pattern = {
                        "type": "failure_pattern",
                        "strategy_id": strategy_id,
                        "symbol": symbol,
                        "failure_rate": failure_rate,
                        "timestamp": int(time.time()),
                        "description": f"Failure pattern for {strategy_id} ({symbol}): Failure rate {failure_rate:.2f}"
                    }
                    failure_patterns.append(pattern)
                    self.logger.log_issue(pattern)
                    self.cache.store_incident(pattern)
                    self.redis_client.set(f"strategy_engine:failure_pattern:{strategy_id}", str(pattern), ex=604800)
                    await/self.notify_training(pattern)

            summary = {
                "type": "failure_analysis_summary",
                "pattern_count": len(failure_patterns),
                "timestamp": int(time.time()),
                "description": f"Identified {len(failure_patterns)} failure patterns"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return failure_patterns
        except Exception as e:
            self.logger.log(f"Error analyzing failures: {e}")
            self.cache.store_incident({
                "type": "research_engine_error",
                "timestamp": int(time.time()),
                "description": f"Error analyzing failures: {str(e)}"
            })
            return []

    async def notify_training(self, pattern: Dict[str, Any]):
        """Notify Training Module of failure patterns."""
        self.logger.log(f"Notifying Training Module: {pattern.get('description', 'unknown')}")
        self.redis_client.publish("training_module", str(pattern))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of failure analysis results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))