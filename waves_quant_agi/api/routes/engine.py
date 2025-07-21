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
    """Start the trading engine"""
    global ENGINE_STATUS
    from datetime import datetime
    
    ENGINE_STATUS = {
        "is_running": True,
        "start_time": datetime.now().isoformat(),
        "total_signals": 0,
        "total_trades": 0,
        "active_pairs": ["BTC/USD", "ETH/USD", "EUR/USD"]
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
