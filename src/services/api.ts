
import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-production-domain.com/api' 
  : 'http://localhost:3000/api';

interface RequestConfig {
  startTime?: Date;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('supabase-auth-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    (config as any).requestStartTime = new Date();
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    const endTime = new Date();
    const startTime = (response.config as any).requestStartTime;
    const duration = startTime ? endTime.getTime() - startTime.getTime() : 0;
    console.log(`API Response: ${response.config.url} (${duration}ms)`);
    return response;
  },
  (error) => {
    const message = error.response?.data?.message || error.message || 'Network Error';
    console.error('API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      message,
      data: error.response?.data
    });
    
    if (error.response?.status === 401) {
      localStorage.removeItem('supabase-auth-token');
      window.location.href = '/auth';
    }
    
    return Promise.reject(error);
  }
);

export const apiService = {
  // Portfolio & Balance
  async getBalance(userId: string) {
    const response = await api.get(`/wallet/balance/exness/default`);
    return response.data;
  },

  async updateBalance(userId: string, balance: any) {
    const response = await api.post(`/wallet/update`, { user_id: userId, ...balance });
    return response.data;
  },

  // Trading Operations
  async executeTrade(symbol: string, tradeType: string, amount: number) {
    const response = await api.post('/trade/execute', {
      symbol,
      trade_type: tradeType,
      amount
    });
    return response.data;
  },

  async getTradeHistory(symbol?: string) {
    const params = symbol ? { symbol } : {};
    const response = await api.get('/trade/history', { params });
    return response.data;
  },

  // AI Strategies & Signals
  async getAISignals(symbol?: string) {
    const params = symbol ? { symbol } : {};
    const response = await api.get('/strategies/signals', { params });
    return response.data;
  },

  async getStrategyPerformance(symbol?: string) {
    const params = symbol ? { symbol } : {};
    const response = await api.get('/strategies/performance', { params });
    return response.data;
  },

  async updateRiskParams(params: any) {
    const response = await api.post('/strategies/risk', params);
    return response.data;
  },

  // Trading Engine Control
  async startTradingEngine() {
    const response = await api.post('/engine/start');
    return response.data;
  },

  async stopTradingEngine() {
    const response = await api.post('/engine/stop');
    return response.data;
  },

  async emergencyStop() {
    const response = await api.post('/engine/emergency-stop');
    return response.data;
  },

  // Market Data
  async getMarketData(symbol: string) {
    const response = await api.get(`/market-data/${symbol}`);
    return response.data;
  },

  async getHistoricalData(symbol: string, timeframe: string = '1h', limit: number = 100) {
    const response = await api.get(`/historical-data/${symbol}/${timeframe}`, {
      params: { limit }
    });
    return response.data;
  },

  // Payments & Transactions
  async processDeposit(data: any) {
    const response = await api.post('/wallet/deposit/exness/default', data);
    return response.data;
  },

  async processWithdrawal(data: any) {
    const response = await api.post('/wallet/withdraw/exness/default', data);
    return response.data;
  },

  // System Health
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }
};

export default apiService;
