from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from .transaction import TransactionOut

class PortfolioBase(BaseModel):
    balance: float
    returns: float
    nav: float

class PortfolioCreate(PortfolioBase):
    user_id: str

class PortfolioOut(PortfolioBase):
    id: str
    user_id: str
    transactions: Optional[List[TransactionOut]] = []

    model_config = ConfigDict(from_attributes=True)

# 👇 Fix import error
PortfolioResponse = PortfolioOut
