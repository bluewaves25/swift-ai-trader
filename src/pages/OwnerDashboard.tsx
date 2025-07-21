
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
import { LiveSignals } from "@/components/owner/LiveSignals";
import { TradeHistory } from "@/components/owner/TradeHistory";
import SubscriptionManagement from '@/components/owner/SubscriptionManagement';
import OwnerDashboardOverview from '@/components/owner/OwnerDashboardOverview';
import apiService from '@/services/api';
import axios from 'axios';

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
  const [subscriptionStatus, setSubscriptionStatus] = useState<any>(null);

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
    axios.get('/api/v1/billing/status', { params: { user_id: 'me' } }).then(res => setSubscriptionStatus(res.data));
  }, []);

  const isPremium = subscriptionStatus?.status === 'active' || subscriptionStatus?.trial;

  const renderContent = () => {
    switch (activeSection) {
      case 'overview':
        return <OwnerDashboardOverview />;
      case 'subscription':
        return <SubscriptionManagement />;
      case 'engine':
        return isPremium ? <EngineControl /> : <div className="text-red-500">Upgrade your subscription to access the Trading Engine.</div>;
      case 'users':
        return <UserManagement />;
      case 'performance':
        return <PerformanceAnalytics />;
      case 'risk':
        return <RiskManagement />;
      case 'strategies':
        return isPremium ? <StrategiesManagement /> : <div className="text-red-500">Upgrade your subscription to access Strategies Management.</div>;
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
        <div className="flex h-screen w-screen max-w-none overflow-hidden bg-background">
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
          />
          {/* Main content wrapper: flex column, header sticky, main scrollable */}
          <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
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
            {/* Main Content (scrollable) */}
            <main className="flex-1 min-h-0 overflow-auto bg-background">
              <div className="main-margin mx-auto section-gap">
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
