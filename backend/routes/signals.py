from fastapi import APIRouter, HTTPException
from redis.asyncio import Redis
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

# Redis client dependency
async def get_redis():
    return Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True  # Ensures .get() returns strings, not bytes
    )

@router.get("/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    redis = await get_redis()
    cache_key = f"sentiment:{symbol}"
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    try:
        # 1. OpenRouter Sentiment Score (LLM)
        openrouter_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "mistralai/mixtral-8x7b-instruct",
                "messages": [{
                    "role": "user",
                    "content": f"Analyze sentiment for {symbol} based on recent financial news. Return only a score between -1 and 1."
                }],
                "max_tokens": 50
            },
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            }
        )
        openrouter_content = openrouter_response.json()["choices"][0]["message"]["content"].strip()
        openrouter_score = float(openrouter_content)

        # 2. X (Twitter) Sentiment Score
        x_response = requests.get(
            "https://api.x.com/2/tweets/search/recent",
            params={"query": f"{symbol} crypto OR forex", "max_results": 100},
            headers={
                "Authorization": f"Bearer {os.getenv('X_API_KEY')}"
            }
        )
        tweets = x_response.json().get("data", [])
        x_score = (
            sum(1 for tweet in tweets if "bullish" in tweet["text"].lower()) -
            sum(1 for tweet in tweets if "bearish" in tweet["text"].lower())
        ) / max(len(tweets), 1)

        sentiment = {
            "symbol": symbol,
            "combined_score": round((openrouter_score + x_score) / 2, 3),
            "details": {
                "openrouter_score": round(openrouter_score, 3),
                "x_score": round(x_score, 3)
            }
        }

        await redis.setex(cache_key, 3600, json.dumps(sentiment))
        return sentiment

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")
