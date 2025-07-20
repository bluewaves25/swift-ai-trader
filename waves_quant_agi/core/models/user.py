# core/models/user.py

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from waves_quant_agi.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relationship to portfolio and transactions
    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    transactions = relationship("Transaction", backref="user")
