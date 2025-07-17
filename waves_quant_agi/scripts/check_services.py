import requests
import redis
import os
import sys
from datetime import datetime

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# --- Check Redis ---
def check_redis():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        pong = r.ping()
        print(f"[OK] Redis: {pong}")
        # Check engine heartbeat
        heartbeat = r.get("engine-heartbeat")
        if heartbeat:
            print(f"[OK] Engine heartbeat: {heartbeat}")
        else:
            print("[WARN] Engine heartbeat not found")
    except Exception as e:
        print(f"[FAIL] Redis: {e}")
        sys.exit(1)

# --- Check Backend ---
def check_backend():
    try:
        r = requests.get(f"{BACKEND_URL}/docs")
        if r.status_code == 200:
            print(f"[OK] Backend FastAPI: {BACKEND_URL}")
        else:
            print(f"[FAIL] Backend FastAPI: {r.status_code}")
            sys.exit(1)
        # Check engine status endpoint
        r2 = requests.get(f"{BACKEND_URL}/api/engine/status")
        if r2.status_code == 200:
            print(f"[OK] Engine status endpoint: {r2.json()}")
        else:
            print(f"[FAIL] Engine status endpoint: {r2.status_code}")
    except Exception as e:
        print(f"[FAIL] Backend: {e}")
        sys.exit(1)

# --- Check Supabase (optional, if supabase-py installed) ---
def check_supabase():
    try:
        from supabase import create_client, Client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            print("[SKIP] Supabase: No URL or key in env")
            return
        supabase: Client = create_client(url, key)
        res = supabase.table("users").select("id").limit(1).execute()
        print(f"[OK] Supabase: {url}")
    except ImportError:
        print("[SKIP] Supabase: supabase-py not installed")
    except Exception as e:
        print(f"[FAIL] Supabase: {e}")

if __name__ == "__main__":
    print("=== Checking Services ===")
    check_redis()
    check_backend()
    check_supabase()
    print("=== All checks complete ===")
