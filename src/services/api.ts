
import axios from 'axios';

const API_BASE_URL = 'http://localhost:3000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('supabase-auth-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Trading operations
  async getBalance(broker: string, account: string, params?: any) {
    const response = await api.get(`/balance/${broker}/${account}`, { params });
    return response.data;
  },

  async executeTrade(broker: string, account: string, tradeData: any, params?: any) {
    const response = await api.post(`/trade/${broker}/${account}`, tradeData, { params });
    return response.data;
  },

  async deposit(broker: string, account: string, depositData: any, params?: any) {
    const response = await api.post(`/deposit/${broker}/${account}`, depositData, { params });
    return response.data;
  },

  async withdraw(broker: string, account: string, withdrawData: any, params?: any) {
    const response = await api.post(`/withdraw/${broker}/${account}`, withdrawData, { params });
    return response.data;
  },

  // Market data
  async getMarketData(symbol: string) {
    const response = await api.get(`/market-data/${symbol}`);
    return response.data;
  },

  async getHistoricalData(symbol: string, timeframe: string, limit?: number) {
    const response = await api.get(`/historical-data/${symbol}/${timeframe}`, {
      params: { limit }
    });
    return response.data;
  },

  // AI Signals
  async getSentiment(symbol: string) {
    const response = await api.get(`/sentiment/${symbol}`);
    return response.data;
  },

  async getAISignals(symbol?: string) {
    const response = await api.get('/ai-signals', {
      params: { symbol }
    });
    return response.data;
  },

  // Portfolio management
  async getPortfolioStats(userId: string) {
    const response = await api.get(`/portfolio/${userId}`);
    return response.data;
  },

  async updateRiskSettings(userId: string, settings: any) {
    const response = await api.put(`/risk-settings/${userId}`, settings);
    return response.data;
  },

  // Strategy management
  async getStrategies() {
    const response = await api.get('/strategies');
    return response.data;
  },

  async updateStrategy(strategyId: string, params: any) {
    const response = await api.put(`/strategies/${strategyId}`, params);
    return response.data;
  },

  // Trading engine control
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

  async closeAllPositions() {
    const response = await api.post('/engine/close-all');
    return response.data;
  },

  // Health check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }
};

export default apiService;
