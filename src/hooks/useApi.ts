
import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';
import { toast } from 'sonner';

export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = [],
  options: {
    immediate?: boolean;
    onSuccess?: (data: T) => void;
    onError?: (error: any) => void;
  } = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { immediate = true, onSuccess, onError } = options;

  const execute = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall();
      setData(result);
      onSuccess?.(result);
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'An error occurred';
      setError(errorMessage);
      onError?.(err);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, dependencies);

  return {
    data,
    loading,
    error,
    execute,
    refetch: execute
  };
}

// Specific hooks for common operations
export function useBalance(broker: string, account: string, params?: any) {
  return useApi(
    () => apiService.getBalance(broker, account, params),
    [broker, account, params],
    { immediate: !!broker && !!account }
  );
}

export function useMarketData(symbol: string) {
  return useApi(
    () => apiService.getMarketData(symbol),
    [symbol],
    { immediate: !!symbol }
  );
}

export function usePortfolioStats(userId: string) {
  return useApi(
    () => apiService.getPortfolioStats(userId),
    [userId],
    { immediate: !!userId }
  );
}

export function useAISignals(symbol?: string) {
  return useApi(
    () => apiService.getAISignals(symbol),
    [symbol]
  );
}
