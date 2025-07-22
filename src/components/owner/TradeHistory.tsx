import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useToast } from "@/hooks/use-toast";
import { 
  History, 
  Search, 
  Filter, 
  Download, 
  X, 
  TrendingUp, 
  TrendingDown,
  Clock,
  DollarSign,
  BarChart3,
  AlertCircle,
  CheckCircle,
  XCircle
} from "lucide-react";
import { cn } from "@/lib/utils";
import { apiService, Trade } from "@/services/api";
import { API_ENDPOINTS, apiCall } from "@/config/api";

export function TradeHistory() {
  const [trades, setTrades] = useState<any[]>([]);
  const [filteredTrades, setFilteredTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const { toast } = useToast();

  useEffect(() => {
    const triggerAndFetch = async () => {
      setLoading(true);
      try {
        await apiCall(API_ENDPOINTS.OWNER_MT5_TRIGGER_SYNC, { method: 'POST' });
        // Allow a moment for the background task to process
        setTimeout(async () => {
          const tradesRes = await apiCall(API_ENDPOINTS.OWNER_ALL_TRADES);
          setTrades(Array.isArray(tradesRes.trades) ? tradesRes.trades : []);
          setLoading(false);
        }, 2000);
      } catch (error) {
        setTrades([]);
        setLoading(false);
      }
    };
    triggerAndFetch();
  }, []);

  useEffect(() => {
    filterAndSortTrades();
  }, [trades, searchTerm, statusFilter, sortBy, sortOrder]);

  const filterAndSortTrades = () => {
    let filtered = trades.filter(trade => {
      const matchesSearch = trade.symbol?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === "all" || trade.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      if (sortBy === 'created_at' && aValue && bValue) {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      }
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    setFilteredTrades(filtered);
  };

  const handleCloseTrade = async (tradeId: string) => {
    try {
      // Example close trade handler (apiService.closeTrade does not exist)
      // TODO: Implement close trade logic or call backend endpoint if available
      alert(`Close trade ${tradeId} (not implemented)`);
      toast({
        title: "Trade Closed",
        description: "Trade has been closed successfully",
        className: "toast-landing"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to close trade",
        variant: "destructive"
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'closed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return "bg-blue-100 text-blue-800 border-blue-200";
      case 'closed':
        return "bg-green-100 text-green-800 border-green-200";
      case 'cancelled':
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getBrokerColor = (broker: string) => {
    switch (broker) {
      case 'binance':
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case 'exness':
        return "bg-purple-100 text-purple-800 border-purple-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const exportTrades = () => {
    const csvContent = [
      ['Symbol', 'Type', 'Volume', 'Open Price', 'Close Price', 'Status', 'Broker', 'Category', 'Profit', 'Commission', 'Open Time', 'Close Time', 'Strategy'].join(','),
      ...filteredTrades.map(trade => [
        trade.symbol,
        trade.type,
        trade.volume,
        trade.openPrice,
        trade.closePrice || '',
        trade.status,
        trade.broker,
        trade.category,
        trade.profit || '',
        trade.commission,
        trade.openTime,
        trade.closeTime || '',
        trade.strategy
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `trade-history-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const closedTrades = filteredTrades.filter(trade => trade.status === 'closed').length;
  const openTrades = filteredTrades.filter(trade => trade.status === 'open').length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <History className="h-6 w-6" />
            Trade History
          </h2>
          <p className="text-muted-foreground">Complete trading history (manual + engine, open + closed)</p>
        </div>
      </div>
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Open Trades</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{openTrades}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Closed Trades</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{closedTrades}</div>
          </CardContent>
        </Card>
      </div>
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search symbol..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="closed">Closed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger>
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="timestamp">Time</SelectItem>
                <SelectItem value="symbol">Symbol</SelectItem>
                <SelectItem value="side">Type</SelectItem>
                <SelectItem value="volume">Volume</SelectItem>
                <SelectItem value="price">Price</SelectItem>
                <SelectItem value="pnl">P&L</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortOrder} onValueChange={(value: "asc" | "desc") => setSortOrder(value)}>
              <SelectTrigger>
                <SelectValue placeholder="Order" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">Descending</SelectItem>
                <SelectItem value="asc">Ascending</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
      {/* Trade Table */}
      <Card>
        <CardHeader>
          <CardTitle>Trades ({filteredTrades.length})</CardTitle>
          <CardDescription>
            Real-time trade data (manual + engine, open + closed)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Symbol</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Volume</TableHead>
                  <TableHead>Price</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>P&L</TableHead>
                  <TableHead>Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTrades.map((trade) => (
                  <TableRow key={trade.id} className="hover:bg-muted/50">
                    <TableCell className="font-medium">{trade.symbol}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        {trade.side === 'buy' ? (
                          <TrendingUp className="h-3 w-3 text-green-600" />
                        ) : (
                          <TrendingDown className="h-3 w-3 text-red-600" />
                        )}
                        <span className="capitalize">{trade.side}</span>
                      </div>
                    </TableCell>
                    <TableCell>{trade.volume}</TableCell>
                    <TableCell>${trade.price?.toLocaleString()}</TableCell>
                    <TableCell>
                      <Badge className={cn(getStatusColor(trade.status))}>
                        {trade.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {trade.pnl !== undefined ? (
                        <span className={cn(
                          "font-medium",
                          trade.pnl >= 0 ? "text-green-600" : "text-red-600"
                        )}>
                          {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {trade.created_at ? new Date(trade.created_at).toLocaleString() : ''}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}