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
import logging
from waves_quant_agi.api.deps import get_mt5_broker
from waves_quant_agi.engine.brokers.mt5_plugin import MT5Broker

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

async def sync_mt5_trades_in_background(db: AsyncSession, broker: MT5Broker):
    """
    The actual trade sync logic that runs in the background.
    """
    logging.info("[MT5 SYNC BG] Background sync task started.")
    try:
        open_positions = broker.get_positions()
        closed_trades = broker.get_closed_trades()
        logging.info(f"[MT5 SYNC BG] Fetched {len(open_positions)} open positions and {len(closed_trades)} closed trades.")

        # --- Your existing sync logic here ---
        # (Adapted to use the broker dependency and corrected schema)
        for pos in open_positions:
            trade_id = str(pos.get('ticket'))
            if not trade_id:
                continue

            existing_trade = await db.get(Trade, trade_id)
            if not existing_trade:
                new_trade = Trade(
                    id=trade_id,
                    user_id="mt5_user", # Placeholder
                    symbol=pos.get('symbol'),
                    side="buy" if pos.get('type') == 0 else "sell",
                    volume=pos.get('volume', 0.0),
                    price=pos.get('price_open', 0.0),
                    pnl=pos.get('profit', 0.0),
                    strategy="manual" if pos.get('magic') == 0 else "engine",
                    created_at=datetime.fromtimestamp(pos.get('time', 0)),
                    status=TradeStatus.OPEN
                )
                db.add(new_trade)
                logging.info(f"[MT5 SYNC BG] Adding new open trade to DB: {trade_id}")
            elif existing_trade.status == TradeStatus.OPEN:
                # Update the status of an existing open trade to closed
                existing_trade.status = TradeStatus.CLOSED
                existing_trade.pnl = pos.get('profit', existing_trade.pnl)
                logging.info(f"[MT5 SYNC BG] Updating trade to closed: {trade_id}")

        for deal in closed_trades:
            trade_id = str(deal.get('order'))
            if not trade_id:
                continue

            existing_trade = await db.get(Trade, trade_id)
            if not existing_trade:
                 # Only add if it's an outgoing trade deal
                if deal.get('entry') == 1: # 0=in, 1=out, 2=in/out
                    new_trade = Trade(
                        id=trade_id,
                        user_id="mt5_user", # Placeholder
                        symbol=deal.get('symbol'),
                        side="buy" if deal.get('type') == 0 else "sell",
                        volume=deal.get('volume', 0.0),
                        price=deal.get('price', 0.0),
                        pnl=deal.get('profit', 0.0),
                        strategy="manual" if deal.get('magic') == 0 else "engine",
                        created_at=datetime.fromtimestamp(deal.get('time', 0)),
                        status=TradeStatus.CLOSED
                    )
                    db.add(new_trade)
                    logging.info(f"[MT5 SYNC BG] Adding new closed trade to DB: {trade_id}")
            elif existing_trade.status == TradeStatus.OPEN:
                # Update the status of an existing open trade to closed
                existing_trade.status = TradeStatus.CLOSED
                existing_trade.pnl = deal.get('profit', existing_trade.pnl)
                logging.info(f"[MT5 SYNC BG] Updating trade to closed: {trade_id}")
        
        await db.commit()
        logging.info("[MT5 SYNC BG] Background sync task finished successfully.")
    except Exception as e:
        import traceback
        logging.error(f"[MT5 SYNC BG] Error during background sync: {e}\n{traceback.format_exc()}")
        await db.rollback()

@router.post("/mt5/trigger-sync", tags=["owner"])
async def trigger_mt5_sync(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), broker: MT5Broker = Depends(get_mt5_broker)):
    """
    Triggers a background task to sync MT5 trades. Returns immediately.
    """
    background_tasks.add_task(sync_mt5_trades_in_background, db, broker)
    return {"message": "MT5 trade synchronization started in the background."}

@router.get("/all-trades", tags=["owner"])
async def get_all_trades_from_db(db: AsyncSession = Depends(get_db)):
    """
    Returns all trades currently stored in the backend database.
    This should be called after triggering a sync.
    """
    all_trades_result = await db.execute(select(Trade).order_by(Trade.created_at.desc()))
    all_trades = all_trades_result.scalars().all()
    
    return {"trades": [
        {
            "id": t.id,
            "symbol": t.symbol,
            "side": t.side,
            "volume": t.volume,
            "price": t.price,
            "pnl": t.pnl,
            "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in all_trades
    ]}

# Refactor other MT5 routes to use the dependency
@router.get("/mt5-status", tags=["owner"])
async def mt5_status(broker: MT5Broker = Depends(get_mt5_broker)):
    account_info = broker.get_balance()
    return {"connected": True, "account": account_info}

@router.get("/mt5/open-trades", tags=["owner"])
async def mt5_open_trades(broker: MT5Broker = Depends(get_mt5_broker)):
    positions = broker.get_positions()
    return {"connected": True, "positions": positions}

@router.post("/mt5/close-all-trades", tags=["owner"])
async def mt5_close_all_trades(broker: MT5Broker = Depends(get_mt5_broker)):
    positions = broker.get_positions()
    results = []
    for pos in positions:
        try:
            res = broker.close_position(pos['ticket'])
            results.append({"ticket": pos['ticket'], "result": res})
        except Exception as e:
            results.append({"ticket": pos['ticket'], "error": str(e)})
    return {"connected": True, "closed": results} 