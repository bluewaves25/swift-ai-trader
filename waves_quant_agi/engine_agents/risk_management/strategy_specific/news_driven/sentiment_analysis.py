from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class SentimentAnalysisRisk:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.sentiment_score_threshold = config.get("sentiment_score_threshold", 0.7)  # 70% sentiment confidence
        self.volatility_tolerance = config.get("volatility_tolerance", 0.4)  # 40% volatility limit

    async def evaluate_risk(self, sentiment_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for sentiment-driven trading strategy."""
        try:
            risk_decisions = []
            for _, row in sentiment_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                sentiment_score = float(row.get("sentiment_score", 0.0))
                volatility = float(row.get("volatility", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if abs(sentiment_score) < self.sentiment_score_threshold or volatility > self.volatility_tolerance:
                    decision = {
                        "type": "sentiment_analysis_risk",
                        "symbol": symbol,
                        "sentiment_score": sentiment_score,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Sentiment analysis denied for {symbol}: Sentiment {sentiment_score:.2f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "sentiment_analysis_risk",
                        "symbol": symbol,
                        "sentiment_score": sentiment_score,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Sentiment analysis approved for {symbol}: Sentiment {sentiment_score:.2f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_risk_assessment("assessment", decision)
                decision)
                self.redis_client.set(f"risk_management:sentiment_analysis:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Sentiment analysis approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "sentiment_analysis_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} sentiment analysis risks"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved sentiment risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of sentiment risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))