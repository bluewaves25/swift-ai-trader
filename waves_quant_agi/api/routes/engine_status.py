from fastapi import APIRouter
import redis
from datetime import datetime

router = APIRouter()

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

@router.get("/api/engine/status")
def engine_status():
    heartbeat = r.get("engine-heartbeat")
    if heartbeat:
        return {"status": "running", "last_heartbeat": heartbeat}
    else:
        return {"status": "not running", "last_heartbeat": None} 