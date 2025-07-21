# core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from waves_quant_agi.shared.settings import Settings

settings = Settings()

# Base class for all ORM models
Base = declarative_base()

# Create the async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create a configured "Session" class
AsyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

# For components that need a synchronous session (like the learning engine)
from sqlalchemy import create_engine
sync_engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


async def get_db() -> AsyncSession:
    """FastAPI dependency to get a DB session."""
    async with AsyncSessionLocal() as session:
        yield session
