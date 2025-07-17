import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from '@supabase/supabase-js';
import { supabase } from '@/integrations/supabase/client';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';

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
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let loadingTimeout: NodeJS.Timeout | null = null;
    // Get initial session
    supabase.auth.getSession()
      .then(({ data: { session } }) => {
        setUser(session?.user ?? null);
        setLoading(false);
        console.log('[Auth] Initial session:', session?.user);
        if (!session?.user) {
          toast.error('No user session found. Please sign in again.');
        }
      })
      .catch((err) => {
        setUser(null);
        setLoading(false);
        console.error('[Auth] getSession error:', err);
        toast.error('Failed to fetch session');
      });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('[Auth] Auth event:', event, session?.user?.id);
        setUser(session?.user ?? null);
        let navigated = false;
        try {
          if (event === 'SIGNED_IN' && session?.user) {
            // Check if user exists in our users table, if not create them
            let existingUser, fetchError;
            try {
              const res = await supabase
                .from('users')
                .select('role')
                .eq('id', session.user.id)
                .single();
              existingUser = res.data;
              fetchError = res.error;
            } catch (e) {
              fetchError = e;
            }
            if (fetchError && fetchError.code === 'PGRST116') {
              // User doesn't exist, create them
              const { error: createError } = await supabase
                .from('users')
                .insert({
                  id: session.user.id,
                  email: session.user.email!,
                  role: 'investor'
                });
              if (createError) {
                console.error('Error creating user:', createError);
                toast.error('Failed to create user profile.');
              }
              navigate('/investor-dashboard');
              toast.success('Account created successfully!');
              navigated = true;
            } else if (fetchError) {
              console.error('Error fetching user role:', fetchError);
              if (session?.user) {
                navigate('/investor-dashboard');
                toast.success('Successfully logged in!');
                navigated = true;
              }
            } else if (existingUser?.role === 'owner') {
              navigate('/owner-dashboard');
              toast.success('Successfully logged in!');
              navigated = true;
            } else {
              navigate('/investor-dashboard');
              toast.success('Successfully logged in!');
              navigated = true;
            }
          }
          if (event === 'SIGNED_OUT') {
            navigate('/auth');
            toast.success('Successfully logged out!');
            navigated = true;
          }
        } catch (error) {
          console.error('Error in auth state change:', error);
          if (!navigated && session?.user) {
            navigate('/investor-dashboard');
            toast.success('Successfully logged in!');
          }
        } finally {
          setLoading(false);
          console.log('[Auth] Loading set to false (onAuthStateChange)');
        }
      }
    );

    // Hard fallback: if loading is stuck for 5s, show error and reload option
    if (loading) {
      loadingTimeout = setTimeout(() => {
        setLoading(false);
        toast.error('Authentication timed out. Please try again.');
        console.error('[Auth] Loading timeout fallback triggered');
        // Optionally force reload
        // window.location.reload();
      }, 5000);
    }

    return () => {
      subscription.unsubscribe();
      if (loadingTimeout) clearTimeout(loadingTimeout);
    };
  }, [navigate, loading]);

  // If loading is stuck, show a retry button
  // REMOVE: do not render a blocking screen, always render children
  // if (loading) {
  //   return (
  //     <div className="flex flex-col items-center justify-center min-h-screen">
  //       <div className="text-lg font-semibold mb-4">Signing in...</div>
  //       <Button onClick={() => window.location.reload()}>Retry</Button>
  //     </div>
  //   );
  // }

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
      // Do not setLoading(false) here!
    } catch (error: any) {
      console.error('Sign in error:', error);
      toast.error(error.message || 'Failed to sign in');
      setLoading(false); // FIX: reset loading on error
      throw error;
    }
  };

  const signUp = async (email: string, password: string, userData?: any) => {
    setLoading(true);
    try {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/`,
        },
      });

      if (error) throw error;
      toast.success('Account created successfully! Please check your email to verify your account.');
    } catch (error: any) {
      console.error('Sign up error:', error);
      toast.error(error.message || 'Failed to create account');
      setLoading(false); // FIX: reset loading on error
      throw error;
    }
    // Do not setLoading(false) here!
  };

  // Add this function to handle API errors globally
  const handleApiError = (error: any, signOut: () => void) => {
    if (error?.response?.status === 401 || error?.response?.status === 403) {
      signOut();
      window.location.href = "/auth";
    }
  };

  // Add getCurrentUser for session persistence
  const getCurrentUser = async () => {
    try {
      const res = await fetch("/api/auth/me", {
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` },
      });
      if (res.status === 200) {
        return await res.json();
      } else {
        throw new Error("Not authenticated");
      }
    } catch (e) {
      return null;
    }
  };

  // Update signOut to only clear session, let onAuthStateChange handle navigation
  const signOut = async () => {
    console.log('Sign out called');
    try {
      await supabase.auth.signOut();
      console.log('Supabase signOut resolved');
    } catch (e) {
      console.error('Supabase signOut error', e);
    }
    // Force remove all Supabase session keys
    Object.keys(localStorage).forEach((key) => {
      if (key.startsWith('sb-')) localStorage.removeItem(key);
    });
    localStorage.removeItem("token");
    // Do not navigate here; let onAuthStateChange handle it
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
