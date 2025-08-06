from typing import Dict, Any, List
import redis
import pandas as pd
from .....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from .....market_conditions.memory.incident_cache import IncidentCache

class ExternalStrategyValidator:
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
        self.risk_compliance_threshold = config.get("risk_compliance_threshold", 0.9)  # 90% compliance score

    async def validate_strategies(self, strategy_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate external strategies for risk compliance."""
        try:
            validation_results = []
            for _, row in strategy_data.iterrows():
                strategy = row.get("strategy", "unknown")
                compliance_score = float(row.get("compliance_score", 0.0))
                symbol = row.get("symbol", "BTC/USD")

                if compliance_score >= self.risk_compliance_threshold:
                    result = {
                        "type": "strategy_validation",
                        "strategy": strategy,
                        "symbol": symbol,
                        "compliance_score": compliance_score,
                        "timestamp": int(time.time()),
                        "description": f"External strategy {strategy} validated for {symbol}: Compliance {compliance_score:.2f}"
                    }
                    validation_results.append(result)
                    self.logger.log_issue(result)
                    self.cache.store_incident(result)
                    self.redis_client.set(f"risk_management:strategy_validation:{strategy}:{symbol}", str(result), ex=3600)
                    await self.notify_execution(result)
                else:
                    result = {
                        "type": "strategy_validation",
                        "strategy": strategy,
                        "symbol": symbol,
                        "compliance_score": compliance_score,
                        "timestamp": int(time.time()),
                        "description": f"External strategy {strategy} failed validation for {symbol}: Compliance {compliance_score:.2f}"
                    }
                    validation_results.append(result)
                    self.logger.log_issue(result)
                    self.cache.store_incident(result)

            summary = {
                "type": "strategy_validation_summary",
                "result_count": len(validation_results),
                "timestamp": int(time.time()),
                "description": f"Validated {len(validation_results)} external strategies"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return validation_results
        except Exception as e:
            self.logger.log(f"Error validating external strategies: {e}")
            self.cache.store_incident({
                "type": "external_strategy_validator_error",
                "timestamp": int(time.time()),
                "description": f"Error validating external strategies: {str(e)}"
            })
            return []

    async def notify_execution(self, result: Dict[str, Any]):
        """Notify Executions Agent of validated strategies."""
        self.logger.log(f"Notifying Executions Agent: {result.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of strategy validation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))