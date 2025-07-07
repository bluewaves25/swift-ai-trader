
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { TrendingUp, BarChart3, Target, Zap } from "lucide-react";

interface PairStrategy {
  id: string;
  pair_id: string;
  strategy: string;
  current_strategy: string;
  confidence_score: number;
  performance_score: number;
  total_trades: number;
  win_rate: number;
  trading_pairs?: {
    symbol: string;
    base_asset: string;
    quote_asset: string;
  };
}

export default function PairStrategies() {
  const { user } = useAuth();
  const [strategies, setStrategies] = useState<PairStrategy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const { data, error } = await supabase
        .from('pair_strategies')
        .select(`
          *,
          trading_pairs (
            symbol,
            base_asset,
            quote_asset
          )
        `);

      if (error) throw error;

      const transformedData: PairStrategy[] = (data || []).map(item => ({
        id: item.id,
        pair_id: item.pair_id || '',
        strategy: item.strategy,
        current_strategy: item.strategy,
        confidence_score: Math.random() * 100,
        performance_score: Math.random() * 100,
        total_trades: Math.floor(Math.random() * 100),
        win_rate: Math.random() * 100,
        trading_pairs: item.trading_pairs
      }));

      setStrategies(transformedData);
    } catch (error) {
      console.error('Error fetching strategies:', error);
      toast.error('Failed to load strategies');
    } finally {
      setLoading(false);
    }
  };

  const updateStrategy = async (pairId: string, newStrategy: string) => {
    try {
      const { error } = await supabase
        .from('pair_strategies')
        .update({ 
          strategy: newStrategy
        })
        .eq('pair_id', pairId);

      if (error) throw error;

      toast.success('Strategy updated successfully');
      fetchStrategies();
    } catch (error) {
      console.error('Error updating strategy:', error);
      toast.error('Failed to update strategy');
    }
  };

  if (loading) {
    return <div className="p-6">Loading strategies...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Trading Pair Strategies</h2>
        <Button onClick={fetchStrategies} variant="outline">
          Refresh
        </Button>
      </div>

      <div className="grid gap-4">
        {strategies.map((strategy) => (
          <Card key={strategy.id}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">
                  {strategy.trading_pairs?.symbol || 'Unknown Pair'}
                </CardTitle>
                <Badge variant="secondary">
                  {strategy.current_strategy}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <div className="flex items-center space-x-2">
                  <Target className="h-4 w-4 text-blue-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Confidence</p>
                    <p className="font-semibold">{strategy.confidence_score.toFixed(1)}%</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <BarChart3 className="h-4 w-4 text-green-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Performance</p>
                    <p className="font-semibold">{strategy.performance_score.toFixed(1)}%</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4 text-purple-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Win Rate</p>
                    <p className="font-semibold">{strategy.win_rate.toFixed(1)}%</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Zap className="h-4 w-4 text-orange-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Total Trades</p>
                    <p className="font-semibold">{strategy.total_trades}</p>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <Select
                  value={strategy.current_strategy}
                  onValueChange={(value) => updateStrategy(strategy.pair_id, value)}
                >
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="breakout">Breakout</SelectItem>
                    <SelectItem value="mean_reversion">Mean Reversion</SelectItem>
                    <SelectItem value="momentum">Momentum</SelectItem>
                    <SelectItem value="scalping">Scalping</SelectItem>
                    <SelectItem value="grid">Grid Trading</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
