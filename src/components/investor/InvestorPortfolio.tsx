
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { 
  Wallet, 
  TrendingUp, 
  TrendingDown, 
  ArrowUpRight, 
  ArrowDownLeft,
  DollarSign,
  Receipt
} from "lucide-react";
import { apiService, Portfolio, Performance } from '@/services/api';

const InvestorPortfolio = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [performance, setPerformance] = useState<Performance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPortfolio = async () => {
      setLoading(true);
      setError(null);
      try {
        const { data: portfolioData } = await apiService.getPortfolio();
        setPortfolio(portfolioData);
        const { data: perfData } = await apiService.getPortfolioPerformance();
        setPerformance(perfData);
      } catch (err) {
        setError('Failed to load portfolio');
        toast.error('Failed to load portfolio');
      } finally {
        setLoading(false);
      }
    };
    fetchPortfolio();
  }, []);

  if (loading) return <div className="p-6">Loading portfolio...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;
  if (!portfolio) return <div className="p-6">No portfolio data found.</div>;

  // Render portfolio and performance data here
  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-2">Portfolio Overview</h2>
      <pre>{JSON.stringify(portfolio, null, 2)}</pre>
      <h3 className="text-lg font-semibold mt-4 mb-2">Performance</h3>
      <pre>{JSON.stringify(performance, null, 2)}</pre>
    </div>
  );
};

export default InvestorPortfolio;
