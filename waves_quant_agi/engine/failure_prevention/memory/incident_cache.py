import redis
from typing import Dict, Any, List
from ..logs.failure_agent_logger import FailureAgentLogger

class IncidentCache:
    def __init__(self, logger: FailureAgentLogger, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.logger = logger
        self.key_prefix = "failure_incident:"

    def store_incident(self, incident: Dict[str, Any]):
        """Store incident in Redis with a unique key."""
        try:
            key = f"{self.key_prefix}{incident['timestamp']}:{incident.get('type', 'unknown')}:{incident.get('source', 'unknown')}"
            self.redis.hset(key, mapping=incident)
            self.redis.expire(key, 604800)  # Expire after 7 days
            self.logger.log(f"Stored incident: {incident.get('description', 'unknown')[:50]}...")
        except Exception as e:
            self.logger.log(f"Error storing incident: {e}")

    def retrieve_incidents(self, key_pattern: str = "*") -> List[Dict[str, Any]]:
        """Retrieve incidents from Redis by key pattern."""
        try:
            keys = self.redis.keys(f"{self.key_prefix}{key_pattern}")
            incidents = []
            for key in keys[:100]:  # Limit to 100 for performance
                data = self.redis.hgetall(key)
                incidents.append({k: float(v) if k in {"timestamp", "value", "threshold", "risk_score", "confidence"} else v for k, v in data.items()})
            self.logger.log(f"Retrieved {len(incidents)} incidents for pattern {key_pattern}")
            return incidents
        except Exception as e:
            self.logger.log(f"Error retrieving incidents: {e}")
            return []