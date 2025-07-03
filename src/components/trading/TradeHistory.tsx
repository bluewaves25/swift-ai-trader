
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { Clock, TrendingUp, TrendingDown, Filter } from "lucide-react";

interface Trade {
  id: string;
  trade_type: string;
  amount: number;
  entry_price: number;
  exit_price: number | null;
  profit_loss: number;
  status: string;
  created_at: string;
  closed_at: string | null;
  trading_pairs: {
    symbol: string;
  };
  ai_signals: {
    strategy_used: string;
    confidence: number;
  } | null;
}

const TradeHistory = () => {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchTrades();
    
    // Set up realtime subscription
    const subscription = supabase
      .channel('trades_changes')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'trades' },
        () => {
          fetchTrades();
        }
      )
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const fetchTrades = async () => {
    try {
      const { data, error } = await supabase
        .from('trades')
        .select(`
          *,
          trading_pairs (symbol),
          ai_signals (strategy_used, confidence)
        `)
        .order('created_at', { ascending: false })
        .limit(100);

      if (error) throw error;
      setTrades(data || []);
    } catch (error) {
      console.error('Error fetching trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTrades = trades.filter(trade => {
    if (filter === 'all') return true;
    if (filter === 'open') return trade.status === 'executed' && !trade.exit_price;
    if (filter === 'closed') return trade.status === 'executed' && trade.exit_price;
    if (filter === 'profitable') return trade.profit_loss > 0;
    return true;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'executed': return 'default';
      case 'pending': return 'secondary';
      case 'cancelled': return 'destructive';
      default: return 'outline';
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Trade History</CardTitle>
            <CardDescription>Complete record of all executed trades</CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant={filter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('all')}
            >
              All
            </Button>
            <Button
              variant={filter === 'open' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('open')}
            >
              Open
            </Button>
            <Button
              variant={filter === 'closed' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('closed')}
            >
              Closed
            </Button>
            <Button
              variant={filter === 'profitable' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('profitable')}
            >
              Profitable
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {loading ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Loading trades...</p>
            </div>
          ) : filteredTrades.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No trades found</h3>
              <p className="text-muted-foreground">
                {filter === 'all' 
                  ? 'The trading engine will execute trades based on AI signals.' 
                  : `No ${filter} trades found.`}
              </p>
            </div>
          ) : (
            filteredTrades.map((trade) => (
              <div key={trade.id} 
                className={`border rounded-lg p-4 space-y-3 ${
                  trade.profit_loss > 0 ? 'border-green-200 bg-green-50/50 dark:border-green-800 dark:bg-green-950/20' :
                  trade.profit_loss < 0 ? 'border-red-200 bg-red-50/50 dark:border-red-800 dark:bg-red-950/20' :
                  'border-border'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Badge variant={trade.trade_type === 'buy' ? 'default' : 'destructive'} 
                           className="flex items-center space-x-1">
                      {trade.trade_type === 'buy' ? 
                        <TrendingUp className="h-3 w-3" /> : 
                        <TrendingDown className="h-3 w-3" />
                      }
                      <span>{trade.trade_type.toUpperCase()}</span>
                    </Badge>
                    <h3 className="font-semibold">{trade.trading_pairs?.symbol}</h3>
                    <Badge variant={getStatusColor(trade.status)} className="capitalize">
                      {trade.status}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${
                      trade.profit_loss > 0 ? 'text-green-600 dark:text-green-400' :
                      trade.profit_loss < 0 ? 'text-red-600 dark:text-red-400' :
                      'text-muted-foreground'
                    }`}>
                      {trade.profit_loss > 0 ? '+' : ''}${trade.profit_loss.toFixed(2)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {((trade.profit_loss / (trade.entry_price * trade.amount)) * 100).toFixed(2)}%
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Amount</p>
                    <p className="font-medium">{trade.amount.toFixed(4)}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Entry Price</p>
                    <p className="font-medium">${trade.entry_price.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Exit Price</p>
                    <p className="font-medium">
                      {trade.exit_price ? `$${trade.exit_price.toFixed(2)}` : 'Open'}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Duration</p>
                    <p className="font-medium">
                      {trade.closed_at ? 
                        `${Math.round((new Date(trade.closed_at).getTime() - new Date(trade.created_at).getTime()) / 60000)}m` :
                        'Open'
                      }
                    </p>
                  </div>
                </div>

                {trade.ai_signals && (
                  <div className="flex items-center space-x-4 text-sm bg-muted/50 p-3 rounded">
                    <Badge variant="outline" className="capitalize">
                      {trade.ai_signals.strategy_used.replace('_', ' ')}
                    </Badge>
                    <span className="text-muted-foreground">
                      Confidence: {(trade.ai_signals.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                )}

                <div className="flex justify-between items-center text-xs text-muted-foreground">
                  <span>Opened: {new Date(trade.created_at).toLocaleString()}</span>
                  {trade.closed_at && (
                    <span>Closed: {new Date(trade.closed_at).toLocaleString()}</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default TradeHistory;
