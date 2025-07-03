
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import TradingChart from "@/components/trading/TradingChart";
import { BarChart3, TrendingUp, TrendingDown, DollarSign, Activity, LogOut } from "lucide-react";

interface Portfolio {
  total_balance: number;
  available_balance: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_trades: number;
  winning_trades: number;
}

interface Trade {
  id: string;
  trade_type: string;
  amount: number;
  entry_price: number;
  exit_price: number | null;
  profit_loss: number;
  status: string;
  created_at: string;
  trading_pairs: {
    symbol: string;
  };
}

const InvestorDashboard = () => {
  const { signOut, user } = useAuth();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPortfolio();
    fetchTrades();
  }, [user]);

  const fetchPortfolio = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('portfolios')
        .select('*')
        .eq('user_id', user.id)
        .single();

      if (error && error.code !== 'PGRST116') {
        console.error('Error fetching portfolio:', error);
        return;
      }

      if (data) {
        setPortfolio(data);
      } else {
        // Create initial portfolio
        const { data: newPortfolio, error: createError } = await supabase
          .from('portfolios')
          .insert({
            user_id: user.id,
            total_balance: 10000,
            available_balance: 10000
          })
          .select()
          .single();

        if (createError) {
          console.error('Error creating portfolio:', createError);
        } else {
          setPortfolio(newPortfolio);
        }
      }
    } catch (error) {
      console.error('Error in fetchPortfolio:', error);
    }
  };

  const fetchTrades = async () => {
    try {
      const { data, error } = await supabase
        .from('trades')
        .select(`
          *,
          trading_pairs (symbol)
        `)
        .order('created_at', { ascending: false })
        .limit(20);

      if (error) throw error;
      setTrades(data || []);
    } catch (error) {
      console.error('Error fetching trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const winRate = portfolio?.total_trades ? 
    (portfolio.winning_trades / portfolio.total_trades * 100) : 0;

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b">
        <div className="flex h-16 items-center px-4 justify-between">
          <div className="flex items-center space-x-4">
            <Activity className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-xl font-bold">Waves Quant Engine</h1>
              <p className="text-sm text-muted-foreground">Investor Dashboard</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            <Badge variant="secondary">{user?.email}</Badge>
            <Button variant="outline" size="sm" onClick={signOut}>
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Portfolio Overview */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Balance</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${portfolio?.total_balance?.toFixed(2) || '0.00'}</div>
              <p className="text-xs text-muted-foreground">
                Available: ${portfolio?.available_balance?.toFixed(2) || '0.00'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Realized P&L</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${
                (portfolio?.realized_pnl || 0) >= 0 ? 'text-green-500' : 'text-red-500'
              }`}>
                ${portfolio?.realized_pnl?.toFixed(2) || '0.00'}
              </div>
              <p className="text-xs text-muted-foreground">
                Unrealized: ${portfolio?.unrealized_pnl?.toFixed(2) || '0.00'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{portfolio?.total_trades || 0}</div>
              <p className="text-xs text-muted-foreground">
                Winning: {portfolio?.winning_trades || 0}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{winRate.toFixed(1)}%</div>
              <Progress value={winRate} className="mt-2" />
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="chart" className="space-y-4">
          <TabsList>
            <TabsTrigger value="chart">Live Chart</TabsTrigger>
            <TabsTrigger value="trades">Trade History</TabsTrigger>
          </TabsList>

          <TabsContent value="chart" className="space-y-4">
            <TradingChart />
          </TabsContent>

          <TabsContent value="trades" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Trades</CardTitle>
                <CardDescription>Your automated trading history</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {trades.map((trade) => (
                    <div key={trade.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <Badge variant={trade.trade_type === 'buy' ? 'default' : 'destructive'}>
                          {trade.trade_type.toUpperCase()}
                        </Badge>
                        <div>
                          <p className="font-medium">{trade.trading_pairs?.symbol}</p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(trade.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">${trade.amount.toFixed(4)}</p>
                        <p className={`text-sm ${
                          trade.profit_loss >= 0 ? 'text-green-500' : 'text-red-500'
                        }`}>
                          {trade.profit_loss >= 0 ? '+' : ''}${trade.profit_loss.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  ))}
                  {trades.length === 0 && (
                    <p className="text-center text-muted-foreground py-8">
                      No trades yet. The AI engine will start trading based on market conditions.
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default InvestorDashboard;
