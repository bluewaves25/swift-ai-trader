import { useContext, useEffect, useState } from 'react';
import { AuthContext } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  useEffect(() => {
    // Add session refresh logic
    const refreshInterval = setInterval(() => {
      supabase.auth.refreshSession();
    }, 9 * 60 * 1000); // every 9 minutes
    return () => clearInterval(refreshInterval);
  }, []);

  return context;
}
