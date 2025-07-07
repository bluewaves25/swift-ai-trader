
import axios from 'axios';

const API_BASE_URL = 'http://localhost:3000';

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
  async getBalance(userId: string) {
    const response = await api.get(`/api/wallet/balance?user_id=${userId}`);
    return response.data;
  },

  async updateBalance(userId: string, balance: any) {
    const response = await api.post(`/api/wallet/update`, { user_id: userId, ...balance });
    return response.data;
  },

  async executeTrade(symbol: string, tradeType: string, amount: number) {
    const response = await api.post('/api/trade/execute', {
      symbol,
      trade_type: tradeType,
      amount
    });
    return response.data;
  },

  async getTradeHistory(symbol?: string) {
    const params = symbol ? { symbol } : {};
    const response = await api.get('/api/trade/history', { params });
    return response.data;
  },

  async getAISignals(symbol?: string) {
    const params = symbol ? { symbol } : {};
    const response = await api.get('/api/strategies/signals', { params });
    return response.data;
  },

  async getStrategyPerformance(symbol?: string) {
    const params = symbol ? { symbol } : {};
    const response = await api.get('/api/strategies/performance', { params });
    return response.data;
  },

  async updateRiskParams(params: any) {
    const response = await api.post('/api/strategies/risk', params);
    return response.data;
  },

  async startTradingEngine() {
    const response = await api.post('/api/engine/start');
    return response.data;
  },

  async stopTradingEngine() {
    const response = await api.post('/api/engine/stop');
    return response.data;
  },

  async emergencyStop() {
    const response = await api.post('/api/engine/emergency-stop');
    return response.data;
  },

  async getMarketData(symbol: string) {
    const response = await api.get(`/api/market-data/${symbol}`);
    return response.data;
  },

  async getHistoricalData(symbol: string, timeframe: string = '1h', limit: number = 100) {
    const response = await api.get(`/api/historical-data/${symbol}/${timeframe}`, {
      params: { limit }
    });
    return response.data;
  },

  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }
};

export default apiService;
