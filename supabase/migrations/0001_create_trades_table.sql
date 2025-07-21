-- =================================================================
-- Create Trades Table for Supabase
--
-- Purpose: This script creates the `trades` table required by the
--          AGI engine for logging and learning from trades.
--
-- How to run:
-- 1. Go to your Supabase project dashboard.
-- 2. Navigate to the SQL Editor.
-- 3. Paste the entire content of this script and click "Run".
-- =================================================================

-- Create the custom ENUM type for trade status if it doesn't exist.
-- This is necessary for the `status` column in the trades table.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trade_status') THEN
        CREATE TYPE public.trade_status AS ENUM ('open', 'closed', 'cancelled');
    END IF;
END$$;

-- Create the main `trades` table.
-- This table will store every trade executed by the engine.
-- Using `IF NOT EXISTS` makes the script safe to re-run.
CREATE TABLE IF NOT EXISTS public.trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    strategy VARCHAR(100) NOT NULL,
    side VARCHAR(10) NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    pnl DOUBLE PRECISION DEFAULT 0.0,
    status public.trade_status NOT NULL DEFAULT 'open',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc', now())
);

-- Add indexes for faster querying of trades by user or symbol.
CREATE INDEX IF NOT EXISTS idx_trades_user_id ON public.trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON public.trades(symbol);

-- Add comments to the table and columns for clarity in the Supabase UI.
COMMENT ON TABLE public.trades IS 'Stores all executed trades from the trading engine.';
COMMENT ON COLUMN public.trades.id IS 'Unique identifier for the trade (UUID).';
COMMENT ON COLUMN public.trades.user_id IS 'Identifier for the user associated with this trade.';
COMMENT ON COLUMN public.trades.symbol IS 'The trading symbol, e.g., XAUUSDm.';
COMMENT ON COLUMN public.trades.strategy IS 'The name of the strategy that generated the signal.';
COMMENT ON COLUMN public.trades.side IS 'The trade side: buy or sell.';
COMMENT ON COLUMN public.trades.volume IS 'The volume or lot size of the trade.';
COMMENT ON COLUMN public.trades.price IS 'The execution price of the trade.';
COMMENT ON COLUMN public.trades.pnl IS 'The final profit or loss of the trade when it is closed.';
COMMENT ON COLUMN public.trades.status IS 'The current status of the trade: open, closed, or cancelled.';
COMMENT ON COLUMN public.trades.timestamp IS 'The UTC timestamp when the trade was executed.'; 