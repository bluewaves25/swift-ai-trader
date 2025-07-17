from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class MarketData(BaseModel):
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float

@router.post("/api/engine/feed")
async def engine_feed(data: List[MarketData]):
    # Stub: In production, push to Redis queue
    return {"status": "success", "received": len(data)} 