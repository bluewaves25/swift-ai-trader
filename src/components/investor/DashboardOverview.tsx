
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  BarChart3,
  Target,
  AlertCircle
} from "lucide-react";

const DashboardOverview = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalBalance: 0,
    availableBalance: 0,
    investedAmount: 0,
    realizedPnL: 0,
    unrealizedPnL: 0,
    totalTrades: 0,
    winRate: 0,
    dailyPnL: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchDashboardStats();
    }
  }, [user]);

  const fetchDashboardStats = async () => {
    try {
      // Fetch portfolio data
      const { data: portfolio } = await supabase
        .from('portfolios')
        .select('*')
        .eq('user_id', user?.id)
        .single();

      if (portfolio) {
        setStats(prev => ({
          ...prev,
          totalBalance: portfolio.total_balance || 0,
          availableBalance: portfolio.available_balance || 0,
          investedAmount: portfolio.invested_amount || 0,
          realizedPnL: portfolio.realized_pnl || 0,
          unrealizedPnL: portfolio.unrealized_pnl || 0
        }));
      }

      // Fetch trade statistics
      const { data: trades } = await supabase
        .from('trades')
        .select('*')
        .eq('user_id', user?.id);

      if (trades) {
        const totalTrades = trades.length;
        const completedTrades = trades.filter(trade => trade.status === 'completed');
        const winningTrades = completedTrades.filter(trade => (Number(trade.price) || 0) > 0);
        const winRate = completedTrades.length > 0 ? (winningTrades.length / completedTrades.length) * 100 : 0;

        // Calculate daily P&L
        const today = new Date().toISOString().split('T')[0];
        const todayTrades = trades.filter(trade => 
          trade.timestamp && trade.timestamp.startsWith(today)
        );
        const dailyPnL = todayTrades.reduce((sum, trade) => sum + (Number(trade.price) || 0), 0);

        setStats(prev => ({
          ...prev,
          totalTrades,
          winRate,
          dailyPnL
        }));
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard Overview</h2>
        <p className="text-muted-foreground">Your trading performance at a glance</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Balance</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${stats.totalBalance.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">
              Available: ${stats.availableBalance.toFixed(2)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily P&L</CardTitle>
            {stats.dailyPnL >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${stats.dailyPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${stats.dailyPnL.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">Today's performance</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalTrades}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.winRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">Success rate</p>
          </CardContent>
        </Card>
      </div>

      {/* Additional Performance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Portfolio Performance</CardTitle>
            <CardDescription>Your investment summary</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span>Invested Amount:</span>
              <span className="font-medium">${stats.investedAmount.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Realized P&L:</span>
              <span className={`font-medium ${stats.realizedPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${stats.realizedPnL.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Unrealized P&L:</span>
              <span className={`font-medium ${stats.unrealizedPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${stats.unrealizedPnL.toFixed(2)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Trading Status</CardTitle>
            <CardDescription>Current trading activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="px-3 py-1">
                <Activity className="h-4 w-4 mr-1" />
                AI Trading Active
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Your AI trading algorithms are currently monitoring the markets and executing trades based on your risk preferences.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardOverview;
