import subprocess
import os
import signal
import psutil
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.models.user import User
from api.auth import get_current_admin
from typing import List, Dict, Any
from core.models.strategy import Strategy
from core.schemas.strategy import StrategyRecordResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import BackgroundTasks
from datetime import datetime

# TODO: Use API/IPC/Redis to communicate with engine for strategy management

router = APIRouter()

ENGINE_PROCESS_FILE = "waves_quant_agi/engine/run_engine_api.py"
ENGINE_PID_FILE = "/tmp/waves_quant_engine.pid"

# ENGINE CONTROL
@router.post("/engine/start")
async def start_engine(current_admin: User = Depends(get_current_admin)):
    if os.path.exists(ENGINE_PID_FILE):
        return {"status": "already running"}
    proc = subprocess.Popen(["python", ENGINE_PROCESS_FILE])
    with open(ENGINE_PID_FILE, "w") as f:
        f.write(str(proc.pid))
    return {"status": "started", "pid": proc.pid}

@router.post("/engine/stop")
async def stop_engine(current_admin: User = Depends(get_current_admin)):
    if not os.path.exists(ENGINE_PID_FILE):
        return {"status": "not running"}
    with open(ENGINE_PID_FILE) as f:
        pid = int(f.read())
    try:
        os.kill(pid, signal.SIGTERM)
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    os.remove(ENGINE_PID_FILE)
    return {"status": "stopped"}

@router.post("/engine/restart")
async def restart_engine(current_admin: User = Depends(get_current_admin)):
    await stop_engine(current_admin)
    return await start_engine(current_admin)

@router.post("/engine/emergency-kill")
async def emergency_kill(current_admin: User = Depends(get_current_admin)):
    if not os.path.exists(ENGINE_PID_FILE):
        return {"status": "not running"}
    with open(ENGINE_PID_FILE) as f:
        pid = int(f.read())
    try:
        os.kill(pid, signal.SIGKILL)
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    os.remove(ENGINE_PID_FILE)
    return {"status": "emergency kill triggered"}

# HEALTH MONITOR
@router.get("/health/system")
async def system_health(current_admin: User = Depends(get_current_admin)):
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    net = psutil.net_io_counters()
    # For demo, errors are empty; in production, pull from logs
    return {
        "cpu": f"{cpu}%",
        "ram": f"{ram.used/1e9:.2f}GB/{ram.total/1e9:.2f}GB",
        "network": {
            "sent": net.bytes_sent,
            "recv": net.bytes_recv
        },
        "errors": []
    }

# STRATEGY CONTROL
@router.get("/strategies", response_model=List[StrategyRecordResponse])
async def list_strategies(current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Strategy))
    records = result.scalars().all()
    return records

@router.post("/strategies/{strategy_id}/disable")
async def disable_strategy(strategy_id: str, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    record = await db.get(Strategy, strategy_id)
    if not record:
        raise HTTPException(status_code=404, detail="Strategy not found")
    record.status = "disabled"
    await db.commit()
    await db.refresh(record)
    return {"strategy_id": strategy_id, "status": "disabled"}

async def retrain_strategy_job(strategy_id: str, db: AsyncSession):
    record = await db.get(Strategy, strategy_id)
    if record:
        record.status = "retraining"
        await db.commit()
        await db.refresh(record)
        # Simulate retrain
        import asyncio
        await asyncio.sleep(5)
        record.status = "active"
        record.last_retrained = datetime.utcnow()
        await db.commit()
        await db.refresh(record)

@router.post("/strategies/{strategy_id}/retrain")
async def retrain_strategy(strategy_id: str, background_tasks: BackgroundTasks, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    record = await db.get(Strategy, strategy_id)
    if not record:
        raise HTTPException(status_code=404, detail="Strategy not found")
    background_tasks.add_task(retrain_strategy_job, strategy_id, db)
    record.status = "retraining"
    await db.commit()
    await db.refresh(record)
    return {"strategy_id": strategy_id, "status": "retraining"}

@router.delete("/strategies/{strategy_id}/delete")
async def delete_strategy(strategy_id: str, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    record = await db.get(Strategy, strategy_id)
    if not record:
        raise HTTPException(status_code=404, detail="Strategy not found")
    await db.delete(record)
    await db.commit()
    return {"strategy_id": strategy_id, "status": "deleted"}

# INVESTOR OVERVIEW
@router.get("/investors/overview")
async def investor_overview(current_admin: User = Depends(get_current_admin)):
    # TODO: Replace with real investor overview data
    return {
        "aum": 1200000.0,
        "inflows": 50000.0,
        "top_investors": [
            {"id": "user1", "name": "Alice", "aum": 300000.0},
            {"id": "user2", "name": "Bob", "aum": 250000.0}
        ],
        "performance": 0.18
    }

# MANUAL SIGNALS
@router.post("/manual-signal")
async def manual_signal(signal: Dict[str, Any], current_admin: User = Depends(get_current_admin)):
    # TODO: Implement manual signal logic
    return {"status": "manual signal submitted", "signal": signal}

# WALLET CONTROL
@router.get("/wallet/overview")
async def wallet_overview(current_admin: User = Depends(get_current_admin)):
    # TODO: Replace with real wallet data
    return {
        "total_balance": 200000.0,
        "paystack_funds": 150000.0,
        "pending_withdrawals": 5000.0
    }

# AUTO-ML STATUS
@router.get("/automl/status")
async def automl_status(current_admin: User = Depends(get_current_admin)):
    # TODO: Replace with real Auto-ML status
    return {
        "evolving_models": ["strat3", "strat4"],
        "validated_models": ["strat1", "strat2"]
    }

# LOGS VIEWER
@router.get("/logs")
async def get_logs(current_admin: User = Depends(get_current_admin)):
    # TODO: Replace with real logs
    return {
        "logs": [
            {"timestamp": "2024-07-08T12:00:00Z", "event": "Engine started"},
            {"timestamp": "2024-07-08T12:05:00Z", "event": "Strategy retrained"}
        ]
    } 