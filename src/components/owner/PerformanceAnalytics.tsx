import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from "recharts";
import { TrendingUp, TrendingDown, BarChart3, PieChart as PieChartIcon, Target, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";
import { apiService, Performance } from "@/services/api";

interface PerformanceData {
  strategies: {
    name: string;
    winRate: number;
    profit: number;
    trades: number;
    roi: number;
  }[];
  riskAdjustments: {
    date: string;
    adjustment: string;
    impact: number;
    profit: number;
  }[];
  overallEngine: {
    daily: { date: string; profit: number; trades: number; winRate: number }[];
    weekly: { week: string; profit: number; trades: number; winRate: number }[];
    monthly: { month: string; profit: number; trades: number; winRate: number }[];
  };
}

export function PerformanceAnalytics() {
  const [timeframe, setTimeframe] = useState<"daily" | "weekly" | "monthly">("daily");
  const [sortBy, setSortBy] = useState<"date" | "profit" | "winRate" | "trades">("date");
  const [data, setData] = useState<Performance | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const { data: analytics } = await apiService.getPerformanceData();
        setData(analytics || null);
      } catch (error) {
        setData(null);
      }
    };
    fetchAnalytics();
  }, []);

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  const getCurrentData = () => {
    if (!data) return [];
    return data.overallEngine[timeframe];
  };

  const getSortedData = () => {
    const currentData = getCurrentData();
    return [...currentData].sort((a, b) => {
      switch (sortBy) {
        case "profit":
          return b.profit - a.profit;
        case "winRate":
          return b.winRate - a.winRate;
        case "trades":
          return b.trades - a.trades;
        default:
          return 0;
      }
    });
  };

  const getPerformanceMetrics = () => {
    const currentData = getCurrentData();
    const totalProfit = currentData.reduce((acc, item) => acc + item.profit, 0);
    const totalTrades = currentData.reduce((acc, item) => acc + item.trades, 0);
    const avgWinRate = currentData.reduce((acc, item) => acc + item.winRate, 0) / currentData.length;
    const bestDay = currentData.reduce((max, item) => item.profit > max.profit ? item : max, currentData[0]);

    return { totalProfit, totalTrades, avgWinRate, bestDay };
  };

  const metrics = getPerformanceMetrics();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Performance Analytics</h2>
        <div className="flex gap-4">
          <Select value={timeframe} onValueChange={(value: any) => setTimeframe(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
              <SelectItem value="monthly">Monthly</SelectItem>
            </SelectContent>
          </Select>
          <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="date">By Date</SelectItem>
              <SelectItem value="profit">By Profit</SelectItem>
              <SelectItem value="winRate">By Win Rate</SelectItem>
              <SelectItem value="trades">By Trades</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Performance Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Profit</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <div className="text-2xl font-bold text-green-600">
                ${metrics.totalProfit.toLocaleString()}
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Trades</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-blue-600" />
              <div className="text-2xl font-bold text-blue-600">{metrics.totalTrades}</div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Win Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-purple-600" />
              <div className="text-2xl font-bold text-purple-600">
                {metrics.avgWinRate.toFixed(1)}%
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Best Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-orange-600" />
              <div>
                <div className="text-lg font-bold text-orange-600">
                  ${metrics.bestDay?.profit.toFixed(2)}
                </div>
                <div className="text-xs text-muted-foreground">
                  {metrics.bestDay?.[timeframe === 'daily' ? 'date' : timeframe === 'weekly' ? 'week' : 'month']}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Profit Trend Chart */}
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-indigo-50/50" />
          <CardHeader className="relative">
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              Profit Trend ({timeframe})
            </CardTitle>
            <CardDescription>
              {timeframe.charAt(0).toUpperCase() + timeframe.slice(1)} profit performance over time
            </CardDescription>
          </CardHeader>
          <CardContent className="relative">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={getSortedData()}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis 
                  dataKey={timeframe === 'daily' ? 'date' : timeframe === 'weekly' ? 'week' : 'month'} 
                  stroke="#6B7280"
                />
                <YAxis stroke="#6B7280" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="profit" 
                  stroke="#3B82F6" 
                  strokeWidth={3}
                  dot={{ fill: '#3B82F6', strokeWidth: 2, r: 6 }}
                  activeDot={{ r: 8, stroke: '#3B82F6', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Win Rate Chart */}
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-green-50/50 to-emerald-50/50" />
          <CardHeader className="relative">
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-green-600" />
              Win Rate Analysis
            </CardTitle>
            <CardDescription>
              Win rate performance across time periods
            </CardDescription>
          </CardHeader>
          <CardContent className="relative">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getSortedData()}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis 
                  dataKey={timeframe === 'daily' ? 'date' : timeframe === 'weekly' ? 'week' : 'month'} 
                  stroke="#6B7280"
                />
                <YAxis stroke="#6B7280" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Bar 
                  dataKey="winRate" 
                  fill="#10B981"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Strategy Performance */}
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-50/50 to-pink-50/50" />
          <CardHeader className="relative">
            <CardTitle className="flex items-center gap-2">
              <PieChartIcon className="h-5 w-5 text-purple-600" />
              Strategy Performance
            </CardTitle>
            <CardDescription>
              Performance breakdown by trading strategy
            </CardDescription>
          </CardHeader>
          <CardContent className="relative">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data?.strategies || []}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="profit"
                  label={({ name, profit }) => `${name}: $${profit.toFixed(0)}`}
                >
                  {data?.strategies?.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Risk Management Impact */}
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-orange-50/50 to-red-50/50" />
          <CardHeader className="relative">
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-orange-600" />
              Risk Management Impact
            </CardTitle>
            <CardDescription>
              Performance impact of risk adjustments
            </CardDescription>
          </CardHeader>
          <CardContent className="relative space-y-4">
            {data?.riskAdjustments?.map((adjustment, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-white/70 rounded-lg">
                <div>
                  <div className="font-medium text-sm">{adjustment.adjustment}</div>
                  <div className="text-xs text-muted-foreground">{adjustment.date}</div>
                </div>
                <div className="text-right">
                  <div className={cn(
                    "font-bold",
                    adjustment.impact > 0 ? "text-green-600" : "text-red-600"
                  )}>
                    {adjustment.impact > 0 ? '+' : ''}{adjustment.impact}%
                  </div>
                  <div className="text-xs text-muted-foreground">
                    ${adjustment.profit.toFixed(2)}
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Strategy Details Table */}
      <Card>
        <CardHeader>
          <CardTitle>Strategy Performance Details</CardTitle>
          <CardDescription>
            Detailed breakdown of each strategy's performance metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Strategy</th>
                  <th className="text-right p-2">Win Rate</th>
                  <th className="text-right p-2">Profit</th>
                  <th className="text-right p-2">Trades</th>
                  <th className="text-right p-2">ROI</th>
                </tr>
              </thead>
              <tbody>
                {data?.strategies?.map((strategy, index) => (
                  <tr key={index} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="p-2 font-medium">{strategy.name}</td>
                    <td className={cn(
                      "p-2 text-right font-bold",
                      strategy.winRate >= 70 ? "text-green-600" : 
                      strategy.winRate >= 60 ? "text-yellow-600" : "text-red-600"
                    )}>
                      {strategy.winRate}%
                    </td>
                    <td className="p-2 text-right font-bold text-blue-600">
                      ${strategy.profit.toLocaleString()}
                    </td>
                    <td className="p-2 text-right">{strategy.trades}</td>
                    <td className={cn(
                      "p-2 text-right font-bold",
                      strategy.roi >= 15 ? "text-green-600" : "text-orange-600"
                    )}>
                      {strategy.roi}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}