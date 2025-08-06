from typing import Dict, Any, List
import redis
import pandas as pd
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
        self.strategy_impact_threshold = config.get("strategy_impact_threshold", 0.6)  # 60% impact score

    async def coordinate_strategies(self, case_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Coordinate risk strategies based on external insights."""
        try:
            coordination_results = []
            for _, row in case_data.iterrows():
                strategy = row.get("strategy", "unknown")
                impact_score = float(row.get("impact_score", 0.0))
                symbol = row.get("symbol", "BTC/USD")

                if impact_score >= self.strategy_impact_threshold:
                    result = {
                        "type": "strategy_coordination",
                        "strategy": strategy,
                        "symbol": symbol,
                        "impact_score": impact_score,
                        "timestamp": int(time.time()),
                        "description": f"Coordinated {strategy} for {symbol}: Impact {impact_score:.2f}"
                    }
                    coordination_results.append(result)
                    self.logger.log_issue(result)
                    self.cache.store_incident(result)
                    self.redis_client.set(f"risk_management:coordination:{strategy}:{symbol}", str(result), ex=3600)
                    await self.notify_execution(result)
                else:
                    result = {
                        "type": "strategy_coordination",
                        "strategy": strategy,
                        "symbol": symbol,
                        "impact_score": impact_score,
                        "timestamp": int(time.time()),
                        "description": f"Skipped coordination for {strategy} on {symbol}: Impact {impact_score:.2f}"
                    }
                    coordination_results.append(result)
                    self.logger.log_issue(result)
                    self.cache.store_incident(result)

            summary = {
                "type": "coordination_summary",
                "result_count": len(coordination_results),
                "timestamp": int(time.time()),
                "description": f"Coordinated {len(coordination_results)} risk strategies"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return coordination_results
        except Exception as e:
            self.logger.log(f"Error coordinating strategies: {e}")
            self.cache.store_incident({
                "type": "orchestration_cases_error",
                "timestamp": int(time.time()),
                "description": f"Error coordinating strategies: {str(e)}"
            })
            return []

    async def notify_execution(self, result: Dict[str, Any]):
        """Notify Executions Agent of coordinated strategies."""
        self.logger.log(f"Notifying Executions Agent: {result.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of strategy coordination results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))