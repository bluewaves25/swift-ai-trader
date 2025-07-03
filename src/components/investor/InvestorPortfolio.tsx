
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { 
  Wallet, 
  TrendingUp, 
  TrendingDown, 
  ArrowUpRight, 
  ArrowDownLeft,
  Clock,
  AlertCircle
} from "lucide-react";

const InvestorPortfolio = () => {
  const { user } = useAuth();
  const [portfolio, setPortfolio] = useState({
    totalBalance: 0,
    availableBalance: 0,
    investedAmount: 0,
    profitLoss: 0,
    unrealizedPnl: 0
  });
  const [depositAmount, setDepositAmount] = useState("");
  const [withdrawAmount, setWithdrawAmount] = useState("");
  const [lastDepositDate, setLastDepositDate] = useState<Date | null>(null);
  const [canWithdraw, setCanWithdraw] = useState(false);

  useEffect(() => {
    fetchPortfolioData();
  }, [user]);

  useEffect(() => {
    // Check if user can withdraw (2 weeks after last deposit)
    if (lastDepositDate) {
      const twoWeeksAgo = new Date();
      twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
      setCanWithdraw(lastDepositDate <= twoWeeksAgo);
    }
  }, [lastDepositDate]);

  const fetchPortfolioData = async () => {
    try {
      const { data, error } = await supabase
        .from('portfolios')
        .select('*')
        .eq('user_id', user?.id)
        .single();

      if (error && error.code !== 'PGRST116') {
        console.error('Error fetching portfolio:', error);
        return;
      }

      if (data) {
        setPortfolio({
          totalBalance: data.total_balance || 0,
          availableBalance: data.available_balance || 0,
          investedAmount: (data.total_balance || 0) - (data.available_balance || 0),
          profitLoss: data.realized_pnl || 0,
          unrealizedPnl: data.unrealized_pnl || 0
        });
        
        // Set last deposit date (mock for now - you'd track this in deposits table)
        setLastDepositDate(new Date(data.updated_at || Date.now()));
      }
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
    }
  };

  const handleDeposit = async () => {
    if (!depositAmount || parseFloat(depositAmount) <= 0) {
      toast.error('Please enter a valid deposit amount');
      return;
    }

    try {
      const amount = parseFloat(depositAmount);
      
      // Update portfolio balance
      const { error } = await supabase
        .from('portfolios')
        .upsert({
          user_id: user?.id,
          total_balance: portfolio.totalBalance + amount,
          available_balance: portfolio.availableBalance + amount,
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'user_id'
        });

      if (error) throw error;

      toast.success(`Deposit of $${amount} initiated. Funds will be available in your trading account within 24 hours.`);
      setDepositAmount("");
      fetchPortfolioData();
    } catch (error) {
      console.error('Error processing deposit:', error);
      toast.error('Failed to process deposit');
    }
  };

  const handleWithdraw = async () => {
    if (!withdrawAmount || parseFloat(withdrawAmount) <= 0) {
      toast.error('Please enter a valid withdrawal amount');
      return;
    }

    if (!canWithdraw) {
      toast.error('Withdrawals are only allowed 2 weeks after your last deposit');
      return;
    }

    const amount = parseFloat(withdrawAmount);
    if (amount > portfolio.availableBalance) {
      toast.error('Insufficient available balance');
      return;
    }

    try {
      // Update portfolio balance
      const { error } = await supabase
        .from('portfolios')
        .upsert({
          user_id: user?.id,
          total_balance: portfolio.totalBalance - amount,
          available_balance: portfolio.availableBalance - amount,
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'user_id'
        });

      if (error) throw error;

      toast.success(`Withdrawal of $${amount} initiated. Funds will be processed within 24-48 hours.`);
      setWithdrawAmount("");
      fetchPortfolioData();
    } catch (error) {
      console.error('Error processing withdrawal:', error);
      toast.error('Failed to process withdrawal');
    }
  };

  const getDaysUntilWithdraw = () => {
    if (!lastDepositDate) return 0;
    const twoWeeksFromDeposit = new Date(lastDepositDate);
    twoWeeksFromDeposit.setDate(twoWeeksFromDeposit.getDate() + 14);
    const now = new Date();
    const diffTime = twoWeeksFromDeposit.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(0, diffDays);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Portfolio Overview */}
      <Card className="col-span-1 lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Wallet className="h-5 w-5" />
            <span>Portfolio Overview</span>
          </CardTitle>
          <CardDescription>
            Your investment performance and balance details
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Total Balance</p>
              <p className="text-2xl font-bold">${portfolio.totalBalance.toFixed(2)}</p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Available</p>
              <p className="text-2xl font-bold text-blue-500">${portfolio.availableBalance.toFixed(2)}</p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Invested</p>
              <p className="text-2xl font-bold text-orange-500">${portfolio.investedAmount.toFixed(2)}</p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Total P&L</p>
              <p className={`text-2xl font-bold ${portfolio.profitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                ${portfolio.profitLoss.toFixed(2)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Deposit */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <ArrowUpRight className="h-5 w-5 text-green-500" />
            <span>Deposit Funds</span>
          </CardTitle>
          <CardDescription>
            Add funds to your trading account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="deposit">Deposit Amount ($)</Label>
            <Input
              id="deposit"
              type="number"
              placeholder="Enter amount"
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              min="0"
              step="0.01"
            />
          </div>
          <Button onClick={handleDeposit} className="w-full" disabled={!depositAmount}>
            <ArrowUpRight className="h-4 w-4 mr-2" />
            Deposit to Exness Account
          </Button>
          <div className="text-xs text-muted-foreground">
            <p>• Funds will be available within 24 hours</p>
            <p>• Minimum deposit: $100</p>
            <p>• Funds are sent directly to the trading account</p>
          </div>
        </CardContent>
      </Card>

      {/* Withdraw */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <ArrowDownLeft className="h-5 w-5 text-red-500" />
            <span>Withdraw Funds</span>
          </CardTitle>
          <CardDescription>
            Withdraw available funds from your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!canWithdraw && (
            <div className="flex items-center space-x-2 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <AlertCircle className="h-4 w-4 text-yellow-500" />
              <div className="text-sm">
                <p className="font-medium">Withdrawal Locked</p>
                <p className="text-muted-foreground">
                  {getDaysUntilWithdraw()} days remaining until withdrawal is available
                </p>
              </div>
            </div>
          )}
          
          <div className="space-y-2">
            <Label htmlFor="withdraw">Withdrawal Amount ($)</Label>
            <Input
              id="withdraw"
              type="number"
              placeholder="Enter amount"
              value={withdrawAmount}
              onChange={(e) => setWithdrawAmount(e.target.value)}
              min="0"
              max={portfolio.availableBalance}
              step="0.01"
              disabled={!canWithdraw}
            />
          </div>
          <Button 
            onClick={handleWithdraw} 
            variant="destructive" 
            className="w-full" 
            disabled={!withdrawAmount || !canWithdraw}
          >
            <ArrowDownLeft className="h-4 w-4 mr-2" />
            Request Withdrawal
          </Button>
          <div className="text-xs text-muted-foreground">
            <p>• Withdrawals processed within 24-48 hours</p>
            <p>• Available only 2 weeks after last deposit</p>
            <p>• Maximum: ${portfolio.availableBalance.toFixed(2)}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default InvestorPortfolio;
