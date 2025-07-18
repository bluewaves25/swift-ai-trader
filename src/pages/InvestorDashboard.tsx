
import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { InvestorSidebar } from "@/components/investor/InvestorSidebar";
import { SupportChat } from "@/components/support/SupportChat";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { useErrorHandler } from "@/hooks/useErrorHandler";
import { 
  Activity, 
  X,
  Menu
} from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { useNavigate } from "react-router-dom";

// Lazy load components for better performance
import { lazy, Suspense } from "react";

const DashboardOverview = lazy(() => import("@/components/investor/DashboardOverview"));
const InvestorPortfolio = lazy(() => import("@/components/investor/InvestorPortfolio"));
const LiveSignals = lazy(() => import("@/components/trading/LiveSignals"));
const TradeHistory = lazy(() => import("@/components/trading/TradeHistory"));
const InvestorJournal = lazy(() => import("@/components/investor/InvestorJournal"));
const DepositForm = lazy(() => import("@/components/payments/PaymentForm"));
const WithdrawalForm = lazy(() => import("@/components/payments/PaymentForm"));
const TransactionsList = lazy(() => import("@/components/payments/TransactionsList").then(module => ({ default: module.TransactionsList })));
const InvestorSettings = lazy(() => import("@/components/investor/InvestorSettings"));
const InvestorProfile = lazy(() => import("@/components/investor/InvestorProfile"));

const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-32 md:h-64">
    <div className="animate-spin rounded-full h-6 w-6 md:h-8 md:w-8 border-b-2 border-primary"></div>
  </div>
);

const InvestorDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { handleError } = useErrorHandler();
  const [activeSection, setActiveSection] = useState('overview');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const renderContent = () => {
    const contentMap = {
      'overview': <DashboardOverview />,
      'portfolio': <InvestorPortfolio />,
      'signals': <LiveSignals />,
      'trades': <TradeHistory />,
      'journal': <InvestorJournal />,
      'deposit': <DepositForm transactionType="deposit" />,
      'withdraw': <WithdrawalForm transactionType="withdrawal" />,
      'transactions': <TransactionsList />,
      'settings': <InvestorSettings />,
      'profile': <InvestorProfile />
    };

    const Component = contentMap[activeSection as keyof typeof contentMap];
    
    if (!Component) {
      return <div className="text-center text-muted-foreground text-sm">Section not found</div>;
    }

    return (
      <Suspense fallback={<LoadingSpinner />}>
        {Component}
      </Suspense>
    );
  };

  return (
    <ErrorBoundary>
      <SidebarProvider>
        <div className="min-h-screen flex w-full bg-background">
          {/* Mobile Overlay */}
          {isMobileSidebarOpen && (
            <div 
              className="fixed inset-0 bg-black/50 z-40 md:hidden" 
              onClick={() => setIsMobileSidebarOpen(false)} 
            />
          )}

          <InvestorSidebar 
            activeSection={activeSection} 
            onSectionChange={(section) => {
              setActiveSection(section);
              setIsMobileSidebarOpen(false);
            }}
            isMobileOpen={isMobileSidebarOpen}
            onMobileToggle={setIsMobileSidebarOpen}
          />
          
          <div className="flex-1 flex flex-col min-w-0 max-w-full">
            {/* Fixed Header */}
            <header className="sticky top-0 z-30 border-b bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/80 p-2 md:p-4 shadow-sm">
              <div className="flex items-center justify-between">
                {/* Mobile Menu Button */}
                <Button
                  variant="ghost"
                  size="sm"
                  className="md:hidden h-8 w-8 p-0"
                  onClick={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
                >
                  {isMobileSidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
                </Button>

                <div className="flex items-center space-x-2 md:space-x-4 min-w-0 flex-1 md:flex-initial">
                  <div className="min-w-0">
                    <h1 className="text-sm md:text-xl lg:text-2xl font-bold truncate bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      Waves Quant Engine
                    </h1>
                    <p className="text-xs md:text-sm text-muted-foreground truncate">
                      Multi-Asset Trading Platform - Investor Dashboard
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-1 md:space-x-4 flex-shrink-0">
                  <Badge variant="outline" className="px-1 md:px-3 py-1 text-xs border-green-200 text-green-700 bg-green-50 dark:border-green-800 dark:text-green-400 dark:bg-green-900/20">
                    <Activity className="h-3 w-3 md:h-4 md:w-4 mr-1" />
                    <span className="hidden sm:inline">Live </span>Trading
                  </Badge>
                  <ThemeToggle />
                </div>
              </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 p-2 md:p-4 lg:p-6 overflow-auto bg-background">
              <div className="max-w-full mx-auto animate-fade-in">
                {renderContent()}
              </div>
            </main>
          </div>

          {/* Support Chat */}
          <SupportChat />
        </div>
      </SidebarProvider>
    </ErrorBoundary>
  );
};

export default InvestorDashboard;
