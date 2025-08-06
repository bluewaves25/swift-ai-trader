from typing import Dict, Any, List
import redis
from .....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from .....market_conditions.memory.incident_cache import IncidentCache

class OrchestrationCases:
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
        self.priority_threshold = config.get("priority_threshold", 0.8)  # Strategy priority score

    async def coordinate_strategies(self, strategy_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Coordinate strategies based on priority and market conditions."""
        try:
            coordinated = []
            for data in strategy_data:
                strategy_id = data.get("strategy_id", "unknown")
                symbol = data.get("symbol", "unknown")
                priority_score = float(data.get("priority_score", 0.0))

                if priority_score > self.priority_threshold:
                    coordination = {
                        "type": "strategy_coordination",
                        "strategy_id": strategy_id,
                        "symbol": symbol,
                        "priority_score": priority_score,
                        "timestamp": int(time.time()),
                        "description": f"Coordinated {strategy_id} for {symbol}: Priority {priority_score:.2f}"
                    }
                    coordinated.append(coordination)
                    self.logger.log_issue(coordination)
                    self.cache.store_incident(coordination)
                    self.redis_client.set(f"strategy_engine:coordination:{strategy_id}", str(coordination), ex=3600)
                    await self.notify_execution(coordination)

            summary = {
                "type": "coordination_summary",
                "coordination_count": len(coordinated),
                "timestamp": int(time.time()),
                "description": f"Coordinated {len(coordinated)} strategies"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return coordinated
        except Exception as e:
            self.logger.log(f"Error coordinating strategies: {e}")
            self.cache.store_incident({
                "type": "orchestration_cases_error",
                "timestamp": int(time.time()),
                "description": f"Error coordinating strategies: {str(e)}"
            })
            return []

    async def notify_execution(self, coordination: Dict[str, Any]):
        """Notify Executions Agent of coordinated strategy."""
        self.logger.log(f"Notifying Executions Agent: {coordination.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(coordination))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of coordination results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))