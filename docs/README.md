
# Waves Quant Engine – Full-Stack AI Trading Platform

## Overview
A modern, modular, AI-powered trading platform supporting both traditional and crypto assets. Features robust FastAPI backend, React/Vite frontend, real-time engine, and full Supabase integration.

---

## Architecture
- **Backend:** Python 3.12 (FastAPI, SQLAlchemy, Pydantic, Redis, Supabase, MT5, Binance)
- **Engine:** Python 3.10 (AI/ML, strategy execution, market data processing)
- **Frontend:** React (Vite, Redux, TypeScript)
- **Database:** PostgreSQL/TimescaleDB (via Supabase)
- **Realtime:** Redis (market data, engine heartbeat)

---

## Key Features
- **User Auth:** Supabase JWT, session persistence, role-based dashboards
- **Investor Dashboard:** Portfolio, trades, payments, analytics
- **Owner Dashboard:** Engine control, strategies, logs, health, support chat, engine feed
- **Support Chat:** Modal for user support (stubbed backend)
- **Engine Feed:** Manual market data injection (for testing)
- **Engine Status:** Live polling of engine health
- **Error Handling:** 401/403 auto signout, session persistence, robust routing

---

## Routing
- `/auth` – Login/Signup/Reset (AuthPage)
- `/investor-dashboard` – Investor dashboard (protected)
- `/owner-dashboard` – Owner dashboard (protected)
- `/about`, `/contact`, `/terms` – Info pages
- `*` – NotFound

---

## Backend API Endpoints
- `/api/auth/me` – Get current user info
- `/api/auth/signup` – Signup (stub)
- `/api/auth/logout` – Logout (stateless)
- `/api/owner/investors/overview` – Investors overview (stub)
- `/api/owner/logs` – Logs (stub)
- `/api/owner/health/system` – System health (stub)
- `/api/owner/strategies` – Strategies list
- `/api/engine/status` – Engine health/heartbeat
- `/api/engine/feed` – Manual market data injection
- `/api/support/chat` – Support chat (stub)

---

## Quickstart
1. **Install dependencies** for both Python environments and frontend.
2. **Set up .env files** for backend and frontend (see templates).
3. **Start Redis, backend, engine, and market data feeder:**
   - `./waves_quant_agi/start_all.ps1` (recommended)
   - Or run each service manually.
4. **Start frontend:**
   - `npm run dev`
5. **Visit** `http://localhost:5173` (or `:3000`) for the app, `:8000/docs` for backend docs.

---

## Environment Setup
- **Backend:** `waves_quant_agi/.env` (see template in repo)
- **Frontend:** `.env` in project root (see template in repo)
- **MT5/Binance:** Set credentials in backend .env
- **Supabase:** Set project URL and anon key in frontend .env

---

## Engine/Market Data Flow
- Market data is pushed to Redis (`market-data` queue) by the feeder script or engine feed UI.
- Engine processes data, places trades via MT5/Binance, updates DB.
- Engine heartbeat is set in Redis (`engine-heartbeat`), polled by backend and frontend.

---

## Troubleshooting
- **401/403 errors:** Check Supabase keys, session, and login status. App will auto signout and redirect to `/auth`.
- **ERR_CONNECTION_REFUSED:** Ensure backend is running on `:8000` and Vite proxy is set up.
- **No trades:** Ensure engine, Redis, and market data feeder are running. Check MT5/Binance credentials and symbols.
- **Signout issues:** Now always redirects to `/auth`.
- **Support chat/engine feed:** Available in Owner Dashboard for testing.

---

## Contributing
- See code comments and docs for extension points (strategies, endpoints, UI).
- PRs and issues welcome!

## Authentication & Session Management

- The app uses Supabase for authentication.
- The Supabase client is initialized in `src/integrations/supabase/client.ts` using environment variables.
- The `AuthProvider` in `src/contexts/AuthContext.tsx` manages user state and session.
- On sign in/out, the app listens for Supabase auth state changes and redirects accordingly.
- If Supabase is unreachable or misconfigured, the app will now show an error and not hang.
- To sign out, the UI calls the `signOut` function from context, which calls `supabase.auth.signOut()` and clears local storage.
- All protected routes use the `ProtectedRoute` component to ensure only authenticated users can access dashboards.

**Troubleshooting:**
- If you see "authentication timed out", check your `.env` for correct Supabase URL and anon key, and ensure your network allows access to Supabase.
- Always restart the dev server after changing environment variables.
