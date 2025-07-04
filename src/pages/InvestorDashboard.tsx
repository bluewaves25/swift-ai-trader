
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { InvestorSidebar } from "@/components/investor/InvestorSidebar";
import { InvestorPayments } from "@/components/investor/InvestorPayments";
import { InvestorSettings } from "@/components/investor/InvestorSettings";
import { InvestorProfile } from "@/components/investor/InvestorProfile";
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  BarChart3,
  X,
  Wallet,
  FileText
} from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import TradingChart from "@/components/trading/TradingChart";
import LiveSignals from "@/components/trading/LiveSignals";
import TradeHistory from "@/components/trading/TradeHistory";
import PerformanceAnalytics from "@/components/trading/PerformanceAnalytics";
import InvestorPortfolio from "@/components/investor/InvestorPortfolio";
import InvestorJournal from "@/components/investor/InvestorJournal";
import { useNavigate } from "react-router-dom";

const InvestorDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('overview');
  const [stats, setStats] = useState({
    totalBalance: 0,
    dailyPnL: 0,
    totalTrades: 0,
    winRate: 0,
    investmentAmount: 0,
    profitLoss: 0
  });

  useEffect(() => {
    fetchInvestorStats();
    const interval = setInterval(fetchInvestorStats, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchInvestorStats = async () => {
    try {
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
    } catch (error) {
      console.error('Error fetching investor stats:', error);
    }
  };

  const handleClose = () => {
    navigate('/');
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'overview':
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
      case 'portfolio':
        return <InvestorPortfolio />;
      case 'signals':
        return <LiveSignals />;
      case 'trades':
        return <TradeHistory />;
      case 'journal':
        return <InvestorJournal />;
      case 'deposit':
      case 'withdraw':
        return <InvestorPayments />;
      case 'settings':
        return <InvestorSettings />;
      case 'profile':
        return <InvestorProfile />;
      default:
        return <div>Section not found</div>;
    }
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <InvestorSidebar 
          activeSection={activeSection} 
          onSectionChange={setActiveSection}
        />
        
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <SidebarTrigger />
                <div>
                  <h1 className="text-2xl font-bold">Waves Quant Engine</h1>
                  <p className="text-sm text-muted-foreground">
                    Multi-Asset Trading Platform - Investor Dashboard
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <Badge variant="outline" className="px-3 py-1">
                  <Activity className="h-4 w-4 mr-1" />
                  Live Trading
                </Badge>
                <ThemeToggle />
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
          </header>

          {/* Main Content */}
          <main className="flex-1 p-6 overflow-auto">
            {renderContent()}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
};

export default InvestorDashboard;
