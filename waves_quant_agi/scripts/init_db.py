# scripts/init_db.py

import asyncio
from core.database import engine, Base
from core.models import user, portfolio, transaction, strategy

# Create all database tables
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)   # Optional: remove in production
        await conn.run_sync(Base.metadata.create_all)
        print("✅ All tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_models())
