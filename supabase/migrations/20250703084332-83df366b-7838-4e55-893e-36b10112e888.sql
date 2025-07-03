
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types for trading
CREATE TYPE trade_status AS ENUM ('pending', 'executed', 'cancelled', 'failed');
CREATE TYPE trade_type AS ENUM ('buy', 'sell');
CREATE TYPE signal_type AS ENUM ('buy', 'sell', 'hold');
CREATE TYPE market_condition AS ENUM ('trending_up', 'trending_down', 'ranging', 'volatile');
CREATE TYPE strategy_type AS ENUM ('breakout', 'mean_reversion', 'momentum', 'scalping', 'grid');
CREATE TYPE user_role AS ENUM ('owner', 'investor');

-- Users table for authentication and roles
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    role user_role NOT NULL DEFAULT 'investor',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trading pairs configuration
CREATE TABLE public.trading_pairs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol TEXT UNIQUE NOT NULL,
    base_currency TEXT NOT NULL,
    quote_currency TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    min_trade_amount DECIMAL(20,8) DEFAULT 0.001,
    max_trade_amount DECIMAL(20,8) DEFAULT 1000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market data for each pair
CREATE TABLE public.market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pair_id UUID REFERENCES trading_pairs(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    open_price DECIMAL(20,8) NOT NULL,
    high_price DECIMAL(20,8) NOT NULL,
    low_price DECIMAL(20,8) NOT NULL,
    close_price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    market_condition market_condition,
    volatility DECIMAL(10,6),
    rsi DECIMAL(5,2),
    macd DECIMAL(10,6),
    bollinger_upper DECIMAL(20,8),
    bollinger_lower DECIMAL(20,8),
    support_level DECIMAL(20,8),
    resistance_level DECIMAL(20,8)
);

-- AI strategies for each pair
CREATE TABLE public.pair_strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pair_id UUID REFERENCES trading_pairs(id) ON DELETE CASCADE,
    current_strategy strategy_type NOT NULL,
    confidence_score DECIMAL(5,4) DEFAULT 0.5,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    strategy_params JSONB DEFAULT '{}',
    performance_score DECIMAL(5,4) DEFAULT 0.5,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    UNIQUE(pair_id)
);

-- AI signals generated for each pair
CREATE TABLE public.ai_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pair_id UUID REFERENCES trading_pairs(id) ON DELETE CASCADE,
    signal signal_type NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    strategy_used strategy_type NOT NULL,
    entry_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    take_profit DECIMAL(20,8),
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed BOOLEAN DEFAULT false
);

-- Automated trades executed by the engine
CREATE TABLE public.trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id UUID REFERENCES ai_signals(id),
    pair_id UUID REFERENCES trading_pairs(id) ON DELETE CASCADE,
    trade_type trade_type NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    entry_price DECIMAL(20,8) NOT NULL,
    exit_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    take_profit DECIMAL(20,8),
    status trade_status DEFAULT 'pending',
    profit_loss DECIMAL(20,8) DEFAULT 0,
    execution_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE
);

-- Portfolio tracking for investors
CREATE TABLE public.portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    total_balance DECIMAL(20,8) DEFAULT 0,
    available_balance DECIMAL(20,8) DEFAULT 0,
    unrealized_pnl DECIMAL(20,8) DEFAULT 0,
    realized_pnl DECIMAL(20,8) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Risk management settings
CREATE TABLE public.risk_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    max_daily_loss DECIMAL(20,8) DEFAULT 100,
    max_position_size DECIMAL(5,4) DEFAULT 0.05,
    stop_loss_percentage DECIMAL(5,4) DEFAULT 0.02,
    take_profit_percentage DECIMAL(5,4) DEFAULT 0.04,
    max_open_positions INTEGER DEFAULT 5,
    risk_per_trade DECIMAL(5,4) DEFAULT 0.01,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Performance analytics
CREATE TABLE public.performance_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    total_profit DECIMAL(20,8) DEFAULT 0,
    total_volume DECIMAL(20,8) DEFAULT 0,
    sharpe_ratio DECIMAL(10,6),
    max_drawdown DECIMAL(5,4),
    win_rate DECIMAL(5,4),
    avg_profit_per_trade DECIMAL(20,8),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date)
);

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trading_pairs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pair_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.risk_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_analytics ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view their own data" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own data" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- RLS Policies for trading_pairs (owners can manage, investors can view)
CREATE POLICY "Anyone can view trading pairs" ON public.trading_pairs
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Only owners can manage trading pairs" ON public.trading_pairs
    FOR ALL TO authenticated USING (
        EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'owner')
    );

-- RLS Policies for market_data (read-only for all authenticated users)
CREATE POLICY "Authenticated users can view market data" ON public.market_data
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Only system can insert market data" ON public.market_data
    FOR INSERT TO authenticated WITH CHECK (
        EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'owner')
    );

-- RLS Policies for portfolios (users can only see their own)
CREATE POLICY "Users can view their own portfolio" ON public.portfolios
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can update their own portfolio" ON public.portfolios
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own portfolio" ON public.portfolios
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- RLS Policies for risk_settings (users can only manage their own)
CREATE POLICY "Users can manage their own risk settings" ON public.risk_settings
    FOR ALL USING (user_id = auth.uid());

-- RLS Policies for other tables (authenticated users can view, owners can manage)
CREATE POLICY "Authenticated users can view strategies" ON public.pair_strategies
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can view signals" ON public.ai_signals
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can view trades" ON public.trades
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can view analytics" ON public.performance_analytics
    FOR SELECT TO authenticated USING (true);

-- Insert some default trading pairs
INSERT INTO public.trading_pairs (symbol, base_currency, quote_currency) VALUES
    ('BTCUSDT', 'BTC', 'USDT'),
    ('ETHUSDT', 'ETH', 'USDT'),
    ('ADAUSDT', 'ADA', 'USDT'),
    ('DOTUSDT', 'DOT', 'USDT'),
    ('LINKUSDT', 'LINK', 'USDT'),
    ('BNBUSDT', 'BNB', 'USDT'),
    ('SOLUSDT', 'SOL', 'USDT'),
    ('MATICUSDT', 'MATIC', 'USDT'),
    ('AVAXUSDT', 'AVAX', 'USDT'),
    ('ATOMUSDT', 'ATOM', 'USDT');

-- Enable realtime for live updates
ALTER PUBLICATION supabase_realtime ADD TABLE public.market_data;
ALTER PUBLICATION supabase_realtime ADD TABLE public.ai_signals;
ALTER PUBLICATION supabase_realtime ADD TABLE public.trades;
ALTER PUBLICATION supabase_realtime ADD TABLE public.portfolios;
ALTER PUBLICATION supabase_realtime ADD TABLE public.performance_analytics;

-- Create indexes for better performance
CREATE INDEX idx_market_data_pair_timestamp ON public.market_data(pair_id, timestamp DESC);
CREATE INDEX idx_ai_signals_pair_created ON public.ai_signals(pair_id, created_at DESC);
CREATE INDEX idx_trades_pair_status ON public.trades(pair_id, status);
CREATE INDEX idx_trades_created_at ON public.trades(created_at DESC);
