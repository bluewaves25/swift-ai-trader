import React from 'react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { LogOut } from 'lucide-react';

export const SignOutTest = () => {
  const { signOut, user } = useAuth();

  const handleSignOut = async () => {
    console.log('[SignOutTest] Sign out button clicked');
    try {
      await signOut();
      console.log('[SignOutTest] Sign out completed');
    } catch (error) {
      console.error('[SignOutTest] Sign out error:', error);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <Button
        onClick={handleSignOut}
        variant="destructive"
        size="sm"
        className="shadow-lg"
      >
        <LogOut className="h-4 w-4 mr-2" />
        Sign Out (Test)
      </Button>
    </div>
  );
}; 