import asyncio
import aiofiles
import os
import shutil
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from supabase import create_client
from dotenv import load_dotenv

from strategy_core.train_trade_model import train  # Fixed import

load_dotenv()

# Supabase client setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MODEL_PATH = "trade_model.pt"
BUCKET_NAME = "ai-models"

async def save_model_to_supabase():
    try:
        with open(MODEL_PATH, "rb") as f:
            content = f.read()
            # Delete if exists
            supabase.storage.from_(BUCKET_NAME).remove([MODEL_PATH])
            # Upload new
            supabase.storage.from_(BUCKET_NAME).upload(MODEL_PATH, content)
            print(f" Model uploaded to Supabase storage at {datetime.utcnow()}")
    except Exception as e:
        print(f" Error uploading model: {str(e)}")

async def retrain_and_upload():
    try:
        print(" Starting model retraining...")
        await train()
        await save_model_to_supabase()
        print(" Retraining & upload complete")
    except Exception as e:
        print(f" Retraining failed: {str(e)}")

async def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Every 2 days at 3am UTC
    scheduler.add_job(lambda: asyncio.create_task(retrain_and_upload()), 'cron', hour=3, minute=0, day='*/2')
    scheduler.start()
    print(" Retraining scheduler started.")

    # Keep the script alive
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(start_scheduler())
