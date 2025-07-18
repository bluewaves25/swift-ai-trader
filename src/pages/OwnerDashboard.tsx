
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
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
        totalUsers: overview?.data?.totalUsers || 0,
        totalTrades: overview?.data?.totalTrades || 0,
        totalRevenue: overview?.data?.totalRevenue || 0,
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
      setSystemHealth(data?.data);
    } catch (error) {
      setSystemHealth(null);
    }
  };

  const handleStartEngine = async () => {
    setLoadingEngine(true);
    try {
      await apiService.startEngine();
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
      await apiService.stopEngine();
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
      setOverview(data?.data);
    } catch (e) { setOverview(null); }
  };

  const fetchTopStrategies = async () => {
    try {
      const data = await apiService.getStrategies();
      setTopStrategies((data?.data as any[])?.slice(0, 3) || []);
    } catch (e) { setTopStrategies([]); }
  };

  const fetchLogs = async () => {
    try {
      const data = await apiService.getLogs();
      setLogs(data?.data?.logs || []);
    } catch (e) { setLogs([]); }
  };

  const fetchAumHistory = async () => {
    try {
      const data = await apiService.getAumHistory?.();
      setAumHistory(data?.data || []);
    } catch (e) {
      setAumHistory([]);
    }
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'overview':
        return (
          <div className="space-y-3 md:space-y-4 animate-fade-in">
            {/* Overview Header with Engine Controls */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 md:gap-3">
              <div>
                <h2 className="text-base md:text-xl lg:text-2xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Dashboard Overview
                </h2>
                <p className="text-xs text-muted-foreground mt-1">
                  Real-time system monitoring and control
                </p>
              </div>
              <div className="flex gap-2">
                <Button 
                  size="sm" 
                  className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 text-xs h-7 md:h-8 px-2 md:px-3" 
                  onClick={handleStartEngine} 
                  disabled={loadingEngine}
                >
                  <Play className="h-3 w-3 mr-1" />
                  Start
                </Button>
                <Button 
                  size="sm" 
                  variant="destructive" 
                  className="shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 text-xs h-7 md:h-8 px-2 md:px-3"
                  onClick={handleStopEngine} 
                  disabled={loadingEngine}
                >
                  <Pause className="h-3 w-3 mr-1" />
                  Stop
                </Button>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid gap-2 md:gap-3 grid-cols-2 lg:grid-cols-4">
              {[
                {
                  title: "Users",
                  value: stats.totalUsers,
                  icon: Users,
                  color: "blue",
                  gradient: "from-blue-500 to-blue-600"
                },
                {
                  title: "Trades", 
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
                  title: "Status",
                  value: stats.systemStatus,
                  icon: Activity,
                  color: "purple",
                  gradient: "from-purple-500 to-purple-600"
                }
              ].map((stat, index) => (
                <Card key={stat.title} className="group relative overflow-hidden border-0 shadow-md hover:shadow-lg transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900">
                  <div className={`absolute inset-0 bg-gradient-to-r ${stat.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-1 p-2 md:p-3">
                    <CardTitle className="text-xs font-medium text-gray-600 dark:text-gray-300 truncate">
                      {stat.title}
                    </CardTitle>
                    <stat.icon className={`h-3 w-3 md:h-4 md:w-4 text-${stat.color}-500 flex-shrink-0`} />
                  </CardHeader>
                  <CardContent className="p-2 md:p-3 pt-0">
                    <div className="text-sm md:text-lg font-bold text-gray-900 dark:text-white truncate">
                      {typeof stat.value === 'string' ? stat.value : stat.value.toLocaleString()}
                    </div>
                    {stat.title === "Status" && (
                      <Badge 
                        variant="outline" 
                        className={`mt-1 text-xs px-1 py-0 ${
                          stat.value === 'active' 
                            ? 'border-green-500 text-green-600 bg-green-50 dark:bg-green-900/20' 
                            : 'border-red-500 text-red-600 bg-red-50 dark:bg-red-900/20'
                        }`}
                      >
                        <div className={`w-1 h-1 md:w-1.5 md:h-1.5 rounded-full mr-1 ${
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
            <Card className="border-0 shadow-md bg-gradient-to-br from-white to-blue-50 dark:from-gray-800 dark:to-blue-900/20">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-1 p-2 md:p-3">
                <CardTitle className="text-xs md:text-sm font-medium flex items-center gap-2">
                  <AlertTriangle className="h-3 w-3 md:h-4 md:w-4 text-orange-500" />
                  System Health
                </CardTitle>
              </CardHeader>
              <CardContent className="p-2 md:p-3 pt-0">
                {systemHealth ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                    <div className="space-y-1">
                      <p className="text-muted-foreground">CPU</p>
                      <p className="font-semibold text-blue-600">{systemHealth.cpu}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Memory</p>
                      <p className="font-semibold text-green-600">{systemHealth.ram}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Net Sent</p>
                      <p className="font-semibold text-purple-600">{systemHealth.network?.sent}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Net Recv</p>
                      <p className="font-semibold text-orange-600">{systemHealth.network?.recv}</p>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center py-2 md:py-4">
                    <div className="animate-spin rounded-full h-3 w-3 md:h-4 md:w-4 border-b-2 border-blue-500"></div>
                    <span className="ml-2 text-muted-foreground text-xs">Loading...</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Charts Section */}
            <div className="grid gap-3 md:gap-4 md:grid-cols-2">
              {/* AUM Trend Chart */}
              <Card className="border-0 shadow-md">
                <CardHeader className="p-2 md:p-3">
                  <CardTitle className="text-xs md:text-sm">AUM Trend</CardTitle>
                  <CardDescription className="text-xs">Assets Under Management</CardDescription>
                </CardHeader>
                <CardContent className="p-2 md:p-3 pt-0">
                  <div className="h-[120px] md:h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={aumHistory} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                        <XAxis dataKey="date" className="text-xs" tick={{ fontSize: 10 }} />
                        <YAxis className="text-xs" tick={{ fontSize: 10 }} />
                        <RechartsTooltip 
                          contentStyle={{ 
                            backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                            border: 'none', 
                            borderRadius: '8px', 
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                            fontSize: '12px'
                          }} 
                        />
                        <Line 
                          type="monotone" 
                          dataKey="aum" 
                          stroke="#3b82f6" 
                          strokeWidth={2} 
                          dot={{ fill: '#3b82f6', strokeWidth: 1, r: 2 }}
                          activeDot={{ r: 3, stroke: '#3b82f6', strokeWidth: 1 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Top Strategies */}
              <Card className="border-0 shadow-md">
                <CardHeader className="p-2 md:p-3">
                  <CardTitle className="text-xs md:text-sm">Top Strategies</CardTitle>
                  <CardDescription className="text-xs">Best performing</CardDescription>
                </CardHeader>
                <CardContent className="p-2 md:p-3 pt-0">
                  <div className="space-y-2">
                    {topStrategies.length > 0 ? topStrategies.map((strategy, index) => (
                      <div key={strategy.id} className="flex items-center justify-between p-2 rounded-lg bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 hover:from-blue-50 hover:to-purple-50 dark:hover:from-blue-900/20 dark:hover:to-purple-900/20 transition-all duration-300">
                        <div className="flex items-center space-x-2 min-w-0">
                          <div className={`w-5 h-5 md:w-6 md:h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                            index === 0 ? 'bg-yellow-100 text-yellow-600' :
                            index === 1 ? 'bg-gray-100 text-gray-600' :
                            'bg-orange-100 text-orange-600'
                          }`}>
                            #{index + 1}
                          </div>
                          <div className="min-w-0">
                            <h4 className="font-semibold text-xs truncate">{strategy.name}</h4>
                            <p className="text-xs text-muted-foreground truncate">{strategy.description}</p>
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <p className="font-bold text-green-600 text-xs">+{strategy.performance?.toFixed(2) || 0}%</p>
                          <p className="text-xs text-muted-foreground">{strategy.status}</p>
                        </div>
                      </div>
                    )) : (
                      <div className="text-center py-4 text-muted-foreground">
                        <TrendingUp className="h-6 w-6 md:h-8 md:w-8 mx-auto mb-2 opacity-50" />
                        <p className="text-xs">No data available</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card className="border-0 shadow-md">
              <CardHeader className="p-2 md:p-3">
                <CardTitle className="text-xs md:text-sm">Recent Activity</CardTitle>
                <CardDescription className="text-xs">Latest system events</CardDescription>
              </CardHeader>
              <CardContent className="p-2 md:p-3 pt-0">
                <div className="space-y-2 max-h-32 md:max-h-48 overflow-y-auto">
                  {logs.length > 0 ? logs.map((log, index) => (
                    <div key={index} className="flex items-start space-x-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors duration-300">
                      <div className="w-1 h-1 md:w-1.5 md:h-1.5 rounded-full bg-blue-500 mt-1 flex-shrink-0"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-gray-900 dark:text-white truncate">{log.event}</p>
                        <p className="text-xs text-muted-foreground font-mono">{log.timestamp}</p>
                      </div>
                    </div>
                  )) : (
                    <div className="text-center py-4 text-muted-foreground">
                      <Activity className="h-6 w-6 md:h-8 md:w-8 mx-auto mb-2 opacity-50" />
                      <p className="text-xs">No recent activity</p>
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
        return <div className="text-center text-muted-foreground text-xs">Section under development</div>;
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
          
          <div className="flex-1 flex flex-col min-w-0 max-w-full">
            {/* Fixed Header */}
            <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/80 p-2 md:p-3 shadow-sm flex-shrink-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 min-w-0">
                  <div className="min-w-0">
                    <h1 className="text-sm md:text-lg lg:text-xl font-bold truncate bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      Owner Dashboard
                    </h1>
                    <p className="text-xs text-muted-foreground truncate">
                      System Management & Analytics
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-1 md:space-x-2 flex-shrink-0">
                  <Badge variant="outline" className="px-1 md:px-2 py-0.5 text-xs border-green-200 text-green-700 bg-green-50 dark:border-green-800 dark:text-green-400 dark:bg-green-900/20">
                    <Activity className="h-2 w-2 md:h-3 md:w-3 mr-1" />
                    <span className="hidden sm:inline text-xs">System </span>Active
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

export default OwnerDashboard;
