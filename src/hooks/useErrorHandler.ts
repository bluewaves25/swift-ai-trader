
import { useCallback } from 'react';
import { toast } from 'sonner';

interface ErrorHandlerOptions {
  showToast?: boolean;
  logError?: boolean;
  fallback?: () => void;
}

export function useErrorHandler() {
  const handleError = useCallback((
    error: any, 
    options: ErrorHandlerOptions = {}
  ) => {
    const { 
      showToast = true, 
      logError = true, 
      fallback 
    } = options;

    // Log error for debugging
    if (logError) {
      console.error('Error occurred:', error);
    }

    // Get error message
    let message = 'An unexpected error occurred';
    if (error?.message) {
      message = error.message;
    } else if (error?.response?.data?.message) {
      message = error.response.data.message;
    } else if (typeof error === 'string') {
      message = error;
    }

    // Show toast notification
    if (showToast) {
      toast.error(message);
    }

    // Execute fallback function
    if (fallback) {
      fallback();
    }

    return message;
  }, []);

  const handleAsyncError = useCallback(async (
    asyncFn: () => Promise<any>,
    options: ErrorHandlerOptions = {}
  ) => {
    try {
      return await asyncFn();
    } catch (error) {
      handleError(error, options);
      throw error;
    }
  }, [handleError]);

  return { handleError, handleAsyncError };
}
