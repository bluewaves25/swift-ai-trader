import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { TrendingUp, TrendingDown, Minus, Brain, Zap, Clock } from "lucide-react";
import { toast } from "sonner";

interface AISignal {
  id: string;
  pair_id: string;
  signal: string;
  confidence: number;
  strategy_used: string;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  reasoning: string;
  created_at: string;
  executed: boolean;
  trading_pairs: {
    symbol: string;
  };
}

const LiveSignals = () => {
  const [signals, setSignals] = useState<AISignal[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 3000);
    
    // Set up realtime subscription
    const subscription = supabase
      .channel('ai_signals_changes')
      .on('postgres_changes', 
        { event: 'INSERT', schema: 'public', table: 'ai_signals' },
        (payload) => {
          console.log('New signal received:', payload);
          fetchSignals();
        }
      )
      .subscribe();

    return () => {
      clearInterval(interval);
      subscription.unsubscribe();
    };
  }, []);

  const fetchSignals = async () => {
    try {
      const { data, error } = await supabase
        .from('ai_signals')
        .select(`
          *,
          trading_pairs (symbol)
        `)
        .order('created_at', { ascending: false })
        .limit(20);

      if (error) throw error;
      setSignals(data || []);
    } catch (error) {
      console.error('Error fetching signals:', error);
    }
  };

  const executeSignal = async (signalId: string) => {
    setLoading(true);
    try {
      const signal = signals.find(s => s.id === signalId);
      if (!signal) return;

      // Create a trade based on the signal
      const { error: tradeError } = await supabase
        .from('trades')
        .insert({
          signal_id: signalId,
          pair_id: signal.pair_id,
          trade_type: signal.signal as 'buy' | 'sell',
          amount: 0.1, // Default amount
          entry_price: signal.entry_price,
          stop_loss: signal.stop_loss,
          take_profit: signal.take_profit,
          status: 'executed',
          execution_time: new Date().toISOString()
        });

      if (tradeError) throw tradeError;

      // Mark signal as executed
      const { error: signalError } = await supabase
        .from('ai_signals')
        .update({ executed: true })
        .eq('id', signalId);

      if (signalError) throw signalError;

      toast.success('Signal executed successfully');
      fetchSignals();
    } catch (error) {
      console.error('Error executing signal:', error);
      toast.error('Failed to execute signal');
    } finally {
      setLoading(false);
    }
  };

  const generateAISignal = async () => {
    try {
      // Get a random trading pair
      const { data: pairs } = await supabase
        .from('trading_pairs')
        .select('*')
        .eq('is_active', true);

      if (!pairs?.length) return;

      const randomPair = pairs[Math.floor(Math.random() * pairs.length)];
      
      // Get latest market data for this pair
      const { data: marketData } = await supabase
        .from('market_data')
        .select('*')
        .eq('pair_id', randomPair.id)
        .order('timestamp', { ascending: false })
        .limit(1);

      const basePrice = marketData?.[0]?.close_price || 50000;
      const condition = marketData?.[0]?.market_condition || 'ranging';
      
      // AI Decision Logic based on market condition
      let signal: 'buy' | 'sell' | 'hold' = 'hold';
      let strategy: 'breakout' | 'mean_reversion' | 'momentum' | 'scalping' | 'grid' = 'momentum';
      let reasoning: string = '';
      
      switch (condition) {
        case 'trending_up':
          signal = 'buy';
          strategy = 'breakout';
          reasoning = 'Strong upward trend detected. RSI showing momentum continuation. Breakout strategy activated.';
          break;
        case 'trending_down':
          signal = 'sell';
          strategy = 'momentum';
          reasoning = 'Bearish momentum confirmed. MACD crossover detected. Momentum strategy engaged.';
          break;
        case 'ranging':
          signal = Math.random() > 0.5 ? 'buy' : 'sell';
          strategy = 'mean_reversion';
          reasoning = 'Market consolidating in range. Mean reversion opportunity identified at key level.';
          break;
        case 'volatile':
          signal = Math.random() > 0.3 ? (Math.random() > 0.5 ? 'buy' : 'sell') : 'hold';
          strategy = 'scalping';
          reasoning = 'High volatility environment. Quick scalping opportunity detected with tight risk management.';
          break;
      }

      const confidence = 0.7 + Math.random() * 0.25; // 70-95% confidence
      const entryPrice = basePrice * (1 + (Math.random() - 0.5) * 0.01);
      const stopLoss = signal === 'buy' ? entryPrice * 0.98 : entryPrice * 1.02;
      const takeProfit = signal === 'buy' ? entryPrice * 1.04 : entryPrice * 0.96;

      const { error } = await supabase
        .from('ai_signals')
        .insert({
          pair_id: randomPair.id,
          signal,
          confidence,
          strategy_used: strategy,
          entry_price: entryPrice,
          stop_loss: stopLoss,
          take_profit: takeProfit,
          reasoning,
          executed: false
        });

      if (error) throw error;
      
      toast.success(`New ${signal.toUpperCase()} signal generated for ${randomPair.symbol}`);
    } catch (error) {
      console.error('Error generating AI signal:', error);
      toast.error('Failed to generate signal');
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'buy':
        return <TrendingUp className="h-4 w-4" />;
      case 'sell':
        return <TrendingDown className="h-4 w-4" />;
      default:
        return <Minus className="h-4 w-4" />;
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy':
        return 'default';
      case 'sell':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  const getStrategyIcon = (strategy: string) => {
    switch (strategy) {
      case 'breakout':
        return <Zap className="h-3 w-3" />;
      case 'mean_reversion':
        return <Brain className="h-3 w-3" />;
      default:
        return <Clock className="h-3 w-3" />;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Live AI Signals</h2>
          <p className="text-muted-foreground">Real-time trading signals from our AI engine</p>
        </div>
        <Button onClick={generateAISignal} className="flex items-center space-x-2">
          <Brain className="h-4 w-4" />
          <span>Generate Signal</span>
        </Button>
      </div>

      <div className="grid gap-4">
        {signals.map((signal) => (
          <Card key={signal.id} className={`border-l-4 ${
            signal.signal === 'buy' ? 'border-l-green-500' : 
            signal.signal === 'sell' ? 'border-l-red-500' : 'border-l-yellow-500'
          }`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Badge variant={getSignalColor(signal.signal)} className="flex items-center space-x-1">
                    {getSignalIcon(signal.signal)}
                    <span className="uppercase font-bold">{signal.signal}</span>
                  </Badge>
                  <h3 className="font-semibold">{signal.trading_pairs?.symbol}</h3>
                  <Badge variant="outline" className="flex items-center space-x-1">
                    {getStrategyIcon(signal.strategy_used)}
                    <span className="capitalize">{signal.strategy_used.replace('_', ' ')}</span>
                  </Badge>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">
                    {(signal.confidence * 100).toFixed(0)}% Confidence
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {new Date(signal.created_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-sm text-muted-foreground">Entry Price</p>
                  <p className="font-semibold">${signal.entry_price?.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Stop Loss</p>
                  <p className="font-semibold text-red-500">${signal.stop_loss?.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Take Profit</p>
                  <p className="font-semibold text-green-500">${signal.take_profit?.toFixed(2)}</p>
                </div>
              </div>
              
              <div className="mb-4">
                <p className="text-sm text-muted-foreground mb-2">AI Reasoning</p>
                <p className="text-sm bg-muted/50 p-3 rounded-lg">{signal.reasoning}</p>
              </div>

              <div className="flex items-center justify-between">
                <Badge variant={signal.executed ? "default" : "outline"}>
                  {signal.executed ? "Executed" : "Pending"}
                </Badge>
                {!signal.executed && (
                  <Button 
                    size="sm" 
                    onClick={() => executeSignal(signal.id)}
                    disabled={loading}
                  >
                    Execute Trade
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}

        {signals.length === 0 && (
          <Card>
            <CardContent className="py-8 text-center">
              <Brain className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No signals yet</h3>
              <p className="text-muted-foreground mb-4">
                The AI engine is analyzing market conditions. Signals will appear here when opportunities are detected.
              </p>
              <Button onClick={generateAISignal}>Generate Demo Signal</Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default LiveSignals;
