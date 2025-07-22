import subprocess
import os
import signal
import psutil
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from waves_quant_agi.core.database import get_db
from waves_quant_agi.core.models.user import User
from waves_quant_agi.api.auth import get_current_admin
from typing import List, Dict, Any
from waves_quant_agi.core.models.strategy import Strategy
from waves_quant_agi.core.schemas.strategy import StrategyRecordResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import BackgroundTasks
from datetime import datetime
from waves_quant_agi.core.models.portfolio import InvestorPortfolio
from waves_quant_agi.core.models.transaction import Trade, TradeStatus
import uuid
from sqlalchemy import func
from datetime import timedelta, date
import traceback
from fastapi import status as http_status

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
# --- OWNER DASHBOARD REAL DATA ENDPOINTS ---
@router.get("/dashboard/stats")
async def owner_dashboard_stats(db: AsyncSession = Depends(get_db)):
    total_users = await db.scalar(select(func.count(User.id)))
    total_trades = await db.scalar(select(func.count(Trade.id)))
    total_revenue = await db.scalar(select(func.sum(Trade.profit)).where(Trade.profit > 0)) or 0
    active_strategies = await db.scalar(select(func.count(Strategy.id)).where(Strategy.status == "active"))
    aum = await db.scalar(select(func.sum(InvestorPortfolio.total_balance))) or 0
    daily_pnl = await db.scalar(select(func.sum(Trade.profit)).where(func.date(Trade.open_time) == func.current_date())) or 0
    win_rate = await db.scalar(select(func.avg(func.case([(Trade.profit > 0, 1)], else_=0)))) or 0
    active_users = await db.scalar(select(func.count(User.id)).where(User.is_active == True))
    return {
        "totalUsers": total_users or 0,
        "totalTrades": total_trades or 0,
        "totalRevenue": total_revenue or 0,
        "activeStrategies": active_strategies or 0,
        "aum": aum or 0,
        "dailyPnL": daily_pnl or 0,
        "winRate": round(win_rate * 100, 2) if win_rate else 0,
        "activeUsers": active_users or 0
    }

@router.get("/dashboard/aum")
async def owner_dashboard_aum(db: AsyncSession = Depends(get_db)):
    # Return 30-day AUM history
    today = date.today()
    data = []
    for i in range(30, -1, -1):
        d = today - timedelta(days=i)
        aum = await db.scalar(select(func.sum(InvestorPortfolio.total_balance)).where(func.date(InvestorPortfolio.updated_at) == d)) or 0
        trades = await db.scalar(select(func.count(Trade.id)).where(func.date(Trade.open_time) == d)) or 0
        data.append({"date": d.isoformat(), "aum": aum, "trades": trades})
    return data

# --- FIX EXISTING ENDPOINTS TO USE ONLY REAL DATA ---
@router.get("/investors/overview")
async def investor_overview(current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    aum = await db.scalar(select(func.sum(InvestorPortfolio.total_balance))) or 0
    inflows = await db.scalar(select(func.sum(Trade.profit)).where(Trade.profit > 0)) or 0
    top_investors = (await db.execute(select(User.id, User.email, InvestorPortfolio.total_balance)
        .join(InvestorPortfolio, InvestorPortfolio.user_id == User.id)
        .order_by(InvestorPortfolio.total_balance.desc()).limit(3))).all()
    performance = await db.scalar(select(func.avg(Trade.profit))) or 0
    return {
        "aum": aum,
        "inflows": inflows,
        "top_investors": [{"id": i[0], "name": i[1], "aum": i[2]} for i in top_investors],
        "performance": performance
    }

@router.get("/wallet/overview")
async def wallet_overview(current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    total_balance = await db.scalar(select(func.sum(InvestorPortfolio.total_balance))) or 0
    paystack_funds = 0 # TODO: Integrate with payment provider
    pending_withdrawals = await db.scalar(select(func.sum(Trade.amount)).where(Trade.status == "pending")) or 0
    return {
        "total_balance": total_balance,
        "paystack_funds": paystack_funds,
        "pending_withdrawals": pending_withdrawals
    }

# --- RISK MANAGEMENT ENDPOINTS ---
@router.get("/risk/settings")
async def get_risk_settings(current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    settings = await db.get(SystemSettings, "risk")
    return settings.data if settings else {}

@router.post("/risk/settings")
async def save_risk_settings(data: dict, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    settings = await db.get(SystemSettings, "risk")
    if settings:
        settings.data = data
    else:
        settings = SystemSettings(id="risk", data=data)
        db.add(settings)
    await db.commit()
    return {"status": "ok"}

# --- PERFORMANCE ANALYTICS ENDPOINT ---
@router.get("/performance/analytics")
async def get_performance_analytics(current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    # Aggregate trades for daily, weekly, monthly performance
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    daily = []
    weekly = []
    monthly = []
    for i in range(30, -1, -1):
        d = today - timedelta(days=i)
        profit = await db.scalar(select(func.sum(Trade.profit)).where(func.date(Trade.open_time) == d)) or 0
        trades = await db.scalar(select(func.count(Trade.id)).where(func.date(Trade.open_time) == d)) or 0
        win_rate = await db.scalar(select(func.avg(func.case([(Trade.profit > 0, 1)], else_=0))).where(func.date(Trade.open_time) == d)) or 0
        daily.append({"date": d.isoformat(), "profit": profit, "trades": trades, "winRate": round(win_rate * 100, 2) if win_rate else 0})
    # Weekly and monthly aggregation (simplified)
    # ... implement as needed ...
    return {"overallEngine": {"daily": daily, "weekly": weekly, "monthly": monthly}}

# --- OWNER SETTINGS ENDPOINTS ---
@router.get("/settings")
async def get_owner_settings(current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    settings = await db.get(SystemSettings, "owner")
    return settings.data if settings else {}

@router.post("/settings")
async def save_owner_settings(data: dict, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    settings = await db.get(SystemSettings, "owner")
    if settings:
        settings.data = data
    else:
        settings = SystemSettings(id="owner", data=data)
        db.add(settings)
    await db.commit()
    return {"status": "ok"}

# MANUAL SIGNALS
@router.post("/manual-signal")
async def manual_signal(signal: Dict[str, Any], current_admin: User = Depends(get_current_admin)):
    # TODO: Implement manual signal logic
    return {"status": "manual signal submitted", "signal": signal}

# WALLET CONTROL
# --- FIX EXISTING ENDPOINTS TO USE ONLY REAL DATA ---
@router.get("/logs")
async def get_logs(current_admin: User = Depends(get_current_admin)):
    # TODO: Integrate with real logs system
    return {"logs": []}

# AUTO-ML STATUS
# --- FIX EXISTING ENDPOINTS TO USE ONLY REAL DATA ---
@router.get("/automl/status")
async def automl_status(current_admin: User = Depends(get_current_admin)):
    # TODO: Integrate with real Auto-ML status
    return {"evolving_models": [], "validated_models": []}

# MT5 HEALTH CHECK ENDPOINT (moved to /mt5-status for clarity)
@router.get("/mt5-status", tags=["owner"])
async def mt5_status():
    """Check MT5 connection and account status."""
    import os
    mt5_login = os.getenv("MT5_LOGIN")
    mt5_password = os.getenv("MT5_PASSWORD")
    mt5_server = os.getenv("MT5_SERVER", "Exness-MT5")
    if not (mt5_login and mt5_password and mt5_server):
        return {
            "connected": False,
            "error": "MT5 credentials not set in environment variables."
        }
    try:
        from waves_quant_agi.engine.brokers.mt5_plugin import MT5Broker
        mt5 = MT5Broker(int(mt5_login), mt5_password, mt5_server)
        mt5.connect()
        account_info = mt5.get_balance()
        return {
            "connected": True,
            "account": account_info,
            "message": f"Connected to {mt5_server} as {mt5_login}"
        }
    except Exception as e:
        import traceback
        return {
            "connected": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }

@router.get("/mt5/open-trades", tags=["owner"])
async def mt5_open_trades():
    """Fetch all open trades/positions from MT5 (manual + automatic)."""
    import os
    from waves_quant_agi.engine.brokers.mt5_plugin import MT5Broker
    mt5_login = os.getenv("MT5_LOGIN")
    mt5_password = os.getenv("MT5_PASSWORD")
    mt5_server = os.getenv("MT5_SERVER", "Exness-MT5")
    if not (mt5_login and mt5_password and mt5_server):
        return {"connected": False, "error": "MT5 credentials not set in environment variables."}
    try:
        mt5 = MT5Broker(int(mt5_login), mt5_password, mt5_server)
        mt5.connect()
        positions = mt5.get_positions()
        return {"connected": True, "positions": positions}
    except Exception as e:
        import traceback
        return {"connected": False, "error": str(e), "trace": traceback.format_exc()}

@router.post("/mt5/close-all-trades", tags=["owner"])
async def mt5_close_all_trades():
    """Emergency stop: Close all open trades in MT5 (manual + automatic)."""
    import os
    from waves_quant_agi.engine.brokers.mt5_plugin import MT5Broker
    mt5_login = os.getenv("MT5_LOGIN")
    mt5_password = os.getenv("MT5_PASSWORD")
    mt5_server = os.getenv("MT5_SERVER", "Exness-MT5")
    if not (mt5_login and mt5_password and mt5_server):
        return {"connected": False, "error": "MT5 credentials not set in environment variables."}
    try:
        mt5 = MT5Broker(int(mt5_login), mt5_password, mt5_server)
        mt5.connect()
        positions = mt5.get_positions()
        results = []
        for pos in positions:
            try:
                res = mt5.close_position(pos['ticket'])
                results.append({"ticket": pos['ticket'], "symbol": pos['symbol'], "result": res})
            except Exception as e:
                results.append({"ticket": pos['ticket'], "symbol": pos['symbol'], "error": str(e)})
        return {"connected": True, "closed": results}
    except Exception as e:
        import traceback
        return {"connected": False, "error": str(e), "trace": traceback.format_exc()}

@router.post("/mt5/sync-trades", tags=["owner"])
async def mt5_sync_trades(db: AsyncSession = Depends(get_db)):
    """
    Sync all trades (open + closed, manual + engine) from MT5 to the backend DB.
    Inserts any missing trades and updates status for closed ones.
    Returns the unified list of all trades.
    """
    import os
    from waves_quant_agi.engine.brokers.mt5_plugin import MT5Broker
    mt5_login = os.getenv("MT5_LOGIN")
    mt5_password = os.getenv("MT5_PASSWORD")
    mt5_server = os.getenv("MT5_SERVER", "Exness-MT5")
    if not (mt5_login and mt5_password and mt5_server):
        raise HTTPException(status_code=400, detail="MT5 credentials not set in environment variables.")
    try:
        mt5 = MT5Broker(int(mt5_login), mt5_password, mt5_server)
        mt5.connect()
        open_positions = mt5.get_positions()  # open trades
        closed_trades = mt5.get_closed_trades()  # closed trades
        # Insert/update open positions
        for pos in open_positions:
            trade_id = str(pos['ticket'])
            result = await db.execute(select(Trade).where(Trade.id == trade_id))
            existing = result.scalar_one_or_none()
            if not existing:
                db.add(Trade(
                    id=trade_id,
                    user_id="manual_or_engine",  # TODO: map to user if possible
                    symbol=pos['symbol'],
                    side="buy" if pos['type'] == 0 else "sell",
                    volume=pos['volume'],
                    price=pos['price_open'],
                    pnl=pos['profit'],
                    strategy=None,
                    timestamp=datetime.fromtimestamp(pos['time']),
                    status=TradeStatus.OPEN
                ))
        # Insert/update closed trades
        for deal in closed_trades:
            trade_id = str(deal['ticket']) if 'ticket' in deal else str(deal['position_id'])
            result = await db.execute(select(Trade).where(Trade.id == trade_id))
            existing = result.scalar_one_or_none()
            if not existing:
                db.add(Trade(
                    id=trade_id,
                    user_id="manual_or_engine",  # TODO: map to user if possible
                    symbol=deal['symbol'],
                    side="buy" if deal['type'] == 0 else "sell",
                    volume=deal['volume'],
                    price=deal['price'],
                    pnl=deal['profit'],
                    strategy=None,
                    timestamp=datetime.fromtimestamp(deal['time']),
                    status=TradeStatus.CLOSED
                ))
            else:
                # If trade exists and is still open, mark as closed
                if existing.status != TradeStatus.CLOSED:
                    existing.status = TradeStatus.CLOSED
                    existing.pnl = deal['profit']
                    existing.price = deal['price']
                    existing.timestamp = datetime.fromtimestamp(deal['time'])
        await db.commit()
        # Return all trades
        all_trades = (await db.execute(select(Trade))).scalars().all()
        return {"trades": [
            {
                "id": t.id,
                "symbol": t.symbol,
                "side": t.side,
                "volume": t.volume,
                "price": t.price,
                "pnl": t.pnl,
                "status": t.status.value if hasattr(t.status, 'value') else t.status,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None
            } for t in all_trades
        ]}
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"MT5 sync error: {e}\n{traceback.format_exc()}") 