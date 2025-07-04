
from fastapi import APIRouter, HTTPException
from supabase_client import SupabaseClient
import ccxt.async_support as ccxt
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

db = SupabaseClient()

@router.post("/execute")
async def execute_trade(symbol: str, trade_type: str, amount: float):
    exness = ccxt.exness({
        'apiKey': os.getenv("EXNESS_API_KEY"),
        'secret': os.getenv("EXNESS_API_SECRET"),
        'enableRateLimit': True,
    })
    try:
        order = await exness.create_market_order(symbol, trade_type, amount)
        trade_data = {
            'symbol': symbol,
            'trade_type': trade_type,
            'amount': amount,
            'entry_price': order['price'],
            'status': 'executed',
            'created_at': datetime.utcnow().isoformat()
        }
        db.save_trade(trade_data)
        return {"status": "success", "order": order}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await exness.close()

@router.get("/history")
async def get_trade_history(symbol: str = None):
    query = db.client.table("trades").select("*")
    if symbol:
        query = query.eq("symbol", symbol)
    return query.execute().data
