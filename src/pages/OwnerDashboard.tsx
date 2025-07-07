
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
  AlertTriangle
} from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";

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
      const [usersResult, tradesResult] = await Promise.all([
        supabase.from('users').select('id', { count: 'exact' }),
        supabase.from('trades').select('id', { count: 'exact' })
      ]);

      setStats({
        totalUsers: usersResult.count || 0,
        totalTrades: tradesResult.count || 0,
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
            <h2 className="text-3xl font-bold tracking-tight">Dashboard Overview</h2>
            
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalUsers}</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalTrades}</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">${stats.totalRevenue}</div>
                </CardContent>
              </Card>
              
              <Card>
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
                  <SidebarTrigger />
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
