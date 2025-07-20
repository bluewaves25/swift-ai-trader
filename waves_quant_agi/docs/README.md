# Waves Quant Engine Documentation

A comprehensive guide to the architecture, features, setup, and revenue streams of the Waves Quant Engine platform.

---

## Overview
- AI-powered trading platform for retail and professional investors
- Modular FastAPI backend, React/Vite frontend, real-time engine
- Revenue features: subscriptions, performance fees, marketplace, affiliate, analytics, B2B

---

## Architecture
- **Backend:** Python 3.12 (FastAPI, SQLAlchemy, Redis, Paystack, MT5, Binance)
- **Engine:** Python 3.10 (AI/ML, strategy execution, market data)
- **Frontend:** React (Vite, Redux, TypeScript)
- **Database:** PostgreSQL/TimescaleDB (via Supabase)
- **Realtime:** Redis (market data, engine heartbeat)

---

## Revenue Features
- **Subscription Plans:** Paystack integration, free trial, premium gating
- **Performance Fees:** Pay only when you profit
- **AI Strategy Marketplace:** Buy, sell, rate, and earn from strategies
- **Affiliate Program:** Referral links, commissions, payouts
- **Premium Analytics:** Real-time dashboards, advanced insights
- **B2B/White-Label:** Multi-tenant, custom branding

---

## Setup & Running
- See main README for setup instructions
- Use `./waves_quant_agi/scripts/run-all.ps1` to start all backend services
- Start frontend with `npm run dev` in `src/`

---

## Navigation & Dashboards
- **Investor Dashboard:** Portfolio, signals, trades, journal, payments, subscription, performance fees, marketplace, affiliate
- **Owner/Admin Dashboard:** Engine control, strategies, analytics, risk, user management, billing, performance fees
- **Premium Gating:** All premium features require active subscription or free trial

---

## API Reference
- See `/api/v1/` endpoints for all features (billing, fees, marketplace, affiliate, analytics)
- Full OpenAPI docs available at `/docs` when running in debug mode

---

## Adding New Features
- To add a new strategy: place it in `engine/strategies/` and it will be auto-discovered
- To add a new marketplace item: use the marketplace endpoints
- To extend affiliate logic: update backend endpoints and UI

---

## Contributing
- PRs and issues welcome! See code comments and this documentation for extension points.

---

## Contact
- For B2B/white-label inquiries, use the Contact page or `/contact` route in the app. 