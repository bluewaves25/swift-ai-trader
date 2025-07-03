
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { supabase } from "@/integrations/supabase/client";
import { Brain, TrendingUp, Settings, BarChart3 } from "lucide-react";
import { toast } from "sonner";

interface PairStrategy {
  id: string;
  pair_id: string;
  current_strategy: string;
  confidence_score: number;
  performance_score: number;
  total_trades: number;
  winning_trades: number;
  last_updated: string;
  trading_pairs: {
    symbol: string;
    base_currency: string;
    quote_currency: string;
  };
}

const PairStrategies = () => {
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
          trading_pairs (symbol, base_currency, quote_currency)
        `)
        .order('performance_score', { ascending: false });

      if (error) throw error;
      setStrategies(data || []);
    } catch (error) {
      console.error('Error fetching strategies:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateStrategy = async (strategyId: string, newStrategy: string) => {
    try {
      const { error } = await supabase
        .from('pair_strategies')
        .update({ 
          current_strategy: newStrategy,
          last_updated: new Date().toISOString()
        })
        .eq('id', strategyId);

      if (error) throw error;
      
      toast.success('Strategy updated successfully');
      fetchStrategies();
    } catch (error) {
      console.error('Error updating strategy:', error);
      toast.error('Failed to update strategy');
    }
  };

  const getStrategyColor = (strategy: string) => {
    switch (strategy) {
      case 'breakout': return 'default';
      case 'mean_reversion': return 'secondary';
      case 'momentum': return 'destructive';
      case 'scalping': return 'outline';
      case 'grid': return 'default';
      default: return 'outline';
    }
  };

  const getStrategyIcon = (strategy: string) => {
    switch (strategy) {
      case 'breakout': return <TrendingUp className="h-4 w-4" />;
      case 'momentum': return <BarChart3 className="h-4 w-4" />;
      default: return <Brain className="h-4 w-4" />;
    }
  };

  const winRate = (strategy: PairStrategy) => {
    return strategy.total_trades > 0 ? (strategy.winning_trades / strategy.total_trades) * 100 : 0;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Brain className="h-5 w-5" />
          <span>AI Strategies per Trading Pair</span>
        </CardTitle>
        <CardDescription>
          Each trading pair uses a unique AI strategy based on market conditions
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {loading ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Loading strategies...</p>
            </div>
          ) : strategies.length === 0 ? (
            <div className="text-center py-8">
              <Brain className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No strategies configured</h3>
              <p className="text-muted-foreground">
                Strategies will be automatically assigned as trading pairs become active.
              </p>
            </div>
          ) : (
            <div className="grid gap-4">
              {strategies.map((strategy) => (
                <div key={strategy.id} className="border rounded-lg p-4 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center space-x-2">
                        {getStrategyIcon(strategy.current_strategy)}
                        <h3 className="font-semibold text-lg">
                          {strategy.trading_pairs?.symbol}
                        </h3>
                      </div>
                      <Badge variant={getStrategyColor(strategy.current_strategy)} className="capitalize">
                        {strategy.current_strategy.replace('_', ' ')}
                      </Badge>
                    </div>
                    <Select 
                      value={strategy.current_strategy} 
                      onValueChange={(value) => updateStrategy(strategy.id, value)}
                    >
                      <SelectTrigger className="w-[180px]">
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

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Performance</p>
                      <div className="space-y-2">
                        <p className="font-semibold">
                          {(strategy.performance_score * 100).toFixed(1)}%
                        </p>
                        <Progress value={strategy.performance_score * 100} className="h-2" />
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Confidence</p>
                      <div className="space-y-2">
                        <p className="font-semibold">
                          {(strategy.confidence_score * 100).toFixed(1)}%
                        </p>
                        <Progress value={strategy.confidence_score * 100} className="h-2" />
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Total Trades</p>
                      <p className="font-semibold text-lg">{strategy.total_trades}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Win Rate</p>
                      <div className="space-y-2">
                        <p className="font-semibold">{winRate(strategy).toFixed(1)}%</p>
                        <Progress value={winRate(strategy)} className="h-2" />
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-between items-center text-sm text-muted-foreground">
                    <span>
                      Winning: {strategy.winning_trades} / {strategy.total_trades}
                    </span>
                    <span>
                      Last Updated: {new Date(strategy.last_updated).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default PairStrategies;
