from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime
import logging
from waves_quant_agi.api.routes import (
    admin, auth_extra, engine, engine_feed, engine_status, investor,
    owner, owner_extra, portfolio, support
)
import redis
import uuid
import json
import time
from waves_quant_agi.engine.core.agi_engine import AGIEngine
from waves_quant_agi.engine.core.strategy_manager import StrategyManager
from waves_quant_agi.core.database import get_db
from fastapi import Depends
from waves_quant_agi.core.models.strategy import Strategy as StrategyModel
from sqlalchemy.future import select
import requests
from fastapi import Request
# SPA handler import - commented out for now to avoid import issues
# from waves_quant_agi.backend_main.spa_handler import setup_spa_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Waves Quant AGI - Main Backend",
    description="Main backend service for Waves Quant AGI trading platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router, prefix="/api/v1/admin")
app.include_router(auth_extra.router, prefix="/api/v1/auth")
app.include_router(engine.router, prefix="/api/v1/engine")
app.include_router(engine_feed.router, prefix="/api/v1/engine-feed")
app.include_router(engine_status.router, prefix="/api/v1/engine-status")
app.include_router(investor.router, prefix="/api/v1/investor")
app.include_router(owner.router, prefix="/api/v1/owner")
app.include_router(owner_extra.router, prefix="/api/v1/owner-extra")
app.include_router(portfolio.router, prefix="/api/v1/portfolio")
app.include_router(support.router, prefix="/api/v1/support")

# Setup SPA handler for React app (if frontend is built)
# setup_spa_handler(app, static_dir="../dist")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(REDIS_URL)

agi_engine = AGIEngine()

strategy_manager = StrategyManager()

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_BASE_URL = "https://api.paystack.co"

# Example plans (replace with DB or config as needed)
PLANS = [
    {"id": "basic", "name": "Basic", "price": 2900, "interval": "monthly"},
    {"id": "pro", "name": "Pro", "price": 9900, "interval": "monthly"},
    {"id": "enterprise", "name": "Enterprise", "price": 29900, "interval": "monthly"},
]

@app.get("/api/v1/billing/plans")
async def list_plans():
    """List available subscription plans."""
    return {"plans": PLANS}

@app.post("/api/v1/billing/initialize")
async def initialize_payment(request: Request):
    """Initialize a Paystack payment and return the payment URL."""
    data = await request.json()
    email = data.get("email")
    amount = data.get("amount")  # in kobo
    plan_id = data.get("plan_id")
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    payload = {
        "email": email,
        "amount": amount,
        "metadata": {"plan_id": plan_id}
    }
    resp = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=payload, headers=headers)
    return resp.json()

@app.get("/api/v1/billing/verify")
async def verify_payment(reference: str):
    """Verify a Paystack payment by reference."""
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    resp = requests.get(f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers)
    return resp.json()

@app.get("/api/v1/billing/status")
async def billing_status(user_id: str):
    """Get current user's subscription status (stub)."""
    # TODO: Implement DB lookup for real status
    return {"status": "active", "plan": "pro", "trial": False}

@app.get("/api/v1/billing/history")
async def billing_history(user_id: str):
    """Get user's billing/payment history (stub)."""
    # TODO: Implement DB lookup for real history
    return {"history": []}

@app.post("/api/v1/billing/cancel")
async def cancel_subscription(user_id: str):
    """Cancel user's subscription (stub)."""
    # TODO: Implement DB update/cancel logic
    return {"status": "cancelled"}

@app.post("/api/v1/billing/webhook")
async def paystack_webhook(request: Request):
    """Handle Paystack webhook events."""
    event = await request.json()
    # TODO: Process event and update user subscription status in DB
    return {"status": "received"}

@app.get("/api/v1/strategies")
async def list_strategies():
    """List all registered strategies."""
    return {"strategies": strategy_manager.list_strategies()}

@app.post("/api/v1/strategies/add")
async def add_strategy(strategy_name: str, db=Depends(get_db)):
    """Add/register a new strategy by name (auto-discovered)."""
    # Auto-discovery already loads all strategies; this can enable/activate a strategy
    # For demo, just return success if exists
    if strategy_name in strategy_manager.strategies:
        await strategy_manager.register_strategy(strategy_manager.strategies[strategy_name], db)
        return {"status": "added", "strategy": strategy_name}
    return {"status": "not found", "strategy": strategy_name}

@app.post("/api/v1/strategies/remove")
async def remove_strategy(strategy_name: str, db=Depends(get_db)):
    """Remove a strategy by name."""
    await strategy_manager.remove_strategy(strategy_name, db)
    return {"status": "removed", "strategy": strategy_name}

@app.post("/api/v1/strategies/update")
async def update_strategy(strategy_name: str, config: dict, db=Depends(get_db)):
    """Update a strategy's config."""
    await strategy_manager.update_strategy(strategy_name, config, db)
    return {"status": "updated", "strategy": strategy_name}

@app.get("/api/v1/strategies/validate/{strategy_name}")
async def validate_strategy(strategy_name: str, db=Depends(get_db)):
    """Run validation checks on a strategy."""
    # For demo, just return a placeholder
    return {"strategy": strategy_name, "validation": "passed (placeholder)"}

@app.get("/api/v1/engine/explainability")
async def explainability_log():
    """Return the engine's explainability log."""
    return agi_engine.get_status().get("explain_log", [])

@app.post("/api/v1/strategies/backtest")
async def backtest_strategy(strategy_name: str, data: list):
    """Run a backtest for a strategy on provided data."""
    strat = strategy_manager.get_strategy(strategy_name)
    if not strat:
        return {"status": "not found", "strategy": strategy_name}
    # For demo, just call generate_signal for each data point
    results = [strat.generate_signal(d) for d in data]
    return {"strategy": strategy_name, "backtest_results": results}

@app.post("/api/v1/ai/predict")
async def ai_predict(payload: dict):
    """
    Enqueue a prediction job to Redis for backend-ml to process.
    Waits for the result and returns it to the frontend.
    """
    job_id = str(uuid.uuid4())
    job_data = {"job_id": job_id, "payload": payload}
    redis_client.rpush("ml:jobs", json.dumps(job_data))
    # Wait for result (simple polling, production should use async or pubsub)
    for _ in range(60):  # Wait up to 30s
        result = redis_client.get(f"ml:results:{job_id}")
        if result:
            redis_client.delete(f"ml:results:{job_id}")
            return json.loads(result)
        time.sleep(0.5)
    raise HTTPException(status_code=504, detail="ML engine did not respond in time")

@app.post("/api/v1/trade/execute")
async def trade_execute(payload: dict):
    """
    Enqueue a trading job to Redis for the trading engine (run_engine_api.py) to process.
    Waits for the result and returns it to the frontend.
    """
    # Use a unique job id for result tracking (optional, for now use single result key)
    redis_client.rpush("market-data", json.dumps(payload))
    # Wait for result (simple polling, production should use async or pubsub)
    for _ in range(60):  # Wait up to 30s
        result = redis_client.get("market-result")
        if result:
            redis_client.delete("market-result")
            return json.loads(result)
        time.sleep(0.5)
    raise HTTPException(status_code=504, detail="Trading engine did not respond in time")

@app.get("/api/v1/fees/performance")
async def get_performance_fees(user_id: str):
    """Get user's performance fee breakdown (stub)."""
    # TODO: Calculate based on real P&L
    return {
        "user_id": user_id,
        "total_profit": 100000,
        "fee_percent": 0.15,
        "fee_due": 15000,
        "last_billed": "2024-07-01",
        "next_billing": "2024-08-01"
    }

@app.post("/api/v1/fees/charge")
async def charge_performance_fee(user_id: str):
    """Trigger performance fee billing (stub)."""
    # TODO: Implement real billing logic
    return {"status": "charged", "user_id": user_id}

@app.get("/api/v1/fees/history")
async def performance_fee_history(user_id: str):
    """Get user's performance fee payment history (stub)."""
    # TODO: Implement real history
    return {"history": [
        {"date": "2024-07-01", "amount": 15000, "status": "paid"},
        {"date": "2024-06-01", "amount": 12000, "status": "paid"}
    ]}

# --- AI Strategy Marketplace Endpoints ---

# In-memory stub for strategies (replace with DB in production)
MARKETPLACE_STRATEGIES = [
    {"id": "sma", "name": "Simple Moving Average", "creator": "admin", "price": 5000, "rating": 4.5, "purchased": 12},
    {"id": "meanrev", "name": "Mean Reversion", "creator": "quant_guru", "price": 8000, "rating": 4.8, "purchased": 7},
    {"id": "momentum", "name": "Momentum Trader", "creator": "ai_bot", "price": 10000, "rating": 4.2, "purchased": 5},
]
USER_PURCHASED = {"me": ["sma"]}

@app.get("/api/v1/marketplace/strategies")
async def list_marketplace_strategies():
    """List all available strategies in the marketplace."""
    return {"strategies": MARKETPLACE_STRATEGIES}

@app.post("/api/v1/marketplace/buy")
async def buy_strategy(user_id: str, strategy_id: str):
    """Buy a strategy from the marketplace (stub)."""
    USER_PURCHASED.setdefault(user_id, []).append(strategy_id)
    return {"status": "purchased", "strategy_id": strategy_id}

@app.post("/api/v1/marketplace/sell")
async def sell_strategy(user_id: str, name: str, price: int):
    """List a strategy for sale (stub)."""
    new_strategy = {"id": name.lower().replace(' ', '_'), "name": name, "creator": user_id, "price": price, "rating": 0, "purchased": 0}
    MARKETPLACE_STRATEGIES.append(new_strategy)
    return {"status": "listed", "strategy": new_strategy}

@app.get("/api/v1/marketplace/my")
async def my_strategies(user_id: str):
    """List user's purchased and created strategies (stub)."""
    purchased = [s for s in MARKETPLACE_STRATEGIES if s["id"] in USER_PURCHASED.get(user_id, [])]
    created = [s for s in MARKETPLACE_STRATEGIES if s["creator"] == user_id]
    return {"purchased": purchased, "created": created}

@app.post("/api/v1/marketplace/rate")
async def rate_strategy(user_id: str, strategy_id: str, rating: float):
    """Rate/review a strategy (stub)."""
    for s in MARKETPLACE_STRATEGIES:
        if s["id"] == strategy_id:
            s["rating"] = (s["rating"] * s["purchased"] + rating) / (s["purchased"] + 1)
            s["purchased"] += 1
            return {"status": "rated", "strategy_id": strategy_id, "new_rating": s["rating"]}
    return {"status": "not found", "strategy_id": strategy_id}

# --- Affiliate Dashboard Endpoints ---

# In-memory stub for affiliate data (replace with DB in production)
AFFILIATE_DATA = {
    "me": {
        "referral_code": "WAVES123",
        "referrals": 8,
        "earnings": 32000,
        "pending": 8000,
        "history": [
            {"date": "2024-07-01", "amount": 8000, "status": "paid"},
            {"date": "2024-06-01", "amount": 12000, "status": "paid"}
        ]
    }
}

@app.get("/api/v1/affiliate/referral")
async def get_referral(user_id: str):
    """Get or generate referral code for user (stub)."""
    data = AFFILIATE_DATA.setdefault(user_id, {"referral_code": f"WAVES{user_id[-3:]}"})
    return {"referral_code": data["referral_code"]}

@app.get("/api/v1/affiliate/stats")
async def affiliate_stats(user_id: str):
    """Get affiliate stats and earnings (stub)."""
    data = AFFILIATE_DATA.get(user_id, {})
    return {
        "referrals": data.get("referrals", 0),
        "earnings": data.get("earnings", 0),
        "pending": data.get("pending", 0),
        "history": data.get("history", [])
    }

@app.post("/api/v1/affiliate/payout")
async def affiliate_payout(user_id: str, amount: int):
    """Request affiliate payout (stub)."""
    data = AFFILIATE_DATA.setdefault(user_id, {})
    data["pending"] = max(0, data.get("pending", 0) - amount)
    data.setdefault("history", []).append({"date": datetime.now().strftime("%Y-%m-%d"), "amount": amount, "status": "paid"})
    return {"status": "payout_requested", "amount": amount}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Waves Quant AGI - Main Backend",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "backend-main",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "service": "backend-main",
        "python_version": "3.12",
        "timestamp": datetime.utcnow().isoformat()
    }

# This endpoint conflicts with the engine router, so we'll remove it
# @app.get("/api/v1/engine/status")
# async def engine_status():
#     """
#     Returns the current status, performance metrics, and explainability log of the AGI engine.
#     """
#     return agi_engine.get_status()

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
