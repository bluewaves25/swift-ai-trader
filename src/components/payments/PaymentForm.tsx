
import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { useAuth } from "@/hooks/useAuth";
import { apiService } from "@/services/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface PaymentFormProps {
  transactionType: "deposit" | "withdrawal";
}

interface PaymentMethodSelectorProps {
  selectedMethod: string | null;
  onMethodChange: (method: string) => void;
  transactionType: "deposit" | "withdrawal";
}

const PaymentMethodSelector: React.FC<PaymentMethodSelectorProps> = ({
  selectedMethod,
  onMethodChange,
  transactionType,
}) => {
  return (
    <div className="space-y-2">
      <Label>Payment Method</Label>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
        <Button
          variant={selectedMethod === "card" ? "default" : "outline"}
          onClick={() => onMethodChange("card")}
          className="justify-start"
        >
          Credit Card
        </Button>
        <Button
          variant={selectedMethod === "bank" ? "default" : "outline"}
          onClick={() => onMethodChange("bank")}
          className="justify-start"
        >
          Bank Transfer
        </Button>
        <Button
          variant={selectedMethod === "crypto" ? "default" : "outline"}
          onClick={() => onMethodChange("crypto")}
          className="justify-start"
        >
          Cryptocurrency
        </Button>
      </div>
    </div>
  );
};

export function PaymentForm({ transactionType }: PaymentFormProps) {
  const { user } = useAuth();
  const [amount, setAmount] = useState<number>(10);
  const [paymentMethod, setPaymentMethod] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [balance, setBalance] = useState<number>(0);

  useEffect(() => {
    const fetchBalance = async () => {
      if (user) {
        try {
          const response = await apiService.getBalance(user.id);
          if (response.data && typeof response.data === 'object' && 'balance' in response.data) {
            setBalance((response.data as any).balance);
          }
        } catch (error) {
          console.error("Failed to fetch balance:", error);
          toast.error("Failed to fetch balance");
        }
      }
    };

    fetchBalance();
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!user) {
      toast.error("Please sign in to continue");
      return;
    }

    if (transactionType === "withdrawal" && amount > balance) {
      toast.error("Insufficient balance");
      return;
    }

    setLoading(true);
    
    try {
      const paymentData = {
        userId: user.id,
        type: transactionType,
        amount: amount,
        method: paymentMethod,
        details: {},
      };

      // Simulate payment processing
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Update balance based on transaction type
      let newBalance = balance;
      if (transactionType === "deposit") {
        newBalance += amount;
      } else {
        newBalance -= amount;
      }

      // Optimistically update the balance
      setBalance(newBalance);

      // Call API to update balance
      await apiService.updateBalance(user.id, newBalance);

      toast.success(
        `${transactionType === "deposit" ? "Deposit" : "Withdrawal"} of $${amount.toLocaleString()} successful!`
      );
      setAmount(10);
    } catch (error) {
      console.error('Payment error:', error);
      toast.error('Payment processing failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="text-center">
          {transactionType === "deposit" ? "Deposit Funds" : "Withdraw Funds"}
        </CardTitle>
        <CardDescription className="text-center">
          {transactionType === "deposit" 
            ? "Add funds to your trading account" 
            : "Withdraw funds from your account"
          }
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Current Balance */}
        <div className="mb-6 p-4 rounded-lg bg-muted">
                          <div className="text-xs text-muted-foreground">Current Balance</div>
          <div className="text-2xl font-bold">${balance.toLocaleString()}</div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Amount Input */}
          <div className="space-y-2">
            <Label htmlFor="amount">Amount ($)</Label>
            <Input
              id="amount"
              type="number"
              min="10"
              max={transactionType === "withdrawal" ? balance : 100000}
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              placeholder="Enter amount"
              required
            />
            {transactionType === "withdrawal" && amount > balance && (
              <p className="text-xs text-destructive">Amount exceeds available balance</p>
            )}
          </div>

          {/* Payment Method Selection */}
          <PaymentMethodSelector
            selectedMethod={paymentMethod}
            onMethodChange={setPaymentMethod}
            transactionType={transactionType}
          />

          {/* Payment Details Form */}
          {paymentMethod && (
            <div className="space-y-4 p-4 border rounded-lg">
              {paymentMethod === 'card' && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="cardNumber">Card Number</Label>
                      <Input
                        id="cardNumber"
                        placeholder="1234 5678 9012 3456"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="cvv">CVV</Label>
                      <Input
                        id="cvv"
                        placeholder="123"
                        maxLength={4}
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="expiry">Expiry Date</Label>
                      <Input
                        id="expiry"
                        placeholder="MM/YY"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="cardName">Cardholder Name</Label>
                      <Input
                        id="cardName"
                        placeholder="John Doe"
                        required
                      />
                    </div>
                  </div>
                </>
              )}

              {paymentMethod === 'bank' && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="accountNumber">Account Number</Label>
                    <Input
                      id="accountNumber"
                      placeholder="Enter account number"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="routingNumber">Routing Number</Label>
                    <Input
                      id="routingNumber"
                      placeholder="Enter routing number"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="accountName">Account Holder Name</Label>
                    <Input
                      id="accountName"
                      placeholder="Enter account holder name"
                      required
                    />
                  </div>
                </>
              )}

              {paymentMethod === 'crypto' && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="cryptoAddress">Wallet Address</Label>
                    <Input
                      id="cryptoAddress"
                      placeholder="Enter your crypto wallet address"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cryptoType">Cryptocurrency</Label>
                    <Select required>
                      <SelectTrigger>
                        <SelectValue placeholder="Select cryptocurrency" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="bitcoin">Bitcoin (BTC)</SelectItem>
                        <SelectItem value="ethereum">Ethereum (ETH)</SelectItem>
                        <SelectItem value="usdt">Tether (USDT)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full"
            disabled={loading || !paymentMethod || amount < 10}
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-2"></div>
                Processing...
              </>
            ) : (
              `${transactionType === "deposit" ? "Deposit" : "Withdraw"} $${amount.toLocaleString()}`
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
