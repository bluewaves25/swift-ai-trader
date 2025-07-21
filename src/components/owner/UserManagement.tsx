import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Switch } from "@/components/ui/switch";
import { Users, Search, UserCheck, UserX, DollarSign, TrendingUp, Activity } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { cn } from "@/lib/utils";

interface User {
  id: string;
  email: string;
  role: string;
  is_admin: boolean;
  created_at: string;
  is_active: boolean; // <-- Added this line
  profile?: {
    full_name: string;
  };
  portfolio?: {
    total_balance: number;
    realized_pnl: number;
  };
  stats: {
    totalTrades: number;
    winRate: number;
    profit: number;
    isActive: boolean;
  };
}

export function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const { toast } = useToast();
  const { user: currentUser } = useAuth();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      // Fetch users (excluding the current admin/owner)
      const { data: usersData, error: usersError } = await supabase
        .from('users')
        .select(`
          id, email, role, is_admin, is_active, created_at,
          profiles (full_name),
          portfolios (total_balance, realized_pnl)
        `)
        .neq('id', currentUser?.id)
        .neq('role', 'owner');

      if (usersError) throw usersError;

      // Fetch trade statistics for each user
      const usersWithStats = await Promise.all(
        (usersData || []).map(async (user: any) => {
          const { data: trades } = await supabase
            .from('trades')
            .select('*')
            .eq('user_id', user.id);

          const totalTrades = trades?.length || 0;
          const winningTrades = trades?.filter(t => t.status === 'filled').length || 0;
          const winRate = totalTrades > 0 ? (winningTrades / totalTrades) * 100 : 0;
          const profit = user.portfolios?.[0]?.realized_pnl || 0;

          return {
            ...user,
            is_active: user.is_active ?? true, // fallback to true if undefined
            stats: {
              totalTrades,
              winRate,
              profit,
              isActive: user.is_active ?? true
            }
          };
        })
      );

      setUsers(usersWithStats);
    } catch (error) {
      console.error('Error fetching users:', error);
      toast({
        title: "Error",
        description: "Failed to fetch users",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (userId: string, currentStatus: boolean) => {
    setActionLoading(userId);
    try {
      // Call backend or Supabase to toggle user status
      const { error } = await supabase
        .from('users')
        .update({ is_active: !currentStatus })
        .eq('id', userId);
      if (error) throw error;
      setUsers(prev => 
        prev.map(user => 
          user.id === userId 
            ? { ...user, is_active: !currentStatus, stats: { ...user.stats, isActive: !currentStatus } }
            : user
        )
      );
      toast({
        title: `User ${!currentStatus ? 'Activated' : 'Deactivated'}`,
        description: `User account has been ${!currentStatus ? 'activated' : 'deactivated'}`,
        className: "bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update user status",
        variant: "destructive"
      });
    } finally {
      setActionLoading(null);
    }
  };

  const filteredUsers = users.filter(user =>
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.profile?.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getInitials = (name: string | undefined, email: string) => {
    if (name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase();
    }
    return email.substring(0, 2).toUpperCase();
  };

  const getUserStats = () => {
    const totalUsers = users.length;
    const activeUsers = users.filter(u => u.stats.isActive).length;
    const totalBalance = users.reduce((acc, u) => acc + (u.portfolio?.total_balance || 0), 0);
    const avgWinRate = users.reduce((acc, u) => acc + u.stats.winRate, 0) / totalUsers || 0;

    return { totalUsers, activeUsers, totalBalance, avgWinRate };
  };

  const stats = getUserStats();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span>Loading users...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">User Management</h2>
        <Badge variant="outline" className="px-3 py-1">
          <Users className="h-3 w-3 mr-1" />
          {stats.activeUsers}/{stats.totalUsers} Active
        </Badge>
      </div>

      {/* User Statistics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-600" />
              <div className="text-2xl font-bold">{stats.totalUsers}</div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <UserCheck className="h-4 w-4 text-green-600" />
              <div className="text-2xl font-bold text-green-600">{stats.activeUsers}</div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Balance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-purple-600" />
              <div className="text-2xl font-bold text-purple-600">
                ${stats.totalBalance.toLocaleString()}
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Win Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-orange-600" />
              <div className="text-2xl font-bold text-orange-600">
                {stats.avgWinRate.toFixed(1)}%
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>User Directory</CardTitle>
          <CardDescription>
            Manage user accounts and monitor trading activity
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search users by email or name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Users Table */}
          <div className="rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Balance</TableHead>
                  <TableHead>Trades</TableHead>
                  <TableHead>Win Rate</TableHead>
                  <TableHead>P&L</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id} className="hover:bg-muted/50">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarFallback className="bg-gradient-to-br from-blue-100 to-purple-100 text-blue-700">
                            {getInitials(user.profile?.full_name, user.email)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium">
                            {user.profile?.full_name || 'No name'}
                          </div>
                          <div className="text-sm text-muted-foreground">{user.email}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">
                        ${(user.portfolio?.total_balance || 0).toLocaleString()}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Activity className="h-3 w-3 text-muted-foreground" />
                        {user.stats.totalTrades}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className={cn(
                        "font-medium",
                        user.stats.winRate >= 60 ? "text-green-600" : "text-red-600"
                      )}>
                        {user.stats.winRate.toFixed(1)}%
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className={cn(
                        "font-medium",
                        user.stats.profit >= 0 ? "text-green-600" : "text-red-600"
                      )}>
                        ${user.stats.profit.toFixed(2)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={user.stats.isActive ? "default" : "secondary"}
                        className={cn(
                          user.stats.isActive 
                            ? "bg-green-100 text-green-800 border-green-200" 
                            : "bg-red-100 text-red-800 border-red-200"
                        )}
                      >
                        {user.stats.isActive ? "Active" : "Suspended"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={user.stats.isActive}
                          onCheckedChange={() => toggleUserStatus(user.id, user.stats.isActive)}
                          disabled={actionLoading === user.id}
                          className="data-[state=checked]:bg-green-600"
                        />
                        {actionLoading === user.id && (
                          <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                        )}
                      </div>
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