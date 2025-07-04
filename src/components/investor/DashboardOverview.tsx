
import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { useErrorHandler } from "@/hooks/useErrorHandler";
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  BarChart3,
  Wallet
} from "lucide-react";
import TradingChart from "@/components/trading/TradingChart";
import PerformanceAnalytics from "@/components/trading/PerformanceAnalytics";

export default function DashboardOverview() {
  const { user } = useAuth();
  const { handleAsyncError } = useErrorHandler();
  const [stats, setStats] = useState({
    totalBalance: 0,
    dailyPnL: 0,
    totalTrades: 0,
    winRate: 0,
    investmentAmount: 0,
    profitLoss: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInvestorStats();
    const interval = setInterval(fetchInvestorStats, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchInvestorStats = async () => {
    await handleAsyncError(async () => {
      const { data: portfolio } = await supabase
        .from('portfolios')
        .select('*')
        .eq('user_id', user?.id)
        .single();

      const today = new Date().toISOString().split('T')[0];
      const { data: todayTrades } = await supabase
        .from('trades')
        .select('profit_loss')
        .gte('created_at', `${today}T00:00:00Z`)
        .lt('created_at', `${today}T23:59:59Z`);

      const dailyPnL = todayTrades?.reduce((sum, trade) => sum + (trade.profit_loss || 0), 0) || 0;
      const winningTrades = todayTrades?.filter(trade => (trade.profit_loss || 0) > 0).length || 0;
      const winRate = todayTrades?.length ? (winningTrades / todayTrades.length) * 100 : 0;

      setStats({
        totalBalance: portfolio?.total_balance || 0,
        dailyPnL,
        totalTrades: portfolio?.total_trades || 0,
        winRate,
        investmentAmount: portfolio?.available_balance || 0,
        profitLoss: portfolio?.realized_pnl || 0
      });
    }, { showToast: false });
    
    setLoading(false);
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
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Investment</p>
                <p className="text-2xl font-bold">${stats.investmentAmount.toFixed(2)}</p>
              </div>
              <Wallet className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total P&L</p>
                <p className={`text-2xl font-bold ${stats.profitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  ${stats.profitLoss.toFixed(2)}
                </p>
              </div>
              {stats.profitLoss >= 0 ? 
                <TrendingUp className="h-8 w-8 text-green-500" /> :
                <TrendingDown className="h-8 w-8 text-red-500" />
              }
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Daily P&L</p>
                <p className={`text-2xl font-bold ${stats.dailyPnL >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  ${stats.dailyPnL.toFixed(2)}
                </p>
              </div>
              {stats.dailyPnL >= 0 ? 
                <TrendingUp className="h-8 w-8 text-green-500" /> :
                <TrendingDown className="h-8 w-8 text-red-500" />
              }
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Trades</p>
                <p className="text-2xl font-bold">{stats.totalTrades}</p>
              </div>
              <Activity className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Win Rate</p>
                <p className="text-2xl font-bold">{stats.winRate.toFixed(1)}%</p>
              </div>
              <BarChart3 className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Balance</p>
                <p className="text-2xl font-bold">${stats.totalBalance.toFixed(2)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TradingChart />
        <PerformanceAnalytics />
      </div>
    </div>
  );
}
