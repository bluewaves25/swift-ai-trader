# Backend Overview – Waves Quant Engine

## What the Backend Does
- Handles all API requests from frontend (investor, owner, admin)
- Manages users, portfolios, payments, strategies, analytics, and more
- Integrates with Paystack, Redis, PostgreSQL, and external brokers (MT5, Binance)
- Runs the AI/ML engine for strategy execution and analytics
- Exposes all revenue features: subscriptions, performance fees, marketplace, affiliate

## Main Components
- **FastAPI**: API layer for all user and admin actions
- **Engine (backend-ml)**: AI/ML, strategy execution, market data processing
- **Database**: PostgreSQL/TimescaleDB (via Supabase)
- **Payments**: Paystack integration for subscriptions and fees
- **Realtime**: Redis for job queues, engine heartbeat, and inter-service communication

## Communication Flow
- Frontend → FastAPI (backend-main) → Engine (backend-ml) via Redis
- All premium features are gated by subscription status
- Marketplace and affiliate endpoints are available for investors

## Revenue Features
- Subscriptions, performance fees, marketplace, affiliate, analytics, B2B

## See also:
- `backend_architecture.md` for folder structure
- `env_README.md` for environment setup
- Main README for full feature list