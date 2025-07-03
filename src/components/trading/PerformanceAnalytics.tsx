
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/integrations/supabase/client";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { TrendingUp, TrendingDown, Activity, DollarSign } from "lucide-react";

interface PerformanceData {
  id: string;
  date: string;
  total_trades: number;
  winning_trades: number;
  total_profit: number;
  total_volume: number;
  win_rate: number;
  sharpe_ratio: number;
  max_drawdown: number;
  avg_profit_per_trade: number;
}

const PerformanceAnalytics = () => {
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalStats, setTotalStats] = useState({
    totalProfit: 0,
    totalTrades: 0,
    winRate: 0,
    sharpeRatio: 0,
    maxDrawdown: 0
  });

  useEffect(() => {
    fetchPerformanceData();
  }, []);

  const fetchPerformanceData = async () => {
    try {
      const { data, error } = await supabase
        .from('performance_analytics')
        .select('*')
        .order('date', { ascending: true })
        .limit(30);

      if (error) throw error;

      const performanceData = data || [];
      setPerformanceData(performanceData);

      // Calculate total stats
      if (performanceData.length > 0) {
        const totalProfit = performanceData.reduce((sum, day) => sum + (day.total_profit || 0), 0);
        const totalTrades = performanceData.reduce((sum, day) => sum + (day.total_trades || 0), 0);
        const totalWinning = performanceData.reduce((sum, day) => sum + (day.winning_trades || 0), 0);
        const avgSharpe = performanceData.reduce((sum, day) => sum + (day.sharpe_ratio || 0), 0) / performanceData.length;
        const maxDrawdown = Math.max(...performanceData.map(day => day.max_drawdown || 0));

        setTotalStats({
          totalProfit,
          totalTrades,
          winRate: totalTrades > 0 ? (totalWinning / totalTrades) * 100 : 0,
          sharpeRatio: avgSharpe,
          maxDrawdown
        });
      }
    } catch (error) {
      console.error('Error fetching performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = performanceData.map(item => ({
    date: new Date(item.date).toLocaleDateString(),
    profit: item.total_profit,
    trades: item.total_trades,
    winRate: item.win_rate * 100
  }));

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Profit</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              totalStats.totalProfit >= 0 ? 'text-green-500' : 'text-red-500'
            }`}>
              ${totalStats.totalProfit.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              Cumulative realized P&L
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalStats.totalTrades}</div>
            <p className="text-xs text-muted-foreground">
              All executed trades
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalStats.winRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              Profitable trades ratio
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sharpe Ratio</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalStats.sharpeRatio.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">
              Risk-adjusted returns
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Daily Profit & Loss</CardTitle>
            <CardDescription>30-day performance overview</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="date" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="profit" 
                    stroke="hsl(var(--primary))" 
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Daily Trading Volume</CardTitle>
            <CardDescription>Number of trades executed daily</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="date" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="trades" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Risk Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Risk Metrics</CardTitle>
          <CardDescription>Key risk and performance indicators</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Maximum Drawdown</span>
                <Badge variant="destructive">
                  {(totalStats.maxDrawdown * 100).toFixed(2)}%
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                Largest peak-to-trough decline
              </p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Sharpe Ratio</span>
                <Badge variant={totalStats.sharpeRatio > 1 ? "default" : "secondary"}>
                  {totalStats.sharpeRatio.toFixed(2)}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                Risk-adjusted return measure
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Avg Profit/Trade</span>
                <Badge variant="outline">
                  ${(totalStats.totalProfit / Math.max(totalStats.totalTrades, 1)).toFixed(2)}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                Average profit per executed trade
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PerformanceAnalytics;
