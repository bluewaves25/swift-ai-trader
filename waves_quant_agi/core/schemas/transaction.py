from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


# --- Base Schema ---
class TransactionBase(BaseModel):
    amount: float
    type: Literal["deposit", "withdrawal"]
    status: Literal["pending", "success", "failed"]


class TransactionCreate(TransactionBase):
    user_id: str
    portfolio_id: str


class TransactionOut(TransactionBase):
    id: str
    user_id: str
    portfolio_id: str
    created_at: datetime

    class Config:
        from_attributes = True  # pydantic v2 replacement for orm_mode


# --- Required by investor.py ---
class DepositRequest(BaseModel):
    amount: float


class WithdrawRequest(BaseModel):
    amount: float


class TransactionResponse(BaseModel):
    id: str
    user_id: str
    type: str
    amount: float
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True
