
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "@/components/theme/theme-provider";
import { AuthProvider } from "@/contexts/AuthContext";
import { useAuth } from "@/hooks/useAuth";
import AuthPage from "@/pages/AuthPage";
import OwnerDashboard from "@/pages/OwnerDashboard";
import InvestorDashboard from "@/pages/InvestorDashboard";
import LoadingScreen from "@/components/LoadingScreen";

const queryClient = new QueryClient();

const ProtectedRoute = ({ children, requiredRole }: { children: React.ReactNode; requiredRole?: 'owner' | 'investor' }) => {
  const { user, loading, userRole } = useAuth();
  
  if (loading) return <LoadingScreen />;
  if (!user) return <Navigate to="/auth" replace />;
  if (requiredRole && userRole !== requiredRole) return <Navigate to="/unauthorized" replace />;
  
  return <>{children}</>;
};

const AppRoutes = () => {
  const { user, loading } = useAuth();

  if (loading) return <LoadingScreen />;

  return (
    <Routes>
      <Route 
        path="/auth" 
        element={user ? <Navigate to="/" replace /> : <AuthPage />} 
      />
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <DashboardRouter />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/owner" 
        element={
          <ProtectedRoute requiredRole="owner">
            <OwnerDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/investor" 
        element={
          <ProtectedRoute requiredRole="investor">
            <InvestorDashboard />
          </ProtectedRoute>
        } 
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const DashboardRouter = () => {
  const { userRole } = useAuth();
  
  if (userRole === 'owner') {
    return <Navigate to="/owner" replace />;
  } else {
    return <Navigate to="/investor" replace />;
  }
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider defaultTheme="dark" storageKey="waves-quant-theme">
      <TooltipProvider>
        <AuthProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </AuthProvider>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
