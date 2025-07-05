
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
  X
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
const InvestorPayments = lazy(() => import("@/components/investor/InvestorPayments").then(module => ({ default: module.InvestorPayments })));
const InvestorSettings = lazy(() => import("@/components/investor/InvestorSettings"));
const InvestorProfile = lazy(() => import("@/components/investor/InvestorProfile"));

const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-64">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
  </div>
);

const InvestorDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { handleError } = useErrorHandler();
  const [activeSection, setActiveSection] = useState('overview');

  const handleClose = () => {
    navigate('/');
  };

  const renderContent = () => {
    const contentMap = {
      'overview': <DashboardOverview />,
      'portfolio': <InvestorPortfolio />,
      'signals': <LiveSignals />,
      'trades': <TradeHistory />,
      'journal': <InvestorJournal />,
      'payments': <InvestorPayments />,
      'settings': <InvestorSettings />,
      'profile': <InvestorProfile />
    };

    const Component = contentMap[activeSection as keyof typeof contentMap];
    
    if (!Component) {
      return <div className="text-center text-muted-foreground">Section not found</div>;
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
          <InvestorSidebar 
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
                    <h1 className="text-2xl font-bold">Waves Quant Engine</h1>
                    <p className="text-sm text-muted-foreground">
                      Multi-Asset Trading Platform - Investor Dashboard
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <Badge variant="outline" className="px-3 py-1">
                    <Activity className="h-4 w-4 mr-1" />
                    Live Trading
                  </Badge>
                  <ThemeToggle />
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleClose}
                    className="h-8 w-8"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 p-6 overflow-auto">
              {renderContent()}
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
