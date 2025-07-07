
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { PaymentMethod } from "@/services/paymentApi";

interface PaymentFormProps {
  paymentMethod: PaymentMethod;
  amount: number;
  onSubmit: (userDetails: any) => void;
  onBack: () => void;
}

interface UserDetails {
  fullName: string;
  phoneNumber: string;
  email: string;
  dateOfBirth: string;
}

export function PaymentForm({ paymentMethod, amount, onSubmit, onBack }: PaymentFormProps) {
  const { user } = useAuth();
  const [userDetails, setUserDetails] = useState<UserDetails>({
    fullName: '',
    phoneNumber: '',
    email: user?.email || '',
    dateOfBirth: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchUserProfile();
  }, [user]);

  const fetchUserProfile = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('user_id', user.id)
        .single();

      if (error && error.code !== 'PGRST116') {
        console.error('Error fetching profile:', error);
        return;
      }

      if (data) {
        setUserDetails(prev => ({
          ...prev,
          fullName: data.full_name || '',
          phoneNumber: data.phone_number || '',
          dateOfBirth: data.date_of_birth || ''
        }));
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userDetails.fullName || !userDetails.phoneNumber || !userDetails.dateOfBirth) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      // Update user profile with new details
      const { error: profileError } = await supabase
        .from('profiles')
        .upsert({
          user_id: user?.id,
          full_name: userDetails.fullName,
          phone_number: userDetails.phoneNumber,
          date_of_birth: userDetails.dateOfBirth,
          updated_at: new Date().toISOString()
        });

      if (profileError) throw profileError;

      onSubmit(userDetails);
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Payment Details</CardTitle>
        <CardDescription>
          Complete your ${amount} deposit via {paymentMethod.name}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fullName">Full Name *</Label>
            <Input
              id="fullName"
              value={userDetails.fullName}
              onChange={(e) => setUserDetails(prev => ({ ...prev, fullName: e.target.value }))}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="phoneNumber">Phone Number *</Label>
            <Input
              id="phoneNumber"
              value={userDetails.phoneNumber}
              onChange={(e) => setUserDetails(prev => ({ ...prev, phoneNumber: e.target.value }))}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              type="email"
              value={userDetails.email}
              onChange={(e) => setUserDetails(prev => ({ ...prev, email: e.target.value }))}
              disabled
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="dateOfBirth">Date of Birth *</Label>
            <Input
              id="dateOfBirth"
              type="date"
              value={userDetails.dateOfBirth}
              onChange={(e) => setUserDetails(prev => ({ ...prev, dateOfBirth: e.target.value }))}
              required
            />
          </div>

          <div className="flex space-x-4">
            <Button type="button" variant="outline" onClick={onBack} className="flex-1">
              Back
            </Button>
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Processing...' : 'Continue to Review'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
