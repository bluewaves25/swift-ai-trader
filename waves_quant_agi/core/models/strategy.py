# core/models/strategy.py

from sqlalchemy import Column, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from core.database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    win_rate = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    sortino_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    validated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Merge fields from StrategyRecord
    status = Column(String, default="active")
    performance = Column(Float, default=0.0)
    last_retrained = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(String, nullable=True)
