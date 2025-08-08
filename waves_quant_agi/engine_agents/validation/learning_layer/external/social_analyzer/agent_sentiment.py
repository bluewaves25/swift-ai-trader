from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class AgentSentiment:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.sentiment_threshold = config.get("sentiment_threshold", 0.6)  # 60% confidence

    async def analyze_sentiment(self, social_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Assess trust perception in validators."""
        try:
            sentiments = []
            for _, row in social_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                sentiment_score = float(row.get("sentiment_score", 0.0))
                source = row.get("source", "unknown")

                if abs(sentiment_score) >= self.sentiment_threshold:
                    sentiment = {
                        "type": "sentiment_analysis",
                        "symbol": symbol,
                        "source": source,
                        "sentiment_score": sentiment_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Validator trust sentiment for {symbol} from {source}: Score {sentiment_score:.2f}"
                    }
                    sentiments.append(sentiment)
                    self.redis_client.set(f"validation:sentiment:{symbol}:{source}", json.dumps(sentiment), ex=604800)
                    await self.notify_fusion(sentiment)

            summary = {
                "type": "sentiment_summary",
                "sentiment_count": len(sentiments),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Analyzed {len(sentiments)} validator trust sentiments"
            }
            self.redis_client.set("validation:sentiment_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return sentiments
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "agent_sentiment_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error analyzing sentiment: {str(e)}"
            }))
            return []

    async def notify_fusion(self, sentiment: Dict[str, Any]):
        """Notify Agent Fusion Engine of sentiment analysis."""
        self.redis_client.publish("agent_fusion_engine", json.dumps(sentiment))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of sentiment analysis results."""
        self.redis_client.publish("validation_output", json.dumps(issue))