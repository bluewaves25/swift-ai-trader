
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { TrendingUp, TrendingDown, Calendar, BarChart3 } from "lucide-react";

interface JournalEntry {
  id: string;
  date: string;
  strategy: string;
  profit_loss: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  total_profit: number;
}

export default function InvestorJournal() {
  const { user } = useAuth();
  const [journalEntries, setJournalEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchJournalData();
    }
  }, [user]);

  const fetchJournalData = async () => {
    try {
      const { data: analytics } = await supabase
        .from('performance_analytics')
        .select('*')
        .eq('user_id', user?.id)
        .order('timestamp', { ascending: false });

      if (analytics) {
        setJournalEntries(analytics);
      }
    } catch (error) {
      console.error('Error fetching journal data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Loading journal...</div>;
  }

  const totalProfit = journalEntries.reduce((sum, entry) => sum + entry.total_profit, 0);
  const totalTrades = journalEntries.reduce((sum, entry) => sum + entry.total_trades, 0);
  const winningTrades = journalEntries.reduce((sum, entry) => sum + entry.winning_trades, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Trading Journal</h2>
        <Badge variant={totalProfit >= 0 ? "default" : "destructive"}>
          {totalProfit >= 0 ? "Profitable" : "Loss"}
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Total Trades</p>
                <p className="text-2xl font-bold">{totalTrades}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <div>
                <p className="text-sm text-muted-foreground">Win Rate</p>
                <p className="text-2xl font-bold">
                  {totalTrades > 0 ? ((winningTrades / totalTrades) * 100).toFixed(1) : 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              {totalProfit >= 0 ? (
                <TrendingUp className="h-4 w-4 text-green-500" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-500" />
              )}
              <div>
                <p className="text-sm text-muted-foreground">Total P&L</p>
                <p className={`text-2xl font-bold ${totalProfit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  ${totalProfit.toFixed(2)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        {journalEntries.map((entry) => (
          <Card key={entry.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{entry.strategy} Strategy</CardTitle>
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">{entry.date}</span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Trades</p>
                  <p className="font-semibold">{entry.total_trades}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Winners</p>
                  <p className="font-semibold text-green-500">{entry.winning_trades}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Profit</p>
                  <p className={`font-semibold ${entry.total_profit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    ${entry.total_profit.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Win Rate</p>
                  <p className="font-semibold">{entry.win_rate.toFixed(1)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
