
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SidebarProvider } from "@/components/ui/sidebar";
import { OwnerSidebar } from "@/components/owner/OwnerSidebar";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { Activity, Users, DollarSign, TrendingUp, Menu, X } from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { EngineControl } from "@/components/owner/EngineControl";
import { UserManagement } from "@/components/owner/UserManagement";
import { PerformanceAnalytics } from "@/components/owner/PerformanceAnalytics";
import { RiskManagement } from "@/components/owner/RiskManagement";
import { StrategiesManagement } from "@/components/owner/StrategiesManagement";
import { OwnerSettings } from "@/components/owner/OwnerSettings";
import LiveSignals from "@/components/owner/LiveSignals";
import TradeHistory from "@/components/owner/TradeHistory";

const OwnerDashboard = () => {
  const [activeSection, setActiveSection] = useState('overview');
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalTrades: 0,
    totalRevenue: 0,
    activeStrategies: 0
  });
  const [recentLogs, setRecentLogs] = useState<any[]>([]);

  useEffect(() => {
    // Mock data for demo
    setStats({
      totalUsers: 2847,
      totalTrades: 156429,
      totalRevenue: 2847592,
      activeStrategies: 12
    });
    
    setRecentLogs([
      { id: 1, timestamp: new Date().toISOString(), level: 'info', message: 'Engine started successfully' },
      { id: 2, timestamp: new Date().toISOString(), level: 'warning', message: 'High volatility detected in EUR/USD' },
      { id: 3, timestamp: new Date().toISOString(), level: 'info', message: 'New user registered' }
    ]);
  }, []);

  const renderContent = () => {
    switch (activeSection) {
      case 'overview':
        return (
          <div className="space-y-2 md:space-y-4">
            {/* Stats Overview */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 md:gap-4">
              <Card className="p-2 md:p-4">
                <CardContent className="p-1 md:p-2">
                  <div className="flex items-center space-x-1 md:space-x-2">
                    <Users className="h-3 w-3 md:h-4 md:w-4 text-blue-600" />
                    <div>
                      <p className="text-xs md:text-sm font-medium">Total Users</p>
                      <p className="text-lg md:text-2xl font-bold">{stats.totalUsers.toLocaleString()}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="p-2 md:p-4">
                <CardContent className="p-1 md:p-2">
                  <div className="flex items-center space-x-1 md:space-x-2">
                    <TrendingUp className="h-3 w-3 md:h-4 md:w-4 text-green-600" />
                    <div>
                      <p className="text-xs md:text-sm font-medium">Total Trades</p>
                      <p className="text-lg md:text-2xl font-bold">{stats.totalTrades.toLocaleString()}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="p-2 md:p-4">
                <CardContent className="p-1 md:p-2">
                  <div className="flex items-center space-x-1 md:space-x-2">
                    <DollarSign className="h-3 w-3 md:h-4 md:w-4 text-purple-600" />
                    <div>
                      <p className="text-xs md:text-sm font-medium">Revenue</p>
                      <p className="text-lg md:text-2xl font-bold">${(stats.totalRevenue / 1000000).toFixed(1)}M</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="p-2 md:p-4">
                <CardContent className="p-1 md:p-2">
                  <div className="flex items-center space-x-1 md:space-x-2">
                    <Activity className="h-3 w-3 md:h-4 md:w-4 text-orange-600" />
                    <div>
                      <p className="text-xs md:text-sm font-medium">Strategies</p>
                      <p className="text-lg md:text-2xl font-bold">{stats.activeStrategies}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader className="p-2 md:p-4">
                <CardTitle className="text-sm md:text-base">Recent System Logs</CardTitle>
                <CardDescription className="text-xs md:text-sm">Latest engine activity and alerts</CardDescription>
              </CardHeader>
              <CardContent className="p-2 md:p-4">
                <div className="space-y-1 md:space-y-2 max-h-32 md:max-h-48 overflow-y-auto">
                  {recentLogs.map((log) => (
                    <div key={log.id} className="flex items-center justify-between text-xs md:text-sm p-1 md:p-2 rounded bg-muted/50">
                      <span className="truncate flex-1">{log.message}</span>
                      <Badge variant={log.level === 'warning' ? 'destructive' : 'default'} className="text-xs ml-2">
                        {log.level}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        );
      case 'engine':
        return <EngineControl />;
      case 'users':
        return <UserManagement />;
      case 'performance':
        return <PerformanceAnalytics />;
      case 'risk':
        return <RiskManagement />;
      case 'strategies':
        return <StrategiesManagement />;
      case 'signals':
        return <LiveSignals />;
      case 'trades':
        return <TradeHistory />;
      case 'settings':
        return <OwnerSettings />;
      default:
        return <div className="text-center text-muted-foreground text-xs md:text-sm">Section under development</div>;
    }
  };

  return (
    <ErrorBoundary>
      <SidebarProvider>
        <div className="min-h-screen flex w-full bg-background">
          {/* Mobile Menu Button */}
          <Button
            variant="outline"
            size="icon"
            className="fixed top-1 left-1 z-50 md:hidden h-6 w-6 text-xs"
            onClick={() => setIsMobileOpen(!isMobileOpen)}
          >
            {isMobileOpen ? <X className="h-2.5 w-2.5" /> : <Menu className="h-2.5 w-2.5" />}
          </Button>

          {/* Mobile Overlay */}
          {isMobileOpen && (
            <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setIsMobileOpen(false)} />
          )}

          <OwnerSidebar 
            activeSection={activeSection} 
            onSectionChange={setActiveSection}
            isMobileOpen={isMobileOpen}
            onMobileToggle={setIsMobileOpen}
          />
          
          <div className="flex-1 flex flex-col min-w-0 max-w-full">
            {/* Fixed Header */}
            <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/95 p-1 md:p-2 shadow-sm flex-shrink-0">
              <div className="flex items-center justify-between ml-6 md:ml-0">
                <div className="flex items-center space-x-1 min-w-0">
                  <div className="min-w-0">
                    <h1 className="text-xs md:text-base lg:text-lg font-bold truncate bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      Owner Dashboard
                    </h1>
                    <p className="text-xs text-muted-foreground truncate hidden sm:block">
                      Platform Management & Control
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-1 flex-shrink-0">
                  <Badge variant="outline" className="px-1 py-0 text-xs border-green-200 text-green-700 bg-green-50 dark:border-green-800 dark:text-green-400 dark:bg-green-900/20">
                    <Activity className="h-2 w-2 mr-0.5" />
                    <span className="hidden sm:inline text-xs">Active</span>
                  </Badge>
                  <ThemeToggle />
                </div>
              </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 p-1 md:p-2 lg:p-3 overflow-auto bg-background">
              <div className="max-w-full mx-auto">
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
