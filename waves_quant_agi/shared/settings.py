from pydantic_settings import BaseSettings
from pydantic import Extra
from typing import Optional
import os

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "WAVES QUANT AGI ENGINE"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://waves:waves123@localhost:5432/waves_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672"

    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Payment (Paystack)
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""

    # Broker APIs
    MT5_LOGIN: str = ""
    MT5_PASSWORD: str = ""
    MT5_SERVER: str = ""

    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""

    # Performance Targets
    TARGET_MONTHLY_RETURN: float = 0.20
    TARGET_SHARPE: float = 3.0
    MAX_DRAWDOWN: float = 0.05
    MIN_WIN_RATE: float = 0.80

    # Engine Settings
    STRATEGY_VALIDATION_TRADES: int = 1000
    MONTE_CARLO_SIMULATIONS: int = 1000
    RESPONSE_TIME_MS: int = 200

    class Config:
        env_file = ".env"
        extra = Extra.allow  # ✅ Allow unknown keys from .env

settings = Settings()
