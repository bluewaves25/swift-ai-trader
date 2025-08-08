from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class ConditionResearcher:
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
        self.metadata_threshold = config.get("metadata_threshold", 0.5)  # Relevance score threshold

    async def gather_condition_metadata(self, key_pattern: str = "market_conditions:*") -> Dict[str, Any]:
        """Gather historical and real-time condition metadata."""
        try:
            metadata = []
            keys = self.redis_client.keys(key_pattern)
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    relevance_score = self._calculate_relevance(data)
                    if relevance_score > self.metadata_threshold:
                        meta = {
                            "type": "condition_metadata",
                            "key": key,
                            "relevance_score": relevance_score,
                            "timestamp": int(time.time()),
                            "description": f"Metadata for {key}: relevance {relevance_score:.2f}"
                        }
                        metadata.append(meta)
                        self.logger.log_issue(meta)
                        self.cache.store_incident(meta)
                        self.redis_client.set(f"market_conditions:metadata:{key}", str(meta), ex=604800)  # Expire after 7 days

            summary = {
                "type": "metadata_summary",
                "metadata_count": len(metadata),
                "timestamp": int(time.time()),
                "description": f"Gathered {len(metadata)} condition metadata entries"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return summary
        except Exception as e:
            self.logger.log(f"Error gathering condition metadata: {e}")
            self.cache.store_incident({
                "type": "condition_researcher_error",
                "timestamp": int(time.time()),
                "description": f"Error gathering condition metadata: {str(e)}"
            })
            return {}

    def _calculate_relevance(self, data: str) -> float:
        """Calculate relevance score (placeholder)."""
        # Mock: Higher data recency increases relevance
        return 0.7 if "timestamp" in data else 0.5

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of metadata results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))