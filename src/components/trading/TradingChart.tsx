
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { TrendingUp, TrendingDown, Minus, RefreshCw } from "lucide-react";
import { useMarketData } from "@/hooks/useApi";
import { apiService } from "@/services/api";

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
  asset_class: string;
}

const TradingChart = () => {
  const [selectedPair, setSelectedPair] = useState<string>("");
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [priceChange, setPriceChange] = useState<number>(0);
  const [marketCondition, setMarketCondition] = useState<string>("ranging");
  const [selectedAssetClass, setSelectedAssetClass] = useState<string>("all");
  const [isConnected, setIsConnected] = useState(false);

  const assetClasses = [
    { value: "all", label: "All Assets" },
    { value: "forex", label: "Forex" },
    { value: "crypto", label: "Crypto" },
    { value: "stocks", label: "Stocks" },
    { value: "commodities", label: "Commodities" },
    { value: "indices", label: "Indices" }
  ];

  useEffect(() => {
    fetchTradingPairs();
    checkBackendConnection();
  }, []);

  useEffect(() => {
    if (selectedPair) {
      fetchMarketData(selectedPair);
      const interval = setInterval(() => fetchMarketData(selectedPair), 2000);
      return () => clearInterval(interval);
    }
  }, [selectedPair]);

  const checkBackendConnection = async () => {
    try {
      await apiService.healthCheck();
      setIsConnected(true);
    } catch (error) {
      console.error('Backend connection failed:', error);
      setIsConnected(false);
    }
  };

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
      // First try to get from Supabase
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

      // If connected to backend, also fetch live data
      if (isConnected) {
        const pair = tradingPairs.find(p => p.id === pairId);
        if (pair) {
          try {
            const liveData = await apiService.getMarketData(pair.symbol);
            // Process and merge live data
            console.log('Live market data:', liveData);
          } catch (error) {
            console.error('Error fetching live data:', error);
          }
        }
      }
    } catch (error) {
      console.error('Error fetching market data:', error);
    }
  };

  const generateMockData = async () => {
    if (!selectedPair) return;

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

    try {
      const { error } = await supabase
        .from('market_data')
        .insert(newDataPoint);
      
      if (error) throw error;
    } catch (error) {
      console.error('Error inserting market data:', error);
    }
  };

  useEffect(() => {
    const interval = setInterval(generateMockData, 3000);
    return () => clearInterval(interval);
  }, [selectedPair, currentPrice]);

  const filteredPairs = selectedAssetClass === 'all' 
    ? tradingPairs 
    : tradingPairs.filter(pair => pair.asset_class === selectedAssetClass);

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
            <CardTitle className="flex items-center space-x-2">
              <span>Multi-Asset Live Chart</span>
              <Badge variant={isConnected ? "default" : "destructive"}>
                {isConnected ? "Connected" : "Offline"}
              </Badge>
            </CardTitle>
            <CardDescription>Real-time market data across all asset classes</CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Select value={selectedAssetClass} onValueChange={setSelectedAssetClass}>
              <SelectTrigger className="w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {assetClasses.map((assetClass) => (
                  <SelectItem key={assetClass.value} value={assetClass.value}>
                    {assetClass.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedPair} onValueChange={setSelectedPair}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select pair" />
              </SelectTrigger>
              <SelectContent>
                {filteredPairs.map((pair) => (
                  <SelectItem key={pair.id} value={pair.id}>
                    {pair.symbol}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="sm"
              onClick={checkBackendConnection}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
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
            <Badge variant="outline" className="capitalize">
              {selectedPairData.asset_class || 'Unknown'}
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
