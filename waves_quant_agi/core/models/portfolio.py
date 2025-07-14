# core/models/portfolio.py

from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class InvestorPortfolio(Base):
    __tablename__ = "investor_portfolios"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    balance = Column(Float, default=0.0)
    nav = Column(Float, default=0.0)
    returns = Column(Float, default=0.0)

    user = relationship("User", back_populates="portfolio")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")
