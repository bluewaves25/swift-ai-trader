from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class AgentSentiment:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.sentiment_threshold = config.get("sentiment_threshold", 0.7)  # 70% sentiment confidence

    async def analyze_sentiment(self, social_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze social sentiment via X API for risk signals."""
        try:
            sentiment_results = []
            for _, row in social_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                sentiment_score = float(row.get("sentiment_score", 0.0))

                if abs(sentiment_score) >= self.sentiment_threshold:
                    result = {
                        "type": "social_sentiment",
                        "symbol": symbol,
                        "sentiment_score": sentiment_score,
                        "timestamp": int(time.time()),
                        "description": f"Significant sentiment for {symbol}: Score {sentiment_score:.2f}"
                    }
                    sentiment_results.append(result)
                    self.logger.log_risk_assessment("assessment", result)
                    self.redis_client.set(f"risk_management:social_sentiment:{symbol}", str(result), ex=3600)
                    await self.notify_execution(result)
                else:
                    result = {
                        "type": "social_sentiment",
                        "symbol": symbol,
                        "sentiment_score": sentiment_score,
                        "timestamp": int(time.time()),
                        "description": f"Neutral sentiment for {symbol}: Score {sentiment_score:.2f}"
                    }
                    sentiment_results.append(result)
                    self.logger.log_risk_assessment("assessment", result)

            summary = {
                "type": "social_sentiment_summary",
                "result_count": len(sentiment_results),
                "timestamp": int(time.time()),
                "description": f"Analyzed sentiment for {len(sentiment_results)} symbols"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return sentiment_results
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, result: Dict[str, Any]):
        """Notify Executions Agent of significant sentiment signals."""
        self.logger.log(f"Notifying Executions Agent: {result.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of social sentiment analysis results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))