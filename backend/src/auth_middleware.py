from fastapi import Request, HTTPException, Depends
from supabase import Client
from db.supabase_client import get_supabase_client
import jwt
import os
from python_dotenv import load_dotenv

load_dotenv()

async def get_current_user(request: Request, supabase: Client = Depends(get_supabase_client)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ")[1]
    try:
        decoded = jwt.decode(token, os.getenv("SUPABASE_JWT_SECRET"), algorithms=["HS256"])
        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: user_id not found")
        user = await supabase.table("users").select("id, is_admin").eq("id", user_id).execute()
        if not user.data:
            raise HTTPException(status_code=401, detail="User not found")
        return {"id": user_id, "is_admin": user.data[0]["is_admin"]}
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")