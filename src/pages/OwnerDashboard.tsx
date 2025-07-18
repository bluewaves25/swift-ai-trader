
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { SidebarProvider } from "@/components/ui/sidebar";
import { OwnerSidebar } from "@/components/owner/OwnerSidebar";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { useErrorHandler } from "@/hooks/useErrorHandler";
import { 
  Activity,
  Users,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  Play,
  Pause
} from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { EngineControl } from "@/components/owner/EngineControl";
import { StrategiesManagement } from "@/components/owner/StrategiesManagement";
import { RiskManagement } from "@/components/owner/RiskManagement";
import { UserManagement } from "@/components/owner/UserManagement";
import { PerformanceAnalytics } from "@/components/owner/PerformanceAnalytics";
import { LiveSignals } from "@/components/owner/LiveSignals";
import { TradeHistory } from "@/components/owner/TradeHistory";
import { OwnerSettings } from "@/components/owner/OwnerSettings";
import { apiService } from '@/services/api';
import { toast } from 'sonner';
import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Legend } from 'recharts';

const OwnerDashboard = () => {
  const { user } = useAuth();
  const { handleError } = useErrorHandler();
  const [activeSection, setActiveSection] = useState('overview');
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalTrades: 0,
    totalRevenue: 0,
    systemStatus: 'active'
  });
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [engineStatus, setEngineStatus] = useState('unknown');
  const [loadingEngine, setLoadingEngine] = useState(false);
  const [overview, setOverview] = useState<any>(null);
  const [topStrategies, setTopStrategies] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [aumHistory, setAumHistory] = useState<any[]>([]);

  useEffect(() => {
    fetchDashboardStats();
    fetchSystemHealth();
    fetchOverview();
    fetchTopStrategies();
    fetchLogs();
    fetchAumHistory();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const overview = await apiService.getOverview();
      setStats({
        totalUsers: overview?.totalUsers || 0,
        totalTrades: overview?.totalTrades || 0,
        totalRevenue: overview?.totalRevenue || 0,
        systemStatus: engineStatus
      });
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      handleError(error);
    }
  };

  const fetchSystemHealth = async () => {
    try {
      const data = await apiService.getSystemHealth();
      setSystemHealth(data);
    } catch (error) {
      setSystemHealth(null);
    }
  };

  const handleStartEngine = async () => {
    setLoadingEngine(true);
    try {
      const res = await apiService.startEngine();
      setEngineStatus('active');
      toast.success('Engine started successfully');
    } catch (error) {
      toast.error('Failed to start engine');
    } finally {
      setLoadingEngine(false);
    }
  };

  const handleStopEngine = async () => {
    setLoadingEngine(true);
    try {
      const res = await apiService.stopEngine();
      setEngineStatus('stopped');
      toast.success('Engine stopped successfully');
    } catch (error) {
      toast.error('Failed to stop engine');
    } finally {
      setLoadingEngine(false);
    }
  };

  const fetchOverview = async () => {
    try {
      const data = await apiService.getOverview();
      setOverview(data);
    } catch (e) { setOverview(null); }
  };

  const fetchTopStrategies = async () => {
    try {
      const data = await apiService.getStrategies();
      setTopStrategies((data as any[]).slice(0, 3));
    } catch (e) { setTopStrategies([]); }
  };

  const fetchLogs = async () => {
    try {
      const data = await apiService.getLogs();
      setLogs((data as { logs?: any[] }).logs || []);
    } catch (e) { setLogs([]); }
  };

  const fetchAumHistory = async () => {
    try {
      const data = await apiService.getAumHistory?.();
      setAumHistory(data || []);
    } catch (e) {
      setAumHistory([]);
    }
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'overview':
        return (
          <div className="space-y-6 animate-fade-in">
            {/* Overview Header with Engine Controls */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl md:text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Dashboard Overview
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Real-time system monitoring and control
                </p>
              </div>
              <div className="flex gap-2">
                <Button 
                  size="sm" 
                  className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105" 
                  onClick={handleStartEngine} 
                  disabled={loadingEngine}
                >
                  <Play className="h-4 w-4 mr-2" />
                  Start Engine
                </Button>
                <Button 
                  size="sm" 
                  variant="destructive" 
                  className="shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                  onClick={handleStopEngine} 
                  disabled={loadingEngine}
                >
                  <Pause className="h-4 w-4 mr-2" />
                  Stop Engine
                </Button>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid gap-4 md:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
              {[
                {
                  title: "Total Users",
                  value: stats.totalUsers,
                  icon: Users,
                  color: "blue",
                  gradient: "from-blue-500 to-blue-600"
                },
                {
                  title: "Total Trades", 
                  value: stats.totalTrades,
                  icon: TrendingUp,
                  color: "green",
                  gradient: "from-green-500 to-green-600"
                },
                {
                  title: "Revenue",
                  value: `$${stats.totalRevenue.toLocaleString()}`,
                  icon: DollarSign,
                  color: "yellow",
                  gradient: "from-yellow-500 to-yellow-600"
                },
                {
                  title: "System Status",
                  value: stats.systemStatus,
                  icon: Activity,
                  color: "purple",
                  gradient: "from-purple-500 to-purple-600"
                }
              ].map((stat, index) => (
                <Card key={stat.title} className="group relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900">
                  <div className={`absolute inset-0 bg-gradient-to-r ${stat.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-300">
                      {stat.title}
                    </CardTitle>
                    <stat.icon className={`h-4 w-4 text-${stat.color}-500`} />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {typeof stat.value === 'string' ? stat.value : stat.value.toLocaleString()}
                    </div>
                    {stat.title === "System Status" && (
                      <Badge 
                        variant="outline" 
                        className={`mt-2 ${
                          stat.value === 'active' 
                            ? 'border-green-500 text-green-600 bg-green-50 dark:bg-green-900/20' 
                            : 'border-red-500 text-red-600 bg-red-50 dark:bg-red-900/20'
                        }`}
                      >
                        <div className={`w-2 h-2 rounded-full mr-2 ${
                          stat.value === 'active' ? 'bg-green-500' : 'bg-red-500'
                        }`} />
                        {stat.value}
                      </Badge>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* System Health Card */}
            <Card className="border-0 shadow-lg bg-gradient-to-br from-white to-blue-50 dark:from-gray-800 dark:to-blue-900/20">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-orange-500" />
                  System Health
                </CardTitle>
              </CardHeader>
              <CardContent>
                {systemHealth ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="space-y-1">
                      <p className="text-muted-foreground">CPU Usage</p>
                      <p className="font-semibold text-blue-600">{systemHealth.cpu}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Memory</p>
                      <p className="font-semibold text-green-600">{systemHealth.ram}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Network Sent</p>
                      <p className="font-semibold text-purple-600">{systemHealth.network?.sent}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Network Received</p>
                      <p className="font-semibold text-orange-600">{systemHealth.network?.recv}</p>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    <span className="ml-3 text-muted-foreground">Loading system health...</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Charts Section */}
            <div className="grid gap-6 md:grid-cols-2">
              {/* AUM Trend Chart */}
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-lg">AUM Trend</CardTitle>
                  <CardDescription>Assets Under Management over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={aumHistory} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                        <XAxis dataKey="date" className="text-xs" />
                        <YAxis className="text-xs" />
                        <RechartsTooltip 
                          contentStyle={{ 
                            backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                            border: 'none', 
                            borderRadius: '8px', 
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' 
                          }} 
                        />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="aum" 
                          stroke="#3b82f6" 
                          strokeWidth={3} 
                          dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                          activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Top Strategies */}
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="text-lg">Top Strategies</CardTitle>
                  <CardDescription>Best performing strategies</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {topStrategies.length > 0 ? topStrategies.map((strategy, index) => (
                      <div key={strategy.id} className="flex items-center justify-between p-3 rounded-lg bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 hover:from-blue-50 hover:to-purple-50 dark:hover:from-blue-900/20 dark:hover:to-purple-900/20 transition-all duration-300">
                        <div className="flex items-center space-x-3">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            index === 0 ? 'bg-yellow-100 text-yellow-600' :
                            index === 1 ? 'bg-gray-100 text-gray-600' :
                            'bg-orange-100 text-orange-600'
                          }`}>
                            <span className="font-bold">#{index + 1}</span>
                          </div>
                          <div>
                            <h4 className="font-semibold text-sm">{strategy.name}</h4>
                            <p className="text-xs text-muted-foreground">{strategy.description}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-green-600">+{strategy.performance.toFixed(2)}%</p>
                          <p className="text-xs text-muted-foreground">{strategy.status}</p>
                        </div>
                      </div>
                    )) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <TrendingUp className="h-12 w-12 mx-auto mb-3 opacity-50" />
                        <p>No strategy data available</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg">Recent Activity</CardTitle>
                <CardDescription>Latest system events and logs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {logs.length > 0 ? logs.map((log, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors duration-300">
                      <div className="w-2 h-2 rounded-full bg-blue-500 mt-2 flex-shrink-0"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{log.event}</p>
                        <p className="text-xs text-muted-foreground font-mono">{log.timestamp}</p>
                      </div>
                    </div>
                  )) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <Activity className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p>No recent activity</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        );
      case 'engine':
        return <EngineControl />;
      case 'signals':
        return <LiveSignals />;
      case 'strategies':
        return <StrategiesManagement />;
      case 'risk':
        return <RiskManagement />;
      case 'analytics':
        return <PerformanceAnalytics />;
      case 'users':
        return <UserManagement />;
      case 'trades':
        return <TradeHistory />;
      case 'settings':
        return <OwnerSettings />;
      default:
        return <div className="text-center text-muted-foreground">Section under development</div>;
    }
  };

  return (
    <ErrorBoundary>
      <SidebarProvider>
        <div className="min-h-screen flex w-full bg-background">
          <OwnerSidebar 
            activeSection={activeSection} 
            onSectionChange={setActiveSection}
          />
          
          <div className="flex-1 flex flex-col min-w-0">
            {/* Fixed Header */}
            <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/80 p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 min-w-0">
                  <div className="min-w-0">
                    <h1 className="text-xl md:text-2xl font-bold truncate">Owner Dashboard</h1>
                    <p className="text-xs md:text-sm text-muted-foreground truncate">
                      System Management & Analytics
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 md:space-x-4 flex-shrink-0">
                  <Badge variant="outline" className="px-2 py-1 text-xs md:text-sm border-green-200 text-green-700 bg-green-50 dark:border-green-800 dark:text-green-400 dark:bg-green-900/20">
                    <Activity className="h-3 w-3 md:h-4 md:w-4 mr-1" />
                    <span className="hidden sm:inline">System </span>Active
                  </Badge>
                  <ThemeToggle />
                </div>
              </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 p-4 md:p-6 overflow-auto bg-background">
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

export default OwnerDashboard;
