import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Play, Pause, Brain, TrendingUp, Activity, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

interface Strategy {
  id: string;
  name: string;
  description: string;
  active: boolean;
  performance: {
    winRate: number;
    profit: number;
    trades: number;
  };
  icon: any;
}

export function StrategiesManagement() {
  const [strategies, setStrategies] = useState<Strategy[]>([
    {
      id: "breakout",
      name: "Breakout Strategy",
      description: "Identifies price breakouts from support/resistance levels",
      active: true,
      performance: { winRate: 68.5, profit: 2450.30, trades: 127 },
      icon: TrendingUp
    },
    {
      id: "mean_reversion", 
      name: "Mean Reversion",
      description: "Trades on price returning to average after extreme moves",
      active: false,
      performance: { winRate: 72.1, profit: 1890.75, trades: 94 },
      icon: Activity
    },
    {
      id: "scalping",
      name: "Scalping Strategy", 
      description: "High-frequency trades on small price movements",
      active: true,
      performance: { winRate: 61.3, profit: 3200.15, trades: 285 },
      icon: Zap
    },
    {
      id: "arbitrage",
      name: "Arbitrage Strategy",
      description: "Exploits price differences across exchanges",
      active: false,
      performance: { winRate: 85.2, profit: 1650.90, trades: 52 },
      icon: Brain
    }
  ]);
  const [loading, setLoading] = useState<string | null>(null);
  const { toast } = useToast();

  const toggleStrategy = async (strategyId: string) => {
    setLoading(strategyId);
    try {
      const strategy = strategies.find(s => s.id === strategyId);
      const newActiveState = !strategy?.active;

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      setStrategies(prev => 
        prev.map(s => 
          s.id === strategyId 
            ? { ...s, active: newActiveState }
            : s
        )
      );

      toast({
        title: `Strategy ${newActiveState ? 'Activated' : 'Deactivated'}`,
        description: `${strategy?.name} has been ${newActiveState ? 'activated' : 'deactivated'}`,
        className: "bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to toggle strategy",
        variant: "destructive"
      });
    } finally {
      setLoading(null);
    }
  };

  const getPerformanceColor = (winRate: number) => {
    if (winRate >= 70) return "text-green-600";
    if (winRate >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Strategy Management</h2>
        <Badge variant="outline" className="px-3 py-1">
          {strategies.filter(s => s.active).length} Active
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {strategies.map((strategy) => {
          const IconComponent = strategy.icon;
          const isLoading = loading === strategy.id;
          
          return (
            <Card 
              key={strategy.id} 
              className={cn(
                "relative overflow-hidden transition-all duration-300 hover:shadow-lg transform hover:scale-[1.02]",
                strategy.active 
                  ? "ring-2 ring-green-200 bg-gradient-to-br from-green-50/50 to-emerald-50/50" 
                  : "bg-gradient-to-br from-gray-50/50 to-slate-50/50"
              )}
            >
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "p-2 rounded-lg transition-colors",
                      strategy.active 
                        ? "bg-green-100 text-green-700" 
                        : "bg-gray-100 text-gray-700"
                    )}>
                      <IconComponent className="h-5 w-5" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{strategy.name}</CardTitle>
                      <CardDescription className="text-sm">
                        {strategy.description}
                      </CardDescription>
                    </div>
                  </div>
                  <Switch
                    checked={strategy.active}
                    onCheckedChange={() => toggleStrategy(strategy.id)}
                    disabled={isLoading}
                    className="data-[state=checked]:bg-green-600"
                  />
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Performance Metrics */}
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className={cn("text-xl font-bold", getPerformanceColor(strategy.performance.winRate))}>
                      {strategy.performance.winRate}%
                    </div>
                    <div className="text-xs text-muted-foreground">Win Rate</div>
                  </div>
                  <div>
                    <div className="text-xl font-bold text-blue-600">
                      ${strategy.performance.profit.toLocaleString()}
                    </div>
                    <div className="text-xs text-muted-foreground">Profit</div>
                  </div>
                  <div>
                    <div className="text-xl font-bold text-purple-600">
                      {strategy.performance.trades}
                    </div>
                    <div className="text-xs text-muted-foreground">Trades</div>
                  </div>
                </div>

                {/* Control Buttons */}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 transition-all duration-200 hover:scale-105"
                    disabled={isLoading}
                  >
                    {strategy.active ? (
                      <>
                        <Pause className="h-3 w-3 mr-1" />
                        Pause
                      </>
                    ) : (
                      <>
                        <Play className="h-3 w-3 mr-1" />
                        Activate
                      </>
                    )}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="flex-1 transition-all duration-200 hover:scale-105"
                  >
                    View Details
                  </Button>
                </div>

                {/* Loading Indicator */}
                {isLoading && (
                  <div className="absolute inset-0 bg-white/80 flex items-center justify-center">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                      Updating...
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Strategy Performance Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Strategy Performance Overview</CardTitle>
          <CardDescription>
            Combined performance metrics across all strategies
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {(strategies.reduce((acc, s) => acc + s.performance.winRate, 0) / strategies.length).toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground">Avg Win Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                ${strategies.reduce((acc, s) => acc + s.performance.profit, 0).toLocaleString()}
              </div>
              <div className="text-sm text-muted-foreground">Total Profit</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {strategies.reduce((acc, s) => acc + s.performance.trades, 0)}
              </div>
              <div className="text-sm text-muted-foreground">Total Trades</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {strategies.filter(s => s.active).length}/{strategies.length}
              </div>
              <div className="text-sm text-muted-foreground">Active/Total</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}