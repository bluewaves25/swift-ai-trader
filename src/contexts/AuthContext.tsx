import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase } from '@/integrations/supabase/client';
import { toast } from 'sonner';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  userRole: 'owner' | 'investor' | null;
  loading: boolean;
  signUp: (email: string, password: string, role?: 'owner' | 'investor') => Promise<{ error: any }>;
  signIn: (email: string, password: string) => Promise<{ error: any }>;
  signOut: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [userRole, setUserRole] = useState<'owner' | 'investor' | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Set up auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setSession(session);
        setUser(session?.user ?? null);
        
        if (session?.user) {
          // Fetch user role from users table
          setTimeout(async () => {
            try {
              const { data: userData, error } = await supabase
                .from('users')
                .select('role')
                .eq('id', session.user.id)
                .single();
              setUserRole(userData?.role || 'investor');
            } catch (error) {
              console.error('Error in role fetch:', error);
              setUserRole('investor');
            }
          }, 0);
        } else {
          setUserRole(null);
        }
        
        setLoading(false);
      }
    );

    // Check for existing session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (!session) setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signUp = async (email: string, password: string, role: 'owner' | 'investor' = 'investor') => {
    try {
      // Only allow investor sign-ups through the UI
      if (role === 'owner') {
        toast.error('Owner accounts must be created manually by the administrator.');
        return { error: new Error('Owner registration not allowed') };
      }

      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/`,
          data: {
            role: 'investor' // Force investor role
          }
        }
      });

      if (error) {
        toast.error(error.message);
        return { error };
      }

      toast.success('Check your email to confirm your investor account');
      return { error: null };
    } catch (error: any) {
      toast.error('An unexpected error occurred');
      return { error };
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password
      });

      if (error) {
        toast.error(error.message);
        return { error };
      }

      toast.success('Successfully signed in');
      return { error: null };
    } catch (error: any) {
      toast.error('An unexpected error occurred');
      return { error };
    }
  };

  const signOut = async () => {
    try {
      await supabase.auth.signOut();
      toast.success('Successfully signed out');
    } catch (error: any) {
      toast.error('Error signing out');
    }
  };

  const value = {
    user,
    session,
    userRole,
    loading,
    signUp,
    signIn,
    signOut
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
