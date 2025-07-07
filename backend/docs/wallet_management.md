Wallet Management
Deposits

Methods: Flutterwave (Momo, bank, card), Stripe (fiat), Coinbase Commerce (crypto).
Flow: User → Owner's Binance USDT wallet → Broker accounts (Exness for forex/commodities/indices, Binance for crypto).
Storage: Supabase (wallets table).
Notifications: Twilio for deposits >$10,000.

Withdrawals

Flow: User request → Owner approval via SendGrid email → Funds from Binance USDT wallet.
KYC: Onfido for withdrawals >$5,000.
Storage: Supabase (withdrawals table).

Profit Transfers

50% daily profits to owner's Binance USDT wallet.
Cron job (APScheduler) using CCXT (Binance) or MT5 logs (Exness).
