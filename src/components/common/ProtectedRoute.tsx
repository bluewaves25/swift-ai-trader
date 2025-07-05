import { ReactNode, useEffect } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  useEffect(() => {
    if (!loading && !user) {
      toast.error("Please sign in to access this page");
    }
  }, [user, loading]);

  if (loading) {
    // Show loading spinner while checking authentication
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    // Redirect to login page with return URL
    return <Navigate to="/auth" state={{ from: location.pathname }} replace />;
  }

  // User is authenticated, render the protected content
  return <>{children}</>;
};

export default ProtectedRoute;

// Example useAuth hook