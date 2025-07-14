### api/deps.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.database import get_db

# Common dependencies placeholder for shared logic or reuse.

def get_async_session() -> AsyncSession:
    return Depends(get_db)