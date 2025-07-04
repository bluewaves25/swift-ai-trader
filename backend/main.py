
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import trade, wallet, strategies
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Waves Quant Engine API",
    description="Multi-Asset Trading Platform Backend",
    version="1.0.0"
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.lovable.app",
        "https://*.supabase.co"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return {"error": "Internal server error", "detail": str(exc)}

# Mount enhanced routes
app.include_router(trade.router, prefix="/api/trade", tags=["Trading"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["Wallet"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["Strategies"])

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Waves Quant Engine API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Waves Quant Engine",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Engine control endpoints
@app.post("/api/engine/start", tags=["Engine"])
async def start_trading_engine():
    try:
        # Add your engine start logic here
        logger.info("Trading engine start requested")
        return {"status": "success", "message": "Trading engine started"}
    except Exception as e:
        logger.error(f"Failed to start engine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/engine/stop", tags=["Engine"])
async def stop_trading_engine():
    try:
        # Add your engine stop logic here
        logger.info("Trading engine stop requested")
        return {"status": "success", "message": "Trading engine stopped"}
    except Exception as e:
        logger.error(f"Failed to stop engine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/engine/emergency-stop", tags=["Engine"])
async def emergency_stop():
    try:
        # Add emergency stop logic here
        logger.info("Emergency stop requested")
        return {"status": "success", "message": "Emergency stop executed"}
    except Exception as e:
        logger.error(f"Failed to execute emergency stop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
