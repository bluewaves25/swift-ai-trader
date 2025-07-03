import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/components/theme/theme-provider";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import LoadingScreen from "@/components/LoadingScreen";
import AuthPage from "@/pages/AuthPage";
import Index from "@/pages/Index";
import OwnerDashboard from "@/pages/OwnerDashboard";
import InvestorDashboard from "@/pages/InvestorDashboard";
import NotFound from "@/pages/NotFound";
import "./App.css";

const queryClient = new QueryClient();

function AppRoutes() {
  const { user, loading, userRole } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Routes>
      <Route path="/auth" element={
        user ? (
          <Navigate to={userRole === 'owner' ? '/owner' : '/investor'} replace />
        ) : (
          <AuthPage />
        )
      } />
      
      <Route path="/" element={
        user ? (
          <Navigate to={userRole === 'owner' ? '/owner' : '/investor'} replace />
        ) : (
          <Index />
        )
      } />

      <Route path="/owner" element={
        user && userRole === 'owner' ? (
          <OwnerDashboard />
        ) : (
          <Navigate to="/auth" replace />
        )
      } />

      <Route path="/investor" element={
        user && userRole === 'investor' ? (
          <InvestorDashboard />
        ) : (
          <Navigate to="/auth" replace />
        )
      } />

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="waves-quant-theme">
        <AuthProvider>
          <Router>
            <AppRoutes />
            <Toaster />
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
