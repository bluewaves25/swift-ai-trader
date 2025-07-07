from fastapi import APIRouter, HTTPException
from redis.asyncio import Redis
import requests
import json
from python_dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

async def get_redis():
    return Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")))

@router.get("/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    redis = await get_redis()
    cached = await redis.get(f"sentiment:{symbol}")
    if cached:
        return json.loads(cached)
    try:
        openrouter_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={"model": "mistralai/mixtral-8x7b-instruct", "messages": [{"role": "user", "content": f"Analyze sentiment for {symbol} based on recent financial news."}], "max_tokens": 50},
            headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}", "Content-Type": "application/json"}
        )
        x_response = requests.get(
            "https://api.x.com/2/tweets/search/recent",
            params={"query": f"{symbol} crypto OR forex", "max_results": 100},
            headers={"Authorization": f"Bearer {os.getenv('X_API_KEY')}"}
        )
        openrouter_score = float(openrouter_response.json()["choices"][0]["message"]["content"].strip())
        tweets = x_response.json().get("data", [])
        x_score = (sum(1 for tweet in tweets if "bullish" in tweet["text"].lower()) - sum(1 for tweet in tweets if "bearish" in tweet["text"].lower())) / max(len(tweets), 1)
        sentiment = {"symbol": symbol, "combined_score": (openrouter_score + x_score) / 2}
        await redis.setex(f"sentiment:{symbol}", 3600, json.dumps(sentiment))
        return sentiment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))