Executor Validator
Validation

Scores trades (90% win rate for crypto, 95% for forex) using XGBoost, LightGBM, CatBoost.
Inputs: TA-Lib indicators, OpenRouter/X API sentiment, market data.
Thresholds: ≥90 (Binance), ≥95 (Exness).

Execution

Binance: CCXT WebSockets (<50ms latency).
Exness: MT5 scripts with Redis-cached logs (<50ms).

Backtesting

6-month 1-minute data (Supabase).
Monte Carlo and walk-forward optimization for 90–95% win rate.
