
import axios from 'axios';
import { supabase } from '@/integrations/supabase/client';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add auth interceptor
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  return config;
});

export const apiService = {
  // Balance operations
  getBalance: (userId: string) => api.get(`/balance/${userId}`),
  updateBalance: (userId: string, balance: number) => api.put(`/balance/${userId}`, { balance }),

  // Portfolio operations
  getPortfolio: () => api.get('/portfolio'),
  updatePortfolio: (data: any) => api.put('/portfolio', data),

  // Trading operations
  getTrades: () => api.get('/trades'),
  createTrade: (data: any) => api.post('/trades', data),
  getLiveSignals: () => api.get('/signals/live'),
  getAISignals: () => api.get('/signals/ai'),

  // Strategy operations
  getStrategies: () => api.get('/strategies'),
  createStrategy: (data: any) => api.post('/strategies', data),
  updateStrategy: (id: string, data: any) => api.put(`/strategies/${id}`, data),
  deleteStrategy: (id: string) => api.delete(`/strategies/${id}`),
  disableStrategy: (id: string) => api.put(`/strategies/${id}/disable`),
  retrainStrategy: (id: string) => api.post(`/strategies/${id}/retrain`),

  // Engine operations
  startEngine: () => api.post('/engine/start'),
  stopEngine: () => api.post('/engine/stop'),
  getEngineStatus: () => api.get('/engine/status'),
  getEngineMetrics: () => api.get('/engine/metrics'),

  // System operations
  getSystemHealth: () => api.get('/system/health'),
  getOverview: () => api.get('/system/overview'),
  getLogs: () => api.get('/system/logs'),
  getAumHistory: () => api.get('/system/aum-history'),

  // User operations
  getUsers: () => api.get('/users'),
  createUser: (data: any) => api.post('/users', data),
  updateUser: (id: string, data: any) => api.put(`/users/${id}`, data),
  deleteUser: (id: string) => api.delete(`/users/${id}`),

  // Analytics
  getPerformanceData: () => api.get('/analytics/performance'),
  getRiskMetrics: () => api.get('/analytics/risk'),

  // Market data
  getMarketData: () => api.get('/market/data'),

  // Transactions
  getTransactions: () => api.get('/transactions'),
  createTransaction: (data: any) => api.post('/transactions', data),

  // Health check
  healthCheck: () => api.get('/health'),
};
