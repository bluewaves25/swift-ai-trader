
import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';
import { toast } from 'sonner';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const executeRequest = async (requestFn: () => Promise<any>) => {
    setLoading(true);
    setError(null);
    try {
      const response = await requestFn();
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'An error occurred';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getBalance = async (userId: string) => {
    return executeRequest(() => apiService.getBalance(userId));
  };

  const updateBalance = async (userId: string, balance: number) => {
    return executeRequest(() => apiService.updateBalance(userId, balance));
  };

  const getPortfolio = async () => {
    return executeRequest(() => apiService.getPortfolio());
  };

  return {
    loading,
    error,
    getBalance,
    updateBalance,
    getPortfolio,
    executeRequest
  };
};
