from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime
import logging
import numpy as np
import pandas as pd
import redis
import threading
import json
import time
import asyncio
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Waves Quant AGI - ML Backend",
    description="Machine Learning backend service for Waves Quant AGI trading platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(REDIS_URL)

logger.info("[ML ENGINE WORKER] Starting ML job listener on 'ml:jobs' queue.")

async def ml_worker_async():
    loop = asyncio.get_event_loop()
    while True:
        job = await loop.run_in_executor(None, lambda: redis_client.blpop("ml:jobs", timeout=5))
        if job:
            _, job_data = job
            job_data = json.loads(job_data)
            job_id = job_data["job_id"]
            payload = job_data["payload"]
            # Here you would run your ML prediction logic
            result = {"job_id": job_id, "result": payload, "status": "done", "timestamp": datetime.utcnow().isoformat()}
            redis_client.set(f"ml:results:{job_id}", json.dumps(result), ex=60)
        else:
            await asyncio.sleep(1)

async def start_trading_engine_worker():
    logger.info("[TRADING ENGINE WORKER] Launching run_engine_api.py as subprocess.")
    subprocess.Popen(["python", "waves_quant_agi/engine/run_engine_api.py"])  # Assumes cwd is project root

@app.on_event("startup")
async def startup_event():
    # Start ML worker
    asyncio.create_task(ml_worker_async())
    # Start Trading Engine worker with correct PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    subprocess.Popen([
        sys.executable, "waves_quant_agi/engine/run_engine_api.py"
    ], env=env)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Waves Quant AGI - ML Backend",
        "version": "1.0.0",
        "status": "running",
        "python_version": "3.10",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "backend-ml",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "service": "backend-ml",
        "python_version": "3.10",
        "ml_capabilities": [
            "torch", "scikit-learn", "prophet", "transformers"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/ml/test")
async def ml_test():
    """Test ML capabilities"""
    try:
        # Test numpy
        arr = np.array([1, 2, 3, 4, 5])
        mean_val = float(np.mean(arr))
        
        # Test pandas
        df = pd.DataFrame({'test': [1, 2, 3]})
        df_sum = int(df['test'].sum())
        
        return {
            "status": "success",
            "numpy_test": mean_val,
            "pandas_test": df_sum,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"ML test failed: {e}")
        raise HTTPException(status_code=500, detail=f"ML test failed: {str(e)}")

@app.post("/api/v1/ml/predict")
async def predict():
    """ML prediction endpoint (placeholder)"""
    return {
        "message": "ML prediction endpoint",
        "status": "placeholder",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port) 