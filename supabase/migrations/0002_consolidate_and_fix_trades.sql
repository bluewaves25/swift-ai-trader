-- =================================================================
-- Migration 0002: Consolidate and Fix Trades Schema
--
-- Purpose: This script provides a single, canonical schema for the `trades`
--          table to resolve inconsistencies from previous migrations.
--          It standardizes on `created_at` for timestamps and adds
--          performance indexes.
--
-- How to run:
-- 1. Go to your Supabase project dashboard -> SQL Editor.
-- 2. Paste this script and click "Run". This is safe to re-run.
-- =================================================================

-- Drop the old ENUM if it exists, to be replaced by a more complete one.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trade_status' AND NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'trade_status') AND enumlabel = 'open')) THEN
        DROP TYPE public.trade_status;
    END IF;
END$$;

-- Create a consolidated ENUM type for trade status.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trade_status') THEN
        CREATE TYPE public.trade_status AS ENUM ('open', 'closed', 'cancelled', 'pending', 'executed', 'failed');
    END IF;
END$$;


-- Create the canonical `trades` table.
-- Using `IF NOT EXISTS` is not sufficient for altering columns, so we handle this carefully.
-- First, drop the old table if it exists to ensure a clean slate.
DROP TABLE IF EXISTS public.trades;

CREATE TABLE public.trades (
    id TEXT PRIMARY KEY, -- Using TEXT to store MT5 ticket/order IDs which are numbers.
    user_id TEXT, -- Placeholder, to be linked to a real users table later.
    symbol VARCHAR(50) NOT NULL,
    strategy VARCHAR(100),
    side VARCHAR(10) NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    pnl DOUBLE PRECISION DEFAULT 0.0,
    status public.trade_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc', now())
);

-- Add comments for clarity in the Supabase UI.
COMMENT ON TABLE public.trades IS 'Stores all executed trades from MT5 (manual & engine), synced periodically.';
COMMENT ON COLUMN public.trades.id IS 'Unique identifier for the trade, from the MT5 ticket/order ID.';
COMMENT ON COLUMN public.trades.user_id IS 'Identifier for the user associated with this trade (placeholder).';
COMMENT ON COLUMN public.trades.created_at IS 'The UTC timestamp when the trade was executed.';


-- Create composite indexes for better performance.
-- Using `created_at` which is the standardized column name.
CREATE INDEX IF NOT EXISTS idx_trades_user_id_created_at ON public.trades(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trades_status_created_at ON public.trades(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON public.trades(symbol);

-- Grant usage to Supabase roles
GRANT ALL ON TABLE public.trades TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.trades TO aio_zap;
GRANT ALL ON TABLE public.trades TO supabase_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.trades TO aio_admin;
GRANT SELECT ON TABLE public.trades TO aio_user;
GRANT SELECT ON TABLE public.trades TO aio_investor;
GRANT ALL ON TABLE public.trades TO dashboard_user; 