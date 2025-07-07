
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { PaymentMethodSelector } from "./PaymentMethodSelector";
import { PaymentReview } from "./PaymentReview";
import { PaymentMethod } from "@/services/paymentApi";

interface PaymentFormProps {
  transactionType: 'deposit' | 'withdrawal';
}

const PaymentForm = ({ transactionType }: PaymentFormProps) => {
  const { user } = useAuth();
  const [step, setStep] = useState(1); // 1: method selection, 2: form, 3: review
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod | null>(null);
  const [amount, setAmount] = useState("");
  const [userDetails, setUserDetails] = useState({
    fullName: "",
    phoneNumber: "",
    email: "",
  });
  const [loading, setLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchUserProfile();
    }
  }, [user]);

  const fetchUserProfile = async () => {
    try {
      const { data: profile } = await supabase
        .from('profiles')
        .select('full_name, phone_number')
        .eq('user_id', user?.id)
        .single();

      if (profile) {
        setUserDetails({
          fullName: profile.full_name || "",
          phoneNumber: profile.phone_number || "",
          email: user?.email || "",
        });
      } else {
        setUserDetails(prev => ({
          ...prev,
          email: user?.email || ""
        }));
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
      setUserDetails(prev => ({
        ...prev,
        email: user?.email || ""
      }));
    } finally {
      setProfileLoading(false);
    }
  };

  const handleMethodSelect = (method: PaymentMethod) => {
    setSelectedMethod(method);
    setStep(2);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userDetails.fullName || !userDetails.phoneNumber) {
      toast.error("Please fill in all required user details");
      return;
    }

    if (!amount || parseFloat(amount) <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    setStep(3);
  };

  const handleConfirmTransaction = async () => {
    setLoading(true);
    
    try {
      // Update user profile if needed
      if (userDetails.fullName || userDetails.phoneNumber) {
        await supabase
          .from('profiles')
          .upsert({
            user_id: user?.id,
            full_name: userDetails.fullName,
            phone_number: userDetails.phoneNumber
          });
      }

      // Create transaction
      const { data: transaction, error: transactionError } = await supabase
        .from('transactions')
        .insert({
          user_id: user?.id,
          type: transactionType,
          amount: parseFloat(amount),
          currency: 'USD',
          payment_method: selectedMethod?.name,
          status: 'pending',
          description: `${transactionType} via ${selectedMethod?.name}`
        })
        .select()
        .single();

      if (transactionError) throw transactionError;

      // Create transaction steps
      await supabase.rpc('create_transaction_steps', {
        p_transaction_id: transaction.id,
        p_transaction_type: transactionType
      });

      if (transactionType === 'deposit') {
        // Update portfolio balance for deposits
        await supabase.rpc('update_portfolio_balance', {
          p_user_id: user?.id,
          p_amount: parseFloat(amount),
          p_transaction_type: 'deposit'
        });
      }

      toast.success(`${transactionType} request submitted successfully!`);
      
      // Reset form and redirect to transactions
      setStep(1);
      setSelectedMethod(null);
      setAmount("");
      
      // Navigate to transactions section
      window.dispatchEvent(new CustomEvent('navigate-to-transactions'));
      
    } catch (error) {
      console.error(`Error processing ${transactionType}:`, error);
      toast.error(`Failed to process ${transactionType}. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  if (profileLoading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight capitalize">{transactionType}</h2>
        <p className="text-muted-foreground">
          {transactionType === 'deposit' 
            ? 'Add funds to your trading account' 
            : 'Withdraw funds from your trading account'
          }
        </p>
      </div>

      {step === 1 && transactionType === 'deposit' && (
        <PaymentMethodSelector
          onSelect={handleMethodSelect}
          selectedMethod={selectedMethod}
        />
      )}

      {(step === 2 || (step === 1 && transactionType === 'withdrawal')) && (
        <Card>
          <CardHeader>
            <CardTitle>
              {transactionType === 'deposit' ? 'Deposit Details' : 'Withdrawal Details'}
            </CardTitle>
            <CardDescription>
              Enter the amount and confirm your details
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleFormSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="amount">Amount (USD)</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  min="1"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="Enter amount"
                  required
                />
              </div>

              <div className="space-y-4">
                <h4 className="font-medium">Personal Information</h4>
                
                <div className="space-y-2">
                  <Label htmlFor="fullName">Full Name *</Label>
                  <Input
                    id="fullName"
                    value={userDetails.fullName}
                    onChange={(e) => setUserDetails(prev => ({ ...prev, fullName: e.target.value }))}
                    placeholder="Enter your full name"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phoneNumber">Phone Number *</Label>
                  <Input
                    id="phoneNumber"
                    value={userDetails.phoneNumber}
                    onChange={(e) => setUserDetails(prev => ({ ...prev, phoneNumber: e.target.value }))}
                    placeholder="Enter your phone number"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={userDetails.email}
                    disabled
                    className="bg-muted"
                  />
                </div>
              </div>

              <div className="flex space-x-4">
                {step === 2 && (
                  <Button type="button" variant="outline" onClick={handleBack} className="flex-1">
                    Back
                  </Button>
                )}
                <Button type="submit" className="flex-1">
                  Continue to Review
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {step === 3 && selectedMethod && (
        <PaymentReview
          paymentMethod={selectedMethod}
          amount={parseFloat(amount)}
          userDetails={userDetails}
          onConfirm={handleConfirmTransaction}
          onBack={handleBack}
          loading={loading}
        />
      )}
    </div>
  );
};

export default PaymentForm;
