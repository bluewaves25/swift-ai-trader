from typing import Dict, Any, List
import time
import redis
import pandas as pd
from .....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from .....market_conditions.memory.incident_cache import IncidentCache

class AgentSentiment:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
                self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.sentiment_threshold = config.get("sentiment_threshold", 0.7)  # Sentiment score threshold

    async def analyze_sentiment(self, social_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze social sentiment for agent-driven trading signals."""
        try:
            opportunities = []
            for _, row in social_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                sentiment_score = float(row.get("sentiment_score", 0.0))

                if sentiment_score > self.sentiment_threshold:
                    signal = "buy"
                    description = f"Bullish social sentiment for {symbol}: Score {sentiment_score:.2f}"
                elif sentiment_score < -self.sentiment_threshold:
                    signal = "sell"
                    description = f"Bearish social sentiment for {symbol}: Score {sentiment_score:.2f}"
                else:
                    continue

                opportunity = {
                    "type": "agent_sentiment",
                    "symbol": symbol,
                    "signal": signal,
                    "sentiment_score": sentiment_score,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                self.logger.log_strategy_deployment("deployment", opportunity)
                opportunity)
                self.redis_client.set(f"strategy_engine:sentiment:{symbol}", str(opportunity), ex=3600)
                await self.notify_execution(opportunity)

            summary = {
                "type": "agent_sentiment_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} social sentiment signals"
            }
            self.logger.log_strategy_deployment("deployment", summary)
            summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error analyzing social sentiment: {e}")
            {
                "type": "agent_sentiment_error",
                "timestamp": int(time.time()),
                "description": f"Error analyzing social sentiment: {str(e)}"
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