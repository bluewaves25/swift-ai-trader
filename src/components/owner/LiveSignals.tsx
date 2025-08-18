import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Activity, Play, Square, TrendingUp, TrendingDown, Pause, RefreshCw } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { apiService, Trade } from "@/services/api";
import { API_ENDPOINTS, apiCall } from "@/config/api";

interface Signal {
  id: string;
  symbol: string;
  signal: 'buy' | 'sell' | 'hold';
  confidence: number;
  timestamp: string;
  source: string;
}

interface Mt5Position {
  ticket: number;
  symbol: string;
  type: number;
  volume: number;
  price_open: number;
  profit: number;
  time: number;
  [key: string]: any;
}

export function LiveSignals() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [allTrades, setAllTrades] = useState<any[]>([]);
  const [mt5Positions, setMt5Positions] = useState<Mt5Position[]>([]);
  const [engineRunning, setEngineRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchLiveData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchLiveData, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchLiveData = async () => {
    try {
      // Fetch real signals
      const { data: signalsData } = await apiService.getLiveSignals();
      setSignals(Array.isArray(signalsData.signals) ? signalsData.signals : []);
      // Fetch all trades (manual + engine, open + closed)
      const syncRes = await apiCall(API_ENDPOINTS.OWNER_MT5_SYNC_TRADES, { method: 'POST' });
      setAllTrades(Array.isArray(syncRes.trades) ? syncRes.trades : []);
      // Fetch open MT5 trades for the dedicated card
      const mt5Res = await apiCall(API_ENDPOINTS.OWNER_MT5_OPEN_TRADES);
      setMt5Positions(Array.isArray(mt5Res.positions) ? mt5Res.positions : []);
    } catch (error) {
      // Only log error once per session to avoid spam
      const errorKey = 'liveSignalsErrorLogged';
      if (!sessionStorage.getItem(errorKey)) {
        console.error('Error fetching live data:', error);
        sessionStorage.setItem(errorKey, 'true');
        setTimeout(() => sessionStorage.removeItem(errorKey), 30000);
      }
      setSignals([]);
      setAllTrades([]);
      setMt5Positions([]);
    }
  };

  const startEngine = async () => {
    setLoading(true);
    try {
      const data = await apiCall(API_ENDPOINTS.ENGINE_START, {
        method: 'POST',
      });
      
      setEngineRunning(true);
      toast({
        title: "Trading Engine Started",
        description: "Live trading has been activated",
        className: "bg-gradient-to-r from-green-50 to-emerald-50 border-green-200"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start trading engine",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const stopEngine = async () => {
    setLoading(true);
    try {
      const data = await apiCall(API_ENDPOINTS.ENGINE_STOP, {
        method: 'POST',
      });
      
      setEngineRunning(false);
      toast({
        title: "Trading Engine Stopped",
        description: "All positions have been closed",
        className: "bg-gradient-to-r from-red-50 to-pink-50 border-red-200"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to stop trading engine",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'buy':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'sell':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Pause className="h-4 w-4 text-yellow-600" />;
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy':
        return "bg-green-100 text-green-800 border-green-200";
      case 'sell':
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'filled':
        return "bg-green-100 text-green-800 border-green-200";
      case 'pending':
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case 'rejected':
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getTotalProfit = () => {
    return allTrades
      .filter(t => t.status === 'filled' && t.pnl)
      .reduce((sum, t) => sum + (t.pnl || 0), 0);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Live Signals & Trading</h2>
        <div className="flex items-center gap-4">
          <Badge 
            variant={engineRunning ? "default" : "secondary"}
            className={cn(
              "px-3 py-1",
              engineRunning 
                ? "bg-green-100 text-green-800 border-green-200" 
                : "bg-red-100 text-red-800 border-red-200"
            )}
          >
            <div className={cn(
              "w-2 h-2 rounded-full mr-2",
              engineRunning ? "bg-green-500 animate-pulse" : "bg-red-500"
            )} />
            {engineRunning ? "Live Trading" : "Stopped"}
          </Badge>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={cn(autoRefresh && "bg-blue-50 border-blue-200")}
          >
            <RefreshCw className={cn("h-4 w-4 mr-2", autoRefresh && "animate-spin")} />
            Auto Refresh
          </Button>
        </div>
      </div>

      {/* Engine Control */}
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-50/50 to-purple-50/50" />
        <CardHeader className="relative">
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-blue-600" />
            Trading Engine Control
          </CardTitle>
          <CardDescription>
            Start or stop the automated trading engine
          </CardDescription>
        </CardHeader>
        <CardContent className="relative">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <div className="text-sm font-medium">
                Status: {engineRunning ? "Active Trading" : "Inactive"}
              </div>
              <div className="text-xs text-muted-foreground">
                Total P&L: <span className={cn(
                  "font-medium",
                  getTotalProfit() >= 0 ? "text-green-600" : "text-red-600"
                )}>
                  ${getTotalProfit().toFixed(2)}
                </span>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button
                onClick={startEngine}
                disabled={loading || engineRunning}
                className="bg-green-600 hover:bg-green-700 transition-all duration-300 transform hover:scale-105"
              >
                <Play className="h-4 w-4 mr-2" />
                Start Engine
              </Button>
              
              <Button
                onClick={stopEngine}
                disabled={loading || !engineRunning}
                variant="destructive"
                className="transition-all duration-300 transform hover:scale-105"
              >
                <Square className="h-4 w-4 mr-2" />
                Stop & Close All
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Live Signals */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-600" />
              Live AI Signals
            </CardTitle>
            <CardDescription>
              Real-time trading signals from AI strategies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {signals.map((signal) => (
                <div 
                  key={signal.id}
                  className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 rounded-lg border"
                >
                  <div className="flex items-center gap-3">
                    {getSignalIcon(signal.signal)}
                    <div>
                      <div className="font-medium text-sm">{signal.symbol}</div>
                      <div className="text-xs text-muted-foreground">{signal.source}</div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <Badge className={cn("mb-1", getSignalColor(signal.signal))}>
                      {signal.signal.toUpperCase()}
                    </Badge>
                    <div className="text-xs text-muted-foreground">
                      {signal.confidence}% confidence
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Open MT5 Trades */}
        <Card>
          <CardHeader>
            <CardTitle>Open MT5 Trades</CardTitle>
            <CardDescription>
              All currently open positions in MT5 (manual + automatic)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {mt5Positions.length === 0 ? (
              <div className="text-muted-foreground text-sm">No open MT5 trades.</div>
            ) : (
              <div className="space-y-3">
                {mt5Positions.map((pos) => (
                  <div key={pos.ticket} className="flex items-center justify-between p-3 bg-gradient-to-r from-yellow-50/50 to-orange-50/50 rounded-lg border">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">{pos.symbol}</span>
                        <Badge variant="outline" className="text-xs">MT5</Badge>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {pos.type === 0 ? 'BUY' : 'SELL'} {pos.volume} @ ${pos.price_open}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={cn("text-xs font-medium", pos.profit >= 0 ? "text-green-600" : "text-red-600")}>{pos.profit >= 0 ? '+' : ''}${pos.profit.toFixed(2)}</div>
                      <div className="text-xs text-muted-foreground">Ticket: {pos.ticket}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Trades */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Trades</CardTitle>
            <CardDescription>
              Latest executed trades from both brokers (manual + engine)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {allTrades.slice(0, 5).map((trade) => (
                <div 
                  key={trade.id}
                  className="flex items-center justify-between p-3 bg-gradient-to-r from-green-50/50 to-emerald-50/50 rounded-lg border"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">{trade.symbol}</span>
                      <Badge variant="outline" className="text-xs">MT5</Badge>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {trade.side?.toUpperCase()} {trade.volume} @ ${trade.price}
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge className={cn("mb-1", getStatusColor(trade.status))}>
                      {trade.status}
                    </Badge>
                    {trade.pnl !== undefined && (
                      <div className={cn(
                        "text-xs font-medium",
                        trade.pnl >= 0 ? "text-green-600" : "text-red-600"
                      )}>
                        {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Trades Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Trades</CardTitle>
          <CardDescription>
            Complete trading history across all brokers (manual + engine)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Volume</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>P&L</TableHead>
                <TableHead>Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {allTrades.map((trade) => (
                <TableRow key={trade.id} className="hover:bg-muted/50">
                  <TableCell className="font-medium">{trade.symbol}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {trade.side === 'buy' ? (
                        <TrendingUp className="h-3 w-3 text-green-600" />
                      ) : (
                        <TrendingDown className="h-3 w-3 text-red-600" />
                      )}
                      <span className="capitalize">{trade.side}</span>
                    </div>
                  </TableCell>
                  <TableCell>{trade.volume}</TableCell>
                  <TableCell>${trade.price?.toLocaleString()}</TableCell>
                  <TableCell>
                    <Badge className={cn(getStatusColor(trade.status))}>
                      {trade.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {trade.pnl !== undefined ? (
                      <span className={cn(
                        "font-medium",
                        trade.pnl >= 0 ? "text-green-600" : "text-red-600"
                      )}>
                        {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                      </span>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {trade.timestamp ? new Date(trade.timestamp).toLocaleTimeString() : ''}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}