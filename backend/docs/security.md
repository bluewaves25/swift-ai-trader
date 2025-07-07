Security Measures
Authentication

JWT with 2FA (TOTP via Google Authenticator).
RBAC: Admin-only for owner dashboard, user-specific for wallets/trades.
Token expiry: 1 hour (access), 7 days (refresh).

Encryption

AES-256 for broker credentials, payment details (Fernet, 32-byte key).
TLS 1.3 for all API/WebSocket communications.
Client-side encryption for withdrawal addresses.

Data Protection

Supabase: Row-level security (RLS) for user data.
Daily encrypted backups to AWS S3 (90-day retention).
Data minimization: No raw card/crypto data stored.

Network Security

Cloudflare WAF: Protects against DDoS, SQL injection, XSS.
Rate limiting: 100 requests/min per IP (FastAPI middleware).
IP whitelisting: Restrict admin endpoints to owner’s IP.
VPC: Redis, Supabase accessible only via secure VPN.

Broker Security

Binance: API keys restricted to trade/withdraw permissions.
Exness: MT5 credentials encrypted, secure server connections.

Payment Security

Stripe/Coinbase: Tokenized payments, no raw data stored.
KYC: Onfido for withdrawals >$5,000.
Escrow: Stripe Connect for 24-hour dispute window.

Monitoring and Response

ELK stack: Logs all API requests, trades, errors.
Prometheus: Anomaly detection (e.g., unusual trade volumes).
Slack/Telegram: Alerts for security events (e.g., >3 failed logins).
Quarterly penetration testing by external auditors.

Anti-Fraud

Flag transactions >$50,000 for owner review.
ML (Isolation Forest): Detects suspicious activity (e.g., rapid withdrawals).
Audit trail: All actions logged in Supabase with timestamps.

Compliance

GDPR/CCPA: Support data deletion requests, user consent.
AML/KYC: Onfido checks, tax reporting (1099-MISC for US).
