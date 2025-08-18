
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/integrations/supabase/client";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";

interface MarketData {
  id: string;
  symbol: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TradingPair {
  id: string;
  symbol: string;
  base_asset: string;
  quote_asset: string;
  broker: string;
}

export default function TradingChart() {
  const [selectedPair, setSelectedPair] = useState<string>('EURUSD');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [priceChange, setPriceChange] = useState<number>(0);

  useEffect(() => {
    fetchTradingPairs();
    fetchMarketData();
    const interval = setInterval(fetchMarketData, 5000);
    return () => clearInterval(interval);
  }, [selectedPair]);

  const fetchTradingPairs = async () => {
    try {
      const { data, error } = await supabase
        .from('trading_pairs')
        .select('*')
        .limit(10);

      if (error) throw error;

      const pairs: TradingPair[] = (data || []).map(pair => ({
        id: pair.id,
        symbol: pair.symbol,
        base_asset: pair.base_asset,
        quote_asset: pair.quote_asset,
        broker: pair.broker || 'Unknown'
      }));

      setTradingPairs(pairs);
    } catch (error) {
      console.error('Error fetching trading pairs:', error);
    }
  };

  const fetchMarketData = async () => {
    try {
      const { data, error } = await supabase
        .from('market_data')
        .select('*')
        .eq('symbol', selectedPair)
        .order('timestamp', { ascending: true })
        .limit(50);

      if (error) throw error;

      let processedData: MarketData[] = [];
      if (data && data.length > 0) {
        processedData = data.map(item => ({
          id: item.id,
          symbol: item.symbol,
          timestamp: item.timestamp || new Date().toISOString(),
          open: item.open || 0,
          high: item.high || 0,
          low: item.low || 0,
          close: item.close || 0,
          volume: item.volume || 0
        }));
      }
      setMarketData(processedData);
      if (processedData.length > 0) {
        const latest = processedData[processedData.length - 1];
        const previous = processedData[processedData.length - 2];
        setCurrentPrice(latest.close);
        setPriceChange(previous ? ((latest.close - previous.close) / previous.close) * 100 : 0);
      }
    } catch (error) {
      console.error('Error fetching market data:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = marketData.map(item => ({
    time: new Date(item.timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    }),
    price: item.close,
    volume: item.volume
  }));

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Live Market Data</CardTitle>
            <Select value={selectedPair} onValueChange={setSelectedPair}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="EURUSD">EUR/USD</SelectItem>
                <SelectItem value="GBPUSD">GBP/USD</SelectItem>
                <SelectItem value="USDJPY">USD/JPY</SelectItem>
                <SelectItem value="AUDUSD">AUD/USD</SelectItem>
                <SelectItem value="USDCAD">USD/CAD</SelectItem>
                {tradingPairs.map(pair => (
                  <SelectItem key={pair.id} value={pair.symbol}>
                    {pair.symbol}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div>
                <p className="text-2xl font-bold">{currentPrice.toFixed(5)}</p>
                <p className="text-xs text-muted-foreground">{selectedPair}</p>
              </div>
              <Badge variant={priceChange >= 0 ? "default" : "destructive"} className="flex items-center space-x-1">
                                  {priceChange >= 0 ? <TrendingUp className="h-1.5 w-1.5" /> : <TrendingDown className="h-1.5 w-1.5" />}
                <span>{priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%</span>
              </Badge>
            </div>
            <div className="flex items-center space-x-2">
                              <Activity className="h-2 w-2 text-green-500" />
                              <span className="text-xs text-green-500">Live</span>
            </div>
          </div>

          {loading ? (
            <div className="h-64 flex items-center justify-center">
              <p className="text-muted-foreground">Loading chart data...</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis 
                  dataKey="time" 
                  tick={{ fontSize: 12 }}
                  interval="preserveStartEnd"
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  domain={['dataMin - 0.001', 'dataMax + 0.001']}
                  tickFormatter={(value) => value.toFixed(5)}
                />
                <Tooltip 
                  labelFormatter={(label) => `Time: ${label}`}
                  formatter={(value: any) => [value.toFixed(5), 'Price']}
                />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
