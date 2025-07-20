
import React, { createContext, useContext, useEffect } from 'react';
import { User } from '@supabase/supabase-js';
import { supabase } from '@/integrations/supabase/client';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useAuthState } from '@/hooks/useAuthState';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, userData?: any) => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { user, loading, isSigningOut, signOut: authSignOut, clearAuthStorage } = useAuthState();
  const navigate = useNavigate();

  // Handle navigation after successful sign in
  useEffect(() => {
    if (!loading && user && !isSigningOut) {
      const currentPath = window.location.pathname;
      const protectedRoutes = ['/investor-dashboard', '/owner-dashboard'];
      const isOnProtectedRoute = protectedRoutes.some(route => currentPath.startsWith(route));
      
      // Only navigate if we're on a protected route
      if (isOnProtectedRoute) {
        (async () => {
          try {
            // Check if user exists in our users table
            const { data: existingUser, error: fetchError } = await supabase
              .from('users')
              .select('role')
              .eq('id', user.id)
              .single();
            
            if (fetchError && fetchError.code === 'PGRST116') {
              // User doesn't exist, create them
              const { error: createError } = await supabase
                .from('users')
                .insert({
                  id: user.id,
                  email: user.email!,
                  role: 'investor'
                });
              if (createError) {
                console.error('Error creating user:', createError);
              }
              navigate('/investor-dashboard');
              toast.success('Account created successfully!');
            } else if (fetchError) {
              console.error('Error fetching user role:', fetchError);
              navigate('/investor-dashboard');
              toast.success('Successfully logged in!');
            } else if (existingUser?.role === 'owner') {
              navigate('/owner-dashboard');
              toast.success('Successfully logged in!');
            } else {
              navigate('/investor-dashboard');
              toast.success('Successfully logged in!');
            }
          } catch (error) {
            console.error('Error in auth state change:', error);
            navigate('/investor-dashboard');
            toast.success('Successfully logged in!');
          }
        })();
      }
    }
  }, [user, loading, isSigningOut, navigate]);

  // TEMP: Log Supabase env keys (remove in production)
  console.log('[Supabase] VITE_SUPABASE_URL:', import.meta.env.VITE_SUPABASE_URL);
  console.log('[Supabase] VITE_SUPABASE_ANON_KEY:', import.meta.env.VITE_SUPABASE_ANON_KEY);

  const signIn = async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      console.log('[Auth] signIn result:', data, error);
      if (error) throw error;
    } catch (error: any) {
      console.error('Sign in error:', error);
      toast.error(error.message || 'Failed to sign in');
      throw error;
    }
  };

  const signUp = async (email: string, password: string, userData?: any) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/`,
        },
      });
      console.log('[Auth] signUp result:', data, error);
      if (error) throw error;
      toast.success('Account created successfully! Please check your email to verify your account.');
    } catch (error: any) {
      console.error('Sign up error:', error);
      toast.error(error.message || 'Failed to create account');
      throw error;
    }
  };

  const signOut = async () => {
    await authSignOut();
  };

  const resetPassword = async (email: string) => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email);
      if (error) throw error;
      toast.success('Password reset email sent!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to send reset email');
      throw error;
    }
  };

  const value = {
    user,
    loading,
    signIn,
    signUp,
    signOut,
    resetPassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
