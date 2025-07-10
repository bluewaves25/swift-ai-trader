import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import redis.asyncio as redis

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

async def update_system_status():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    
    try:
        while True:
            response = supabase.table("system").select("trading_active").limit(1).execute()
            if response.data:
                status = response.data[0]["trading_active"]
                await redis_client.set("system_status", status)
                print(f" Updated Redis with system status: {status}")
            else:
                print(" No system status found")
            await asyncio.sleep(60)  # Update every minute
    except Exception as e:
        print(f" Error updating system status: {str(e)}")
    finally:
        await redis_client.close()

if __name__ == "__main__":
    asyncio.run(update_system_status())
