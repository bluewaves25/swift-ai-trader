// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Engine endpoints
  ENGINE_STATUS: `${API_BASE_URL}/api/v1/engine/status`,
  ENGINE_START: `${API_BASE_URL}/api/v1/engine/start`,
  ENGINE_STOP: `${API_BASE_URL}/api/v1/engine/stop`,
  ENGINE_EMERGENCY_STOP: `${API_BASE_URL}/api/v1/engine/emergency-stop`,
  
  // Engine feed endpoints
  ENGINE_FEED: `${API_BASE_URL}/api/v1/engine-feed`,
  
  // Portfolio endpoints
  PORTFOLIO: `${API_BASE_URL}/api/v1/portfolio`,
  PORTFOLIO_HISTORY: `${API_BASE_URL}/api/v1/portfolio/history`,
  
  // Trading endpoints
  TRADE_HISTORY: `${API_BASE_URL}/api/v1/trade/history`,
  LIVE_SIGNALS: `${API_BASE_URL}/api/v1/signals/live`,
  
  // Performance endpoints
  PERFORMANCE_ANALYTICS: `${API_BASE_URL}/api/v1/analytics/performance`,
  PERFORMANCE_FEES: `${API_BASE_URL}/api/v1/fees/performance`,
  
  // User management endpoints
  USERS: `${API_BASE_URL}/api/v1/admin/users`,
  USER_ROLES: `${API_BASE_URL}/api/v1/admin/users/roles`,
  
  // Strategies endpoints
  STRATEGIES: `${API_BASE_URL}/api/v1/strategies`,
  STRATEGY_VALIDATE: `${API_BASE_URL}/api/v1/strategies/validate`,
  
  // Billing endpoints
  BILLING_PLANS: `${API_BASE_URL}/api/v1/billing/plans`,
  BILLING_INITIALIZE: `${API_BASE_URL}/api/v1/billing/initialize`,
  BILLING_VERIFY: `${API_BASE_URL}/api/v1/billing/verify`,
  
  // Support endpoints
  SUPPORT_TICKETS: `${API_BASE_URL}/api/v1/support/tickets`,
  SUPPORT_CHAT: `${API_BASE_URL}/api/v1/support/chat`,
  
  // Owner dashboard endpoints
  OWNER_DASHBOARD_STATS: `${API_BASE_URL}/api/v1/owner/dashboard/stats`,
  OWNER_DASHBOARD_AUM: `${API_BASE_URL}/api/v1/owner/dashboard/aum`,
};

export const API_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// Helper function to make API calls
export const apiCall = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<any> => {
  const config = {
    ...API_CONFIG.headers,
    ...options.headers,
  };

  try {
    const response = await fetch(endpoint, {
      ...options,
      headers: config,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
}; 