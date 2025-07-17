
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { paymentApi } from "@/services/paymentApi";
import { toast } from "sonner";
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  DollarSign,
  ArrowUpCircle,
  ArrowDownCircle,
  Gift
} from "lucide-react";
import { apiService } from '@/services/api';

interface Transaction {
  id: string;
  type: string;
  amount: number;
  currency: string;
  status: string;
  payment_method: string;
  description: string;
  created_at: string;
  failure_reason?: string;
  transaction_steps?: TransactionStep[];
}

interface TransactionStep {
  id: string;
  step_name: string;
  status: string;
  completed_at?: string;
  notes?: string;
}

interface Bonus {
  id: string;
  amount: number;
  bonus_type: string;
  description: string;
  status: string;
  created_at: string;
}

export function TransactionsList() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [bonuses, setBonuses] = useState<Bonus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTransactions = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiService.getTransactions();
        setTransactions(data);
      } catch (err) {
        setError('Failed to fetch transactions');
        toast.error('Failed to fetch transactions');
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [transactionsData, bonusesData] = await Promise.all([
        paymentApi.getTransactions(),
        paymentApi.getBonuses()
      ]);
      setTransactions(transactionsData);
      setBonuses(bonusesData);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'pending':
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'failed':
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTransactionIcon = (type: string) => {
    return type === 'deposit' ? 
      <ArrowUpCircle className="h-4 w-4 text-green-500" /> :
      <ArrowDownCircle className="h-4 w-4 text-red-500" />;
  };

  const getFailureMessage = (reason?: string, status?: string) => {
    if (!reason && status === 'failed') return 'Transaction failed';
    if (reason?.includes('cancelled_by_admin')) return 'Cancelled by Waves Quant';
    if (reason?.includes('provider_error')) return 'Cancelled by payment provider';
    if (reason?.includes('insufficient_funds')) return 'Insufficient funds';
    return reason || 'Unknown error';
  };

  const renderTransactionSteps = (steps: TransactionStep[] = []) => {
    const stepLabels = {
      'charged_by_provider': 'Charged by Provider',
      'received_in_wallet': 'Received in Wallet',
      'deposited_to_account': 'Deposited to Trading Account',
      'received_request': 'Request Received',
      'sent_to_provider': 'Sent to Provider',
      'withdrawn_to_account': 'Withdrawn to Your Account'
    };

    return (
      <div className="space-y-3">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center space-x-3">
            <div className={`h-3 w-3 rounded-full ${
              step.status === 'completed' ? 'bg-green-500' : 
              step.status === 'failed' ? 'bg-red-500' : 'bg-gray-300'
            }`} />
            <div className="flex-1">
              <p className="font-medium">{stepLabels[step.step_name] || step.step_name}</p>
              {step.completed_at && (
                <p className="text-sm text-muted-foreground">
                  {new Date(step.completed_at).toLocaleString()}
                </p>
              )}
              {step.notes && (
                <p className="text-sm text-muted-foreground">{step.notes}</p>
              )}
            </div>
            <Badge variant={
              step.status === 'completed' ? 'default' :
              step.status === 'failed' ? 'destructive' : 'secondary'
            }>
              {step.status}
            </Badge>
          </div>
        ))}
      </div>
    );
  };

  const filterTransactions = (status: string) => {
    switch (status) {
      case 'processing':
        return transactions.filter(t => ['pending', 'processing'].includes(t.status));
      case 'success':
        return transactions.filter(t => ['completed', 'success'].includes(t.status));
      case 'failed':
        return transactions.filter(t => ['failed', 'cancelled'].includes(t.status));
      default:
        return transactions;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return <div className="p-6 text-red-500">{error}</div>;
  }

  if (!transactions.length) {
    return <div className="p-6">No transactions found.</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Transactions</h2>
        <p className="text-muted-foreground">Track all your deposits, withdrawals, and bonuses</p>
      </div>

      <Tabs defaultValue="all" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="processing">Processing</TabsTrigger>
          <TabsTrigger value="success">Success</TabsTrigger>
          <TabsTrigger value="failed">Failed</TabsTrigger>
          <TabsTrigger value="bonuses">Bonuses</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <TransactionCards transactions={transactions} renderSteps={renderTransactionSteps} />
        </TabsContent>

        <TabsContent value="processing">
          <TransactionCards transactions={filterTransactions('processing')} renderSteps={renderTransactionSteps} />
        </TabsContent>

        <TabsContent value="success">
          <TransactionCards transactions={filterTransactions('success')} renderSteps={renderTransactionSteps} />
        </TabsContent>

        <TabsContent value="failed">
          <Card>
            <CardHeader>
              <CardTitle>Failed Transactions</CardTitle>
              <CardDescription>Transactions that could not be completed</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filterTransactions('failed').map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(transaction.status)}
                      {getTransactionIcon(transaction.type)}
                      <div>
                        <p className="font-medium capitalize">{transaction.type}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(transaction.created_at).toLocaleDateString()}
                        </p>
                        <p className="text-sm text-red-600">
                          {getFailureMessage(transaction.failure_reason, transaction.status)}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-red-600">
                        ${transaction.amount}
                      </p>
                      <Badge variant="destructive">{transaction.status}</Badge>
                    </div>
                  </div>
                ))}
                {filterTransactions('failed').length === 0 && (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-4" />
                    <p className="text-muted-foreground">No failed transactions</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bonuses">
          <Card>
            <CardHeader>
              <CardTitle>Bonuses</CardTitle>
              <CardDescription>Your earned bonuses and rewards</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {bonuses.map((bonus) => (
                  <div key={bonus.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Gift className="h-4 w-4 text-green-500" />
                      <div>
                        <p className="font-medium">{bonus.bonus_type}</p>
                        <p className="text-sm text-muted-foreground">{bonus.description}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(bonus.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-green-600">+${bonus.amount}</p>
                      <Badge variant="outline" className="capitalize">
                        {bonus.status}
                      </Badge>
                    </div>
                  </div>
                ))}
                {bonuses.length === 0 && (
                  <div className="text-center py-8">
                    <Gift className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No bonuses yet</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function TransactionCards({ transactions, renderSteps }: { transactions: Transaction[], renderSteps: (steps: any[]) => JSX.Element }) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'pending':
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'failed':
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTransactionIcon = (type: string) => {
    return type === 'deposit' ? 
      <ArrowUpCircle className="h-4 w-4 text-green-500" /> :
      <ArrowDownCircle className="h-4 w-4 text-red-500" />;
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          {transactions.map((transaction) => (
            <div key={transaction.id} className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                {getStatusIcon(transaction.status)}
                {getTransactionIcon(transaction.type)}
                <div>
                  <p className="font-medium capitalize">{transaction.type}</p>
                  <p className="text-sm text-muted-foreground">
                    {transaction.description}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {new Date(transaction.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
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
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="outline" size="sm">View Details</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Transaction Details</DialogTitle>
                      <DialogDescription>
                        Track the progress of your {transaction.type}
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">Transaction Information</h4>
                        <div className="space-y-1 text-sm">
                          <p><span className="font-medium">Amount:</span> ${transaction.amount}</p>
                          <p><span className="font-medium">Type:</span> {transaction.type}</p>
                          <p><span className="font-medium">Status:</span> {transaction.status}</p>
                          <p><span className="font-medium">Date:</span> {new Date(transaction.created_at).toLocaleString()}</p>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Processing Steps</h4>
                        {renderSteps(transaction.transaction_steps || [])}
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </div>
          ))}
          {transactions.length === 0 && (
            <div className="text-center py-8">
              <DollarSign className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No transactions found</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
