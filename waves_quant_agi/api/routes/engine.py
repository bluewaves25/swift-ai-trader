# api/routes/engine.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from waves_quant_agi.core.database import get_db
from waves_quant_agi.api.auth import get_current_user
from waves_quant_agi.core.models.user import User
from typing import List
from datetime import datetime
from pydantic import BaseModel
import httpx

router = APIRouter()


# === Schema ===
class MarketData(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


# === Config ===
ENGINE_URL = "http://localhost:9001"
ENGINE_STATUS = {
    "is_running": False,
    "start_time": None,
    "total_signals": 0,
    "total_trades": 0,
    "active_pairs": []
}


# === Routes ===
@router.post("/register-strategy")
async def register_strategy(
    strategy_name: str,
    current_user: User = Depends(get_current_user)
):
    return {"message": f"Strategy {strategy_name} registered."}


@router.post("/feed")
async def feed_market_data(
    data: List[MarketData],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ENGINE_URL}/predict/",
                json=[d.dict() for d in data]
            )
            response.raise_for_status()
            return {"executed_trades": response.json()}
    except httpx.HTTPStatusError as http_err:
        raise HTTPException(status_code=http_err.response.status_code, detail=http_err.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regime")
async def get_market_regime():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ENGINE_URL}/regime/")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as http_err:
        raise HTTPException(status_code=http_err.response.status_code, detail=http_err.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_engine_status():
    """Get current engine status"""
    return ENGINE_STATUS


@router.post("/start")
async def start_engine():
    """
    Start the trading engine and fetch active pairs from MT5.
    """
    global ENGINE_STATUS
    import os
    from waves_quant_agi.engine_agents.adapters.brokers.mt5_plugin import MT5Broker

    active_pairs = []
    try:
        mt5_login = int(os.getenv("MT5_LOGIN"))
        mt5_password = os.getenv("MT5_PASSWORD")
        mt5_server = os.getenv("MT5_SERVER")
        
        if mt5_login and mt5_password and mt5_server:
            mt5_broker = MT5Broker(login=mt5_login, password=mt5_password, server=mt5_server)
            mt5_broker.connect()
            all_symbols = mt5_broker.get_all_symbols()
            # Filter for common forex pairs and gold, especially with 'm' suffix for Exness
            desired_pairs = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
            active_pairs = [s for s in all_symbols if any(p in s for p in desired_pairs) and s.endswith('m')]
            if not active_pairs: # Fallback if no 'm' suffix pairs found
                active_pairs = [s for s in all_symbols if any(p in s for p in desired_pairs)]
    except Exception as e:
        print(f"Could not fetch MT5 symbols: {e}")
        # Fallback to default if MT5 connection fails
        active_pairs = ["BTC/USD", "ETH/USD", "EUR/USD"]

    ENGINE_STATUS = {
        "is_running": True,
        "start_time": datetime.now().isoformat(),
        "total_signals": 0,
        "total_trades": 0,
        "active_pairs": active_pairs or ["No compatible pairs found"]
    }
    
    return {"message": "Engine started successfully", "status": ENGINE_STATUS}


@router.post("/stop")
async def stop_engine():
    """Stop the trading engine"""
    global ENGINE_STATUS
    
    ENGINE_STATUS = {
        "is_running": False,
        "start_time": None,
        "total_signals": ENGINE_STATUS.get("total_signals", 0),
        "total_trades": ENGINE_STATUS.get("total_trades", 0),
        "active_pairs": []
    }
    
    return {"message": "Engine stopped successfully", "status": ENGINE_STATUS}


@router.post("/emergency-stop")
async def emergency_stop_engine():
    """Emergency stop the trading engine"""
    global ENGINE_STATUS
    
    ENGINE_STATUS = {
        "is_running": False,
        "start_time": None,
        "total_signals": ENGINE_STATUS.get("total_signals", 0),
        "total_trades": ENGINE_STATUS.get("total_trades", 0),
        "active_pairs": []
    }
    
    return {"message": "Emergency stop executed", "status": ENGINE_STATUS}
