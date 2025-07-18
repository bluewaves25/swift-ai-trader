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
import { apiService } from "@/services/api";

interface Trade {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  volume: number;
  openPrice: number;
  closePrice?: number;
  status: 'open' | 'closed' | 'cancelled';
  broker: 'binance' | 'exness';
  category: 'crypto' | 'forex' | 'commodities' | 'indices';
  profit?: number;
  commission: number;
  openTime: string;
  closeTime?: string;
  strategy: string;
  userId: string;
}

export function TradeHistory() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [filteredTrades, setFilteredTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [brokerFilter, setBrokerFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [sortBy, setSortBy] = useState("openTime");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const { toast } = useToast();

  useEffect(() => {
    fetchTrades();
  }, []);

  useEffect(() => {
    filterAndSortTrades();
  }, [trades, searchTerm, statusFilter, brokerFilter, categoryFilter, sortBy, sortOrder]);

  const fetchTrades = async () => {
    setLoading(true);
    try {
      const data = await apiService.getTrades();
      setTrades(data || []);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch trade history",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortTrades = () => {
    let filtered = trades.filter(trade => {
      const matchesSearch = trade.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           trade.strategy.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === "all" || trade.status === statusFilter;
      const matchesBroker = brokerFilter === "all" || trade.broker === brokerFilter;
      const matchesCategory = categoryFilter === "all" || trade.category === categoryFilter;
      
      return matchesSearch && matchesStatus && matchesBroker && matchesCategory;
    });

    filtered.sort((a, b) => {
      let aValue: any = a[sortBy as keyof Trade];
      let bValue: any = b[sortBy as keyof Trade];
      
      if (sortBy === 'openTime' || sortBy === 'closeTime') {
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
      // TODO: Implement API call to close trade
      setTrades(prev => prev.map(trade => 
        trade.id === tradeId 
          ? { ...trade, status: 'closed' as const, closeTime: new Date().toISOString() }
          : trade
      ));
      
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

  const totalProfit = filteredTrades.reduce((sum, trade) => sum + (trade.profit || 0), 0);
  const totalCommission = filteredTrades.reduce((sum, trade) => sum + trade.commission, 0);
  const openTrades = filteredTrades.filter(trade => trade.status === 'open').length;
  const closedTrades = filteredTrades.filter(trade => trade.status === 'closed').length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <History className="h-6 w-6" />
            Trade History
          </h2>
          <p className="text-muted-foreground">Complete trading history across all brokers and instruments</p>
        </div>
        <Button onClick={exportTrades} variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Export CSV
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total P&L</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={cn("text-2xl font-bold", totalProfit >= 0 ? "text-green-600" : "text-red-600")}>
              ${totalProfit.toFixed(2)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Commission</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">${totalCommission.toFixed(2)}</div>
          </CardContent>
        </Card>
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
          <div className="grid gap-4 md:grid-cols-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search symbol or strategy..."
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
            <Select value={brokerFilter} onValueChange={setBrokerFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Broker" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Brokers</SelectItem>
                <SelectItem value="binance">Binance</SelectItem>
                <SelectItem value="exness">Exness MT5</SelectItem>
              </SelectContent>
            </Select>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="crypto">Crypto</SelectItem>
                <SelectItem value="forex">Forex</SelectItem>
                <SelectItem value="commodities">Commodities</SelectItem>
                <SelectItem value="indices">Indices</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger>
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="openTime">Open Time</SelectItem>
                <SelectItem value="closeTime">Close Time</SelectItem>
                <SelectItem value="symbol">Symbol</SelectItem>
                <SelectItem value="profit">Profit</SelectItem>
                <SelectItem value="volume">Volume</SelectItem>
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
            Real-time trade data from Binance and Exness MT5
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Symbol</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Volume</TableHead>
                  <TableHead>Open Price</TableHead>
                  <TableHead>Close Price</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Broker</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>P&L</TableHead>
                  <TableHead>Commission</TableHead>
                  <TableHead>Open Time</TableHead>
                  <TableHead>Strategy</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTrades.map((trade) => (
                  <TableRow key={trade.id} className="hover:bg-muted/50">
                    <TableCell className="font-medium">{trade.symbol}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        {trade.type === 'buy' ? (
                          <TrendingUp className="h-3 w-3 text-green-600" />
                        ) : (
                          <TrendingDown className="h-3 w-3 text-red-600" />
                        )}
                        <span className="capitalize">{trade.type}</span>
                      </div>
                    </TableCell>
                    <TableCell>{trade.volume}</TableCell>
                    <TableCell>${trade.openPrice.toLocaleString()}</TableCell>
                    <TableCell>
                      {trade.closePrice ? `$${trade.closePrice.toLocaleString()}` : '-'}
                    </TableCell>
                    <TableCell>
                      <Badge className={cn(getStatusColor(trade.status))}>
                        <div className="flex items-center gap-1">
                          {getStatusIcon(trade.status)}
                          {trade.status}
                        </div>
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={cn(getBrokerColor(trade.broker))}>
                        {trade.broker.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {trade.category}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {trade.profit !== undefined ? (
                        <span className={cn(
                          "font-medium",
                          trade.profit >= 0 ? "text-green-600" : "text-red-600"
                        )}>
                          {trade.profit >= 0 ? '+' : ''}${trade.profit.toFixed(2)}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="text-orange-600">${trade.commission.toFixed(2)}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(trade.openTime).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">{trade.strategy}</Badge>
                    </TableCell>
                    <TableCell>
                      {trade.status === 'open' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleCloseTrade(trade.id)}
                          className="h-8 w-8 p-0"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
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