from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class ExternalStrategyValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.validation_threshold = config.get("validation_threshold", 0.9)  # 90% compliance

    async def validate_strategies(self, strategy_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate external strategies for quality."""
        try:
            validations = []
            for _, row in strategy_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                strategy_type = row.get("strategy_type", "default")
                compliance_score = float(row.get("compliance_score", 0.0))

                if compliance_score >= self.validation_threshold:
                    validation = {
                        "type": "strategy_validation",
                        "symbol": symbol,
                        "strategy_type": strategy_type,
                        "compliance_score": compliance_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Validated {strategy_type} for {symbol}: Score {compliance_score:.2f}"
                    }
                    validations.append(validation)
                    self.redis_client.set(f"validation:strategy:{symbol}:{strategy_type}", json.dumps(validation), ex=604800)
                    await self.notify_core(validation)
                else:
                    validation = {
                        "type": "strategy_validation",
                        "symbol": symbol,
                        "strategy_type": strategy_type,
                        "compliance_score": compliance_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Failed validation for {strategy_type} on {symbol}: Score {compliance_score:.2f}"
                    }
                    validations.append(validation)
                    self.redis_client.lpush("validation:errors", json.dumps(validation))

            summary = {
                "type": "strategy_validation_summary",
                "validation_count": len(validations),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Validated {len(validations)} external strategies"
            }
            self.redis_client.set("validation:strategy_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return validations
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "external_strategy_validator_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error validating strategies: {str(e)}"
            }))
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of validation results."""
        self.redis_client.publish("validation_output", json.dumps(issue))