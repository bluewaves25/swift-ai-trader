
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

import { OwnerSidebar } from "@/components/owner/OwnerSidebar";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { Activity, Users, DollarSign, TrendingUp, Menu, X, Bell, Calendar, Search, Plus, Folder, Play, Clock, Target, BarChart3, Shield, Brain, Cpu } from "lucide-react";
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
    activeStrategies: 0,
    aum: 0,
    is_running: false,
    dailyPnL: 0,
    winRate: 0,
    activeUsers: 0
  });
  const [recentLogs, setRecentLogs] = useState<any[]>([]);
  const [subscriptionStatus, setSubscriptionStatus] = useState<any>(null);

  useEffect(() => {
    // Mock data for demo
    setStats({
      totalUsers: 2847,
      totalTrades: 156429,
      totalRevenue: 2847592,
      activeStrategies: 12,
      aum: 12345678,
      is_running: true,
      dailyPnL: 123.45,
      winRate: 65.2,
      activeUsers: 1500
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

  const renderOverviewWidgets = () => (
    <div className="space-y-6">
      {/* Row 1 - Key Platform Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total AUM Card */}
        <Card className="relative overflow-hidden">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <CardTitle className="text-lg font-semibold">Total AUM</CardTitle>
                <CardDescription className="text-xs text-muted-foreground">
                  ${stats.aum?.toLocaleString() || '0'} managed
                </CardDescription>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <DollarSign className="w-4 h-4 text-white" />
                </div>
              </div>
            </div>
            <Button size="icon" className="absolute bottom-4 right-4 w-10 h-10 rounded-full bg-blue-500 hover:bg-blue-600">
              <TrendingUp className="w-4 h-4" />
            </Button>
          </CardContent>
        </Card>

        {/* Trading Engine Status */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <Badge variant="outline" className="mb-2 text-xs">
                  {stats.is_running ? 'ACTIVE' : 'STOPPED'}
                </Badge>
                <CardTitle className="text-lg font-semibold">Trading Engine</CardTitle>
                <CardDescription className="text-xs text-muted-foreground">
                  {stats.is_running ? 'Running smoothly' : 'Engine stopped'}
                </CardDescription>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <Cpu className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <Button variant="link" className="p-0 h-auto text-blue-600 hover:text-blue-700">
              Manage engine
            </Button>
          </CardContent>
        </Card>

        {/* Active Strategies */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <CardTitle className="text-lg font-semibold">Active Strategies</CardTitle>
                <CardDescription className="text-xs text-muted-foreground">
                  {stats.activeStrategies} strategies running
                </CardDescription>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Daily Performance */}
        <Card className="bg-blue-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <CardTitle className="text-lg font-semibold text-white">Daily P&L</CardTitle>
                <CardDescription className="text-xs text-blue-100">
                  {stats.dailyPnL >= 0 ? 'Profitable day' : 'Loss today'}
                </CardDescription>
              </div>
              <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-orange-300" />
              </div>
            </div>
            <div className="text-2xl font-bold text-white">
              ${stats.dailyPnL?.toFixed(2) || '0.00'}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 2 - Platform Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Platform Users</CardTitle>
            <div className="flex space-x-1">
              <Button variant="ghost" size="sm" className="text-xs px-2 py-1 h-auto bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                Total
              </Button>
              <Button variant="ghost" size="sm" className="text-xs px-2 py-1 h-auto">
                Active
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center">
                <span className="text-xs font-semibold text-green-700 dark:text-green-300">T</span>
              </div>
              <span className="text-xs font-medium">Total Users</span>
              <span className="ml-auto text-xs font-semibold text-green-600">{stats.totalUsers?.toLocaleString() || '0'}</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center">
                <span className="text-xs font-semibold text-blue-700 dark:text-blue-300">A</span>
              </div>
              <span className="text-xs font-medium">Active Users</span>
              <span className="ml-auto text-xs font-semibold text-blue-600">{stats.activeUsers?.toLocaleString() || '0'}</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900/20 rounded-full flex items-center justify-center">
                <span className="text-xs font-semibold text-purple-700 dark:text-purple-300">R</span>
              </div>
              <span className="text-xs font-medium">Revenue</span>
              <span className="ml-auto text-xs font-semibold text-purple-600">${stats.totalRevenue?.toLocaleString() || '0'}</span>
            </div>
          </CardContent>
        </Card>

        {/* Win Rate Gauge */}
        <Card className="text-center">
          <CardContent className="p-6">
            <div className="relative w-32 h-32 mx-auto mb-4">
              <div className="w-full h-full rounded-full border-8 border-gray-200 dark:border-gray-700 flex items-center justify-center">
                <div className="text-3xl font-bold text-blue-600">{stats.winRate?.toFixed(1) || '0'}%</div>
              </div>
              <div className="absolute inset-0 w-full h-full rounded-full border-8 border-transparent border-t-green-500 border-r-green-500 transform rotate-45"></div>
            </div>
            <CardTitle className="text-lg">Win Rate</CardTitle>
          </CardContent>
        </Card>

        {/* Trading Summary */}
        <Card className="bg-gradient-to-br from-green-500 to-blue-600 text-white">
          <CardContent className="p-6">
            <CardTitle className="text-lg text-white mb-2">Trading Summary</CardTitle>
            <div className="text-4xl font-bold text-white mb-2">{stats.totalTrades?.toLocaleString() || '0'}</div>
            <CardDescription className="text-sm text-green-100 mb-4">
              Total trades executed
            </CardDescription>
            <Button variant="link" className="p-0 h-auto text-green-100 hover:text-white">
              view details
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );

  return (
    <ErrorBoundary>
      <div className="flex h-screen w-screen max-w-none overflow-hidden bg-background">
          {/* Mobile Menu Button */}
          <Button
            variant="outline"
            size="icon"
            className="fixed top-1 left-1 z-50 md:hidden h-5 w-5 text-xs"
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
          
          {/* Main content wrapper */}
          <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
            {/* Fixed Header */}
            <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/95 p-4 shadow-sm flex-shrink-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div>
                    <p className="text-xs text-muted-foreground">Hello Dave, Welcome back</p>
                    <h1 className="text-2xl font-bold text-foreground">Your Dashboard is updated</h1>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Button variant="ghost" size="icon">
                    <Bell className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <Calendar className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <Search className="h-3 w-3" />
                  </Button>
                  <ThemeToggle />
                </div>
              </div>
            </header>
            
            {/* Main Content */}
            <main className="flex-1 min-h-0 overflow-auto bg-background">
              <div className="main-margin mx-auto section-gap">
                {activeSection === 'overview' ? renderOverviewWidgets() : renderContent()}
              </div>
            </main>
          </div>
        </div>
      </ErrorBoundary>
    );
};

export default OwnerDashboard;
