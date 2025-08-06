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
        self.validation_threshold = config.get("validation_threshold", 0.7)  # Validation score

    async def validate_strategy(self, strategy_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate external strategies for integration."""
        try:
            validations = []
            for _, row in strategy_data.iterrows():
                strategy_id = row.get("strategy_id", "unknown")
                symbol = row.get("symbol", "BTC/USD")
                performance_score = float(row.get("performance_score", 0.0))

                if performance_score >= self.validation_threshold:
                    validation = {
                        "type": "strategy_validation",
                        "strategy_id": strategy_id,
                        "symbol": symbol,
                        "performance_score": performance_score,
                        "timestamp": int(time.time()),
                        "description": f"Validated strategy {strategy_id} for {symbol}: Score {performance_score:.2f}"
                    }
                    validations.append(validation)
                    self.logger.log_issue(validation)
                    self.cache.store_incident(validation)
                    self.redis_client.set(f"strategy_engine:validation:{strategy_id}", str(validation), ex=604800)
                    await self.notify_core(validation)
                else:
                    self.logger.log(f"Strategy {strategy_id} failed validation: Score {performance_score:.2f}")

            summary = {
                "type": "validation_summary",
                "validation_count": len(validations),
                "timestamp": int(time.time()),
                "description": f"Validated {len(validations)} external strategies"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return validations
        except Exception as e:
            self.logger.log(f"Error validating external strategy: {e}")
            self.cache.store_incident({
                "type": "external_strategy_validator_error",
                "timestamp": int(time.time()),
                "description": f"Error validating external strategy: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of validation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))