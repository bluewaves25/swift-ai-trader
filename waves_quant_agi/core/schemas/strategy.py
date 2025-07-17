from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StrategyRecordResponse(BaseModel):
    id: str
    name: str
    status: str
    performance: float
    last_retrained: datetime
    description: Optional[str]

    class Config:
        orm_mode = True 