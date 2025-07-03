
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/integrations/supabase/client";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MarketData {
  id: string;
  timestamp: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
  market_condition: string;
  rsi: number;
  macd: number;
  bollinger_upper: number;
  bollinger_lower: number;
  support_level: number;
  resistance_level: number;
}

interface TradingPair {
  id: string;
  symbol: string;
  base_currency: string;
  quote_currency: string;
}

const TradingChart = () => {
  const [selectedPair, setSelectedPair] = useState<string>("");
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [priceChange, setPriceChange] = useState<number>(0);
  const [marketCondition, setMarketCondition] = useState<string>("ranging");

  useEffect(() => {
    fetchTradingPairs();
  }, []);

  useEffect(() => {
    if (selectedPair) {
      fetchMarketData(selectedPair);
      const interval = setInterval(() => fetchMarketData(selectedPair), 2000);
      return () => clearInterval(interval);
    }
  }, [selectedPair]);

  const fetchTradingPairs = async () => {
    try {
      const { data, error } = await supabase
        .from('trading_pairs')
        .select('*')
        .eq('is_active', true)
        .order('symbol');

      if (error) throw error;
      
      setTradingPairs(data || []);
      if (data?.length && !selectedPair) {
        setSelectedPair(data[0].id);
      }
    } catch (error) {
      console.error('Error fetching trading pairs:', error);
    }
  };

  const fetchMarketData = async (pairId: string) => {
    try {
      const { data, error } = await supabase
        .from('market_data')
        .select('*')
        .eq('pair_id', pairId)
        .order('timestamp', { ascending: false })
        .limit(50);

      if (error) throw error;

      const formattedData = (data || []).reverse().map(item => ({
        ...item,
        time: new Date(item.timestamp).toLocaleTimeString(),
        price: item.close_price
      }));

      setMarketData(formattedData);
      
      if (formattedData.length > 0) {
        const latest = formattedData[formattedData.length - 1];
        const previous = formattedData[formattedData.length - 2];
        
        setCurrentPrice(latest.close_price);
        setMarketCondition(latest.market_condition || 'ranging');
        
        if (previous) {
          setPriceChange(((latest.close_price - previous.close_price) / previous.close_price) * 100);
        }
      }
    } catch (error) {
      console.error('Error fetching market data:', error);
    }
  };

  const generateMockData = () => {
    if (!selectedPair) return;

    // Generate realistic market data with technical indicators
    const basePrice = currentPrice || 50000;
    const volatility = 0.02;
    const now = new Date();
    
    const conditions: Array<'trending_up' | 'trending_down' | 'ranging' | 'volatile'> = 
      ['trending_up', 'trending_down', 'ranging', 'volatile'];
    
    const newDataPoint = {
      pair_id: selectedPair,
      timestamp: now.toISOString(),
      open_price: basePrice * (1 + (Math.random() - 0.5) * volatility),
      high_price: basePrice * (1 + Math.random() * volatility),
      low_price: basePrice * (1 - Math.random() * volatility),
      close_price: basePrice * (1 + (Math.random() - 0.5) * volatility),
      volume: Math.random() * 1000000,
      market_condition: conditions[Math.floor(Math.random() * conditions.length)],
      rsi: 30 + Math.random() * 40,
      macd: (Math.random() - 0.5) * 100,
      bollinger_upper: basePrice * 1.02,
      bollinger_lower: basePrice * 0.98,
      support_level: basePrice * 0.95,
      resistance_level: basePrice * 1.05
    };

    // Insert into database
    supabase
      .from('market_data')
      .insert(newDataPoint)
      .then(({ error }) => {
        if (error) console.error('Error inserting market data:', error);
      });
  };

  // Generate mock data every 3 seconds for demo
  useEffect(() => {
    const interval = setInterval(generateMockData, 3000);
    return () => clearInterval(interval);
  }, [selectedPair, currentPrice]);

  const selectedPairData = tradingPairs.find(pair => pair.id === selectedPair);
  const getMarketConditionIcon = (condition: string) => {
    switch (condition) {
      case 'trending_up':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'trending_down':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <Minus className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getMarketConditionColor = (condition: string) => {
    switch (condition) {
      case 'trending_up':
        return 'default';
      case 'trending_down':
        return 'destructive';
      case 'volatile':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  return (
    <Card className="h-[500px]">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Live Chart</CardTitle>
            <CardDescription>Real-time market data with technical analysis</CardDescription>
          </div>
          <div className="flex items-center space-x-4">
            <Select value={selectedPair} onValueChange={setSelectedPair}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select pair" />
              </SelectTrigger>
              <SelectContent>
                {tradingPairs.map((pair) => (
                  <SelectItem key={pair.id} value={pair.id}>
                    {pair.symbol}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        
        {selectedPairData && (
          <div className="flex items-center space-x-4">
            <div>
              <p className="text-2xl font-bold">${currentPrice.toFixed(2)}</p>
              <p className={`text-sm ${priceChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%
              </p>
            </div>
            <Badge variant={getMarketConditionColor(marketCondition)} className="flex items-center space-x-1">
              {getMarketConditionIcon(marketCondition)}
              <span className="capitalize">{marketCondition.replace('_', ' ')}</span>
            </Badge>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={marketData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis 
                dataKey="time" 
                className="text-xs"
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                domain={['dataMin - 100', 'dataMax + 100']}
                className="text-xs"
                tick={{ fontSize: 12 }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="close_price" 
                stroke="hsl(var(--primary))" 
                strokeWidth={2}
                dot={false}
              />
              {marketData.length > 0 && marketData[marketData.length - 1] && (
                <>
                  <ReferenceLine 
                    y={marketData[marketData.length - 1].support_level} 
                    stroke="hsl(var(--destructive))" 
                    strokeDasharray="5 5"
                    label="Support"
                  />
                  <ReferenceLine 
                    y={marketData[marketData.length - 1].resistance_level} 
                    stroke="hsl(var(--chart-2))" 
                    strokeDasharray="5 5"
                    label="Resistance"
                  />
                </>
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

export default TradingChart;
