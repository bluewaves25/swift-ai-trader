
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { Calendar, TrendingUp, TrendingDown, Filter, Search } from "lucide-react";
import { apiService } from '@/services/api';
import { toast } from 'sonner';

interface Trade {
  id: string;
  symbol: string;
  trade_type: string;
  amount: number;
  entry_price: number;
  exit_price: number;
  profit_loss: number;
  status: string;
  timestamp: string;
  strategy: string;
  trading_pairs?: {
    symbol: string;
    base_asset: string;
    quote_asset: string;
  };
}

export default function TradeHistory() {
  const { user } = useAuth();
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchTrades = async () => {
      setLoading(true);
      setError(null);
      try {
        const { data } = await apiService.getTradeHistory();
        setTrades(
          Array.isArray(data.trades)
            ? data.trades.map((trade: any) => ({
                ...trade,
                symbol: trade.symbol ?? '',
                trade_type: trade.trade_type ?? '',
                amount: trade.amount ?? 0,
                entry_price: trade.entry_price ?? 0,
                exit_price: trade.exit_price ?? 0,
                profit_loss: trade.profit_loss ?? 0,
                status: trade.status ?? '',
                timestamp: trade.timestamp ?? '',
                strategy: trade.strategy ?? '',
              }))
            : []
        );
      } catch (err) {
        setError('Failed to fetch trade history');
        toast.error('Failed to fetch trade history');
      } finally {
        setLoading(false);
      }
    };
    fetchTrades();
  }, []);

  if (loading) return <div className="p-6">Loading trade history...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;
  if (!trades.length) return <div className="p-6">No trades found.</div>;

  const filteredTrades = trades.filter(trade => {
    const matchesStatus = filterStatus === 'all' || trade.status === filterStatus;
    const matchesSearch = trade.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         trade.strategy.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Trade History</h2>
        <Button onClick={() => {
          const fetchTrades = async () => {
            setLoading(true);
            setError(null);
            try {
              const { data } = await apiService.getTradeHistory();
              setTrades(
                Array.isArray(data.trades)
                  ? data.trades.map((trade: any) => ({
                      ...trade,
                      symbol: trade.symbol ?? '',
                      trade_type: trade.trade_type ?? '',
                      amount: trade.amount ?? 0,
                      entry_price: trade.entry_price ?? 0,
                      exit_price: trade.exit_price ?? 0,
                      profit_loss: trade.profit_loss ?? 0,
                      status: trade.status ?? '',
                      timestamp: trade.timestamp ?? '',
                      strategy: trade.strategy ?? '',
                    }))
                  : []
              );
            } catch (err) {
              setError('Failed to fetch trade history');
              toast.error('Failed to fetch trade history');
            } finally {
              setLoading(false);
            }
          };
          fetchTrades();
        }} variant="outline">
          Refresh
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
                      <Search className="absolute left-3 top-3 h-3 w-3 text-muted-foreground" />
          <Input
            placeholder="Search trades..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-48">
            <Filter className="h-3 w-3 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Trades</SelectItem>
            <SelectItem value="executed">Executed</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-4">
        {filteredTrades.map((trade) => (
          <Card key={trade.id}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    {trade.trade_type === 'buy' ? (
                      <TrendingUp className="h-3 w-3 text-green-500" />
                    ) : (
                                              <TrendingDown className="h-3 w-3 text-red-500" />
                    )}
                    <div>
                      <p className="font-semibold">{trade.symbol}</p>
                      <p className="text-sm text-muted-foreground">{trade.strategy}</p>
                    </div>
                  </div>
                  
                  <Badge variant={
                    trade.status === 'executed' ? 'default' :
                    trade.status === 'pending' ? 'secondary' : 'destructive'
                  }>
                    {trade.status}
                  </Badge>
                </div>

                <div className="text-right">
                  <p className={`font-semibold ${trade.profit_loss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {trade.profit_loss >= 0 ? '+' : ''}${trade.profit_loss.toFixed(2)}
                  </p>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Calendar className="h-3 w-3 mr-1" />
                    {new Date(trade.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t">
                <div>
                  <p className="text-sm text-muted-foreground">Type</p>
                  <p className="font-medium capitalize">{trade.trade_type}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Amount</p>
                  <p className="font-medium">{trade.amount.toFixed(4)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Entry Price</p>
                  <p className="font-medium">${trade.entry_price.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Exit Price</p>
                  <p className="font-medium">${trade.exit_price.toFixed(2)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredTrades.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-muted-foreground">No trades found matching your criteria.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
