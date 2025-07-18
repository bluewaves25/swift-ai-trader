
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
  getBalance: (userId: string) => api.get(`/api/balance/${userId}`),
  updateBalance: (userId: string, balance: number) => api.post(`/api/balance/${userId}`, { balance }),
  
  // Portfolio operations
  getPortfolio: () => api.get('/api/portfolio'),
  getPortfolioPerformance: () => api.get('/api/portfolio/performance'),
  
  // Trading operations
  getLiveSignals: () => api.get('/api/signals/live'),
  getTradeHistory: () => api.get('/api/trades/history'),
  
  // Performance data
  getPerformanceData: () => api.get('/api/performance'),
  
  // Engine operations
  getEngineStatus: () => api.get('/api/engine/status'),
  
  // Strategies
  getStrategies: () => api.get('/api/strategies'),
  
  // Transactions
  getTransactions: () => api.get('/api/transactions'),
  
  // Owner operations
  getOwnerStats: () => api.get('/api/owner/stats'),
  getOwnerSettings: () => api.get('/api/owner/settings'),
  saveOwnerSettings: (settings: any) => api.post('/api/owner/settings', settings),
  
  // Journal operations
  getJournalEntries: () => api.get('/api/journal'),
  
  // Health check
  healthCheck: () => api.get('/api/health'),
};

export default apiService;
