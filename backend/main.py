# --- backend/main.py ---
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, signals, charts, strategies, users, trades

app = FastAPI()

origins = [
    "http://localhost:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(signals.router)
app.include_router(charts.router)
app.include_router(strategies.router)
app.include_router(users.router)
app.include_router(trades.router)

@app.get("/")
def root():
    return {"status": "Waves Quant Engine Backend is running"}

# --- backend/routers/auth.py ---
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    # Dummy validation
    if data.email == "admin@waves.ai" and data.password == "secure":
        return {"token": "fake-jwt-token", "role": "owner"}
    raise HTTPException(status_code=401, detail="Invalid credentials")