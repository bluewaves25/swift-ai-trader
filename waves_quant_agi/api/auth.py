from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from waves_quant_agi.shared.settings import settings
from waves_quant_agi.core.models.user import User
from waves_quant_agi.core.database import get_db
import logging
import requests
from functools import lru_cache

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Token utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

SUPABASE_JWKS_URL = 'https://YOUR_SUPABASE_PROJECT_ID.supabase.co/auth/v1/keys'  # <-- Replace with your actual Supabase project ID

@lru_cache(maxsize=1)
def get_supabase_jwks():
    resp = requests.get(SUPABASE_JWKS_URL)
    resp.raise_for_status()
    return resp.json()['keys']

def get_supabase_public_key(kid):
    keys = get_supabase_jwks()
    for key in keys:
        if key['kid'] == kid:
            return key
    return None

def verify_supabase_jwt(token):
    try:
        unverified_header = jwt.get_unverified_header(token)
        key = get_supabase_public_key(unverified_header['kid'])
        if not key:
            raise JWTError('Public key not found for kid')
        return jwt.decode(token, key, algorithms=[key['alg']], options={"verify_aud": False})
    except Exception as e:
        raise JWTError(f"Supabase JWT validation failed: {e}")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Try Supabase JWT validation first
        try:
            payload = verify_supabase_jwt(token)
        except Exception:
            # Fallback to legacy/local JWT validation
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT Decode Error: {e}")
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ✅ Renamed to match the expected import
async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return current_user
