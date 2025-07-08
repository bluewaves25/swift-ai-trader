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
      // Fetch the count of users from the users table
      const { count: userCount, error: userError } = await supabase
        .from('users')
        .select('id', { count: 'exact', head: true });

      // Fetch the count of trades from the trades table
      const { count: tradeCount, error: tradeError } = await supabase
        .from('trades')
        .select('id', { count: 'exact', head: true });

      if (userError) throw userError;
      if (tradeError) throw tradeError;

      setStats({
        totalUsers: userCount || 0,
        totalTrades: tradeCount || 0,
        totalRevenue: 0,
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
      default:
        return <div className="text-center text-muted-foreground">Section under development</div>;
    }
  };

  return (
    <ErrorBoundary>
      <SidebarProvider>
        <div className="min-h-screen flex w-full bg-background">
          <OwnerSidebar 
            activeSection={activeSection} 
            onSectionChange={setActiveSection}
          />
          
          <div className="flex-1 flex flex-col">
            {/* Header */}
            <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div>
                    <h1 className="text-2xl font-bold">Owner Dashboard</h1>
                    <p className="text-sm text-muted-foreground">
                      System Management & Analytics
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <Badge variant="outline" className="px-3 py-1">
                    <Activity className="h-4 w-4 mr-1" />
                    System Active
                  </Badge>
                  <ThemeToggle />
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
    </ErrorBoundary>
  );
};

export default OwnerDashboard;
