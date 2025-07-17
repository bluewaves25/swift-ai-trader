from fastapi import APIRouter, Depends, HTTPException, status
from api.auth import get_current_user
from core.models.user import User
from pydantic import BaseModel, EmailStr

router = APIRouter()

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

@router.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "is_admin": current_user.is_admin}

@router.post("/api/auth/signup")
async def signup(req: SignupRequest):
    # Stub: In production, create user in DB/Supabase
    return {"status": "success", "message": "Signup not implemented (use Supabase client)"}

@router.post("/api/auth/logout")
async def logout():
    # Stub: In production, handle token/session invalidation if needed
    return {"status": "success", "message": "Logout is stateless (client should remove token)"} 