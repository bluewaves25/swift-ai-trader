from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase import Client
from db.supabase_client import get_supabase_client
from scripts.exness_trade import BinanceBroker, ExnessBroker

router = APIRouter()

class Deposit(BaseModel):
    currency: str
    amount: float

class Withdraw(BaseModel):
    currency: str
    amount: float
    address: str

@router.post("/deposit/{broker}/{account}")
async def deposit(broker: str, account: str, deposit: Deposit, supabase: Client = Depends(get_supabase_client)):
    try:
        from routes.payments import PaymentService
        payment_service = PaymentService()
        payment_url = await payment_service.initiate_payment(deposit.amount, deposit.currency, "user_id")
        await supabase.table("wallets").insert({"broker": broker, "account_number": account, "balance": 0, "currency": deposit.currency}).execute()
        return {"payment_url": payment_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/withdraw/{broker}/{account}")
async def withdraw(broker: str, account: str, withdraw: Withdraw, supabase: Client = Depends(get_supabase_client)):
    try:
        from routes.payments import PaymentService
        payment_service = PaymentService()
        await supabase.table("withdrawals").insert({"broker": broker, "account_number": account, "amount": withdraw.amount, "currency": withdraw.currency, "address": withdraw.address, "status": "pending"}).execute()
        await payment_service.notify_owner_withdrawal("user_id", withdraw.amount, withdraw.currency, withdraw.address)
        return {"message": "Withdrawal request submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/balance/{broker}/{account}")
async def get_balance(broker: str, account: str, supabase: Client = Depends(get_supabase_client)):
    if broker == "binance":
        balance = await BinanceBroker().get_balance()
    elif broker == "exness":
        balance = await ExnessBroker().get_balance(account)
    else:
        raise HTTPException(status_code=400, detail="Unsupported broker")
    return balance