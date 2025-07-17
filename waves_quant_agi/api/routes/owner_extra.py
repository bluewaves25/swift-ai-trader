from fastapi import APIRouter, Depends
from api.auth import get_current_admin

router = APIRouter()

@router.get("/api/owner/investors/overview")
async def investors_overview(current_admin = Depends(get_current_admin)):
    return {"investors": 42, "total_balance": 100000, "active": 40}

@router.get("/api/owner/logs")
async def get_logs(current_admin = Depends(get_current_admin)):
    return {"logs": [
        {"timestamp": "2024-07-08T12:00:00Z", "event": "Engine started"},
        {"timestamp": "2024-07-08T12:05:00Z", "event": "Strategy retrained"}
    ]}

@router.get("/api/owner/health/system")
async def system_health(current_admin = Depends(get_current_admin)):
    return {
        "cpu": "10%",
        "ram": "2.0GB/8.0GB",
        "network": {"sent": 123456, "recv": 654321},
        "errors": []
    } 