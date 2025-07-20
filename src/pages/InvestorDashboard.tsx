
import { useState, Suspense, lazy, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SidebarProvider } from "@/components/ui/sidebar";
import { InvestorSidebar } from "@/components/investor/InvestorSidebar";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { Activity, Menu, X } from "lucide-react";
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

          <InvestorSidebar 
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
                      Trading Dashboard
                    </h1>
                    <p className="text-xs text-muted-foreground truncate hidden sm:block">
                      Investment Management Platform
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

export default InvestorDashboard;
