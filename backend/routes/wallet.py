
from fastapi import APIRouter
from supabase_client import SupabaseClient

router = APIRouter()

db = SupabaseClient()

@router.get("/balance")
async def get_balance(user_id: str):
    result = db.client.table("portfolios").select("*").eq("user_id", user_id).execute()
    return result.data

@router.post("/update")
async def update_balance(user_id: str, balance: dict):
    result = db.client.table("portfolios").upsert({"user_id": user_id, **balance}).execute()
    return result.data
