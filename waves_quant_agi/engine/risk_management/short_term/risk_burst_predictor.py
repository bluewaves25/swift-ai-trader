from typing import Dict, Any, List
import redis
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from ..market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ..market_conditions.memory.incident_cache import IncidentCache

class RiskBurstPredictor:
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
        self.model = RandomForestClassifier(n_estimators=config.get("n_estimators", 100))
        self.risk_probability_threshold = config.get("risk_probability_threshold", 0.7)

    async def predict_risk_pulse(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Predict risk pulses based on patterns, news, and anomalies."""
        try:
            features = market_data[["volatility", "news_sentiment", "anomaly_score"]].fillna(0).values
            labels = (market_data["loss_event"] > 0).astype(int).values
            self.model.fit(features, labels)
            risk_probabilities = self.model.predict_proba(features)[:, 1]

            predictions = []
            for i, row in market_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                risk_probability = float(risk_probabilities[i])

                if risk_probability > self.risk_probability_threshold:
                    prediction = {
                        "type": "risk_pulse",
                        "symbol": symbol,
                        "risk_probability": risk_probability,
                        "timestamp": int(time.time()),
                        "description": f"Risk pulse predicted for {symbol}: Probability {risk_probability:.2f}"
                    }
                    predictions.append(prediction)
                    self.logger.log_issue(prediction)
                    self.cache.store_incident(prediction)
                    self.redis_client.set(f"risk_management:risk_pulse:{symbol}", str(prediction), ex=3600)
                    await self.notify_execution(prediction)

            summary = {
                "type": "risk_pulse_summary",
                "prediction_count": len(predictions),
                "timestamp": int(time.time()),
                "description": f"Predicted {len(predictions)} risk pulses"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return predictions
        except Exception as e:
            self.logger.log(f"Error predicting risk pulse: {e}")
            self.cache.store_incident({
                "type": "risk_burst_predictor_error",
                "timestamp": int(time.time()),
                "description": f"Error predicting risk pulse: {str(e)}"
            })
            return []

    async def notify_execution(self, prediction: Dict[str, Any]):
        """Notify Executions Agent of risk pulse predictions."""
        self.logger.log(f"Notifying Executions Agent: {prediction.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(prediction))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of risk pulse prediction results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))