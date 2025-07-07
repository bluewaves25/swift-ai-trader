import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from '@supabase/supabase-js';
import { supabase } from '@/integrations/supabase/client';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

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
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth event:', event, session?.user?.id);
        setUser(session?.user ?? null);
        setLoading(false);

        if (event === 'SIGNED_IN' && session?.user) {
          try {
            // Check if user exists in our users table, if not create them
            const { data: existingUser, error: fetchError } = await supabase
              .from('users')
              .select('role')
              .eq('id', session.user.id)
              .single();

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
              }
              
              // Default to investor dashboard for new users
              navigate('/investor-dashboard');
              toast.success('Account created successfully!');
              return;
            }

            if (fetchError) {
              console.error('Error fetching user role:', fetchError);
              navigate('/investor-dashboard');
              toast.success('Successfully logged in!');
              return;
            }

            // Redirect based on role
            if (existingUser?.role === 'owner') {
              navigate('/owner-dashboard');
            } else {
              navigate('/investor-dashboard');
            }
            toast.success('Successfully logged in!');
          } catch (error) {
            console.error('Error in auth state change:', error);
            navigate('/investor-dashboard');
            toast.success('Successfully logged in!');
          }
        }

        if (event === 'SIGNED_OUT') {
          navigate('/');
          toast.success('Successfully logged out!');
        }
      }
    );

    return () => subscription.unsubscribe();
  }, [navigate]);

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
      // Do not setLoading(false) here!
    } catch (error: any) {
      console.error('Sign in error:', error);
      toast.error(error.message || 'Failed to sign in');
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
      throw error;
    }
    // Do not setLoading(false) here!
  };

  const signOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      setUser(null);         // Clear user immediately
      setLoading(false);     // Stop loading state
      if (error) throw error;
      toast.success('Successfully logged out!');
      navigate('/');         // Optionally navigate here for instant effect
    } catch (error: any) {
      console.error('Sign out error:', error);
      toast.error(error.message || 'Failed to sign out');
    }
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
