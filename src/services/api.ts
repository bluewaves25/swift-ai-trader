
import axios, { AxiosResponse } from 'axios';
import { supabase } from '@/integrations/supabase/client';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const apiService = {
  // User management
  getBalance: (userId: string) => api.get(`/api/users/${userId}/balance`),
  updateBalance: (userId: string, balance: any) => api.put(`/api/users/${userId}/balance`, { balance }),
  
  // Portfolio
  getPortfolio: () => api.get('/api/portfolio'),
  getPortfolioPerformance: () => api.get('/api/portfolio/performance'),
  
  // Trading
  getTrades: () => api.get('/api/trades'),
  createTrade: (trade: any) => api.post('/api/trades', trade),
  closeTrade: (tradeId: string) => api.post(`/api/trades/${tradeId}/close`),
  
  // Signals
  getLiveSignals: () => api.get('/api/signals/live'),
  getSignalHistory: () => api.get('/api/signals/history'),
  
  // Engine
  getEngineStatus: () => api.get('/api/engine/status'),
  startEngine: () => api.post('/api/engine/start'),
  stopEngine: () => api.post('/api/engine/stop'),
  getEngineStats: () => api.get('/api/engine/stats'),
  
  // Strategies
  getStrategies: () => api.get('/api/strategies'),
  createStrategy: (strategy: any) => api.post('/api/strategies', strategy),
  updateStrategy: (id: string, strategy: any) => api.put(`/api/strategies/${id}`, strategy),
  deleteStrategy: (id: string) => api.delete(`/api/strategies/${id}`),
  
  // Risk Management
  getRiskParams: () => api.get('/api/risk/params'),
  updateRiskParams: (params: any) => api.put('/api/risk/params', params),
  
  // Analytics
  getPerformanceAnalytics: () => api.get('/api/analytics/performance'),
  getAumHistory: () => api.get('/api/analytics/aum-history'),
  
  // Owner specific
  getUserCount: () => api.get('/api/admin/users/count'),
  getOwnerDashboard: () => api.get('/api/admin/dashboard'),
  getOwnerSettings: () => api.get('/api/admin/settings'),
  saveOwnerSettings: (settings: any) => api.put('/api/admin/settings', settings),
  
  // Payments
  getTransactions: () => api.get('/api/payments/transactions'),
  processPayment: (payment: any) => api.post('/api/payments/process', payment),
  
  // Health check
  healthCheck: () => api.get('/api/health'),
};

export default api;
