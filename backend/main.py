
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import trade, wallet, strategies

app = FastAPI(title="Waves Quant Engine")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(trade.router, prefix="/api/trade")
app.include_router(wallet.router, prefix="/api/wallet")
app.include_router(strategies.router, prefix="/api/strategies")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
