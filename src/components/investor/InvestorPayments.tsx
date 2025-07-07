
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useNavigate } from "react-router-dom";
import { PaymentMethodSelector } from "@/components/payments/PaymentMethodSelector";
import { PaymentForm } from "@/components/payments/PaymentForm";
import { PaymentReview } from "@/components/payments/PaymentReview";
import { TransactionsList } from "@/components/payments/TransactionsList";
import { paymentApi, PaymentMethod } from "@/services/paymentApi";
import { toast } from "sonner";
import { 
  ArrowUpCircle, 
  ArrowDownCircle, 
  Receipt,
  ArrowLeft
} from "lucide-react";

type PaymentStep = 'method' | 'form' | 'review' | 'transactions';
type TransactionType = 'deposit' | 'withdrawal';

export function InvestorPayments() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<PaymentStep>('transactions');
  const [transactionType, setTransactionType] = useState<TransactionType>('deposit');
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod>();
  const [amount, setAmount] = useState<string>('');
  const [userDetails, setUserDetails] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const startDeposit = () => {
    setTransactionType('deposit');
    setCurrentStep('method');
  };

  const startWithdrawal = () => {
    setTransactionType('withdrawal');
    setCurrentStep('form'); // Skip method selection for withdrawals
  };

  const handleMethodSelect = (method: PaymentMethod) => {
    setSelectedMethod(method);
    setCurrentStep('form');
  };

  const handleFormSubmit = (details: any) => {
    setUserDetails(details);
    setCurrentStep('review');
  };

  const handleConfirm = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    setLoading(true);
    try {
      if (transactionType === 'deposit' && selectedMethod) {
        await paymentApi.processDeposit({
          amount: parseFloat(amount),
          currency: 'USD',
          paymentMethod: selectedMethod,
          userDetails
        });
        toast.success('Deposit initiated successfully! Check Transactions for progress.');
      } else if (transactionType === 'withdrawal') {
        await paymentApi.processWithdrawal({
          amount: parseFloat(amount),
          currency: 'USD',
          userDetails
        });
        toast.success('Withdrawal request submitted! Check Transactions for progress.');
      }

      // Reset form and go to transactions
      setAmount('');
      setSelectedMethod(undefined);
      setUserDetails(null);
      setCurrentStep('transactions');
    } catch (error) {
      console.error('Payment error:', error);
      toast.error('Payment processing failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'method':
        return (
          <PaymentMethodSelector
            onSelect={handleMethodSelect}
            selectedMethod={selectedMethod}
          />
        );

      case 'form':
        return selectedMethod || transactionType === 'withdrawal' ? (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>
                  {transactionType === 'deposit' ? 'Deposit' : 'Withdrawal'} Amount
                </CardTitle>
                <CardDescription>
                  Enter the amount you'd like to {transactionType}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Label htmlFor="amount">Amount (USD)</Label>
                  <Input
                    id="amount"
                    type="number"
                    placeholder="Enter amount"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    min="10"
                    step="10"
                  />
                </div>
              </CardContent>
            </Card>
            
            <PaymentForm
              paymentMethod={selectedMethod || { id: 'previous', name: 'Previous Method', icon: '💳', type: 'card' }}
              amount={parseFloat(amount) || 0}
              onSubmit={handleFormSubmit}
              onBack={() => transactionType === 'deposit' ? setCurrentStep('method') : setCurrentStep('transactions')}
            />
          </div>
        ) : null;

      case 'review':
        return selectedMethod && userDetails ? (
          <PaymentReview
            paymentMethod={selectedMethod}
            amount={parseFloat(amount) || 0}
            userDetails={userDetails}
            onConfirm={handleConfirm}
            onBack={() => setCurrentStep('form')}
            loading={loading}
          />
        ) : null;

      case 'transactions':
      default:
        return <TransactionsList />;
    }
  };

  if (currentStep === 'transactions') {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Payments</h2>
            <p className="text-muted-foreground">Manage your deposits and withdrawals</p>
          </div>
          <div className="flex space-x-2">
            <Button onClick={startDeposit} className="flex items-center space-x-2">
              <ArrowUpCircle className="h-4 w-4" />
              <span>Deposit</span>
            </Button>
            <Button onClick={startWithdrawal} variant="outline" className="flex items-center space-x-2">
              <ArrowDownCircle className="h-4 w-4" />
              <span>Withdraw</span>
            </Button>
          </div>
        </div>
        
        {renderCurrentStep()}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCurrentStep('transactions')}
          className="flex items-center space-x-2"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Transactions</span>
        </Button>
        <div>
          <h2 className="text-2xl font-bold capitalize">{transactionType}</h2>
          <p className="text-muted-foreground">
            {transactionType === 'deposit' ? 'Add funds to your account' : 'Withdraw funds from your account'}
          </p>
        </div>
      </div>

      {renderCurrentStep()}
    </div>
  );
}
