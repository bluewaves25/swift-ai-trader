
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  AlertCircle,
  Clock,
  Target,
  DollarSign
} from "lucide-react";

interface AISignal {
  id: string;
  symbol: string;
  signal: string;
  confidence: number;
  timestamp: string;
}

interface MarketData {
  id: string;
  symbol: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  timestamp: string;
}

const LiveSignals = () => {
  const { user } = useAuth();
  const [signals, setSignals] = useState<AISignal[]>([]);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSignals();
    fetchMarketData();
    
    // Set up real-time subscription
    const signalsSubscription = supabase
      .channel('ai_signals')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'ai_signals' },
        () => fetchSignals()
      )
      .subscribe();

    return () => {
      signalsSubscription.unsubscribe();
    };
  }, []);

  const fetchSignals = async () => {
    try {
      const { data, error } = await supabase
        .from('ai_signals')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(10);

      if (error) throw error;
      
      if (data) {
        setSignals(data);
      }
    } catch (error) {
      console.error('Error fetching signals:', error);
      toast.error('Failed to fetch live signals');
    } finally {
      setLoading(false);
    }
  };

  const fetchMarketData = async () => {
    try {
      const { data, error } = await supabase
        .from('market_data')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(20);

      if (error) throw error;
      
      if (data) {
        setMarketData(data);
      }
    } catch (error) {
      console.error('Error fetching market data:', error);
    }
  };

  const executeSignal = async (signal: AISignal) => {
    if (!user) {
      toast.error("Please sign in to execute trades");
      return;
    }

    try {
      const { error } = await supabase
        .from('trades')
        .insert({
          user_id: user.id,
          symbol: signal.symbol,
          side: signal.signal.toLowerCase(),
          price: 0, // Will be filled by the trading system
          volume: 1000, // Default volume
          account_number: `${user.id}-default`,
          status: 'pending'
        });

      if (error) throw error;

      toast.success(`Trade signal executed for ${signal.symbol}`);
    } catch (error) {
      console.error('Error executing trade:', error);
      toast.error('Failed to execute trade signal');
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal?.toLowerCase()) {
      case 'buy':
        return <TrendingUp className="h-3 w-3 text-green-600" />;
      case 'sell':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-yellow-600" />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return <div className="animate-pulse">Loading live signals...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Live AI Signals</h2>
        <p className="text-muted-foreground">Real-time trading signals from our AI algorithms</p>
      </div>

      {/* Live Signals */}
      <div className="grid grid-cols-1 gap-4">
        {signals.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center">
              <AlertCircle className="h-7 w-7 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">No live signals available at the moment</p>
            </CardContent>
          </Card>
        ) : (
          signals.map((signal) => (
            <Card key={signal.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {getSignalIcon(signal.signal)}
                      <div>
                        <h3 className="font-semibold text-lg">{signal.symbol}</h3>
                        <p className="text-sm text-muted-foreground">
                          Signal: <span className="font-medium capitalize">{signal.signal}</span>
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${getConfidenceColor(signal.confidence)}`}>
                        {signal.confidence}%
                      </div>
                      <p className="text-xs text-muted-foreground">Confidence</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">
                        <Clock className="h-4 w-4 inline mr-1" />
                        {new Date(signal.timestamp).toLocaleTimeString()}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(signal.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                    
                    <Button
                      onClick={() => executeSignal(signal)}
                      variant={signal.signal?.toLowerCase() === 'buy' ? 'default' : 'destructive'}
                      size="sm"
                    >
                      Execute
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Market Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Market Overview</CardTitle>
          <CardDescription>Current market conditions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {marketData.slice(0, 4).map((data) => (
              <div key={data.id} className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">{data.symbol}</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Price:</span>
                    <span className="font-medium">{data.close.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Change:</span>
                    <span className={`font-medium ${
                      data.close > data.open ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {((data.close - data.open) / data.open * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Volume:</span>
                    <span className="font-medium">{data.volume.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LiveSignals;
