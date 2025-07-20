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
