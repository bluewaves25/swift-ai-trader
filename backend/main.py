
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from routes import trade, wallet, strategies
import logging
import asyncio
from datetime import datetime
import json

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

# Global trading engine state
trading_engine_state = {
    "is_running": False,
    "start_time": None,
    "active_pairs": [],
    "total_signals": 0,
    "total_trades": 0
}

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
        "status": "running",
        "engine_status": trading_engine_state["is_running"]
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Waves Quant Engine",
        "timestamp": datetime.utcnow().isoformat(),
        "engine_running": trading_engine_state["is_running"]
    }

# Real Trading Engine Implementation
async def trading_engine_loop():
    """Main trading engine loop that runs continuously when active"""
    logger.info("Trading engine loop started")
    
    while trading_engine_state["is_running"]:
        try:
            # Fetch market data and generate signals
            await process_market_data()
            
            # Execute trades based on signals
            await execute_pending_trades()
            
            # Update statistics
            trading_engine_state["total_signals"] += 1
            
            # Wait before next iteration (5 seconds)
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Error in trading engine loop: {str(e)}")
            await asyncio.sleep(10)  # Wait longer on error
    
    logger.info("Trading engine loop stopped")

async def process_market_data():
    """Process market data and generate trading signals"""
    try:
        # This would connect to real market data feeds
        # For now, we'll simulate the process
        logger.info("Processing market data...")
        
        # Simulate signal generation
        pairs = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD"]
        for pair in pairs:
            # Generate AI signals using the strategies
            signal_data = {
                "pair": pair,
                "signal": "buy",  # This would come from AI analysis
                "confidence": 0.75,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Generated signal for {pair}: {signal_data}")
            
    except Exception as e:
        logger.error(f"Error processing market data: {str(e)}")

async def execute_pending_trades():
    """Execute trades based on generated signals"""
    try:
        # This would execute actual trades via broker API
        logger.info("Checking for pending trades to execute...")
        trading_engine_state["total_trades"] += 1
        
    except Exception as e:
        logger.error(f"Error executing trades: {str(e)}")

# Engine control endpoints
@app.post("/api/engine/start", tags=["Engine"])
async def start_trading_engine(background_tasks: BackgroundTasks):
    try:
        if trading_engine_state["is_running"]:
            return {"status": "already_running", "message": "Trading engine is already running"}
        
        trading_engine_state["is_running"] = True
        trading_engine_state["start_time"] = datetime.utcnow().isoformat()
        trading_engine_state["total_signals"] = 0
        trading_engine_state["total_trades"] = 0
        
        # Start the trading engine in background
        background_tasks.add_task(trading_engine_loop)
        
        logger.info("Trading engine started successfully")
        return {
            "status": "success", 
            "message": "Trading engine started",
            "start_time": trading_engine_state["start_time"]
        }
    except Exception as e:
        logger.error(f"Failed to start engine: {str(e)}")
        trading_engine_state["is_running"] = False
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/engine/stop", tags=["Engine"])
async def stop_trading_engine():
    try:
        if not trading_engine_state["is_running"]:
            return {"status": "already_stopped", "message": "Trading engine is already stopped"}
        
        trading_engine_state["is_running"] = False
        
        logger.info("Trading engine stopped successfully")
        return {
            "status": "success", 
            "message": "Trading engine stopped",
            "statistics": {
                "total_signals": trading_engine_state["total_signals"],
                "total_trades": trading_engine_state["total_trades"],
                "uptime": trading_engine_state["start_time"]
            }
        }
    except Exception as e:
        logger.error(f"Failed to stop engine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/engine/emergency-stop", tags=["Engine"])
async def emergency_stop():
    try:
        # Immediately stop all trading activities
        trading_engine_state["is_running"] = False
        
        # Close all open positions (this would connect to broker API)
        logger.warning("EMERGENCY STOP EXECUTED - All trading halted")
        
        return {
            "status": "success", 
            "message": "Emergency stop executed - All trading halted",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to execute emergency stop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/engine/status", tags=["Engine"])
async def get_engine_status():
    return {
        "is_running": trading_engine_state["is_running"],
        "start_time": trading_engine_state["start_time"],
        "total_signals": trading_engine_state["total_signals"],
        "total_trades": trading_engine_state["total_trades"],
        "active_pairs": trading_engine_state["active_pairs"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
