from typing import Dict, Any, List
import redis
import pandas as pd
import numpy as np
from .....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from .....market_conditions.memory.incident_cache import IncidentCache

class SystemPredictor:
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
        self.performance_threshold = config.get("performance_threshold", 0.8)  # 80% performance score

    async def predict_performance(self, system_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Predict system performance for risk management."""
        try:
            performance_predictions = []
            for _, row in system_data.iterrows():
                component = row.get("component", "unknown")
                performance_score = float(row.get("performance_score", 0.0))

                if performance_score < self.performance_threshold:
                    prediction = {
                        "type": "system_performance",
                        "component": component,
                        "performance_score": performance_score,
                        "timestamp": int(time.time()),
                        "description": f"Low performance predicted for {component}: Score {performance_score:.2f}"
                    }
                    performance_predictions.append(prediction)
                    self.logger.log_issue(prediction)
                    self.cache.store_incident(prediction)
                    self.redis_client.set(f"risk_management:system_performance:{component}", str(prediction), ex=3600)
                    await self.notify_maintenance(prediction)
                else:
                    prediction = {
                        "type": "system_performance",
                        "component": component,
                        "performance_score": performance_score,
                        "timestamp": int(time.time()),
                        "description": f"Stable performance predicted for {component}: Score {performance_score:.2f}"
                    }
                    performance_predictions.append(prediction)
                    self.logger.log_issue(prediction)
                    self.cache.store_incident(prediction)

            summary = {
                "type": "system_performance_summary",
                "prediction_count": len(performance_predictions),
                "timestamp": int(time.time()),
                "description": f"Predicted performance for {len(performance_predictions)} components"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return performance_predictions
        except Exception as e:
            self.logger.log(f"Error predicting system performance: {e}")
            self.cache.store_incident({
                "type": "system_predictor_error",
                "timestamp": int(time.time()),
                "description": f"Error predicting system performance: {str(e)}"
            })
            return []

    async def notify_maintenance(self, prediction: Dict[str, Any]):
        """Notify Maintenance System of low performance predictions."""
        self.logger.log(f"Notifying Maintenance System: {prediction.get('description', 'unknown')}")
        self.redis_client.publish("maintenance_system", str(prediction))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of system performance predictions."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))