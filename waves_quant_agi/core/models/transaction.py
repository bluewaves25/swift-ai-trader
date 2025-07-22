from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.sql import func
from waves_quant_agi.core.database import Base
import enum
from sqlalchemy.orm import relationship

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(String, ForeignKey("investor_portfolios.id"), nullable=True)

    # Use SqlEnum and set native_enum=False for better cross-database compatibility
    type = Column(SqlEnum(TransactionType, native_enum=False), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(SqlEnum(TransactionStatus, native_enum=False), default=TransactionStatus.PENDING)

    # Optional: Add these if needed for deposit/withdraw tracking
    reference = Column(String, unique=True, nullable=True)
    description = Column(String, nullable=True)

    portfolio = relationship("InvestorPortfolio", back_populates="transactions")

class TradeStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class Trade(Base):
    __tablename__ = "trades"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=True) # Changed to nullable to support placeholder
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # buy/sell
    volume = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    pnl = Column(Float, default=0.0)
    strategy = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # Standardized to created_at
    status = Column(SqlEnum(TradeStatus, native_enum=False), default=TradeStatus.PENDING) # Changed default
