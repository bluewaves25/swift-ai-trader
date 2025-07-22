from fastapi import APIRouter, Depends, HTTPException, status, Body
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
    # 1. Check if email already exists in your users table
    from sqlalchemy.future import select
    result = await db.execute(select(User).where(User.email == req.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")

    # 2. Register with Supabase Auth REST API
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
            # If Supabase says user exists, return 409
            msg = resp.json().get("msg") or resp.text
            if "already registered" in msg.lower() or "duplicate" in msg.lower():
                raise HTTPException(status_code=409, detail="Email already exists")
            raise HTTPException(status_code=400, detail=msg)
        user_data = resp.json()["user"] if "user" in resp.json() else resp.json()
        user_id = user_data["id"]

    # 3. Insert into your users table
    user = User(
        id=user_id,
        email=req.email,
        is_active=True,
        is_admin=False,
        role="investor"
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except Exception as e:
        await db.rollback()
        print(f"[SIGNUP ERROR] {e}")
        raise HTTPException(status_code=500, detail=f"Database error saving new user: {e}")
    return {"status": "success", "user_id": user_id}

@router.post("/api/auth/logout")
async def logout():
    # Stub: In production, handle token/session invalidation if needed
    return {"status": "success", "message": "Logout is stateless (client should remove token)"}

@router.post("/api/auth/resend-confirmation")
async def resend_confirmation(email: str = Body(..., embed=True)):
    """
    Resend the confirmation email to the given user email using Supabase Auth API.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/auth/v1/recover",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            },
            json={"email": email}
        )
        if resp.status_code >= 400:
            raise HTTPException(status_code=400, detail=resp.text)
    return {"status": "confirmation email resent"} 