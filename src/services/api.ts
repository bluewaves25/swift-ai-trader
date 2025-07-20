
import axios, { AxiosRequestConfig } from 'axios';
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

export const apiService = {
  // Balance operations
  getBalance: (userId: string) => api.get(`/api/v1/investor/balance/${userId}`),
  updateBalance: (userId: string, balance: number) => api.post(`/api/v1/investor/balance/${userId}`, { balance }),
  
  // Portfolio operations
  getPortfolio: () => api.get('/api/v1/portfolio'),
  getPortfolioPerformance: () => api.get('/api/v1/portfolio/performance'),
  
  // Trading operations
  getLiveSignals: () => api.get('/api/v1/engine-feed/signals/live'),
  getTradeHistory: () => api.get('/api/v1/investor/trades/history'),
  
  // Performance data
  getPerformanceData: () => api.get('/api/v1/investor/performance'),
  
  // Engine operations
  getEngineStatus: () => api.get('/api/v1/engine-status'),
  
  // Strategies
  getStrategies: () => api.get('/api/v1/owner/strategies'),
  
  // Transactions
  getTransactions: () => api.get('/api/v1/investor/transactions'),
  
  // Owner operations
  getOwnerStats: () => api.get('/api/v1/owner/stats'),
  getOwnerSettings: () => api.get('/api/v1/owner/settings'),
  saveOwnerSettings: (settings: any) => api.post('/api/v1/owner/settings', settings),
  
  // Journal operations
  getJournalEntries: () => api.get('/api/v1/investor/journal'),
  
  // Health check
  healthCheck: () => api.get('/api/v1/health'),
};

export default apiService;
