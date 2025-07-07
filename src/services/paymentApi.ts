
import { supabase } from "@/integrations/supabase/client";
import { apiService } from "./api";

export interface PaymentMethod {
  id: string;
  name: string;
  icon: string;
  type: 'mobile_money' | 'bank' | 'card' | 'crypto';
}

export interface DepositRequest {
  amount: number;
  currency: string;
  paymentMethod: PaymentMethod;
  userDetails: {
    fullName: string;
    phoneNumber: string;
    email: string;
    dateOfBirth: string;
  };
}

export interface WithdrawalRequest {
  amount: number;
  currency: string;
  userDetails: {
    fullName: string;
    phoneNumber: string;
    email: string;
    dateOfBirth: string;
  };
}

export const paymentMethods: PaymentMethod[] = [
  { id: 'momo', name: 'Mobile Money', icon: '📱', type: 'mobile_money' },
  { id: 'bank', name: 'Bank Transfer', icon: '🏦', type: 'bank' },
  { id: 'card', name: 'Credit/Debit Card', icon: '💳', type: 'card' },
  { id: 'btc', name: 'Bitcoin', icon: '₿', type: 'crypto' },
  { id: 'eth', name: 'Ethereum', icon: 'Ξ', type: 'crypto' },
  { id: 'usdt', name: 'USDT', icon: '₮', type: 'crypto' },
];

export const paymentApi = {
  async processDeposit(request: DepositRequest) {
    try {
      const { data: user } = await supabase.auth.getUser();
      if (!user.user) throw new Error('User not authenticated');

      // Create transaction record
      const { data: transaction, error: transactionError } = await supabase
        .from('transactions')
        .insert({
          user_id: user.user.id,
          type: 'deposit',
          amount: request.amount,
          currency: request.currency,
          payment_method: request.paymentMethod.id,
          status: 'pending',
          description: `Deposit via ${request.paymentMethod.name} - $${request.amount}`
        })
        .select()
        .single();

      if (transactionError) throw transactionError;

      // Create transaction steps
      await supabase.rpc('create_transaction_steps', {
        p_transaction_id: transaction.id,
        p_transaction_type: 'deposit'
      });

      // Call backend to process payment
      const response = await fetch('/api/wallet/deposit/exness/default', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          currency: request.currency,
          amount: request.amount,
          payment_method: request.paymentMethod.id,
          user_details: request.userDetails
        })
      });

      if (!response.ok) throw new Error('Payment processing failed');

      return { transaction, success: true };
    } catch (error) {
      console.error('Deposit processing error:', error);
      throw error;
    }
  },

  async processWithdrawal(request: WithdrawalRequest) {
    try {
      const { data: user } = await supabase.auth.getUser();
      if (!user.user) throw new Error('User not authenticated');

      // Create transaction record
      const { data: transaction, error: transactionError } = await supabase
        .from('transactions')
        .insert({
          user_id: user.user.id,
          type: 'withdrawal',
          amount: request.amount,
          currency: request.currency,
          status: 'pending',
          description: `Withdrawal request - $${request.amount}`
        })
        .select()
        .single();

      if (transactionError) throw transactionError;

      // Create transaction steps
      await supabase.rpc('create_transaction_steps', {
        p_transaction_id: transaction.id,
        p_transaction_type: 'withdrawal'
      });

      // Call backend to process withdrawal
      const response = await fetch('/api/wallet/withdraw/exness/default', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          currency: request.currency,
          amount: request.amount,
          address: 'user_withdrawal_address',
          user_details: request.userDetails
        })
      });

      if (!response.ok) throw new Error('Withdrawal processing failed');

      return { transaction, success: true };
    } catch (error) {
      console.error('Withdrawal processing error:', error);
      throw error;
    }
  },

  async getTransactions() {
    try {
      const { data: user } = await supabase.auth.getUser();
      if (!user.user) throw new Error('User not authenticated');

      const { data, error } = await supabase
        .from('transactions')
        .select(`
          *,
          transaction_steps (*)
        `)
        .eq('user_id', user.user.id)
        .order('created_at', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error fetching transactions:', error);
      throw error;
    }
  },

  async getBonuses() {
    try {
      const { data: user } = await supabase.auth.getUser();
      if (!user.user) throw new Error('User not authenticated');

      const { data, error } = await supabase
        .from('bonuses')
        .select('*')
        .eq('user_id', user.user.id)
        .order('created_at', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error fetching bonuses:', error);
      throw error;
    }
  }
};
