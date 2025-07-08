-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop all tables to ensure clean setup
DROP TABLE IF EXISTS users, profiles, user_settings, portfolios, trades, transactions, market_data, ai_signals, pair_strategies, trading_pairs, performance_analytics, risk_settings, support_tickets, wallets, fees, withdrawals, subscriptions, system, losses CASCADE;

-- Create tables in dependency order
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE trading_pairs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL UNIQUE,
    base_asset VARCHAR(10) NOT NULL,
    quote_asset VARCHAR(10) NOT NULL,
    broker VARCHAR(20) CHECK (broker IN ('binance', 'exness')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    notifications BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker VARCHAR(20) CHECK (broker IN ('binance', 'exness')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pair_id UUID REFERENCES trading_pairs(id) ON DELETE RESTRICT,
    broker VARCHAR(20) CHECK (broker IN ('binance', 'exness')),
    account_number VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) CHECK (side IN ('buy', 'sell')),
    volume DECIMAL(15,2) NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    stop_loss DECIMAL(15,2) DEFAULT 0.0,
    take_profit DECIMAL(15,2) DEFAULT 0.0,
    order_id VARCHAR(50),
    status VARCHAR(20),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker VARCHAR(20) CHECK (broker IN ('binance', 'exness')),
    type VARCHAR(20) CHECK (type IN ('deposit', 'withdrawal', 'fee')),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    open DECIMAL(15,2),
    high DECIMAL(15,2),
    low DECIMAL(15,2),
    close DECIMAL(15,2),
    volume DECIMAL(15,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE ai_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    signal VARCHAR(20) CHECK (signal IN ('buy', 'sell', 'hold')),
    confidence DECIMAL(5,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE pair_strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pair_id UUID REFERENCES trading_pairs(id) ON DELETE RESTRICT,
    strategy VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE performance_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    strategy VARCHAR(50) NOT NULL,
    win_rate DECIMAL(5,2),
    profit_loss DECIMAL(15,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE risk_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    max_loss DECIMAL(15,2) DEFAULT 0.05,
    max_position_size DECIMAL(15,2) DEFAULT 0.07,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker VARCHAR(20) CHECK (broker IN ('binance', 'exness')),
    account_number VARCHAR(50) NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    currency VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE fees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker VARCHAR(20) CHECK (broker IN ('binance', 'exness')),
    amount DECIMAL(15,2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE withdrawals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker VARCHAR(20) CHECK (broker IN ('binance', 'exness')),
    account_number VARCHAR(50) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    address VARCHAR(255) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tier VARCHAR(20) CHECK (tier IN ('premium', 'pro')) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('active', 'cancelled')) DEFAULT 'active',
    renewal_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE system (
    id INTEGER PRIMARY KEY DEFAULT 1,
    trading_active BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT single_row CHECK (id = 1)
);

CREATE TABLE losses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pair_id UUID REFERENCES trading_pairs(id) ON DELETE RESTRICT,
    broker VARCHAR(20) CHECK (broker IN ('binance', 'exness')),
    type VARCHAR(20) CHECK (type IN ('small', 'medium', 'large')),
    amount DECIMAL(15,2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_pair_id ON trades(pair_id);
CREATE INDEX idx_trades_broker ON trades(broker);
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_losses_user_id ON losses(user_id);
CREATE INDEX idx_losses_pair_id ON losses(pair_id);
CREATE INDEX idx_losses_timestamp ON losses(timestamp);
CREATE INDEX idx_wallets_user_id ON wallets(user_id);
CREATE INDEX idx_wallets_broker ON wallets(broker);
CREATE INDEX idx_fees_user_id ON fees(user_id);
CREATE INDEX idx_fees_timestamp ON fees(timestamp);
CREATE INDEX idx_withdrawals_user_id ON withdrawals(user_id);
CREATE INDEX idx_withdrawals_status ON withdrawals(status);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_renewal_date ON subscriptions(renewal_date);
CREATE INDEX idx_trading_pairs_symbol ON trading_pairs(symbol);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE pair_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_pairs ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE fees ENABLE ROW LEVEL SECURITY;
ALTER TABLE withdrawals ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE system ENABLE ROW LEVEL SECURITY;
ALTER TABLE losses ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY user_access ON users FOR ALL USING (auth.uid() = id);
CREATE POLICY user_profiles ON profiles FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_settings_access ON user_settings FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_portfolios ON portfolios FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_trades ON trades FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_transactions ON transactions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_wallets ON wallets FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_fees ON fees FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_withdrawals ON withdrawals FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_subscriptions ON subscriptions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_losses ON losses FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_support_tickets ON support_tickets FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_risk_settings ON risk_settings FOR ALL USING (auth.uid() = user_id);
CREATE POLICY read_market_data ON market_data FOR SELECT USING (true);
CREATE POLICY read_ai_signals ON ai_signals FOR SELECT USING (true);
CREATE POLICY read_pair_strategies ON pair_strategies FOR SELECT USING (true);
CREATE POLICY read_trading_pairs ON trading_pairs FOR SELECT USING (true);
CREATE POLICY read_performance_analytics ON performance_analytics FOR SELECT USING (true);
CREATE POLICY admin_system ON system FOR ALL USING ((SELECT is_admin FROM users WHERE id = auth.uid()) = true);
CREATE POLICY admin_withdrawals ON withdrawals FOR ALL USING ((SELECT is_admin FROM users WHERE id = auth.uid()) = true);
CREATE POLICY admin_fees ON fees FOR ALL USING ((SELECT is_admin FROM users WHERE id = auth.uid()) = true);

-- Enable real-time
DROP PUBLICATION IF EXISTS supabase_realtime;
CREATE PUBLICATION supabase_realtime FOR TABLE trades, wallets, withdrawals, ai_signals;
ALTER TABLE trades REPLICA IDENTITY FULL;
ALTER TABLE wallets REPLICA IDENTITY FULL;
ALTER TABLE withdrawals REPLICA IDENTITY FULL;
ALTER TABLE ai_signals REPLICA IDENTITY FULL;

-- Insert initial data after all tables are created
DO $$
BEGIN
    -- Insert trading pairs
    INSERT INTO trading_pairs (symbol, base_asset, quote_asset, broker) VALUES
    ('BTCUSDT', 'BTC', 'USDT', 'binance'),
    ('ETHUSDT', 'ETH', 'USDT', 'binance'),
    ('EURUSD', 'EUR', 'USD', 'exness'),
    ('GBPUSD', 'GBP', 'USD', 'exness');

    -- Insert test user
    INSERT INTO users (id, email, is_admin) VALUES (uuid_generate_v4(), 'test@swift-ai-trader.com', false);

    -- Insert test wallet
    INSERT INTO wallets (user_id, broker, account_number, balance, currency) 
    SELECT id, 'binance', 'test_account', 1000.0, 'USDT' FROM users WHERE email='test@swift-ai-trader.com';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error during data insertion: %', SQLERRM;
END $$;