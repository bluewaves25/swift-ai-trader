import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  BarChart3,
  Target,
  Users,
  Zap,
  AlertCircle,
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";
import { API_ENDPOINTS, apiCall } from "@/config/api";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface DashboardStats {
  totalUsers: number;
  totalTrades: number;
  totalRevenue: number;
  activeStrategies: number;
  aum: number;
  dailyPnL: number;
  winRate: number;
  activeUsers: number;
  is_running: boolean;
}

interface AUMData {
  date: string;
  aum: number;
  trades: number;
}

const OwnerDashboardOverview = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 0,
    totalTrades: 0,
    totalRevenue: 0,
    activeStrategies: 0,
    aum: 0,
    dailyPnL: 0,
    winRate: 0,
    activeUsers: 0,
    is_running: false
  });
  const [aumData, setAumData] = useState<AUMData[]>([]);
  const [loading, setLoading] = useState(true);
  const [engineStatus, setEngineStatus] = useState<DashboardStats | null>(null);

  useEffect(() => {
    fetchDashboardData();
    fetchEngineStatus();
    
    // Refresh data every 30 seconds
    const interval = setInterval(() => {
      fetchDashboardData();
      fetchEngineStatus();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch all stats from backend
      const statsRes: DashboardStats = await apiCall(API_ENDPOINTS.OWNER_DASHBOARD_STATS);
      setStats(statsRes);
      // Fetch AUM chart data from backend
      const aumRes = await apiCall(API_ENDPOINTS.OWNER_DASHBOARD_AUM);
      setAumData(Array.isArray(aumRes.data) ? aumRes.data : []);
    } catch (error) {
      setStats({
        totalUsers: 0,
        totalTrades: 0,
        totalRevenue: 0,
        activeStrategies: 0,
        aum: 0,
        dailyPnL: 0,
        winRate: 0,
        activeUsers: 0,
        is_running: false
      });
      setAumData([]);
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEngineStatus = async () => {
    try {
      const data: DashboardStats = await apiCall(API_ENDPOINTS.ENGINE_STATUS);
      setEngineStatus(data);
    } catch (error) {
      console.error('Error fetching engine status:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(1)}K`;
    }
    return `$${amount.toFixed(0)}`;
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-muted rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Platform Overview</h2>
        <p className="text-muted-foreground">Real-time platform performance and metrics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total AUM</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(stats.aum)}</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <ArrowUpRight className="h-3 w-3 mr-1 text-green-600" />
              +2.4% from last month
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily P&L</CardTitle>
            {stats.dailyPnL >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${stats.dailyPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(stats.dailyPnL)}
            </div>
            <div className="flex items-center text-xs text-muted-foreground">
              {stats.dailyPnL >= 0 ? (
                <ArrowUpRight className="h-3 w-3 mr-1 text-green-600" />
              ) : (
                <ArrowDownRight className="h-3 w-3 mr-1 text-red-600" />
              )}
              {stats.dailyPnL >= 0 ? '+' : ''}{((stats.dailyPnL / stats.aum) * 100).toFixed(2)}% today
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeUsers.toLocaleString()}</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <ArrowUpRight className="h-3 w-3 mr-1 text-green-600" />
              +12% from last week
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.winRate.toFixed(1)}%</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <ArrowUpRight className="h-3 w-3 mr-1 text-green-600" />
              +1.2% from last month
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AUM Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Assets Under Management (AUM)</CardTitle>
          <CardDescription>30-day AUM performance and trading activity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={aumData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`}
                />
                <Tooltip 
                  formatter={(value: any) => [`$${(value / 1000000).toFixed(2)}M`, 'AUM']}
                  labelFormatter={(label) => new Date(label).toLocaleDateString()}
                />
                <Area 
                  type="monotone" 
                  dataKey="aum" 
                  stroke="#3b82f6" 
                  fill="#3b82f6" 
                  fillOpacity={0.1}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Engine Status and Trading Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-blue-600" />
              Trading Engine Status
            </CardTitle>
            <CardDescription>Current engine performance and status</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Engine Status:</span>
              <Badge 
                variant={engineStatus?.is_running ? "default" : "secondary"}
                className={engineStatus?.is_running ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}
              >
                {engineStatus?.is_running ? "Running" : "Stopped"}
              </Badge>
            </div>
            
            {/* Add more fields here if you add them to DashboardStats and your backend returns them */}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-600" />
              Platform Metrics
            </CardTitle>
            <CardDescription>Key platform performance indicators</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Total Users:</span>
              <span className="font-semibold">{stats.totalUsers.toLocaleString()}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Total Trades:</span>
              <span className="font-semibold">{stats.totalTrades.toLocaleString()}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Total Revenue:</span>
              <span className="font-semibold">{formatCurrency(stats.totalRevenue)}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Active Strategies:</span>
              <span className="font-semibold">{stats.activeStrategies}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Avg. Daily Volume:</span>
              <span className="font-semibold">{formatCurrency(stats.totalTrades * 100)}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default OwnerDashboardOverview; 