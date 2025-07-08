from fastapi import FastAPI, Depends, HTTPException
from dotenv import load_dotenv
from supabase import create_client, Client
from redis.asyncio import Redis
import os
from routes.signal import router as signal_router
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

app = FastAPI()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
redis = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")))

app.include_router(signal_router, prefix="/signal")
app.include_router(strategies_router, prefix="/strategies")
app.include_router(trade_router, prefix="/trade")
app.include_router(wallet_router, prefix="/wallet")
app.include_router(payments_router, prefix="/payments")
app.include_router(admin_router, prefix="/admin")

@app.get("/health")
async def health_check():
    try:
        # Check Supabase connection
        await supabase.table("system").select("id").limit(1).execute()
        # Check Redis connection
        await redis.ping()
        logger.info("Health check passed")
        return {"status": "healthy", "supabase": "ok", "redis": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)