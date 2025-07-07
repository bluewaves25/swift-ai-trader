
-- Update portfolios table to include balance fields
ALTER TABLE public.portfolios ADD COLUMN IF NOT EXISTS total_balance DECIMAL DEFAULT 0;
ALTER TABLE public.portfolios ADD COLUMN IF NOT EXISTS available_balance DECIMAL DEFAULT 0;
ALTER TABLE public.portfolios ADD COLUMN IF NOT EXISTS invested_amount DECIMAL DEFAULT 0;
ALTER TABLE public.portfolios ADD COLUMN IF NOT EXISTS realized_pnl DECIMAL DEFAULT 0;
ALTER TABLE public.portfolios ADD COLUMN IF NOT EXISTS unrealized_pnl DECIMAL DEFAULT 0;

-- Update profiles table to include required user information
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS phone_number TEXT;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS full_name TEXT;

-- Update transactions table for better tracking
ALTER TABLE public.transactions ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending';
ALTER TABLE public.transactions ADD COLUMN IF NOT EXISTS payment_method TEXT;
ALTER TABLE public.transactions ADD COLUMN IF NOT EXISTS provider_transaction_id TEXT;
ALTER TABLE public.transactions ADD COLUMN IF NOT EXISTS failure_reason TEXT;
ALTER TABLE public.transactions ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE public.transactions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE public.transactions ADD COLUMN IF NOT EXISTS method TEXT;
ALTER TABLE public.transactions ADD COLUMN IF NOT EXISTS description TEXT;

-- Create transaction_steps table to track transaction process
CREATE TABLE IF NOT EXISTS public.transaction_steps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  transaction_id UUID REFERENCES public.transactions(id) ON DELETE CASCADE,
  step_name TEXT NOT NULL,
  status TEXT DEFAULT 'pending', -- pending, completed, failed
  completed_at TIMESTAMPTZ,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS on transaction_steps
ALTER TABLE public.transaction_steps ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view their own transaction steps
CREATE POLICY "user_transaction_steps" ON public.transaction_steps
FOR ALL
USING (
  EXISTS (
    SELECT 1 FROM public.transactions 
    WHERE transactions.id = transaction_steps.transaction_id 
    AND transactions.user_id = auth.uid()
  )
);

-- Create bonuses table
CREATE TABLE IF NOT EXISTS public.bonuses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  amount DECIMAL NOT NULL,
  bonus_type TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS on bonuses
ALTER TABLE public.bonuses ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view their own bonuses
CREATE POLICY "user_bonuses" ON public.bonuses
FOR ALL
USING (auth.uid() = user_id);

-- Update users table to include role for admin identification
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'investor';

-- Create function to update portfolio balance
CREATE OR REPLACE FUNCTION update_portfolio_balance(
  p_user_id UUID,
  p_amount DECIMAL,
  p_transaction_type TEXT
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  IF p_transaction_type = 'deposit' THEN
    INSERT INTO public.portfolios (user_id, total_balance, available_balance)
    VALUES (p_user_id, p_amount, p_amount)
    ON CONFLICT (user_id) DO UPDATE SET
      total_balance = portfolios.total_balance + p_amount,
      available_balance = portfolios.available_balance + p_amount,
      updated_at = now();
  ELSIF p_transaction_type = 'withdrawal' THEN
    UPDATE public.portfolios 
    SET 
      total_balance = total_balance - p_amount,
      available_balance = available_balance - p_amount,
      updated_at = now()
    WHERE user_id = p_user_id;
  END IF;
END;
$$;

-- Create function to create transaction steps
CREATE OR REPLACE FUNCTION create_transaction_steps(
  p_transaction_id UUID,
  p_transaction_type TEXT
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  IF p_transaction_type = 'deposit' THEN
    INSERT INTO public.transaction_steps (transaction_id, step_name) VALUES
    (p_transaction_id, 'charged_by_provider'),
    (p_transaction_id, 'received_in_wallet'),
    (p_transaction_id, 'deposited_to_account');
  ELSIF p_transaction_type = 'withdrawal' THEN
    INSERT INTO public.transaction_steps (transaction_id, step_name) VALUES
    (p_transaction_id, 'received_request'),
    (p_transaction_id, 'sent_to_provider'),
    (p_transaction_id, 'withdrawn_to_account');
  END IF;
END;
$$;
