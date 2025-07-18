
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { 
  Cpu, 
  Zap, 
  Brain, 
  Activity, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock
} from "lucide-react";
import { toast } from "sonner";
import { apiService } from "@/services/api";

interface TradingEngineProps {
  isRunning: boolean;
}

const TradingEngine = ({ isRunning }: TradingEngineProps) => {
  const [engineStats, setEngineStats] = useState<any>(null);

  const [autoTrading, setAutoTrading] = useState(false);
  const [riskManagement, setRiskManagement] = useState(true);

  useEffect(() => {
    if (isRunning) {
      const fetchStats = async () => {
        try {
          const stats = await apiService.getEngineStats?.();
          setEngineStats(stats || null);
        } catch (error) {
          setEngineStats(null);
        }
      };
      fetchStats();
      const interval = setInterval(fetchStats, 2000);
      return () => clearInterval(interval);
    }
  }, [isRunning]);

  const handleAutoTradingToggle = (enabled: boolean) => {
    setAutoTrading(enabled);
    toast.success(enabled ? 'Auto-trading enabled' : 'Auto-trading disabled');
  };

  const handleRiskToggle = (enabled: boolean) => {
    setRiskManagement(enabled);
    toast.success(enabled ? 'Risk management enabled' : 'Risk management disabled');
  };

  if (!engineStats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Cpu className="h-5 w-5" />
            <span>Trading Engine Status</span>
            <Badge variant={isRunning ? "default" : "secondary"} className="ml-2">
              {isRunning ? "Running" : "Stopped"}
            </Badge>
          </CardTitle>
          <CardDescription>
            Real-time engine performance and configuration
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center py-4">
            <p className="text-muted-foreground mb-4">
              Loading engine statistics...
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Cpu className="h-5 w-5" />
          <span>Trading Engine Status</span>
          <Badge variant={isRunning ? "default" : "secondary"} className="ml-2">
            {isRunning ? "Running" : "Stopped"}
          </Badge>
        </CardTitle>
        <CardDescription>
          Real-time engine performance and configuration
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Engine Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center space-x-2">
            <Switch
              id="auto-trading"
              checked={autoTrading}
              onCheckedChange={handleAutoTradingToggle}
              disabled={!isRunning}
            />
            <Label htmlFor="auto-trading" className="flex items-center space-x-2">
              <Zap className="h-4 w-4" />
              <span>Auto Trading</span>
            </Label>
          </div>
          
          <div className="flex items-center space-x-2">
            <Switch
              id="risk-management"
              checked={riskManagement}
              onCheckedChange={handleRiskToggle}
            />
            <Label htmlFor="risk-management" className="flex items-center space-x-2">
              <AlertTriangle className="h-4 w-4" />
              <span>Risk Management</span>
            </Label>
          </div>
        </div>

        {/* Engine Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Brain className="h-4 w-4 text-blue-500" />
              <span className="text-sm text-muted-foreground">Signals</span>
            </div>
            <p className="text-2xl font-bold">{engineStats.signalsGenerated}</p>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Activity className="h-4 w-4 text-green-500" />
              <span className="text-sm text-muted-foreground">Trades</span>
            </div>
            <p className="text-2xl font-bold">{engineStats.tradesExecuted}</p>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-purple-500" />
              <span className="text-sm text-muted-foreground">Success Rate</span>
            </div>
            <p className="text-2xl font-bold">{engineStats.successRate.toFixed(1)}%</p>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-orange-500" />
              <span className="text-sm text-muted-foreground">Avg Time (ms)</span>
            </div>
            <p className="text-2xl font-bold">{engineStats.avgExecutionTime.toFixed(0)}</p>
          </div>
        </div>

        {/* System Performance */}
        <div className="space-y-4">
          <h4 className="font-semibold">System Performance</h4>
          
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>CPU Usage</span>
                <span>{engineStats.cpuUsage.toFixed(1)}%</span>
              </div>
              <Progress value={engineStats.cpuUsage} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Memory Usage</span>
                <span>{engineStats.memoryUsage.toFixed(1)}%</span>
              </div>
              <Progress value={engineStats.memoryUsage} className="h-2" />
            </div>
          </div>
        </div>

        {/* Active Status */}
        <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
            <div>
              <p className="font-medium">
                {isRunning ? 'Engine Active' : 'Engine Stopped'}
              </p>
              <p className="text-sm text-muted-foreground">
                {isRunning 
                  ? `Monitoring ${engineStats.activePairs} trading pairs`
                  : 'Engine is currently offline'
                }
              </p>
            </div>
          </div>
          
          {isRunning && (
            <TrendingUp className="h-6 w-6 text-green-500" />
          )}
        </div>

        {!isRunning && (
          <div className="text-center py-4">
            <p className="text-muted-foreground mb-4">
              Start the trading engine to begin automated signal generation and execution
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TradingEngine;
