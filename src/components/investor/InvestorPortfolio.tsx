
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { 
  Wallet, 
  TrendingUp, 
  TrendingDown, 
  ArrowUpRight, 
  ArrowDownLeft,
  DollarSign,
  Receipt
} from "lucide-react";

const InvestorPortfolio = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState({
    totalBalance: 0,
    availableBalance: 0,
    investedAmount: 0,
    profitLoss: 0,
    unrealizedPnl: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPortfolioData();
    const interval = setInterval(fetchPortfolioData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [user]);

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
          investedAmount: data.invested_amount || 0,
          profitLoss: data.realized_pnl || 0,
          unrealizedPnl: data.unrealized_pnl || 0
        });
      }
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Portfolio Overview</h2>
          <p className="text-muted-foreground">Your investment performance and balance details</p>
        </div>
        <Button onClick={() => navigate('/investor?section=payments')} className="flex items-center space-x-2">
          <Receipt className="h-4 w-4" />
          <span>View Transactions</span>
        </Button>
      </div>

      {/* Portfolio Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Balance</p>
                <p className="text-2xl font-bold">${portfolio.totalBalance.toFixed(2)}</p>
              </div>
              <Wallet className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Available</p>
                <p className="text-2xl font-bold text-green-500">${portfolio.availableBalance.toFixed(2)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Invested</p>
                <p className="text-2xl font-bold text-orange-500">${portfolio.investedAmount.toFixed(2)}</p>
              </div>
              <ArrowUpRight className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total P&L</p>
                <p className={`text-2xl font-bold ${portfolio.profitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  ${portfolio.profitLoss.toFixed(2)}
                </p>
              </div>
              {portfolio.profitLoss >= 0 ? 
                <TrendingUp className="h-8 w-8 text-green-500" /> :
                <TrendingDown className="h-8 w-8 text-red-500" />
              }
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
          <CardContent>
            <Button 
              onClick={() => navigate('/investor?section=payments')} 
              className="w-full"
            >
              <ArrowUpRight className="h-4 w-4 mr-2" />
              Go to Deposits
            </Button>
            <div className="text-xs text-muted-foreground mt-4">
              <p>• Multiple payment methods available</p>
              <p>• Funds processed within 24 hours</p>
              <p>• Minimum deposit: $10</p>
            </div>
          </CardContent>
        </Card>

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
          <CardContent>
            <Button 
              onClick={() => navigate('/investor?section=payments')} 
              variant="outline" 
              className="w-full"
            >
              <ArrowDownLeft className="h-4 w-4 mr-2" />
              Go to Withdrawals
            </Button>
            <div className="text-xs text-muted-foreground mt-4">
              <p>• Withdrawals processed within 24-48 hours</p>
              <p>• Available only after 2 weeks of investment</p>
              <p>• Maximum: ${portfolio.availableBalance.toFixed(2)}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Summary</CardTitle>
          <CardDescription>Your trading performance overview</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Realized P&L</p>
              <p className={`text-xl font-bold ${portfolio.profitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                ${portfolio.profitLoss.toFixed(2)}
              </p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Unrealized P&L</p>
              <p className={`text-xl font-bold ${portfolio.unrealizedPnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                ${portfolio.unrealizedPnl.toFixed(2)}
              </p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Total Return</p>
              <p className={`text-xl font-bold ${(portfolio.profitLoss + portfolio.unrealizedPnl) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                ${(portfolio.profitLoss + portfolio.unrealizedPnl).toFixed(2)}
              </p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Return %</p>
              <p className={`text-xl font-bold ${(portfolio.profitLoss + portfolio.unrealizedPnl) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {portfolio.totalBalance > 0 ? 
                  (((portfolio.profitLoss + portfolio.unrealizedPnl) / portfolio.totalBalance) * 100).toFixed(2) : 
                  '0.00'
                }%
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default InvestorPortfolio;
