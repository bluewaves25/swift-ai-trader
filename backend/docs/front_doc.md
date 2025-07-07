Frontend Integration Points
Authentication

Use Supabase Auth for login/signup (email, OAuth).
Include JWT in Authorization: Bearer <token> for all API requests.

API Endpoints

POST /wallet/deposit/{broker}/{account}: Initiate deposits (Flutterwave, Stripe, Coinbase). Returns payment URL. Brokers: binance, exness.
POST /wallet/withdraw/{broker}/{account}: Submit withdrawal requests, triggers owner email. Brokers: binance, exness.
GET /wallet/balance/{broker}/{account}: Fetch wallet balances. Brokers: binance, exness.
POST /trade/{broker}/{account}: Execute trades (90% win rate for Binance, 95% for Exness). Requires symbol mapped to trading_pairs.
GET /signal/sentiment/{symbol}: Get OpenRouter/X API sentiment scores.
POST /strategies/select: Select active strategy (breakout, mean_reversion, scalping, arbitrage).
GET /strategies/active: List active strategies.
POST /payments/subscribe: Subscribe to premium ($12/month) or Pro ($25/month).
POST /admin/start: Start trading (owner only, requires is_admin).
POST /admin/stop: Stop trading, close positions (owner only).
POST /admin/approve-withdrawal/{request_id}: Approve/reject withdrawals (owner only).

WebSocket Endpoints

/ws/trades: Live trade updates (filtered by user_id).
/ws/balances: Real-time wallet balances.
/ws/metrics: Performance metrics (win rate, P/L, risk).

Frontend Components

Investor Dashboard:
Display balances, trades (with symbol from trading_pairs), fees, subscription status.
Strategy leaderboard (win rate, Sharpe ratio).


Deposit Form: Fields for payment method (Momo, bank, card, crypto), amount, currency.
Withdrawal Form: Fields for amount, method, bank/crypto address, KYC status.
Admin Dashboard:
Start/stop button.
Withdrawal approval queue.
Grafana charts (iframe for metrics).
Strategy override selector.


Analytics Page: Show sentiment scores, risk metrics, loss analysis (SHAP values, pair_id for losses).

Redux Actions

setBroker: Update selected broker (binance, exness).
addWallet: Add broker account.
updateBalance: Sync wallet balances.
addTrade: Log new trades (include pair_id, symbol).
setSubscription: Update subscription status (premium, pro).
setUser: Store authenticated user’s id and is_admin.
