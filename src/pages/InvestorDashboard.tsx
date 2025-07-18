
import { useState, Suspense, lazy } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SidebarProvider } from "@/components/ui/sidebar";
import { InvestorSidebar } from "@/components/investor/InvestorSidebar";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { Activity, Menu, X } from "lucide-react";
import DashboardOverview from "@/components/investor/DashboardOverview";
import InvestorPortfolio from "@/components/investor/InvestorPortfolio";
import { LiveSignals } from "@/components/trading/LiveSignals";
import { TradeHistory } from "@/components/trading/TradeHistory";
import InvestorJournal from "@/components/investor/InvestorJournal";
import InvestorSettings from "@/components/investor/InvestorSettings";
import InvestorProfile from "@/components/investor/InvestorProfile";
import InvestorPayments from "@/components/investor/InvestorPayments";
import { ThemeToggle } from "@/components/theme/theme-toggle";

// Lazy load payment components
const LazyPaymentForm = lazy(() => import("@/components/payments/PaymentForm").then(module => ({ default: module.PaymentForm })));
const LazyWithdrawForm = lazy(() => import("@/components/payments/PaymentForm").then(module => ({ default: module.PaymentForm })));

const InvestorDashboard = () => {
  const [activeSection, setActiveSection] = useState('overview');
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const renderContent = () => {
    switch (activeSection) {
      case 'overview':
        return <DashboardOverview />;
      case 'portfolio':
        return <InvestorPortfolio />;
      case 'signals':
        return <LiveSignals />;
      case 'trades':
        return <TradeHistory />;
      case 'journal':
        return <InvestorJournal />;
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
      case 'settings':
        return <InvestorSettings />;
      case 'profile':
        return <InvestorProfile />;
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
            className="fixed top-2 left-2 z-50 md:hidden h-7 w-7"
            onClick={() => setIsMobileOpen(!isMobileOpen)}
          >
            {isMobileOpen ? <X className="h-3 w-3" /> : <Menu className="h-3 w-3" />}
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
            <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/80 p-2 md:p-3 shadow-sm flex-shrink-0">
              <div className="flex items-center justify-between ml-8 md:ml-0">
                <div className="flex items-center space-x-2 min-w-0">
                  <div className="min-w-0">
                    <h1 className="text-sm md:text-lg lg:text-xl font-bold truncate bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      Trading Dashboard
                    </h1>
                    <p className="text-xs text-muted-foreground truncate">
                      Investment Management Platform
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-1 md:space-x-2 flex-shrink-0">
                  <Badge variant="outline" className="px-1 md:px-2 py-0.5 text-xs border-green-200 text-green-700 bg-green-50 dark:border-green-800 dark:text-green-400 dark:bg-green-900/20">
                    <Activity className="h-2 w-2 md:h-3 md:w-3 mr-1" />
                    <span className="hidden sm:inline text-xs">Trading </span>Active
                  </Badge>
                  <ThemeToggle />
                </div>
              </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 p-2 md:p-3 lg:p-4 overflow-auto bg-background">
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
