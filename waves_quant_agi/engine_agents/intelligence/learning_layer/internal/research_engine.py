from typing import Dict, Any, List
import redis
import time
from ...logs.intelligence_logger import IntelligenceLogger

class ResearchEngine:
    def __init__(self, config: Dict[str, Any], logger: IntelligenceLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.pattern_threshold = config.get("pattern_threshold", 0.5)

    async def analyze_coordination_patterns(self, key_pattern: str = "*") -> Dict[str, Any]:
        """Analyze agent coordination patterns from Redis data."""
        try:
            # Get data from Redis instead of cache
            incidents = []
            try:
                # Get recent incidents from Redis
                recent_data = self.redis_client.get("intelligence:recent_incidents")
                if recent_data:
                    incidents = eval(recent_data)  # Simple parsing for demo
            except:
                incidents = []

            patterns = {"by_agent": {}, "by_task": {}, "conflict_patterns": []}
            for incident in incidents:
                agent = incident.get("agent", "unknown")
                task = incident.get("task", "unknown")
                performance_score = float(incident.get("performance_score", 0.0))

                # Aggregate by agent and task
                patterns["by_agent"].setdefault(agent, []).append(performance_score)
                patterns["by_task"].setdefault(task, []).append(performance_score)

                # Detect conflict patterns
                if incident.get("type") in ["conflict_resolution", "low_reward"]:
                    patterns["conflict_patterns"].append({
                        "agents": incident.get("agents", []),
                        "task": task,
                        "score": performance_score
                    })

            # Filter high-impact patterns
            high_impact = [
                p for p in patterns["conflict_patterns"]
                if any(score < self.pattern_threshold for score in patterns["by_agent"].get(p["agents"][0], [1.0]))
            ]
            patterns["high_impact_conflicts"] = high_impact

            result = {
                "type": "coordination_patterns",
                "pattern_count": len(high_impact),
                "timestamp": int(time.time()),
                "description": f"Identified {len(high_impact)} high-impact coordination patterns"
            }
            self.logger.log_alert(result)
            self.redis_client.set("intelligence:coordination_patterns", str(patterns), ex=604800)  # Expire after 7 days
            await self.notify_core(result)
            return patterns
        except Exception as e:
            self.logger.log_error(f"Error analyzing coordination patterns: {e}")
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of coordination pattern analysis."""
        self.logger.log_info(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish to Core Agent