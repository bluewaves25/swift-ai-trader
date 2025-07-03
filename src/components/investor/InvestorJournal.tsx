
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { 
  FileText, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Calendar,
  DollarSign,
  Target
} from "lucide-react";

interface JournalEntry {
  date: string;
  totalTrades: number;
  winningTrades: number;
  profitLoss: number;
  notes: string;
  performance: 'excellent' | 'good' | 'average' | 'poor';
}

const InvestorJournal = () => {
  const { user } = useAuth();
  const [journalEntries, setJournalEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJournalData();
  }, [user]);

  const fetchJournalData = async () => {
    try {
      // Fetch performance analytics data
      const { data: analytics, error } = await supabase
        .from('performance_analytics')
        .select('*')
        .order('date', { ascending: false })
        .limit(30);

      if (error) throw error;

      // Transform analytics data into journal entries
      const entries: JournalEntry[] = (analytics || []).map(entry => {
        const winRate = entry.total_trades ? (entry.winning_trades || 0) / entry.total_trades * 100 : 0;
        let performance: JournalEntry['performance'] = 'average';
        
        if (winRate >= 80) performance = 'excellent';
        else if (winRate >= 70) performance = 'good';
        else if (winRate >= 50) performance = 'average';
        else performance = 'poor';

        return {
          date: entry.date,
          totalTrades: entry.total_trades || 0,
          winningTrades: entry.winning_trades || 0,
          profitLoss: entry.total_profit || 0,
          notes: generateNotes(entry),
          performance
        };
      });

      setJournalEntries(entries);
    } catch (error) {
      console.error('Error fetching journal data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateNotes = (entry: any) => {
    const winRate = entry.total_trades ? (entry.winning_trades || 0) / entry.total_trades * 100 : 0;
    const profit = entry.total_profit || 0;
    
    let notes = [];
    
    if (winRate >= 80) {
      notes.push("Exceptional performance today with high win rate.");
    } else if (winRate >= 70) {
      notes.push("Strong trading performance with good risk management.");
    } else if (winRate < 50) {
      notes.push("Below average performance. Risk management protocols engaged.");
    }
    
    if (profit > 1000) {
      notes.push("Significant profit achieved through AI-driven strategies.");
    } else if (profit < -500) {
      notes.push("Defensive trading mode activated due to market volatility.");
    }
    
    if (entry.max_drawdown && entry.max_drawdown > 0.1) {
      notes.push("Higher than usual drawdown observed. Position sizing adjusted.");
    }
    
    return notes.join(" ") || "Standard trading session with automated execution.";
  };

  const getPerformanceBadge = (performance: JournalEntry['performance']) => {
    const variants = {
      excellent: { variant: "default" as const, color: "text-green-500" },
      good: { variant: "secondary" as const, color: "text-blue-500" },
      average: { variant: "outline" as const, color: "text-yellow-500" },
      poor: { variant: "destructive" as const, color: "text-red-500" }
    };
    
    return variants[performance];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center">
            <Activity className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">Loading trading journal...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>Trading Journal</span>
          </CardTitle>
          <CardDescription>
            Daily performance tracking and AI trading insights
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="space-y-4">
        {journalEntries.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg font-medium mb-2">No Journal Entries Yet</p>
              <p className="text-muted-foreground">
                Trading journal entries will appear here once trading begins
              </p>
            </CardContent>
          </Card>
        ) : (
          journalEntries.map((entry, index) => (
            <Card key={`${entry.date}-${index}`}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Calendar className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <h3 className="font-semibold">{formatDate(entry.date)}</h3>
                      <p className="text-sm text-muted-foreground">Automated AI Trading Session</p>
                    </div>
                  </div>
                  <Badge {...getPerformanceBadge(entry.performance)}>
                    {entry.performance.charAt(0).toUpperCase() + entry.performance.slice(1)}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="flex items-center space-x-2">
                    <Activity className="h-4 w-4 text-blue-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Total Trades</p>
                      <p className="font-semibold">{entry.totalTrades}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Target className="h-4 w-4 text-green-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Winning Trades</p>
                      <p className="font-semibold">{entry.winningTrades}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <DollarSign className="h-4 w-4 text-purple-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Win Rate</p>
                      <p className="font-semibold">
                        {entry.totalTrades ? ((entry.winningTrades / entry.totalTrades) * 100).toFixed(1) : 0}%
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {entry.profitLoss >= 0 ? 
                      <TrendingUp className="h-4 w-4 text-green-500" /> :
                      <TrendingDown className="h-4 w-4 text-red-500" />
                    }
                    <div>
                      <p className="text-sm text-muted-foreground">Daily P&L</p>
                      <p className={`font-semibold ${entry.profitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        ${entry.profitLoss.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>

                <Separator className="my-4" />

                <div>
                  <h4 className="font-medium mb-2">AI Trading Notes</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {entry.notes}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default InvestorJournal;
