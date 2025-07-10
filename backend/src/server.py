import sys
sys.path.append(r"C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\ai-env\Lib\site-packages")
from fastapi import FastAPI, Depends, HTTPException
from dotenv import load_dotenv
import os
import redis.asyncio as redis
from routes.signals import router as signal_router
from routes.strategies import router as strategies_router
from routes.trade import router as trade_router
from routes.wallet import router as wallet_router
from routes.payments import router as payments_router
from routes.admin import router as admin_router
from src.auth_middleware import get_current_user
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

app = FastAPI()

# Redis dependency
async def get_redis():
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()

app.include_router(signal_router, prefix="/signals")
app.include_router(strategies_router, prefix="/strategies")
app.include_router(trade_router, prefix="/trade")
app.include_router(wallet_router, prefix="/wallet")
app.include_router(payments_router, prefix="/payments")
app.include_router(admin_router, prefix="/admin")

@app.get("/health")
async def health_check(redis_client: redis.Redis = Depends(get_redis)):
    try:
        # Check Redis connection
        await redis_client.ping()
        # Check system status from Redis (populated by system_status.py)
        system_status = await redis_client.get("system_status")
        if system_status is None:
            raise HTTPException(status_code=503, detail="System status unavailable")
        logger.info("Health check passed")
        return {"status": "healthy", "redis": "ok", "system_status": system_status}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)