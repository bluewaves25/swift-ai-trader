# api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from shared.settings import settings
from api.middleware import PrometheusMiddleware
from api.routes import investor, portfolio, admin, engine

app = FastAPI(
    title=settings.APP_NAME,
    description="🌊 WAVES Quant AGI Backend API",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(PrometheusMiddleware)

# Routers
app.include_router(investor.router, prefix="/api/investor", tags=["Investor"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(engine.router, prefix="/api/engine", tags=["Engine"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "project": settings.APP_NAME,
        "status": "🚀 running",
        "version": settings.VERSION
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
