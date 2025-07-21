
import axios from 'axios';
import { supabase } from '@/integrations/supabase/client';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
});

// Add auth interceptor
api.interceptors.request.use(
  async (config) => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Define API response types
export interface Portfolio {
  id: string;
  user_id: string;
  total_balance: number;
  available_balance: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_trades?: number;
  winning_trades?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Performance {
  // Define as needed
  [key: string]: any;
}

export interface Trade {
  timestamp: string | number | Date;
  id: string;
  signal_id?: string;
  pair_id?: string;
  trade_type?: 'buy' | 'sell';
  amount?: number;
  entry_price?: number;
  exit_price?: number;
  stop_loss?: number;
  take_profit?: number;
  status?: string;
  profit_loss?: number;
  execution_time?: string;
  created_at?: string;
  closed_at?: string;
  // Owner component fields:
  profit?: number;
  symbol?: string;
  broker?: 'binance' | 'exness';
  type?: 'buy' | 'sell';
  volume?: number;
  price?: number;
  openPrice?: number;
  closePrice?: number;
  commission?: number;
  openTime?: string;
  closeTime?: string;
  strategy?: string;
  userId?: string;
  category?: 'crypto' | 'forex' | 'commodities' | 'indices';
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  role: string;
  created_at: string;
}

export const apiService = {
  // Balance operations
  getBalance: (userId: string) => api.get<{ balance: number }>(`/api/v1/investor/balance/${userId}`),
  updateBalance: (userId: string, balance: number) => api.post<{ success: boolean }>(`/api/v1/investor/balance/${userId}`, { balance }),
  
  // Portfolio operations
  getPortfolio: () => api.get<Portfolio>('/api/v1/portfolio'),
  getPortfolioPerformance: () => api.get<Performance>('/api/v1/portfolio/performance'),
  
  // Trading operations
  getLiveSignals: () => api.get<{ signals: any[] }>('/api/v1/engine-feed'),
  getTradeHistory: () => api.get<{ trades: Trade[] }>('/api/v1/investor/trades/history'),
  
  // Performance data
  getPerformanceData: () => api.get<Performance>('/api/v1/investor/performance'),
  
  // Engine operations
  getEngineStatus: () => api.get<any>('/api/v1/engine-status'),
  
  // Strategies
  getStrategies: () => api.get<any[]>('/api/v1/owner/strategies'),
  addStrategy: (strategyName: string) => api.post<{ success: boolean }>( '/api/v1/strategies/add', null, { params: { strategy_name: strategyName } }),
  removeStrategy: (strategyName: string) => api.post<{ success: boolean }>( '/api/v1/strategies/remove', null, { params: { strategy_name: strategyName } }),
  updateStrategy: (strategyName: string, config: any) => api.post<{ success: boolean }>( '/api/v1/strategies/update', { strategy_name: strategyName, config }),
  validateStrategy: (strategyName: string) => api.get<any>(`/api/v1/strategies/validate/${strategyName}`),
  backtestStrategy: (strategyName: string, data: any[]) => api.post<any>( '/api/v1/strategies/backtest', { strategy_name: strategyName, data }),
  getExplainabilityLog: () => api.get<any[]>('/api/v1/engine/explainability'),
  
  // Transactions
  getTransactions: () => api.get<any[]>('/api/v1/investor/transactions'),
  
  // Owner operations
  getOwnerStats: () => api.get<any>('/api/v1/owner/stats'),
  getOwnerSettings: () => api.get<any>('/api/v1/owner/settings'),
  saveOwnerSettings: (settings: any) => api.post<{ success: boolean }>('/api/v1/owner/settings', settings),
  // Risk management
  getRiskSettings: () => api.get<any>('/api/v1/owner/risk-settings'),
  saveRiskSettings: (settings: any) => api.post<{ success: boolean }>('/api/v1/owner/risk-settings', settings),
  // Billing
  getBillingPlans: () => api.get<any>('/api/v1/billing/plans'),
  initializeBilling: (payload: any) => api.post<any>('/api/v1/billing/initialize', payload),
  // Performance fees
  getPerformanceFees: (userId: string) => api.get<any>(`/api/v1/fees/performance?user_id=${userId}`),
  
  // Journal operations
  getJournalEntries: () => api.get<any[]>('/api/v1/investor/journal'),
  
  // Health check
  healthCheck: () => api.get('/api/v1/health'),
};

export default apiService;
