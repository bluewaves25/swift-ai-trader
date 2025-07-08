import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Play, Pause, Square, AlertTriangle, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

interface EngineState {
  is_running: boolean;
  start_time: string | null;
  total_signals: number;
  total_trades: number;
  active_pairs: string[];
}

export function EngineControl() {
  const [engineState, setEngineState] = useState<EngineState>({
    is_running: false,
    start_time: null,
    total_signals: 0,
    total_trades: 0,
    active_pairs: []
  });
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchEngineStatus();
    const interval = setInterval(fetchEngineStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchEngineStatus = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/engine/status');
      const data = await response.json();
      setEngineState(data);
    } catch (error) {
      console.error('Failed to fetch engine status:', error);
    }
  };

  const startEngine = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:3000/api/engine/start', {
        method: 'POST',
      });
      const data = await response.json();
      
      if (response.ok) {
        toast({
          title: "Engine Started",
          description: "Trading engine has been started successfully",
          className: "bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200"
        });
        fetchEngineStatus();
      } else {
        throw new Error(data.detail || 'Failed to start engine');
      }
    } catch (error) {
      toast({
        title: "Start Failed",
        description: error instanceof Error ? error.message : "Failed to start engine",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const stopEngine = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:3000/api/engine/stop', {
        method: 'POST',
      });
      const data = await response.json();
      
      if (response.ok) {
        toast({
          title: "Engine Stopped",
          description: "Trading engine has been stopped successfully",
          className: "bg-gradient-to-r from-orange-50 to-red-50 border-orange-200"
        });
        fetchEngineStatus();
      } else {
        throw new Error(data.detail || 'Failed to stop engine');
      }
    } catch (error) {
      toast({
        title: "Stop Failed",
        description: error instanceof Error ? error.message : "Failed to stop engine",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const emergencyStop = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:3000/api/engine/emergency-stop', {
        method: 'POST',
      });
      const data = await response.json();
      
      if (response.ok) {
        toast({
          title: "Emergency Stop Executed",
          description: "All trading activities have been halted immediately",
          className: "bg-gradient-to-r from-red-50 to-pink-50 border-red-200"
        });
        fetchEngineStatus();
      } else {
        throw new Error(data.detail || 'Failed to execute emergency stop');
      }
    } catch (error) {
      toast({
        title: "Emergency Stop Failed",
        description: error instanceof Error ? error.message : "Failed to execute emergency stop",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getUptime = () => {
    if (!engineState.start_time) return "Not running";
    const startTime = new Date(engineState.start_time);
    const now = new Date();
    const diffMs = now.getTime() - startTime.getTime();
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Trading Engine Control</h2>
        <Badge 
          variant={engineState.is_running ? "default" : "secondary"}
          className={cn(
            "px-3 py-1",
            engineState.is_running 
              ? "bg-green-100 text-green-800 border-green-200" 
              : "bg-red-100 text-red-800 border-red-200"
          )}
        >
          <div className={cn(
            "w-2 h-2 rounded-full mr-2",
            engineState.is_running ? "bg-green-500 animate-pulse" : "bg-red-500"
          )} />
          {engineState.is_running ? "Running" : "Stopped"}
        </Badge>
      </div>

      {/* Control Buttons */}
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-50/50 to-purple-50/50" />
        <CardHeader className="relative">
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-blue-600" />
            Engine Controls
          </CardTitle>
          <CardDescription>
            Start, stop, or emergency halt the trading engine
          </CardDescription>
        </CardHeader>
        <CardContent className="relative">
          <div className="flex flex-wrap gap-4">
            <Button
              onClick={startEngine}
              disabled={loading || engineState.is_running}
              className="bg-green-600 hover:bg-green-700 text-white transition-all duration-300 transform hover:scale-105"
              size="lg"
            >
              <Play className="h-4 w-4 mr-2" />
              Start Engine
            </Button>
            
            <Button
              onClick={stopEngine}
              disabled={loading || !engineState.is_running}
              variant="outline"
              className="border-orange-300 text-orange-700 hover:bg-orange-50 transition-all duration-300 transform hover:scale-105"
              size="lg"
            >
              <Pause className="h-4 w-4 mr-2" />
              Stop Engine
            </Button>
            
            <Button
              onClick={emergencyStop}
              disabled={loading}
              variant="destructive"
              className="bg-red-600 hover:bg-red-700 transition-all duration-300 transform hover:scale-105"
              size="lg"
            >
              <Square className="h-4 w-4 mr-2" />
              Emergency Stop
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Engine Statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Uptime</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{getUptime()}</div>
          </CardContent>
        </Card>
        
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Signals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{engineState.total_signals}</div>
          </CardContent>
        </Card>
        
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Trades</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{engineState.total_trades}</div>
          </CardContent>
        </Card>
        
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Pairs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{engineState.active_pairs.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Active Pairs Display */}
      {engineState.active_pairs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Active Trading Pairs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {engineState.active_pairs.map((pair) => (
                <Badge key={pair} variant="secondary" className="px-3 py-1">
                  {pair}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}