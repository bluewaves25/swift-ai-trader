from fastapi import APIRouter, Depends, HTTPException, status
from waves_quant_agi.api.auth import get_current_user
from waves_quant_agi.core.models.user import User
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from waves_quant_agi.core.database import get_db
import os
import httpx

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

@router.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "is_admin": current_user.is_admin}

@router.post("/api/auth/signup")
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    # 1. Register with Supabase Auth REST API
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/auth/v1/admin/users",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            },
            json={"email": req.email, "password": req.password, "email_confirm": True}
        )
        if resp.status_code >= 400:
            raise HTTPException(status_code=400, detail=resp.json().get("msg") or resp.text)
        user_data = resp.json()["user"] if "user" in resp.json() else resp.json()
        user_id = user_data["id"]

    # 2. Insert into your users table
    user = User(id=user_id, email=req.email, is_active=True, is_admin=False)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"status": "success", "user_id": user_id}

@router.post("/api/auth/logout")
async def logout():
    # Stub: In production, handle token/session invalidation if needed
    return {"status": "success", "message": "Logout is stateless (client should remove token)"} 