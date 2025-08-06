from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class SentimentAnalysis:
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
        self.sentiment_threshold = config.get("sentiment_threshold", 0.7)  # Sentiment score threshold

    async def detect_sentiment_signal(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect trading signals based on social/news sentiment."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                sentiment_score = float(row.get("sentiment_score", 0.0))

                if sentiment_score > self.sentiment_threshold:
                    signal = "buy"
                    description = f"Bullish sentiment for {symbol}: Score {sentiment_score:.2f}"
                elif sentiment_score < -self.sentiment_threshold:
                    signal = "sell"
                    description = f"Bearish sentiment for {symbol}: Score {sentiment_score:.2f}"
                else:
                    continue

                opportunity = {
                    "type": "sentiment_analysis",
                    "symbol": symbol,
                    "signal": signal,
                    "sentiment_score": sentiment_score,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                self.logger.log_issue(opportunity)
                self.cache.store_incident(opportunity)
                self.redis_client.set(f"strategy_engine:sentiment_analysis:{symbol}", str(opportunity), ex=3600)
                await self.notify_execution(opportunity)

            summary = {
                "type": "sentiment_analysis_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} sentiment-based opportunities"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting sentiment signal: {e}")
            self.cache.store_incident({
                "type": "sentiment_analysis_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting sentiment signal: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of sentiment signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of sentiment results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))