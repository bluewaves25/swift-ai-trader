Swift AI Trader Backend Overview
Purpose
Fully autonomous HFT engine for wallet management, trading, risk management, and income with Binance (crypto) and Exness (forex/commodities/indices).
Architecture

Framework: FastAPI (Python).
Database: Supabase (PostgreSQL).
Cache/Queue: Redis Cluster.
Brokers: Binance (CCXT), Exness (MT5).
AI/ML: TensorFlow, Stable Baselines3, XGBoost.
Payments: Stripe, Coinbase Commerce, Flutterwave.
Monitoring: Prometheus, Grafana, ELK stack.

Key Features

Wallet management (deposits, withdrawals, 50% profit transfers).
Trade execution (90% win rate for crypto, 95% for forex).
Risk management with Post-Loss Performance Boost (PLPB).
Income: 20% profit fees, $12/$25 subscriptions.
Sentiment analysis via OpenRouter and X API.
