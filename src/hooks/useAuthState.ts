import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '@/integrations/supabase/client';
import { User } from '@supabase/supabase-js';
import { toast } from 'sonner';

export function useAuthState() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSigningOut, setIsSigningOut] = useState(false);
  const navigate = useNavigate();

  // Clear all auth-related storage
  const clearAuthStorage = useCallback(() => {
    console.log('[AuthState] Clearing auth storage');
    
    // Clear Supabase storage
    Object.keys(localStorage).forEach((key) => {
      if (key.startsWith('sb-') || key.startsWith('supabase')) {
        localStorage.removeItem(key);
      }
    });
    
    // Clear other auth storage
    localStorage.removeItem("token");
    sessionStorage.clear();
    
    // Clear any cookies that might be set
    document.cookie.split(";").forEach((c) => {
      document.cookie = c
        .replace(/^ +/, "")
        .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
  }, []);

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        if (error) throw error;
        
        console.log('[AuthState] Initial session:', session?.user?.id);
        setUser(session?.user ?? null);
      } catch (error) {
        console.error('[AuthState] getSession error:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        console.log('[AuthState] Auth event:', event, session?.user?.id);
        
        switch (event) {
          case 'SIGNED_OUT':
            console.log('[AuthState] User signed out, clearing state');
            setUser(null);
            setLoading(false);
            clearAuthStorage();
            break;
            
          case 'SIGNED_IN':
            console.log('[AuthState] User signed in:', session?.user?.id);
            setUser(session?.user ?? null);
            setLoading(false);
            break;
            
          case 'TOKEN_REFRESHED':
            console.log('[AuthState] Token refreshed');
            setUser(session?.user ?? null);
            break;
            
          default:
            setUser(session?.user ?? null);
            setLoading(false);
        }
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, [clearAuthStorage]);

  // Clean sign out function
  const signOut = useCallback(async () => {
    console.log('[AuthState] Sign out initiated');
    setIsSigningOut(true);
    setLoading(true);
    
    try {
      // Clear storage first
      clearAuthStorage();
      
      // Sign out from Supabase
      const { error } = await supabase.auth.signOut();
      console.log('[AuthState] signOut result:', error);
      
      if (error) throw error;
      
      // Clear user state
      setUser(null);
      
      // Navigate to auth page
      navigate('/auth', { replace: true });
      
      toast.success('Successfully logged out!');
      
      // Force clean reload to clear any cached state
      setTimeout(() => {
        console.log('[AuthState] Performing clean reload after sign out');
        window.location.href = '/auth';
      }, 500);
      
    } catch (error: any) {
      console.error('[AuthState] Sign out error:', error);
      toast.error('Failed to sign out');
      
      // Even if there's an error, clear the user state and redirect
      setUser(null);
      navigate('/auth', { replace: true });
    } finally {
      setLoading(false);
      setIsSigningOut(false);
    }
  }, [navigate, clearAuthStorage]);

  return {
    user,
    loading,
    isSigningOut,
    signOut,
    clearAuthStorage
  };
} 