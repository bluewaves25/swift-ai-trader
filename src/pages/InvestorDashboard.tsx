
import { useState, Suspense, lazy, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

import { InvestorSidebar } from "@/components/investor/InvestorSidebar";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { Activity, Menu, X, Bell, Calendar, Search, Plus, Folder, Play, Clock, Target, TrendingUp, Wallet, History, BookOpen, Brain, Users, CreditCard, DollarSign, Settings, User } from "lucide-react";
import DashboardOverview from "@/components/investor/DashboardOverview";
import InvestorPortfolio from "@/components/investor/InvestorPortfolio";
import LiveSignals from "@/components/trading/LiveSignals";
import TradeHistory from "@/components/trading/TradeHistory";
import InvestorJournal from "@/components/investor/InvestorJournal";
import InvestorSettings from "@/components/investor/InvestorSettings";
import InvestorProfile from "@/components/investor/InvestorProfile";
import InvestorPayments from "@/components/investor/InvestorPayments";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import SubscriptionManagement from '@/components/owner/SubscriptionManagement';
import PerformanceFees from '@/components/owner/PerformanceFees';
import axios from 'axios';
import StrategyMarketplace from '@/components/investor/StrategyMarketplace';
import AffiliateDashboard from '@/components/investor/AffiliateDashboard';
import { SupportChat } from "@/components/support/SupportChat";
// Lazy load payment components
const LazyPaymentForm = lazy(() => import("@/components/payments/PaymentForm").then(module => ({ default: module.PaymentForm })));
const LazyWithdrawForm = lazy(() => import("@/components/payments/PaymentForm").then(module => ({ default: module.PaymentForm })));

const InvestorDashboard = () => {
  const [activeSection, setActiveSection] = useState('overview');
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [subscriptionStatus, setSubscriptionStatus] = useState<any>(null);

  useEffect(() => {
    axios.get('/api/v1/billing/status', { params: { user_id: 'me' } }).then(res => setSubscriptionStatus(res.data));
  }, []);

  const isPremium = subscriptionStatus?.status === 'active' || subscriptionStatus?.trial;

  const renderContent = () => {
    switch (activeSection) {
      case 'overview':
        return <DashboardOverview />;
      case 'portfolio':
        return <InvestorPortfolio />;
      case 'signals':
        return isPremium ? <LiveSignals /> : <div className="text-red-500">Upgrade your subscription to access Live Signals.</div>;
      case 'trades':
        return isPremium ? <TradeHistory /> : <div className="text-red-500">Upgrade your subscription to access Trade History.</div>;
      case 'journal':
        return isPremium ? <InvestorJournal /> : <div className="text-red-500">Upgrade your subscription to access the Journal.</div>;
      case 'deposit':
        return (
          <Suspense fallback={<div className="animate-pulse bg-gray-200 rounded h-64"></div>}>
            <LazyPaymentForm transactionType="deposit" />
          </Suspense>
        );
      case 'withdraw':
        return (
          <Suspense fallback={<div className="animate-pulse bg-gray-200 rounded h-64"></div>}>
            <LazyWithdrawForm transactionType="withdrawal" />
          </Suspense>
        );
      case 'transactions':
        return <InvestorPayments />;
      case 'subscription':
        return <SubscriptionManagement />;
      case 'fees':
        return <PerformanceFees />;
      case 'settings':
        return <InvestorSettings />;
      case 'profile':
        return <InvestorProfile />;
      case 'marketplace':
        return isPremium ? <StrategyMarketplace isPremium={isPremium} /> : <div className="text-red-500">Upgrade your subscription to access the AI Strategy Marketplace.</div>;
      case 'affiliate':
        return <AffiliateDashboard />;
      default:
        return <div className="text-center text-muted-foreground text-xs md:text-sm">Section under development</div>;
    }
  };

  const renderOverviewWidgets = () => (
    <div className="space-y-6">
      {/* Row 1 - Portfolio & Trading Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Portfolio Balance Card */}
        <Card className="relative overflow-hidden">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <CardTitle className="text-lg font-semibold">Portfolio Balance</CardTitle>
                <CardDescription className="text-xs text-muted-foreground">
                  Total portfolio value
                </CardDescription>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg flex items-center justify-center">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <Wallet className="w-4 h-4 text-white" />
                </div>
              </div>
            </div>
            <Button size="icon" className="absolute bottom-4 right-4 w-10 h-10 rounded-full bg-blue-500 hover:bg-blue-600">
              <Plus className="w-4 h-4" />
            </Button>
          </CardContent>
        </Card>

        {/* Active Trades */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <Badge variant="outline" className="mb-2 text-xs">ACTIVE</Badge>
                <CardTitle className="text-lg font-semibold">Open Positions</CardTitle>
                <CardDescription className="text-xs text-muted-foreground">
                  Current market exposure
                </CardDescription>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <Button variant="link" className="p-0 h-auto text-blue-600 hover:text-blue-700">
              View positions
            </Button>
          </CardContent>
        </Card>

        {/* Live Signals */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <CardTitle className="text-lg font-semibold">Live Signals</CardTitle>
                <CardDescription className="text-xs text-muted-foreground">
                  AI trading signals
                </CardDescription>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Market Status */}
        <Card className="bg-blue-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <CardTitle className="text-lg font-semibold text-white">Market Status</CardTitle>
                <CardDescription className="text-xs text-blue-100">
                  Current market conditions
                </CardDescription>
              </div>
              <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-orange-300" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 2 - Performance & Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Performance Metrics</CardTitle>
            <div className="flex space-x-1">
              <Button variant="ghost" size="sm" className="text-xs px-2 py-1 h-auto bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                This week
              </Button>
              <Button variant="ghost" size="sm" className="text-xs px-2 py-1 h-auto">
                This month
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center">
                <span className="text-xs font-semibold text-green-700 dark:text-green-300">P</span>
              </div>
              <span className="text-xs font-medium">Portfolio P&L</span>
              <span className="ml-auto text-xs font-semibold text-green-600">+$2,450</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center">
                <span className="text-xs font-semibold text-blue-700 dark:text-blue-300">W</span>
              </div>
              <span className="text-xs font-medium">Win Rate</span>
              <span className="ml-auto text-xs font-semibold text-blue-600">76%</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900/20 rounded-full flex items-center justify-center">
                <span className="text-xs font-semibold text-purple-700 dark:text-purple-300">T</span>
              </div>
              <span className="text-xs font-medium">Total Trades</span>
              <span className="ml-auto text-xs font-semibold text-purple-600">156</span>
            </div>
          </CardContent>
        </Card>

        {/* Risk Metrics */}
        <Card className="text-center">
          <CardContent className="p-6">
            <div className="relative w-32 h-32 mx-auto mb-4">
              <div className="w-full h-full rounded-full border-8 border-gray-200 dark:border-gray-700 flex items-center justify-center">
                <div className="text-3xl font-bold text-blue-600">Low</div>
              </div>
              <div className="absolute inset-0 w-full h-full rounded-full border-8 border-transparent border-t-green-500 border-r-green-500 transform rotate-45"></div>
            </div>
            <CardTitle className="text-lg">Risk Level</CardTitle>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="bg-gradient-to-br from-purple-500 to-pink-600 text-white">
          <CardContent className="p-6">
            <CardTitle className="text-lg text-white mb-2">Quick Actions</CardTitle>
            <div className="space-y-3">
              <Button variant="outline" size="sm" className="w-full bg-white/20 text-white border-white/30 hover:bg-white/30">
                Deposit Funds
              </Button>
              <Button variant="outline" size="sm" className="w-full bg-white/20 text-white border-white/30 hover:bg-white/30">
                Withdraw
              </Button>
              <Button variant="outline" size="sm" className="w-full bg-white/20 text-white border-white/30 hover:bg-white/30">
                View Journal
              </Button>
            </div>
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

          <InvestorSidebar 
            activeSection={activeSection} 
            onSectionChange={setActiveSection}
            isMobileOpen={isMobileOpen}
            onMobileToggle={setIsMobileOpen}
          />
          
          {/* Main content wrapper */}
          <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
            {/* Fixed Header */}
            <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/95 p-4 shadow-sm flex-shrink-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div>
                    <p className="text-xs text-muted-foreground">Hello Dave, Welcome back</p>
                    <h1 className="text-2xl font-bold text-foreground">Your Trading Dashboard</h1>
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
            <SupportChat />
          </div>
        </div>
      </ErrorBoundary>
    );
};

export default InvestorDashboard;
