
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { supabase } from "@/integrations/supabase/client";
import { 
  ArrowUpCircle, 
  ArrowDownCircle, 
  Clock, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  DollarSign
} from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/hooks/useAuth";

export function InvestorPayments() {
  const { user } = useAuth();
  const [depositAmount, setDepositAmount] = useState("");
  const [withdrawAmount, setWithdrawAmount] = useState("");
  const [loading, setLoading] = useState(false);
  const [transactions, setTransactions] = useState([]);

  const handleDeposit = async () => {
    if (!depositAmount || parseFloat(depositAmount) <= 0) {
      toast.error("Please enter a valid deposit amount");
      return;
    }

    setLoading(true);
    try {
      // Create deposit transaction
      const { error } = await supabase
        .from('transactions')
        .insert({
          user_id: user?.id,
          type: 'deposit',
          amount: parseFloat(depositAmount),
          status: 'pending',
          method: 'bank_transfer',
          description: `Deposit to Exness account - $${depositAmount}`
        });

      if (error) throw error;

      // Update portfolio balance
      const { error: portfolioError } = await supabase
        .from('portfolios')
        .upsert({
          user_id: user?.id,
          available_balance: parseFloat(depositAmount),
          updated_at: new Date().toISOString()
        });

      if (portfolioError) throw portfolioError;

      toast.success("Deposit request submitted successfully");
      setDepositAmount("");
      fetchTransactions();
    } catch (error) {
      console.error('Deposit error:', error);
      toast.error("Failed to process deposit");
    } finally {
      setLoading(false);
    }
  };

  const handleWithdraw = async () => {
    if (!withdrawAmount || parseFloat(withdrawAmount) <= 0) {
      toast.error("Please enter a valid withdrawal amount");
      return;
    }

    setLoading(true);
    try {
      // Check if user has been invested for at least 2 weeks
      const twoWeeksAgo = new Date();
      twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);

      const { data: portfolio } = await supabase
        .from('portfolios')
        .select('created_at')
        .eq('user_id', user?.id)
        .single();

      if (portfolio && new Date(portfolio.created_at) > twoWeeksAgo) {
        toast.error("Withdrawal is only allowed after 2 weeks of investment");
        return;
      }

      // Create withdrawal transaction
      const { error } = await supabase
        .from('transactions')
        .insert({
          user_id: user?.id,
          type: 'withdrawal',
          amount: parseFloat(withdrawAmount),
          status: 'pending',
          method: 'bank_transfer',
          description: `Withdrawal request - $${withdrawAmount}`
        });

      if (error) throw error;

      toast.success("Withdrawal request submitted for review");
      setWithdrawAmount("");
      fetchTransactions();
    } catch (error) {
      console.error('Withdrawal error:', error);
      toast.error("Failed to process withdrawal");
    } finally {
      setLoading(false);
    }
  };

  const fetchTransactions = async () => {
    try {
      const { data, error } = await supabase
        .from('transactions')
        .select('*')
        .eq('user_id', user?.id)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setTransactions(data || []);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Payments</h2>
          <p className="text-muted-foreground">Manage your deposits and withdrawals</p>
        </div>
      </div>

      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Deposits are processed within 24 hours. Withdrawals require a minimum 2-week investment period and are subject to review.
        </AlertDescription>
      </Alert>

      <Tabs defaultValue="deposit" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="deposit">Deposit</TabsTrigger>
          <TabsTrigger value="withdraw">Withdraw</TabsTrigger>
        </TabsList>

        <TabsContent value="deposit">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <ArrowUpCircle className="h-5 w-5 text-green-500" />
                <span>Deposit Funds</span>
              </CardTitle>
              <CardDescription>
                Deposit funds to your Exness trading account
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="deposit-amount">Amount (USD)</Label>
                <Input
                  id="deposit-amount"
                  type="number"
                  placeholder="Enter amount"
                  value={depositAmount}
                  onChange={(e) => setDepositAmount(e.target.value)}
                  min="100"
                  step="10"
                />
              </div>
              <div className="bg-muted/50 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Deposit Information</h4>
                <ul className="text-sm space-y-1 text-muted-foreground">
                  <li>• Minimum deposit: $100</li>
                  <li>• Processing time: 1-24 hours</li>
                  <li>• Funds are deposited directly to Exness</li>
                  <li>• Bank transfer fees may apply</li>
                </ul>
              </div>
              <Button 
                onClick={handleDeposit} 
                disabled={loading}
                className="w-full"
              >
                <DollarSign className="h-4 w-4 mr-2" />
                Deposit ${depositAmount || '0'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="withdraw">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <ArrowDownCircle className="h-5 w-5 text-red-500" />
                <span>Withdraw Funds</span>
              </CardTitle>
              <CardDescription>
                Request withdrawal from your investment
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="withdraw-amount">Amount (USD)</Label>
                <Input
                  id="withdraw-amount"
                  type="number"
                  placeholder="Enter amount"
                  value={withdrawAmount}
                  onChange={(e) => setWithdrawAmount(e.target.value)}
                  min="50"
                  step="10"
                />
              </div>
              <div className="bg-muted/50 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Withdrawal Information</h4>
                <ul className="text-sm space-y-1 text-muted-foreground">
                  <li>• Minimum withdrawal: $50</li>
                  <li>• Available after 2 weeks of investment</li>
                  <li>• Processing time: 2-5 business days</li>
                  <li>• Subject to review and approval</li>
                </ul>
              </div>
              <Button 
                onClick={handleWithdraw} 
                disabled={loading}
                variant="destructive"
                className="w-full"
              >
                <ArrowDownCircle className="h-4 w-4 mr-2" />
                Withdraw ${withdrawAmount || '0'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader>
          <CardTitle>Transaction History</CardTitle>
          <CardDescription>Your recent deposits and withdrawals</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {transactions.length === 0 ? (
              <div className="text-center py-8">
                <DollarSign className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No transactions yet</p>
              </div>
            ) : (
              transactions.map((transaction: any) => (
                <div key={transaction.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(transaction.status)}
                    <div>
                      <p className="font-medium capitalize">{transaction.type}</p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(transaction.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-medium ${
                      transaction.type === 'deposit' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.type === 'deposit' ? '+' : '-'}${transaction.amount}
                    </p>
                    <Badge variant="outline" className="capitalize">
                      {transaction.status}
                    </Badge>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
