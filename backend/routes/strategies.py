from fastapi import APIRouter
from supabase_client import SupabaseClient
from strategy_core.selector import StrategySelector
from ai_brains.breakout import BreakoutStrategy
from ai_brains.scalping import ScalpingStrategy
from ai_brains.mean_reversion import MeanReversionStrategy

router = APIRouter()

db = SupabaseClient()
selector = StrategySelector()
strategies = {
    'breakout': BreakoutStrategy(),
    'scalping': ScalpingStrategy(),
    'mean_reversion': MeanReversionStrategy()
}

@router.get("/signals")
async def get_signals(symbol: str):
    data = db.get_historical_data(symbol, (datetime.utcnow() - timedelta(days=1)).isoformat(), datetime.utcnow().isoformat()).data
    strategy_name = selector.select_strategy(symbol, data[-1])
    strategy = strategies[strategy_name]
    signal = strategy.analyze(data)
    return {"symbol": symbol, "signal": signal['signal'], "confidence": signal['confidence']}

@router.get("/performance")
async def get_performance(symbol: str = None):
    query = db.client.table("pair_strategies").select("*")
    if symbol:
        query = query.eq("symbol", symbol)
    return query.execute().data

@router.post("/risk")
async def update_risk_params(params: dict):
    db.client.table("risk_params").upsert(params).execute()
    return {"status": "success"}