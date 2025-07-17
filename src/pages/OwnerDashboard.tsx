import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
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
import EngineFeed from "../components/engine/EngineFeed";
import SupportChatModal from "../components/support/SupportChatModal";

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
  const [aumHistory, setAumHistory] = useState<any[]>([]); // For AUM trend chart
  const [chatOpen, setChatOpen] = useState(false);

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
      toast.success('Engine started');
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
      toast.success('Engine stopped');
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
          <div className="space-y-6">
            {/* Overview Cards */}
            <div className="flex items-center justify-between">
              <h2 className="text-3xl font-bold tracking-tight">Dashboard Overview</h2>
              <div className="flex gap-2">
                <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={handleStartEngine} disabled={loadingEngine}>
                  <Play className="h-4 w-4 mr-2" />
                  Start Engine
                </Button>
                <Button size="sm" variant="destructive" onClick={handleStopEngine} disabled={loadingEngine}>
                  <Pause className="h-4 w-4 mr-2" />
                  Stop Engine
                </Button>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalUsers}</div>
                </CardContent>
              </Card>
              
              <Card className="transition-all duration-300 hover:shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalTrades}</div>
                </CardContent>
              </Card>
              
              <Card className="transition-all duration-300 hover:shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">${stats.totalRevenue}</div>
                </CardContent>
              </Card>
              
              <Card className="transition-all duration-300 hover:shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">System Status</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <Badge variant="outline" className="text-green-600">
                    {stats.systemStatus}
                  </Badge>
                </CardContent>
              </Card>
              <Card className="transition-all duration-300 hover:shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">System Health</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  {systemHealth ? (
                    <div className="text-xs">
                      <div>CPU: {systemHealth.cpu}</div>
                      <div>RAM: {systemHealth.ram}</div>
                      <div>Net: sent {systemHealth.network?.sent}, recv {systemHealth.network?.recv}</div>
                    </div>
                  ) : (
                    <div className="text-xs text-muted-foreground">Loading...</div>
                  )}
                </CardContent>
              </Card>
            </div>
            {/* Analytics Section */}
            <div className="mt-8 space-y-8">
              <h3 className="text-xl font-bold mb-2">Analytics</h3>
              {/* AUM Trend Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>AUM Trend</CardTitle>
                  <CardDescription>Assets Under Management over time</CardDescription>
                </CardHeader>
                <CardContent style={{ height: 250 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={aumHistory} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Line type="monotone" dataKey="aum" stroke="#8884d8" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
              {/* Top Strategies */}
              <Card>
                <CardHeader>
                  <CardTitle>Top Strategies</CardTitle>
                  <CardDescription>Best performing strategies</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {topStrategies.map((s) => (
                      <div key={s.id} className="p-4 bg-muted rounded-lg">
                        <div className="font-bold text-lg">{s.name}</div>
                        <div className="text-xs text-muted-foreground">{s.description}</div>
                        <div className="mt-2 text-blue-600 font-bold">Performance: {s.performance.toFixed(2)}</div>
                        <div className="text-xs">Status: {s.status}</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
              {/* Recent Activity / Audit Log */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Audit log of recent actions</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="text-xs space-y-1">
                    {logs.map((log, i) => (
                      <li key={i} className="border-b last:border-b-0 py-1">
                        <span className="font-mono text-gray-500">{log.timestamp}</span> — {log.event}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
            <button onClick={() => setChatOpen(true)} style={{ marginBottom: 16 }}>Open Support Chat</button>
            <SupportChatModal open={chatOpen} onClose={() => setChatOpen(false)} />
            <EngineFeed />
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
          <div className="hidden md:block fixed inset-y-0 z-50">
            <OwnerSidebar 
              activeSection={activeSection} 
              onSectionChange={setActiveSection}
            />
          </div>
          
          <div className="flex-1 flex flex-col md:pl-64">
            {/* Mobile sidebar */}
            <div className="md:hidden fixed inset-y-0 z-50 w-full">
              <OwnerSidebar 
                activeSection={activeSection} 
                onSectionChange={setActiveSection}
              />
            </div>
            
            {/* Header - Fixed */}
            <header className="sticky top-0 z-40 border-b bg-card/80 backdrop-blur-md supports-[backdrop-filter]:bg-card/80 p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <SidebarTrigger className="md:hidden" />
                  <div>
                    <h1 className="text-xl md:text-2xl font-bold">Owner Dashboard</h1>
                    <p className="text-xs md:text-sm text-muted-foreground">
                      System Management & Analytics
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 md:space-x-4">
                  <Badge variant="outline" className="px-2 py-1 text-xs md:text-sm">
                    <Activity className="h-3 w-3 md:h-4 md:w-4 mr-1" />
                    <span className="hidden sm:inline">System </span>Active
                  </Badge>
                  <ThemeToggle />
                </div>
              </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 p-3 md:p-6 overflow-auto bg-background">
              <div className="max-w-full">
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
