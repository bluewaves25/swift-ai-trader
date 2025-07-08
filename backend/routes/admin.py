from fastapi import APIRouter, HTTPException, Depends
from supabase import Client
from db.supabase_client import get_supabase_client
from pydantic import BaseModel
from routes.payments import PaymentService

router = APIRouter()

class User(BaseModel):
    id: str
    is_admin: bool = False

# 👇 This now returns both user and client
async def get_current_user_with_client(supabase: Client = Depends(get_supabase_client)):
    user_result = await supabase.table("users").select("*").eq("id", "user_id").execute()
    if not user_result.data or not user_result.data[0]["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return User(**user_result.data[0]), supabase

@router.post("/start")
async def start_trading(user_supabase=Depends(get_current_user_with_client)):
    user, supabase = user_supabase
    await supabase.table("system").update({"trading_active": True}).eq("id", 1).execute()
    return {"message": "Trading started"}

@router.post("/stop")
async def stop_trading(user_supabase=Depends(get_current_user_with_client)):
    user, supabase = user_supabase
    await supabase.table("system").update({"trading_active": False}).eq("id", 1).execute()
    return {"message": "Trading stopped, positions closed"}

@router.post("/approve-withdrawal/{request_id}")
async def approve_withdrawal(request_id: str, approve: bool, user_supabase=Depends(get_current_user_with_client)):
    user, supabase = user_supabase
    withdrawal = await supabase.table("withdrawals").select("*").eq("id", request_id).execute()
    if not withdrawal.data:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    
    payment_service = PaymentService()
    if approve:
        await payment_service.process_withdrawal(
            withdrawal.data[0]["user_id"],
            withdrawal.data[0]["amount"],
            withdrawal.data[0]["currency"],
            withdrawal.data[0]["address"]
        )
        await supabase.table("withdrawals").update({"status": "approved"}).eq("id", request_id).execute()
    else:
        await supabase.table("withdrawals").update({"status": "rejected"}).eq("id", request_id).execute()
    
    return {"message": f"Withdrawal {request_id} {'approved' if approve else 'rejected'}"}
