import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { OwnerSidebar } from "@/components/owner/OwnerSidebar";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { useErrorHandler } from "@/hooks/useErrorHandler";
import { 
  Activity,
  Users,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  Play,
  Pause
} from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { EngineControl } from "@/components/owner/EngineControl";
import { StrategiesManagement } from "@/components/owner/StrategiesManagement";
import { RiskManagement } from "@/components/owner/RiskManagement";
import { UserManagement } from "@/components/owner/UserManagement";
import { PerformanceAnalytics } from "@/components/owner/PerformanceAnalytics";
import { LiveSignals } from "@/components/owner/LiveSignals";
import { TradeHistory } from "@/components/owner/TradeHistory";
import { OwnerSettings } from "@/components/owner/OwnerSettings";

const OwnerDashboard = () => {
  const { user } = useAuth();
  const { handleError } = useErrorHandler();
  const [activeSection, setActiveSection] = useState('overview');
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalTrades: 0,
    totalRevenue: 0,
    systemStatus: 'active'
  });

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      // Fetch the count of users excluding owners
      const { count: userCount, error: userError } = await supabase
        .from('users')
        .select('id', { count: 'exact', head: true })
        .neq('role', 'owner');

      // Fetch the count of trades from the trades table
      const { count: tradeCount, error: tradeError } = await supabase
        .from('trades')
        .select('id', { count: 'exact', head: true });

      // Fetch portfolio data for revenue calculation
      const { data: portfolioData, error: portfolioError } = await supabase
        .from('portfolios')
        .select('total_balance, realized_pnl');

      if (userError) {
        console.error('User count error:', userError);
        handleError(userError);
      }
      if (tradeError) {
        console.error('Trade count error:', tradeError);
        handleError(tradeError);
      }
      if (portfolioError) {
        console.error('Portfolio error:', portfolioError);
        handleError(portfolioError);
      }

      const totalRevenue = portfolioData?.reduce((sum, portfolio) => 
        sum + (portfolio.realized_pnl || 0), 0) || 0;

      setStats({
        totalUsers: userCount || 0,
        totalTrades: tradeCount || 0,
        totalRevenue,
        systemStatus: 'active'
      });
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      handleError(error);
    }
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'overview':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-3xl font-bold tracking-tight">Dashboard Overview</h2>
              <div className="flex gap-2">
                <Button size="sm" className="bg-green-600 hover:bg-green-700">
                  <Play className="h-4 w-4 mr-2" />
                  Start Engine
                </Button>
                <Button size="sm" variant="destructive">
                  <Pause className="h-4 w-4 mr-2" />
                  Stop Engine
                </Button>
              </div>
            </div>
            
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalUsers}</div>
                </CardContent>
              </Card>
              
              <Card className="transition-all duration-300 hover:shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalTrades}</div>
                </CardContent>
              </Card>
              
              <Card className="transition-all duration-300 hover:shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">${stats.totalRevenue}</div>
                </CardContent>
              </Card>
              
              <Card className="transition-all duration-300 hover:shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">System Status</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <Badge variant="outline" className="text-green-600">
                    {stats.systemStatus}
                  </Badge>
                </CardContent>
              </Card>
            </div>
          </div>
        );
      case 'engine':
        return <EngineControl />;
      case 'signals':
        return <LiveSignals />;
      case 'strategies':
        return <StrategiesManagement />;
      case 'risk':
        return <RiskManagement />;
      case 'analytics':
        return <PerformanceAnalytics />;
      case 'users':
        return <UserManagement />;
      case 'trades':
        return <TradeHistory />;
      case 'settings':
        return <OwnerSettings />;
      default:
        return <div className="text-center text-muted-foreground">Section under development</div>;
    }
  };

  return (
    <ErrorBoundary>
      <SidebarProvider>
        <div className="min-h-screen flex w-full bg-background">
          <div className="hidden md:block fixed inset-y-0 z-50">
            <OwnerSidebar 
              activeSection={activeSection} 
              onSectionChange={setActiveSection}
            />
          </div>
          
          <div className="flex-1 flex flex-col md:pl-64">
            {/* Mobile sidebar */}
            <div className="md:hidden fixed inset-y-0 z-50 w-full">
              <OwnerSidebar 
                activeSection={activeSection} 
                onSectionChange={setActiveSection}
              />
            </div>
            
            {/* Header - Fixed */}
            <header className="sticky top-0 z-40 border-b bg-card/80 backdrop-blur-md supports-[backdrop-filter]:bg-card/80 p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <SidebarTrigger className="md:hidden" />
                  <div>
                    <h1 className="text-xl md:text-2xl font-bold">Owner Dashboard</h1>
                    <p className="text-xs md:text-sm text-muted-foreground">
                      System Management & Analytics
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 md:space-x-4">
                  <Badge variant="outline" className="px-2 py-1 text-xs md:text-sm">
                    <Activity className="h-3 w-3 md:h-4 md:w-4 mr-1" />
                    <span className="hidden sm:inline">System </span>Active
                  </Badge>
                  <ThemeToggle />
                </div>
              </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 p-3 md:p-6 overflow-auto bg-background">
              <div className="max-w-full">
                {renderContent()}
              </div>
            </main>
          </div>
        </div>
      </SidebarProvider>
    </ErrorBoundary>
  );
};

export default OwnerDashboard;
