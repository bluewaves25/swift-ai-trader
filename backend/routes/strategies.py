from fastapi import APIRouter, Depends
from strategy_core.selector import StrategySelector
from db.supabase_client import get_supabase_client
from supabase import Client

router = APIRouter()

@router.get("/active")
async def get_active_strategies(supabase: Client = Depends(get_supabase_client)):
    strategies = await supabase.table("strategies").select("*").eq("active", True).execute()
    return strategies.data

@router.post("/select")
async def select_strategy(strategy_name: str, supabase: Client = Depends(get_supabase_client)):
    selector = StrategySelector()
    await selector.select_strategy(strategy_name)
    await supabase.table("strategies").update({"active": True}).eq("name", strategy_name).execute()
    return {"message": f"Strategy {strategy_name} selected"}