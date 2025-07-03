
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  BarChart3, 
  Settings, 
  LogOut,
  Zap,
  Brain,
  Target,
  Shield,
  Cpu,
  X,
  Square,
  Play,
  Pause
} from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import TradingChart from "@/components/trading/TradingChart";
import LiveSignals from "@/components/trading/LiveSignals";
import TradeHistory from "@/components/trading/TradeHistory";
import PairStrategies from "@/components/trading/PairStrategies";
import RiskManagement from "@/components/trading/RiskManagement";
import PerformanceAnalytics from "@/components/trading/PerformanceAnalytics";
import TradingEngine from "@/components/trading/TradingEngine";
import { useNavigate } from "react-router-dom";

const OwnerDashboard = () => {
  const { signOut, user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalBalance: 0,
    dailyPnL: 0,
    totalTrades: 0,
    winRate: 0,
    activePairs: 0,
    engineStatus: 'stopped'
  });
  const [isEngineRunning, setIsEngineRunning] = useState(false);
  const [canClosePositions, setCanClosePositions] = useState(false);

  useEffect(() => {
    fetchDashboardStats();
    const interval = setInterval(fetchDashboardStats, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardStats = async () => {
    try {
      // Fetch portfolio data
      const { data: portfolio } = await supabase
        .from('portfolios')
        .select('*')
        .eq('user_id', user?.id)
        .single();

      // Fetch today's trades
      const today = new Date().toISOString().split('T')[0];
      const { data: todayTrades } = await supabase
        .from('trades')
        .select('profit_loss, status')
        .gte('created_at', `${today}T00:00:00Z`)
        .lt('created_at', `${today}T23:59:59Z`);

      // Fetch active pairs
      const { data: activePairs } = await supabase
        .from('trading_pairs')
        .select('id')
        .eq('is_active', true);

      // Check if there are open positions
      const { data: openTrades } = await supabase
        .from('trades')
        .select('id')
        .eq('status', 'executed');

      const dailyPnL = todayTrades?.reduce((sum, trade) => sum + (trade.profit_loss || 0), 0) || 0;
      const winningTrades = todayTrades?.filter(trade => (trade.profit_loss || 0) > 0).length || 0;
      const winRate = todayTrades?.length ? (winningTrades / todayTrades.length) * 100 : 0;

      setStats({
        totalBalance: portfolio?.total_balance || 0,
        dailyPnL,
        totalTrades: portfolio?.total_trades || 0,
        winRate,
        activePairs: activePairs?.length || 0,
        engineStatus: isEngineRunning ? 'running' : 'stopped'
      });

      setCanClosePositions((openTrades?.length || 0) > 0);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  const handleEngineToggle = () => {
    setIsEngineRunning(!isEngineRunning);
    toast.success(isEngineRunning ? 'Trading engine stopped - automated trading disabled' : 'Trading engine started - automated trading enabled');
  };

  const handleCloseAllPositions = async () => {
    try {
      // Close all open positions
      const { error } = await supabase
        .from('trades')
        .update({ 
          status: 'cancelled',
          closed_at: new Date().toISOString()
        })
        .eq('status', 'executed');

      if (error) throw error;

      toast.success('All open positions closed successfully');
      fetchDashboardStats();
    } catch (error) {
      console.error('Error closing positions:', error);
      toast.error('Failed to close positions');
    }
  };

  const handleEmergencyStop = () => {
    setIsEngineRunning(false);
    handleCloseAllPositions();
    toast.warning('EMERGENCY STOP: All trading halted and positions closed');
  };

  const handleClose = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-8 w-8 text-primary" />
                <div>
                  <h1 className="text-2xl font-bold">Waves Quant Engine</h1>
                  <p className="text-sm text-muted-foreground">Owner Control Panel</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge variant={isEngineRunning ? "default" : "secondary"} className="px-3 py-1">
                <Cpu className="h-4 w-4 mr-1" />
                {isEngineRunning ? "Engine Running" : "Engine Stopped"}
              </Badge>
              <ThemeToggle />
              <Button variant="outline" onClick={signOut}>
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleClose}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Cards */}
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Balance</p>
                  <p className="text-2xl font-bold">${stats.totalBalance.toFixed(2)}</p>
                </div>
                <DollarSign className="h-8 w-8 text-green-500" />
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
                <Activity className="h-8 w-8 text-blue-500" />
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
                <Target className="h-8 w-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Pairs</p>
                  <p className="text-2xl font-bold">{stats.activePairs}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-center">
                <Button 
                  variant={isEngineRunning ? "destructive" : "default"}
                  onClick={handleEngineToggle}
                  className="w-full"
                >
                  {isEngineRunning ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
                  {isEngineRunning ? "Stop" : "Start"}
                </Button>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col space-y-2">
                <Button 
                  variant="outline"
                  onClick={handleCloseAllPositions}
                  disabled={!canClosePositions}
                  className="w-full text-xs"
                >
                  <Square className="h-3 w-3 mr-1" />
                  Close All
                </Button>
                <Button 
                  variant="destructive"
                  onClick={handleEmergencyStop}
                  className="w-full text-xs"
                >
                  <Shield className="h-3 w-3 mr-1" />
                  Emergency
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="signals">Live Signals</TabsTrigger>
            <TabsTrigger value="strategies">Strategies</TabsTrigger>
            <TabsTrigger value="trades">Trades</TabsTrigger>
            <TabsTrigger value="risk">Risk</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <TradingChart />
              <TradingEngine isRunning={isEngineRunning} />
            </div>
          </TabsContent>
          
          <TabsContent value="signals">
            <LiveSignals />
          </TabsContent>
          
          <TabsContent value="strategies">
            <PairStrategies />
          </TabsContent>
          
          <TabsContent value="trades">
            <TradeHistory />
          </TabsContent>
          
          <TabsContent value="risk">
            <RiskManagement />
          </TabsContent>
          
          <TabsContent value="analytics">
            <PerformanceAnalytics />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default OwnerDashboard;
