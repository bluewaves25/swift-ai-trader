# Waves Quant Engine

A modern, modular, AI-powered trading platform for retail and professional investors. Features robust FastAPI backend, React/Vite frontend, real-time engine, and full Paystack integration.

---

## Features
- **Subscription Plans** (Paystack, free trial, premium gating)
- **Performance Fees** (pay only when you profit)
- **AI Strategy Marketplace** (buy, sell, rate, earn)
- **Affiliate Program** (referral links, commissions, payouts)
- **Premium Analytics** (real-time dashboards, advanced insights)
- **B2B/White-Label** (multi-tenant, custom branding)
- **Owner/Admin & Investor Dashboards**
- **Robust Risk Management, Multi-Broker Execution**

---

## Architecture
- **Backend:** Python 3.12 (FastAPI, SQLAlchemy, Redis, Paystack, MT5, Binance)
- **Engine:** Python 3.10 (AI/ML, strategy execution, market data)
- **Frontend:** React (Vite, Redux, TypeScript)
- **Database:** PostgreSQL/TimescaleDB (via Supabase)
- **Realtime:** Redis (market data, engine heartbeat)

---

## Setup

### 1. Clone & Install
```bash
# Backend
cd waves_quant_agi
# Setup Python envs (see docs/env_README.md)
# Install requirements for both env_main and env_310

# Frontend
cd ../src
npm install
```

### 2. Configure Environment
- Copy `.env.example` to `.env` in backend and frontend, fill in credentials (Paystack, DB, etc.)

### 3. Run All Services
```bash
# From project root
./waves_quant_agi/scripts/run-all.ps1
# Or use Docker for production
```

### 4. Start Frontend
```bash
cd src
npm run dev
```

---

## Dashboards & Navigation
- **Investor Dashboard:** Portfolio, signals, trades, journal, payments, subscription, performance fees, marketplace, affiliate
- **Owner/Admin Dashboard:** Engine control, strategies, analytics, risk, user management, billing, performance fees
- **Premium Gating:** All premium features require active subscription or free trial

---

## Revenue Features
- **Subscription Plans:** `/investor-dashboard?section=subscription`
- **Performance Fees:** `/investor-dashboard?section=fees`
- **Marketplace:** `/investor-dashboard?section=marketplace`
- **Affiliate:** `/investor-dashboard?section=affiliate`
- **Analytics:** `/investor-dashboard?section=overview`

---

## API Reference (Key Endpoints)
- `/api/v1/billing/plans` — List subscription plans
- `/api/v1/billing/initialize` — Start Paystack payment
- `/api/v1/billing/status` — Get subscription status
- `/api/v1/fees/performance` — Get performance fee breakdown
- `/api/v1/marketplace/strategies` — List strategies
- `/api/v1/marketplace/buy` — Buy a strategy
- `/api/v1/affiliate/referral` — Get referral code
- `/api/v1/affiliate/stats` — Affiliate stats

(See `/docs` for full API reference)

---

## Documentation
- See `docs/` for:
  - System architecture
  - Backend/frontend setup
  - Revenue roadmap
  - API reference
  - User and admin guides

---

## Contributing
- PRs and issues welcome! See code comments and docs for extension points (strategies, endpoints, UI).

---

## License
MIT
